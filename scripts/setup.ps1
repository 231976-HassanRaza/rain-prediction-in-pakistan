# Run from project root:  powershell -ExecutionPolicy Bypass -File scripts\setup.ps1
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
.\.venv\Scripts\python.exe backend\make_payload.py
.\.venv\Scripts\python.exe backend\test_pipeline.py
.\.venv\Scripts\python.exe -m pytest -q backend\tests
Push-Location frontend
npm install
Pop-Location
Write-Host "SETUP DONE. Now open 2 terminals: run scripts\start_flask.ps1 and scripts\start_angular.ps1"
