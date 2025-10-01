import importlib.util
import os
import sys
from types import ModuleType

import pytest


def _load_module_with_env(env: dict[str, str]) -> ModuleType:
    path = os.path.join("src", "human_evaluation_tool", "__init__.py")
    spec = importlib.util.spec_from_file_location(
        "human_evaluation_tool.temp_init_module", path, submodule_search_locations=[]
    )
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    module_name = spec.name  # type: ignore[union-attr]
    saved_override = os.environ.pop("SQLALCHEMY_DATABASE_URI", None)
    saved_values = {key: os.environ.get(key) for key in env}
    source_config = os.path.join(os.getcwd(), "flask.config.json")
    target_config = os.path.abspath(os.path.join(os.getcwd(), "..", "..", "flask.config.json"))
    created_config = False
    try:
        os.environ.update(env)
        if os.path.exists(source_config) and not os.path.exists(target_config):
            with open(source_config, "r", encoding="utf-8") as src, open(
                target_config, "w", encoding="utf-8"
            ) as dst:
                dst.write(src.read())
            created_config = True
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        for key, value in saved_values.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        if saved_override is not None:
            os.environ["SQLALCHEMY_DATABASE_URI"] = saved_override
        else:
            os.environ.pop("SQLALCHEMY_DATABASE_URI", None)
        if created_config:
            os.remove(target_config)
        sys.modules.pop(module_name, None)


def test_database_uri_constructed_when_override_missing():
    module = _load_module_with_env(
        {
            "JWT_SECRET_KEY": "secret",
            "DB_HOST": "localhost",
            "DB_NAME": "db",
            "DB_PASSWORD": "pw",
            "DB_PORT": "5432",
            "DB_USER": "user",
        }
    )
    assert module.app.config["SQLALCHEMY_DATABASE_URI"].startswith("postgresql://")


def test_database_uri_missing_env_raises_runtime_error(monkeypatch):
    for key in ["DB_HOST", "DB_NAME", "DB_PASSWORD", "DB_PORT", "DB_USER"]:
        monkeypatch.delenv(key, raising=False)

    with pytest.raises(RuntimeError):
        _load_module_with_env({"JWT_SECRET_KEY": "secret"})
