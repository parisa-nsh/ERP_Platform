# Contributing

## Branching

- **`main`** – Production-ready code. Only merge when tests pass and the change is ready to deploy.
- **`develop`** – Integration branch for ongoing work. Feature branches merge here first; `develop` is then merged into `main` for releases (optional: you can also merge feature branches directly into `main`).
- **Feature branches** – One branch per feature or fix. Create from `main` (or `develop` if you use it), then merge back when done.
  - **Features:** `feature/add-reporting`, `feature/export-pdf`
  - **Fixes:** `fix/login-validation`, `fix/csv-encoding`

## Workflow

1. Update your base branch:  
   `git checkout main` → `git pull`
2. Create a branch:  
   `git checkout -b feature/your-feature` (or `fix/issue-name`)
3. Make changes, commit:  
   `git add .` → `git commit -m "Add reporting page"`
4. Push and open a pull request (or merge locally):  
   `git push -u origin feature/your-feature` → open PR into `main` (or `develop`).
5. After review/approval, merge into `main` (or into `develop`, then merge `develop` into `main` when releasing).

## Commit messages

Keep them short and clear, e.g.:

- `Add anomaly score filter to Transactions page`
- `Fix CSV export encoding for special characters`
- `Update README with branching section`

## Pull requests

- Describe what changed and why.
- Ensure the app runs and any affected flows work (backend, frontend, ML pipeline as relevant).
