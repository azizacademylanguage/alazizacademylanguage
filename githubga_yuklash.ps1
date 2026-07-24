$ErrorActionPreference = "Stop"
$RepoUrl = "https://github.com/azizacademylanguage/alazizacademylanguage.git"

Write-Host "AL-AZIZ loyihasini GitHub'ga yuklash boshlandi..." -ForegroundColor Cyan

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "XATO: Git kompyuterga o'rnatilmagan." -ForegroundColor Red
    Write-Host "Git for Windows'ni o'rnating va terminalni qayta oching."
    exit 1
}

Set-Location $PSScriptRoot

if (-not (Test-Path ".git")) {
    git init
}

git branch -M main

$originExists = git remote 2>$null | Select-String -SimpleMatch "origin"
if ($originExists) {
    git remote set-url origin $RepoUrl
} else {
    git remote add origin $RepoUrl
}

git add .

$hasChanges = git status --porcelain
if ($hasChanges) {
    try {
        git commit -m "AL-AZIZ language platform: Railway and Netlify ready"
    } catch {
        Write-Host "Commit yaratilmadi. Git ism/email sozlanmagan bo'lishi mumkin." -ForegroundColor Yellow
        Write-Host "Masalan:" -ForegroundColor Yellow
        Write-Host 'git config --global user.name "Aziz Academy"'
        Write-Host 'git config --global user.email "EMAILINGIZ@gmail.com"'
        exit 1
    }
} else {
    Write-Host "Yangi o'zgarish topilmadi; mavjud commit yuboriladi." -ForegroundColor Yellow
}

Write-Host "GitHub'ga yuborilmoqda. Login oynasi chiqsa GitHub hisobingiz bilan kiring..." -ForegroundColor Cyan

git push -u origin main

Write-Host "TAYYOR: loyiha GitHub'ga joylandi." -ForegroundColor Green
Write-Host $RepoUrl -ForegroundColor Green
