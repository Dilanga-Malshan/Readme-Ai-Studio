$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) { throw "Install GitHub CLI first: winget install --id GitHub.cli" }
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw "Install Git first." }
gh auth status
if ($LASTEXITCODE -ne 0) { gh auth login; if ($LASTEXITCODE -ne 0) { throw "GitHub sign-in failed." } }
$login = gh api user --jq .login
if ($LASTEXITCODE -ne 0 -or $login.Trim() -ne "Dilanga-Malshan") { throw "Sign in as Dilanga-Malshan before publishing this repository." }
if (-not (Test-Path .git)) { git init -b main; if ($LASTEXITCODE -ne 0) { throw "Git initialization failed." } }
git add .
if ($LASTEXITCODE -ne 0) { throw "Git staging failed." }
git diff --cached --quiet
if ($LASTEXITCODE -eq 1) { git commit -m "Build README.AI Angular and FastAPI studio"; if ($LASTEXITCODE -ne 0) { throw "Configure Git user.name and user.email, then retry." } }
gh repo create Dilanga-Malshan/readme-ai-studio --public --source . --remote origin --push --description "AI-powered GitHub profile README studio built with Angular and FastAPI"
if ($LASTEXITCODE -ne 0) { throw "Repository creation failed. Check whether the repository name already exists. Existing repositories are not overwritten by this script." }
gh repo view Dilanga-Malshan/readme-ai-studio --json url,isPrivate
if ($LASTEXITCODE -ne 0) { throw "Repository verification failed." }
