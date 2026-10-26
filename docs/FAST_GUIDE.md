# FAST GUIDE — finish the lab in ~45–60 minutes
Everything the manual asks you to *write* is already in this folder and tested. You only need to run commands,
take screenshots, and push to GitHub. Replace `D:\ml_project` with wherever you unzip the project.

## A. One-time installs (skip what you already have) — manual Stage 2
Install: VS Code, Python 3.12, Git, Node.js LTS, and make a GitHub account. Then in a NEW PowerShell:
```
py -3.12 --version
git --version
node --version
npm --version
```
Paste those 4 outputs into `docs\environment.txt` (screenshot them too).

## B. Open the project — Stage 3
1. Unzip `ml_project.zip` to `D:\ml_project` and run `cd D:\ml_project` then `code .`
2. One-command setup (venv + packages + tests + npm install):
```
powershell -ExecutionPolicy Bypass -File scripts\setup.ps1
```
Expected: `PASS: local inference`, `5 passed` ... wait for the last npm install to finish.
(If you prefer the manual's exact steps, use README section 5.)

## C. Check the model — Stages 4–5 (already done for you)
```
.\.venv\Scripts\Activate.ps1
python -c "import joblib; b=joblib.load('backend/models/model_bundle.joblib'); print(b.keys()); print(len(b['features'])); print(type(b['pipeline']))"
python backend\make_payload.py
python backend\test_pipeline.py
```
Expected: 68 features, `Prediction: [1]`, `Probabilities: [[0.195, 0.805]]`, `PASS: local inference`.
(Optional: `python backend\train_model.py` rebuilds the model from `data\model_ready.csv` in about a minute.)

## D. Flask API — Stages 6–7
**Terminal 1** (Terminal → New Terminal), keep it open:
```
cd D:\ml_project
.\.venv\Scripts\Activate.ps1
python backend\app.py
```
Browser: http://127.0.0.1:5000/health → `{"features":68,"status":"ok","task":"classification"}` (screenshot).

**Terminal 3** (new terminal, keep Terminal 1 running):
```
cd D:\ml_project
.\.venv\Scripts\Activate.ps1
curl.exe --noproxy "*" -i http://127.0.0.1:5000/health
curl.exe --noproxy "*" -i -X POST "http://127.0.0.1:5000/predict" -H "Content-Type: application/json" --data-binary "@backend/test_payload.json"
python backend\test_api.py
python -m pytest -q backend\tests
```
Expected: HTTP 200 twice, `PASS: API request`, `5 passed`. (Manual says 4 tests + the structure test = 5.)
Screenshot the pytest output.

## E. Angular — Stages 8–10
**Terminal 2** (new terminal), keep it open:
```
cd D:\ml_project\frontend
npm install        # only if setup.ps1 did not finish it
ng serve --open --proxy-config proxy.conf.json
```
If `ng` is blocked in PowerShell use `npx ng serve --open --proxy-config proxy.conf.json`.
(If asked about usage data, type N.)

Terminal 3:
```
curl.exe --noproxy "*" -i http://localhost:4200/api/health
```
Expected HTTP 200 + Flask JSON.

Browser http://localhost:4200:
1. Click **Load sample: Islamabad (rain followed)** → **Run local prediction** → "Rain tomorrow", 80.5% (screenshot).
2. Click **Load sample: Karachi (dry followed)** → predict → "No rain tomorrow".
3. Click **Clear** → submit → a validation message appears (screenshot).
4. Validation of server failure (Stage 10.4): press Ctrl+C in Terminal 1, click predict → "API error 500/502…" appears (screenshot), then restart Flask.

## F. Git + GitHub — Stages 11–12
1. In GitHub: **+ → New repository**, name e.g. `rain-prediction-ml`, **Public**, do NOT tick README/.gitignore/license → Create.
2. **Do this now, before pushing** (Stage 14.1): repo → Settings → Pages → Source → **GitHub Actions**.
3. In Terminal 3:
```
cd D:\ml_project
git init
git branch -M main
git config --global user.name "Hassan Raza"
git config --global user.email "YOUR_GITHUB_EMAIL"
git add .
git status --short
```
Check that `.venv`, `node_modules`, `dist` are NOT listed. Then:
```
git commit -m "Initial full-stack ML application"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```
Log in with the browser window that pops up (never type your password in the terminal).

For a clean commit history (graders like this), you can split into a few commits instead of one; e.g. commit backend first, then frontend, then workflows:
```
git add backend data notebooks README.md .gitignore && git commit -m "Add trained model, Flask API and tests"
git add frontend && git commit -m "Add Angular prediction form"
git add .github scripts docs && git commit -m "Add CI, Pages workflow and docs"
git push -u origin main
```

## G. CI + Pages — Stages 13–14 (workflows are already included)
1. Repo → **Actions**. Wait for **Full-stack CI** (jobs backend + frontend) and **Deploy Angular to GitHub Pages** to turn green.
   If Pages ran before you set Source = GitHub Actions: Actions → Deploy… → **Re-run all jobs**.
2. Settings → Pages → **Visit site** → `https://YOUR_USERNAME.github.io/YOUR_REPO/` — the form shows, the button is
   disabled and a yellow "Static GitHub Pages demonstration only" notice appears (screenshot).
3. In the green CI run, scroll to **Artifacts** → `angular-build` (screenshot).
The Pages workflow uses the repository name automatically for `--base-href`, so there is nothing to edit.

## H. Finish — Stage 15
1. Edit `README.md`: replace `YOUR_USERNAME` / `YOUR_REPO` (2 places) with your real URLs, commit and push:
```
git add .
git commit -m "Update README with repository and Pages URLs"
git push
```
2. Run and save the outputs for docs:
```
git status
git log --oneline -5
git remote -v
```
3. Put screenshots in `docs\` (suggested names below) and commit them: `git add docs && git commit -m "Add evidence" && git push`.
4. Optional: turn `docs\technical_report.md` into Word/PDF (the numbers are already filled in).

### Screenshot checklist (submission evidence)
1. Version outputs  2. `/health` in browser  3. curl predict 200  4. pytest `5 passed`  5. Angular form with result
6. Validation error  7. API error when Flask is stopped  8. GitHub repo file list  9. Commit history
10. Green CI run + artifact  11. Green Pages run  12. Live Pages site with the static notice

### Submit (Stage 15.5)
Model bundle + docs; Flask API + test output; Angular screenshot; repo URL; CI run URLs + artifact; Pages URL; README + report.

## Quick fixes
| Problem | Fix |
|---|---|
| `Activate.ps1` blocked | `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned` |
| `ng` not recognised | close ALL VS Code windows, reopen; or `npx ng ...` / `ng.cmd ...` |
| `npm install` error | the project already has `frontend\.npmrc` (legacy-peer-deps); delete `node_modules` and retry |
| Pages 404 / blank | Settings → Pages → Source = GitHub Actions, then re-run the Pages workflow |
| Port 5000 busy | close the old Flask terminal |
| pip fails to install pinned packages | you need Python 3.11+ (3.12 recommended) |
| 502 on localhost from Python | already handled (`trust_env=False`) |
