# Human Evaluation Tool

## 1. Building Dockerfile

You can build this project with the following command:

```sh
$ docker build -t yaraku/human-evaluation-tool .
```

That should build the docker image. Once it's done, you can execute it with a command like this:

```sh
$ docker run --rm -it -p 8000:8000 yaraku/human-evaluation-tool
```
