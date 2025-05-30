## Intro
DIY ATS resume reviewer

## How to get started
1. git clone this repo by running `git clone <url>`
2. create a `.env` file in `@/backend/` and add `PINECONE_API_KEY=<your_api_key>` in it
3. in `@/backend/` run `python -m venv venv` then run `venv\scripts\activate`
4. run `pip install -r requirements.text`
5. in `@/frontend/` run `npm install`

## How to run the app
1. run `cd backend`
2. run `venv\scripts\activate`
3. run `fastapi dev main.py`
4. on another terminal run `cd frontend`
5. run `npm run dev`
6. click on `http://localhost:3000`
7. paste a sample job description from `@/backend/job-descriptions`; upload your resume in pdf or use the one from `@/backend/resumes`
8. it might not work the first time, but the second time onward it works

## Frontend
1. from `ats-resume-reviewer` run `cd frontend`
2. run `npm run dev`

## Backend
1. from `ats-resume-reviewer` run `cd backend`
2. run `venv\scripts\activate`
3. run `fastapi dev main.py`
4. How to test:

<ul>
    <li>click on `http://127.0.0.1:8000/docs`</li>
    <li>upload your sample pdf file and paste job description</li>
    <li>run it</li>
</ul>

5. make sure to `Ctrl + C` to terminate server then run `deactivate` to exit venv

