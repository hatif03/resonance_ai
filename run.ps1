# Run the backend within the virtual environment
& "$PSScriptRoot\venv\Scripts\Activate.ps1"
Set-Location "$PSScriptRoot\backend"
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
