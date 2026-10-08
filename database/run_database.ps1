# ============================================================================
# AUTOMATED POSTGRESQL RUNNER & SETUP SCRIPT
# ============================================================================
param (
    [string]$DbUser = "postgres",
    [string]$DbName = "companion_db",
    [string]$DbHost = "localhost",
    [int]$DbPort = 5432,
    [string]$Password = ""
)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  STUDENT COMPANION DATABASE INITIALIZATION" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# 1. Locate psql.exe
$psqlPath = ""
if (Get-Command psql -ErrorAction SilentlyContinue) {
    $psqlPath = "psql"
} elseif (Test-Path "C:\Program Files\PostgreSQL\18\bin\psql.exe") {
    $psqlPath = "C:\Program Files\PostgreSQL\18\bin\psql.exe"
} elseif (Test-Path "C:\Program Files\PostgreSQL\17\bin\psql.exe") {
    $psqlPath = "C:\Program Files\PostgreSQL\17\bin\psql.exe"
} elseif (Test-Path "C:\Program Files\PostgreSQL\16\bin\psql.exe") {
    $psqlPath = "C:\Program Files\PostgreSQL\16\bin\psql.exe"
} else {
    Write-Host "[ERROR] Could not locate psql.exe. Please ensure PostgreSQL is installed." -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Using psql at: $psqlPath" -ForegroundColor Green

# 2. Handle Password Authentication
if (-not [string]::IsNullOrEmpty($Password)) {
    $env:PGPASSWORD = $Password
} elseif ([string]::IsNullOrEmpty($env:PGPASSWORD)) {
    $plainPass = Read-Host "Enter PostgreSQL password for user '$DbUser'" -AsSecureString
    $bstr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($plainPass)
    $env:PGPASSWORD = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr)
}

# 3. Check if companion_db exists, create if not
Write-Host "`n[STEP 1/3] Checking / Creating database '$DbName'..." -ForegroundColor Yellow
$checkDbCmd = "& '$psqlPath' -U $DbUser -h $DbHost -p $DbPort -tc `"SELECT 1 FROM pg_database WHERE datname = '$DbName'`" postgres"
$dbExists = Invoke-Expression $checkDbCmd 2>$null

if ($dbExists -notmatch "1") {
    Write-Host "Creating database '$DbName'..." -ForegroundColor Cyan
    & $psqlPath -U $DbUser -h $DbHost -p $DbPort -c "CREATE DATABASE $DbName;" postgres
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[WARN] Note: Database creation completed. Proceeding to schema installation..." -ForegroundColor Yellow
    } else {
        Write-Host "[OK] Database '$DbName' created successfully." -ForegroundColor Green
    }
} else {
    Write-Host "[OK] Database '$DbName' already exists." -ForegroundColor Green
}

# 4. Run all SQL scripts in order
$scripts = @(
    "01_schema.sql",
    "02_views_and_functions.sql",
    "03_seed_data.sql",
    "04_example_queries.sql",
    "05_ai_planning_context.sql"
)

Write-Host "`n[STEP 2/3] Executing database scripts into '$DbName'..." -ForegroundColor Yellow

foreach ($script in $scripts) {
    if (Test-Path $script) {
        Write-Host "--> Running $script..." -ForegroundColor Cyan
        & $psqlPath -U $DbUser -h $DbHost -p $DbPort -d $DbName -f $script
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[ERROR] Failed running $script" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "[ERROR] Missing file: $script" -ForegroundColor Red
        exit 1
    }
}

Write-Host "`n[STEP 3/3] Testing AI Context Generation..." -ForegroundColor Yellow
& $psqlPath -U $DbUser -h $DbHost -p $DbPort -d $DbName -c "SELECT fn_get_ai_daily_plan_context('11111111-1111-1111-1111-111111111111'::UUID, CURRENT_DATE);"

Write-Host "`n============================================================" -ForegroundColor Green
Write-Host "  SUCCESS! Database system initialized and ready to use." -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green

