# Instructions to Run Locally

## One time Set Up
1. Ensure Python is installed: `python --version`
2. Ensure Node is installed: `node -v`
3. Ensure npm is installed: `npm -v`
4. Navigate to root directory: `cd ./..`
5. Create a Virtual Environment: `py -m venv .venv`
6. Activate Virtual Environment: `.venv/Scripts/activate`
7. Install dependencies: `pip install -r requirements.txt`
8. Return to src directory: `cd ./src`

## Start Front End
0. Ensure Virtual Environment is activated
1. Navigate to frontend directory: `cd ./frontend`
2. Install Node dependencies: `npm install`
3. Start local host: `npm run dev`
4. Open in browser at address provided
5. (Optional) Connect Backend functionality by following Instructions below

## Start Back End
0. Ensure Virtual Environment is activated
1. Navigate to backend directory: `cd ./backend`
2. Start FastApi with Uvicorn: `uvicorn main:app --reload`
3. (Optional) Make a request through implemented front end functionality
4. (Optional) Visit `127.0.0.1:8000/docs` in your browser to test different requests and responses
