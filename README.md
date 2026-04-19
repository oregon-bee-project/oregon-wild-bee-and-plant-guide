🐝 Bee and Plant Data Exploration — Computer Science Capstone Project 🐝

# Overview

This repository contains work focused on data exploration and behavioral analysis of bee–flower interactions. Our goal is to leverage machine learning and data visualization techniques to study pollinator behavior patterns and help develop an interactive front-end tool for exploring these relationships.

The project integrates data science, machine learning, and web development to provide researchers and land managers in Oregon with an accessible way to investigate how bees interact with different flower species — insights that can contribute to ecological monitoring, pollination research, and environmental conservation efforts.

# Workflow

## Fork

### **note:** If your working branch isn't showing up in the repo to merge but you have created it locally, run `git push --set-upstream origin <your-branch-name>` in your terminal to have it track to origin and you should be good

Fork is an awesome way to keep track of commits, branches, and the overall workflow. It is used commonly in the industry

### How to use

1. Download fork from [https://git-fork.com/], this should be free even though it says $59.99.
2. Once you have it downloaded and opened on your computer, make sure that you have cloned the repo onto your machine somewhere and know where it is
3. Go to the "file" option on your computer when the application is open (for example on mac it is in the top right of my screen, I don't know where that is for windows), it should give you a dropdown
4. Click on "open"
5. Navigate to the cloned repo and open it
6. Once you are here you should see a screen with a whole bunch of pathway looking things with commits on them
7. To checkout a branch, find the "branches" section on the right and either double click on the branch you want, or right click and select "checkout"
8. To branch into a new branch, right click on a branch and click "new branch"
9. You will not be allowed to branch or checkout somewhere else unless your changes are stashed or commited.
10. Stashing changes is basically saving your local changes for later use.
11. Staging your changes can be done very easily by going to your "local changes" and staging (or discarding) whatever changes you've made. Then when you are comfortable with that, you can commit the changed files with a message
12. Once changes have been commited, you can push them and then go to the repo and create a merge request for review.

# File Heirarchy Overview

- The `frontend` folder holds the files for the website developement. Currently there are just the basic 3 web dev source files but more may be needed

- The `model` folder will be where the ML/AI applications are developed. It contains a file for data loading, training, and model making

- The `data` folder will hold anything relating to the data for the model, this will make it easier to use in model development

- The `docs` folder will hold documents for assignments and other aspects of the projects. It is mainly used to keep everything clean and organized

# Running the app locally

**Prerequisite:** Make sure Node.js (version >= 18) is installed on your machine.  
You can check by running:

```
node -v
```

1. Clone the repository (if not already done).
2. From the project root, navigate to `frontend` and install dependencies:

```
cd src/frontend
npm install
```

3. Run the dev server:

```
npm run dev
```

4. Once the server is running, press `o + enter` to open the app in your browser (`q + enter` will stop the dev server).

# Backend Stress Guardrails (Render)

The API now includes fail-fast guardrails for heavy endpoints so public traffic cannot overwhelm the free Render instance.

## What is guarded

- `GET /api/detailed-report/`
- `POST /api/export-detailed-pdf/`
- `POST /api/export-pdf/`

When limits are exceeded, the API intentionally returns:

- `429` when too many heavy requests are already running.
- `503` when memory pressure is above threshold (if `psutil` is installed and memory guard is enabled).

Error responses include:

- `detail.code`
- `detail.message`
- `detail.retryAfterSeconds`

## Environment variables

All guardrails are configurable without code changes:

- `MAX_HEAVY_INFLIGHT` (default `1`): total concurrent heavy requests across guarded endpoints.
- `MAX_REPORT_INFLIGHT` (default `1`): concurrent `detailed-report` requests.
- `MAX_EXPORT_INFLIGHT` (default `1`): concurrent export requests.
- `MEMORY_GUARD_ENABLED` (default `true`): enables memory pressure rejection logic.
- `MEMORY_USAGE_REJECT_PCT` (default `88`): reject heavy requests when memory usage is at/above this percentage.
- `GUARDRAIL_RETRY_AFTER_SECONDS` (default `8`): retry hint returned to clients.
- `GUARDRAIL_LOG_REJECTIONS` (default `true`): logs when guardrails reject requests.

## Tuning guidance by deployment tier

- **Free/small RAM tiers:** start with all inflight limits at `1`.
- **After RAM upgrade:** raise limits gradually (for example one setting at a time) and run `stress_test.py` after each change.
- **If users see frequent 503s:** either lower concurrency settings or increase available RAM.
- **If memory guard is unavailable:** install `psutil` to enable memory-based rejection; concurrency guardrails still work without it.
