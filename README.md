# **My temporary blog use Hugo and GitHub V2**

I have multiples projects build in my own, but I never expose to other. So, I allway want to
have my own server with my own domaine name, but for personal resons I can't have persistant server.
I found a solution to host blog in minutes with hugo and GitHub, so was I.

## **Blog access**

[My blog](https://eliorion.github.io/My-blog)

## **Topics**

I am a tech guy, work in **developpement** first, with **management**, **process optimisation** and **project management**.

## **Post cration process**

### **Archetypes**

The archetypes give you the template when you creat new content. This is what is defined:

- `default.md`: use when nothing is specify
- `kubernetes.md`: add some kubernetes labels and tags for a post base on kubernetes
- `homlab.md`: add specifique project, labels and tags

Use the `-k ARCHETYPE` option to specify which one you wanna use. By default it's the first one who is choose.

### **Content structure**

The `content` directory contain all the ressource use for the site. The structure use the Jhonny Decimals system with the `11 - Posts` folder who containe all the posts of the blog.
The `11 - Posts` folder is structured with date format for sort all posts by date naturaly, note by topics. The format use `YYYY-MM-DD - [POST TITLE]`.

## **Create new post**

### **!Blog script in progress!**

A blog script is plan for simplify the utilisation.

### **Manuel creation**

With the default archetypes file:

```bash
hugo new content -k [ARCHETYPE]  "posts/[CREATION DATE (YYYY-MM-DD)] - [POST TITLE]/index.md" -s blog
```

- `new content`: creation of content
- `-k [ARCHETYPE]`: select the temple for your content on the `archetypes` folder
- `"posts/[CREATION DATE (YYYY-MM-DD)] - [POST TITLE]/index.md"`: create the right folder in `11 - Posts` with the bundle
- `-s blog`: redirect the base Hugo floder to `blog` then `root`

Exemple:

```bash
hugo new content -k default  "posts/2026-03-28 - Refactoring my blog/index.md" -s blog
```

With specifique template file :

```bash
hugo --kind <NAME_OF_YOUR_TEMPLATE> posts/<NAME_OF_YOUR_POST>/index.md
```

## **Generate localy**

If you want to test, or writ and see the result in live, you can use this command:

```bash
hugo server -s blog
```

The server is accessible at: [Local access](http://localhost:1313).

## **Pipeline status**

Eliorion blog
[![.github/workflows/hugo.yaml](https://github.com/eliorion/My-blog/actions/workflows/hugo.yaml/badge.svg?branch=main)](https://github.com/eliorion/My-blog/actions/workflows/hugo.yml)
