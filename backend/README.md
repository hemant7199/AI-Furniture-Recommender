# Backend (No venv) Quickstart (Windows PowerShell)

```powershell
# From this folder:
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
# If uvicorn not found:
# .\..\..\Python\Scripts\uvicorn.exe app.main:app --reload --port 8000
```
