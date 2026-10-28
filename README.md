# AI Resume Builder

Create an ATS-friendly resume, ATS report, improvement plan, and tailored cover letter from a student profile and job description. The project uses FastAPI and a React/Vite dashboard. All generation runs locally in the backend: no AI provider, API key, or network quota is required.

## Requirements

- Python 3.10 or newer.
- Node.js 18 or newer.

## Run locally

Open PowerShell in the project folder and run these exact commands:

```powershell
cd C:\path\to\ai_resume_builder
```

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Create the document template if it is missing, then start the backend:

```powershell
python create_template.py
uvicorn main:app --reload
```

Leave that terminal open. The backend is ready when `http://localhost:8000/docs` opens in your browser.

Open a **second** PowerShell window for the frontend:

```powershell
cd C:\Users\GURU\OneDrive\Desktop\ai_resume_builder\resume-builder-ui
npm install
npm run dev
```

Open the URL printed by Vite, normally `http://localhost:5173`.

If PowerShell blocks environment activation, run this once in the same terminal and then activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## Verify the app

1. Paste your details into **Student profile** and **Job description**.
2. Select **Generate Resume**. Confirm the preview and DOCX download appear.
3. Select **Check ATS Score**. Confirm score, keywords, and improvement plan appear.
4. Select **Generate Cover Letter** and test **Copy to Clipboard**.

Generation is deterministic and uses only the profile and job description you provide. It does not invent details, but unlike a hosted language model, it will not paraphrase or enrich sparse input; review all wording before applying.

PDF download is optional: it appears only when LibreOffice or the Windows-compatible `docx2pdf` conversion succeeds. DOCX download always remains available.

## Project structure

```text
main.py                  FastAPI endpoints
services/local_generator.py  Offline resume and application-material generation
services/export.py       Document export
inputs/                  Demo profile and job description
templates/               Generated DOCX resume template
output/                  Generated documents
resume-builder-ui/       React and Vite frontend
```

## API endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/generate-resume` | Generate a resume plus document links |
| POST | `/ats-report` | Compare a resume to a job description |
| POST | `/improvement-plan` | Create a skills and certification roadmap |
| POST | `/cover-letter` | Generate a tailored cover letter |
| GET | `/download/{filename}` | Download an output file |
