# Human Evaluation Tool

## 0. Usage Demo

Below is a quick video showing how the Human Evaluation Tool looks and works:

https://github.com/yaraku/he-tool/assets/5934186/bb1dcf1c-a1e2-464c-af0a-1225e57eef56

## 1. Building Dockerfile

You can build this project with the following command:

```sh
$ docker build -t yaraku/human-evaluation-tool .
```

That should build the docker image. Once it's done, you can execute it with a command like this:

```sh
$ docker run --rm -it -p 8000:8000 yaraku/human-evaluation-tool
```
