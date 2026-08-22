---
title: Containerise Python application
date: 2026-03-27T09:38:10+01:00
draft: false
aliases: ["/11---posts/2026-03-24---containerise-python-application/"]
topics:
  - Homelab
  - DevOps
tags:
projects:
  - KubeCraft_learning
categories:
  - IT
  - Learning
weight: 2
cover:
  image: cover.svg
  alt: homelab
  caption: ""
  relative: true
  hidden: true
  hiddenInList: true
  hiddenInSingle: false
---
## **Fist conplete containerise Python application**

In the context of the KubeCraft course, I needed to create a complet containerise Python application from scratch. The course is focus on the DecSecOps implementation, note the Python part.

## **Pre-require**

The first step to have a nice DevSecOps environnement is the team work. I will be the only one who use this project, but in reality a hole team will need to have access and modify some piece of the application. First think in mind when you have IT project and team work, you think about Git. Even you haven't a team to work with, use Git is a nice way to have log of your work and explain why the application don't work after a modification, and be able to come back to a secure version.

### **Why standard commit is required**

Git is very useful anyways. However, when your project have more and more people on it, you can start facing some issue with the commit hell. This consist to have a good track of your commits, but you couldn't understand what's going on on this commit because is named like this:

- fix stuff
- update code
- changes
- bug fix login
- final version

So we all know this type of commits name on our repositories, and I am the first one who is guilty. The solution to have a nice and understandable Git history is to standardiese all this mess.
I discovered "Conventional commit" how explain how to have a proper naming commit base on what you do and what is the range of your intervention. For exemple, after the "Conventional commit", the 5 commits name above look like this:

- fix(auth): resolve login crash when password is empty
- feat(ui): add loading spinner to login button
- refactor(api): simplify user validation logic
- fix(session): prevent token expiration issue
- chore: clean unused imports in project

You can see how clean this is. On the first read you have what the commit purpuse is and what type of layout it touch, with a description very clear and understandable.

### **Why is complicated to implement**

This is a great idea but, if you simply said to your developer team and your operation team, some will take it with greace and implement the standard in instant, but for some of then or the new guy who just came to the team, it can be complecated to force people to use this standard. That why it's required to help your team to use the right format for the beginning at least. It's why the tool "Commitizen" is the perfect match. With simple setup and a Git hook, you can force people use the standard commit directly on the workstation of your team. And if you still forgot the standard, you just have to use the "Commitizen" guide to help you create the right commit name and description.

## **Setup the environnement**

### **Devcontainer setup**

To build the application, I choose to use a devcontainer with Docker install. For a DevOps engineer, best the best practice is to use devcontainers. So, if you have a new guy who came on the team, he can be up and running on the code in minutes. With this said I use DevPod to manage my differents project environnement because it's very convinient with my dotfiles configuration.

Whit that said, I use "Mise" to install my tools kit on the decontainer. To do so there is some setup to make:

".devcontainer/devcontainer.json":

```bash
{
  "build": {
    "context": "..",
    "dockerfile": "Dockerfile"
  },
  "postCreateCommand": "scripts/setup",
  "features": {
    "ghcr.io/devcontainers/features/docker-in-docker:2": {}
  },
  "forwardPorts": [
    "22111",
    "22112"
  ]
}
```

The devcontainer use the Dockerfile image as base image, install docker in docker to be able to use it in the container it self. This devcontainer execute the "setup" script and forware the ports `22111` and the `22112` for the developement.

".devcontainer/Dockerfile":

```bash
FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

COPY --from=jdxcode/mise /usr/local/bin/mise /usr/local/bin/

# make sure mise is activated in both zsh and bash. Might be overridden by a user's dotfiles.
RUN echo 'eval "$(mise activate bash)"' >> /home/vscode/.bashrc && \
  echo 'eval "$(mise activate zsh)"' >> /home/vscode/.zshrc
```

This file specify the base image of the devcontainer, and copy the binary of "mise", with the comment to activate it on the devcontainer.

"scripts/setup":

```bash

#!/bin/bash

/usr/local/bin/mise trust /workspaces/"$DEVPOD_WORKSPACE_ID"/mise.toml && /usr/local/bin/mise install
```

The setup script trust the workspaces and install all the dependencies of the project.

### **mise configuration**

"mise.toml":

```bash
[tools]
pre-commit = "latest"
python = "3.13"
trivy = "0.69.2"
uv = "latest"

[settings]
python.uv_venv_auto = true
idiomatic_version_file_enable_tools = ["python"]
experimental = true

[env]
APP_REPO = 'devops-study-app'
GITOPS_REPO = 'devops-study-app-gitops'

[hooks]
enter = "bash ./scripts/setup_project"
```

On this file, all the tools required for the project is set. Also, the hook execute the "scripts/setup_project" file when the devcontainer is create. This is the only one this script will be execute.

```bash
#!/bin/bash

if ! command -v cz >/dev/null && [ "$DEVPOD" = "true" ]; then
  git config --global push.autoSetupRemote true
  git config --global --add safe.directory /workspaces/devops-study-app/
  pip install --user pipx
  pipx install commitizen
  pre-commit install
  pre-commit install --hook-type commit-msg
fi
```

