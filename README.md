🐝 Bee and Plant Data Exploration — Computer Science Capstone Project 🐝

# Overview

This repository contains work focused on data exploration and behavioral analysis of bee–flower interactions. Our goal is to leverage machine learning and data visualization techniques to study pollinator behavior patterns and help develop an interactive front-end tool for exploring these relationships.

The project integrates data science, machine learning, and web development to provide researchers and land managers in Oregon with an accessible way to investigate how bees interact with different flower species — insights that can contribute to ecological monitoring, pollination research, and environmental conservation efforts.

# Workflow

## Fork

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
