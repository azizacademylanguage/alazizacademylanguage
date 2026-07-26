$ErrorActionPreference = "Stop"
$RepoUrl = "https://github.com/azizacademylanguage/alazizacademylanguage.git"

function Run-Git {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments)
    & git @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Git buyrug'i xato bilan tugadi: git $($Arguments -join ' ')"
    }
}

Write-Host "AL-AZIZ loyihasini GitHub'ga yuklash boshlandi..." -ForegroundColor Cyan

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "XATO: Git kompyuterga o'rnatilmagan." -ForegroundColor Red
    exit 1
}

Set-Location $PSScriptRoot

if (-not (Test-Path ".git")) {
    Run-Git init
}

Run-Git branch -M main

$originExists = (& git remote 2>$null) -contains "origin"
if ($originExists) {
    Run-Git remote set-url origin $RepoUrl
} else {
    Run-Git remote add origin $RepoUrl
}

Run-Git add .

$hasChanges = git status --porcelain
if ($hasChanges) {
    Run-Git commit -m "Fix Railway admin login and deployment startup"
} else {
    Write-Host "Yangi o'zgarish topilmadi; mavjud commit yuboriladi." -ForegroundColor Yellow
}

Write-Host "GitHub'ga yuborilmoqda..." -ForegroundColor Cyan
Run-Git push -u origin main

Write-Host "TAYYOR: GitHub push muvaffaqiyatli tugadi." -ForegroundColor Green
Write-Host $RepoUrl -ForegroundColor Green
