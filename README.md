# New Hospital Project

This workspace contains a minimal Flask backend and a Vite React frontend scaffold.

Backend (API):
- Folder: `BACKEND`
- Run:

```bash
python -m venv .venv
.venv\Scripts\activate    # Windows
pip install -r BACKEND/requirements.txt
python BACKEND/app.py
```

Frontend (React + Vite):
- Folder: `FRONTEND/frontend`
- Run:

```bash
cd FRONTEND/frontend
npm install
npm run dev
```

The backend listens on http://localhost:8000 by default. The frontend dev server runs on port 5173 (Vite default).
