## Intro
DIY ATS resume reviewer

## Frontend
1. from `ats-resume-reviewer` run `cd frontend`
2. run `npm run dev`

## Backend
1. from `ats-resume-reviewer` run `cd backend`
2. run `venv\scripts\activate`
3. run `fastapi dev main.py` or `uvicorn main:app --reload`
4. How to test:

<ul>
    <li>click on `http://127.0.0.1:8000/docs`</li>
    <li>upload your sample pdf file and paste job description</li>
    <li>run it</li>
</ul>

5. make sure to `Ctrl + C` to terminate server then run `deactivate` to exit venv

