# Red Hat Assignment SRE

## Problem statement -

The task is to build a tool, in which for a given list of github repositories, it identifies all the Dockerfile files inside each repository, extracts the image names from the **FROM** statement, and returns a json with the aggregated information for all the repositories.

## Pre-requisite -

- python 3+
- Docker (Optional)
- Kubernetes cluster (Optional)

## How to run?

```shell
$ git clone git@github.com:amitech/redhat-assignment.git
$ cd redhat-assignment
$ pip3 install -r requirements.txt
$ python3 dockerfile_scanner.py https://gist.githubusercontent.com/jmelis/c60e61a893248244dc4fa12b946585c4/raw/25d39f67f2405330a6314cad64fac423a171162c/sources.txt
```

### Example -

```shell
$ python3 dockerfile_scanner.py -h
usage: dockerfile_scanner.py [-h] url

Enter valid url which contains github repo url and commit SHA

positional arguments:
  url         URL which contains github repo url and commit SHA

optional arguments:
  -h, --help  show this help message and exit


$ python3 dockerfile_scanner.py https://gist.githubusercontent.com/jmelis/c60e61a893248244dc4fa12b946585c4/raw/25d39f67f2405330a6314cad64fac423a171162c/sources.txt
{
  "data": {
    "https://github.com/app-sre/qontract-reconcile.git:30af65af14a2dce962df923446afff24dd8f123e": {
      "dockerfiles/Dockerfile": [
        "quay.io/app-sre/qontract-reconcile-base:0.2.1"
      ]
    },
    "https://github.com/app-sre/container-images.git:c260deaf135fc0efaab365ea234a5b86b3ead404": {
      "jiralert/Dockerfile": [
        "registry.access.redhat.com/ubi8/go-toolset:latest",
        "registry.access.redhat.com/ubi8-minimal:8.2"
      ],
      "qontract-reconcile-base/Dockerfile": [
        "registry.access.redhat.com/ubi8/ubi:8.2",
        "registry.access.redhat.com/ubi8/ubi:8.2",
        "registry.access.redhat.com/ubi8/ubi:8.2"
      ]
    }
  }
}

# First line format is incorrect, it will skip that line
$ python3 dockerfile_scanner.py https://test1.amitech.me/sources.txt
2021-11-07 18:20:20,081 - WARNING - Invalid Github URL and/or SHA. Skipping for line https://github.com/app-sre/qontract-reconcile.git
{
  "data": {
    "https://github.com/app-sre/container-images.git:c260deaf135fc0efaab365ea234a5b86b3ead404": {
      "jiralert/Dockerfile": [
        "registry.access.redhat.com/ubi8/go-toolset:latest",
        "registry.access.redhat.com/ubi8-minimal:8.2"
      ],
      "qontract-reconcile-base/Dockerfile": [
        "registry.access.redhat.com/ubi8/ubi:8.2",
        "registry.access.redhat.com/ubi8/ubi:8.2",
        "registry.access.redhat.com/ubi8/ubi:8.2"
      ]
    }
  }
}


```

## Build Docker Image -

```shell
$ docker build -t docker-scanner:latest .
$ docker tag docker-scanner:latest docker_registry_url_username/docker-scanner   # Tag image with docker registry url and username to push on docker registry
$ docker push docker_registry_url_username/docker-scanner:latest
```

## Run with Docker -

We need to pass URL in environment variable **REPOSITORY_LIST_URL**. Example -

```shell
$ docker run --env REPOSITORY_LIST_URL=https://gist.githubusercontent.com/jmelis/c60e61a893248244dc4fa12b946585c4/raw/25d39f67f2405330a6314cad64fac423a171162c/sources.txt docker-scanner:latest
{
  "data": {
    "https://github.com/app-sre/qontract-reconcile.git:30af65af14a2dce962df923446afff24dd8f123e": {
      "dockerfiles/Dockerfile": [
        "quay.io/app-sre/qontract-reconcile-base:0.2.1"
      ]
    },
    "https://github.com/app-sre/container-images.git:c260deaf135fc0efaab365ea234a5b86b3ead404": {
      "jiralert/Dockerfile": [
        "registry.access.redhat.com/ubi8/go-toolset:latest",
        "registry.access.redhat.com/ubi8-minimal:8.2"
      ],
      "qontract-reconcile-base/Dockerfile": [
        "registry.access.redhat.com/ubi8/ubi:8.2",
        "registry.access.redhat.com/ubi8/ubi:8.2",
        "registry.access.redhat.com/ubi8/ubi:8.2"
      ]
    }
  }
}
```

## Running as Kubernetes Job -

Make sure Kuberenetes is authenticated to pull images from above docker registry OR push image as public.
Update Github repos URL in spec.template.spec.containers.env.value in [job.yaml](./job.yaml) file.  

```shell
$ kubectl apply -f job.yaml
job.batch/dockerfile-scanner created

$ kubectl get jobs
NAME                 COMPLETIONS   DURATION   AGE
dockerfile-scanner   1/1           15s        5m40s

$ kubectl get pods
NAME                       READY   STATUS      RESTARTS   AGE
dockerfile-scanner-949l9   0/1     Completed   0          5m56s

$ kubectl logs dockerfile-scanner-949l9 
{
  "data": {
    "https://github.com/app-sre/qontract-reconcile.git:30af65af14a2dce962df923446afff24dd8f123e": {
      "dockerfiles/Dockerfile": [
        "quay.io/app-sre/qontract-reconcile-base:0.2.1"
      ]
    },
    "https://github.com/app-sre/container-images.git:c260deaf135fc0efaab365ea234a5b86b3ead404": {
      "jiralert/Dockerfile": [
        "registry.access.redhat.com/ubi8/go-toolset:latest",
        "registry.access.redhat.com/ubi8-minimal:8.2"
      ],
      "qontract-reconcile-base/Dockerfile": [
        "registry.access.redhat.com/ubi8/ubi:8.2",
        "registry.access.redhat.com/ubi8/ubi:8.2",
        "registry.access.redhat.com/ubi8/ubi:8.2"
      ]
    }
  }
}

```

## Additional information -

I have used [pylint](https://pylint.pycqa.org/en/latest/) to follow Python coding standards.

```shell
$ pylint dockerfile_scanner.py

--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00
```

