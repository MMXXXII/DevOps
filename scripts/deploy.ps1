$ErrorActionPreference = "Stop"

$SourceDir = (Resolve-Path "$PSScriptRoot\..").Path
$DeployRoot = if ($env:DEPLOY_ROOT) { $env:DEPLOY_ROOT } else { "C:\JenkinsDeploy\my-fastapi" }
$AppPort = if ($env:APP_PORT) { $env:APP_PORT } else { "8000" }

$VenvDir = Join-Path $DeployRoot "venv"
$PythonExe = Join-Path $VenvDir "Scripts\python.exe"
$PidFile = Join-Path $DeployRoot "app.pid"
$OutputLog = Join-Path $DeployRoot "app.stdout.log"
$ErrorLog = Join-Path $DeployRoot "app.stderr.log"

New-Item -ItemType Directory -Force -Path $DeployRoot | Out-Null

if (Test-Path $PidFile) {
    $OldProcessId = Get-Content $PidFile -ErrorAction SilentlyContinue

    if ($OldProcessId) {
        Stop-Process `
            -Id $OldProcessId `
            -Force `
            -ErrorAction SilentlyContinue
    }

    Remove-Item `
        $PidFile `
        -Force `
        -ErrorAction SilentlyContinue
}

$PortProcesses = Get-NetTCPConnection `
    -LocalPort $AppPort `
    -State Listen `
    -ErrorAction SilentlyContinue |
    Select-Object -ExpandProperty OwningProcess -Unique

foreach ($PortProcessId in $PortProcesses) {
    Stop-Process `
        -Id $PortProcessId `
        -Force `
        -ErrorAction SilentlyContinue
}

Start-Sleep -Seconds 2

& robocopy `
    $SourceDir `
    $DeployRoot `
    /E `
    /R:2 `
    /W:1 `
    /NFL `
    /NDL `
    /NJH `
    /NJS `
    /NP `
    /XD .git .venv venv __pycache__ .pytest_cache `
    /XF *.pyc *.db app.pid app.stdout.log app.stderr.log

if ($LASTEXITCODE -ge 8) {
    throw "File copy failed"
}

if (-not (Test-Path $PythonExe)) {
    & $env:PYTHON_EXE -m venv $VenvDir

    if ($LASTEXITCODE -ne 0) {
        throw "Virtual environment creation failed"
    }
}

& $PythonExe -m pip install --upgrade pip

if ($LASTEXITCODE -ne 0) {
    throw "Pip upgrade failed"
}

& $PythonExe -m pip install -r "$DeployRoot\requirements.txt"

if ($LASTEXITCODE -ne 0) {
    throw "Dependency installation failed"
}

$env:JENKINS_NODE_COOKIE = "fastapi-app-service"

$Process = Start-Process `
    -FilePath $PythonExe `
    -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", $AppPort `
    -WorkingDirectory $DeployRoot `
    -RedirectStandardOutput $OutputLog `
    -RedirectStandardError $ErrorLog `
    -WindowStyle Hidden `
    -PassThru

$Process.Id | Set-Content $PidFile

$Started = $false

for ($Attempt = 1; $Attempt -le 10; $Attempt++) {
    Start-Sleep -Seconds 1

    if ($Process.HasExited) {
        break
    }

    try {
        $Response = Invoke-WebRequest `
            -Uri "http://127.0.0.1:$AppPort" `
            -UseBasicParsing `
            -TimeoutSec 2

        if ($Response.StatusCode -eq 200) {
            $Started = $true
            break
        }
    }
    catch {
    }
}

if (-not $Started) {
    if (Test-Path $ErrorLog) {
        Get-Content $ErrorLog -Tail 50
    }

    throw "Application startup failed"
}

Write-Host "Site started: http://127.0.0.1:$AppPort"