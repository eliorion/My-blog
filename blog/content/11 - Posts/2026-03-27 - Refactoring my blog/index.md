---
title: 'Refactoring My Blog'
date: '2026-03-27'
draft: false
aliases: ["/11---posts/2026-03-27---refactoring-my-blog/"]
topics:
  - blog
  - refactoring
tags:
  - blog
  - hugo
  - CI/CD
projects:
  - blog
categories:
weight: 10 # Lower number = toper in the list
cover:
  image: "cover.png"
  alt: 'Refactoring My Blog'
  caption: ""
  relative: true
  hidden: true            # si true → pas de cover sur la page du post
  hiddenInList: true      # si true → pas de cover dans la liste des posts
  hiddenInSingle: false    # si true → pas de cover sur la page individuelle
---

## **Why refactoring?**

The first reason is that I didn’t put much thought into this side project. Also, I spent time trying to build a complicated CI/CD pipeline with GitHub Actions, and the result was not what I wanted.

## **Separate tasks**

In the previous version of my blog, all the Hugo file system and the translations were in the `root` of the project. I started to structure things better by separating tasks:

* `/blog`: contains the Hugo site with all its resources
* `/translation`: [**!!not implemented yet!!**] all resources for translation
* `/...`: future features or tasks I could add without making the project root messy

## **New framework**

I discovered the Johnny Decimal system and started to implement it in my personal life. I think it is a game changer for my perspective because I was very focused on labeling things with categories.

In my blog, I started to label every post I made, but I got stuck very quickly with this approach. After that, I decided to use a very granular, date-based structure:

```bash
content/posts
├── 2025
│   ├── 09
│   │   ├── 00-intro
│   │   ├── 01-first-step-in-homelab
│   │   ├── 02-network-configuration
│   └── 12
│       ├── new-homelab-workflow
│       └── persistent-volume-with-nfs
└── 2026
    └── 01
        └── become-beginer-again
```

It was messy and had no real consistency in organization or naming.

The Johnny Decimal system helped me realize that I can simply use bundles with an `index.md` file and keep all related resources inside it. Also, I can rely on the native date of the post for natural sorting.

## **New organization for posts**

With this in mind, I chose a simpler structure:

```bash
blog/content/posts/
├── 2025-08-31 - Intro
├── 2025-09-01 - First-step-in-homelab
├── 2025-09-02 - Network-configuration
├── 2025-09-15 - Architecture-learning-project
├── 2025-12-11 - New-homelab-workflow
├── 2025-12-11 - Persistent-volume-with-nfs
├── 2026-01-01 - Become-beginer-again
├── 2026-02-23 - Why learn linux before containerisation
├── 2026-02-26 - First GitOps implementation
├── 2026-03-24 - Containerise Python application
└── 2026-03-27 - Refactoring my blog
```

With this approach, I have no restriction on topics. Even if I create another post with the same title, it won’t conflict because the date ensures natural sorting.

Also, I use the same date-based logic in my own Johnny Decimal system, so it takes less effort to understand what’s going on and how to create a new post.

## **Clean up the CI/CD pipeline**

The previous version was very messy and unnecessarily complicated. The process was:

* make a change (e.g., add a new post) on the `dev` branch
* the pipeline merges `dev` into `main`
* a Hugging Face LLM translates `*/index.md` into `*/index.fr.md`
* the pipeline builds and deploys the site to GitHub Pages

### **Simple new pipeline**

The new pipeline is much simpler because I decided not to handle translation for now:

1. add a new post directly to the `main` branch (**ONLY NEW POSTS**)
2. push to remote
3. GitHub Actions builds the Hugo site
4. GitHub Actions deploys it to GitHub Pages

For now, I am the only one using this repository, so I don’t need a complex CI/CD pipeline.

## **Adding posts becomes simpler**

One of the goals of this refactoring is to make post creation simple.

With this setup, I can create a new post with a single command:

Post creation for this one:

```bash
hugo new content -k default "posts/2026-03-28 - Refactoring my blog/index.md" -s blog
```