This file set "Git" to be able to use "pre-commit" to manage the commit message and verify if the standard are respected.

## **Python project structure**

The project structure is base on the standard Python structure. So, this is the current folder structure of the project:

```bash
└── src
    ├── backend
    │   ├── Dockerfile
    │   ├── pyproject.toml
    │   ├── README.md
    │   ├── src
    │   │   └── backend
    │   │       ├── __init__.py
    │   │       ├── config.py
    │   │       ├── main.py
    │   │       ├── models.py
    │   │       └── storage.py
    │   └── uv.lock
    └── frontend
        ├── Dockerfile
        ├── pyproject.toml
        ├── README.md
        ├── src
        │   └── frontend
        │       ├── __init__.py
        │       ├── main.py
        │       └── templates
        │           ├── base.html
        │           └── index.html
        └── uv.lock
```

With this structure, each area of the project is separate correctly with is own `pyproject.toml`. The goal is to use `uv` to build and run the two project, but in a container.

## **Containerisation of the application**

### **Creation of the Dockerfile**

The first step is to create the `Dockerfile` for the frontend and the backend application. For learning purpuse, I will spleet the end version of the file in four parts:

Backend `Dockerfile` V0:

```bash
# Base image of the container
FROM python:latest
# Install uv on the container
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Current directory is '/app'
WORKDIR /app
# Copy the current directory in the '/app' container directory
COPY . /app

# Use uv to compile the project
RUN uv sync --locked --no-editable
# Execute the backend binary with uv
CMD ["uv", "run", "study-tracker-api"]
```

The container is base on the Python latest image in the docker registery. It is a heavie image base on Debian with a lot of tools incorporate. There is many ways to save some space and performance but for now it good for the beginning.

### **Build the container image**

Use the `docker build` command with a flag for verisioning.

```bash
docker build -t backend:00 .
```

Now, with the command `docker images or docker image ls` see the image in your local Docker registery.
If you wanna go deeper in how the image is build of you can use `docker history backend:00` to see the layout of your image.

### **Run the image**

Run:

```bash
docker run backend:00
```

You can add the flag `-d` to execute the container in detach mode.

### **Securisation with `Trivy`**

Being able to push your image with a security audit is a good security practice for DevOps engineer. `Trivy`is one of the most popular security check use nowadays. For this project, I simply use for analyse the container images.

`Trivy` is olready install with `mise`, so it's simple to use directly in the devcontainer:

```bash
trivy image --format table --severity CRITICAL,HIGH backend:00
```

This command show you on a table forma the most danjerous security issues in your container image. So, with this version, trivy found some issues. This process is necessariy before run in production any image.

### **Image size optimisation**

The base image use is the default `Python:latest`, but if you seach in the Python Docker Hub registery, you will find many versions of the Python base image. By default, after build our image size 440MB. So, for a small application like that it's overkill. Plus, `Trivy` found most of the security issues on the Debian base image. So, if the image have less available tools, it's also mean less attacks surface possible for the hackers.

#### **Python slim**

Use a defined verion of Python with the subtatle `slim`: `FROM python:3.13-slim`.
  
You need to:

1. Rebuild your image with new tag like: 01
2. Scanne with `Trivy`
3. Run to verify if it's work

#### **Python alpine**

Use a defined verion of Python with the subtatle `alpine`: `FROM python:3.13-alpine`. The alpine image is creat very lightweigh and secure. So it's the perfect feet for our application. By the way Alpine image is hardely use on containerisation environnement.
  
You need to:

1. Rebuild your image with new tag like: 02
2. Scanne with `Trivy`
3. Run to verify if it's work

### **Build optimisation**

To be able to gain size on our image, it's possible to not add the Python files on the image but only the binary and just what the application absolutly needed to work. The method is to use a base image to build the project with cach, so our build will take less time, and after the build use another base image with only the binary of the application. This way the final image doesn't have to contain uv at all.

Backend `Dockerfile` V4:

```bash
# Building step
FROM python:3.13-alpine AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
# Change the working directory to the `app` directory
WORKDIR /app
# Install dependencies in a cache layer. This speeds up build time
RUN --mount=type=cache,target=/root/.cache/uv \
  --mount=type=bind,source=uv.lock,target=uv.lock \
  --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
  uv sync --locked --no-install-project --no-editable
# Copy the project into the intermediate image
COPY . /app
# Sync the project and install it, now that we have access to the source code
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --locked --no-editable

# Image creation
FROM python:3.13-alpine
# Create a non-root user and group with specific IDs
RUN addgroup -S -g 1000 app && adduser -S -u 1000 -G app app
# Copy the environment, but not the source code
COPY --from=builder --chown=app:app /app/.venv /app/.venv
# Switch to the non-root user
USER app
# Expose the correct port
EXPOSE 22112
# Run the application
CMD ["/app/.venv/bin/study-tracker-api"]
```
