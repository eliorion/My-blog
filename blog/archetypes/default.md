---
title: '{{ index (split .File.ContentBaseName " - ") 1 | title }}'
date: '{{ time.Now.Format "2006-01-02" }}'
draft: false
topics:
tags:
projects:
categories:
weight: 10 # Lower number = toper in the list
cover:
  image: "cover.svg"
  alt: '{{ index (split .File.ContentBaseName " - ") 1 | title }}'
  caption: ""
  relative: true
  hidden: true            # si true → pas de cover sur la page du post
  hiddenInList: true      # si true → pas de cover dans la liste des posts
  hiddenInSingle: false    # si true → pas de cover sur la page individuelle
---
