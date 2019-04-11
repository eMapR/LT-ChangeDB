---
title: Directory Setup
layout: default
has_children: false
nav_order: 2
---

# Directory Setup
{:.no_toc}

## Table of contents
{:.no_toc .text-delta}

* TOC
{:toc}

There are three major directories that are required for the process of generating annual change polygons. 

1. A programming environment directory

2. A script directory

3. A project directory

All three directories could be created in a single parent folder or spread out among paths that make sense for your system (more on this in the following steps). For the purpose of this guide we’ll put all three directories in the same parent folder called **_LandTrendrGEE_**. We’ll put it directly under the C drive.

If you have write privilege to the C drive, create a folder at this location: **_C:\LandTrendrGEE_**, if you don’t have write permission to this directory, choose a different location.

You now should have a **LandTrendrGEE **folder somewhere on your computer. In the next few steps we’ll add the three major directories to it, making it look something like this:

```shell
C:\LandTrendrGEE
├───LandTrendrPyEnv
├───LT-ChangeDB
└───projects
    ├───<project head folder 1>
    ├───<project head folder 2>
    └───<etc>
```

Throughout this demo I’ll be referring to this directory structure frequently. Blah blah blah