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
    $OldProcessId = Get-Content $PidFile

    Stop-Process `
        -Id $OldProcessId `
        -Force `
        -ErrorAction SilentlyContinue

    Remove-Item $PidFile -Force
}

& robocopy `
    $SourceDir `
    $DeployRoot `
    /E `
    /R:2 `
    /W:1 `
    /XD .git .venv __pycache__ .pytest_cache `
    /XF *.pyc *.db app.pid app.stdout.log app.stderr.log

if ($LASTEXITCODE -ge 8) {
    throw "Ошибка копирования файлов"
}

if (-not (Test-Path $PythonExe)) {
    & py -3 -m venv $VenvDir

    if ($LASTEXITCODE -ne 0) {
        throw "Не удалось создать виртуальное окружение"
    }
}

& $PythonExe -m pip install --upgrade pip

if ($LASTEXITCODE -ne 0) {
    throw "Не удалось обновить pip"
}

& $PythonExe -m pip install -r "$DeployRoot\requirements.txt"

if ($LASTEXITCODE -ne 0) {
    throw "Не удалось установить зависимости"
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

Start-Sleep -Seconds 2

if ($Process.HasExited) {
    Get-Content $ErrorLog -ErrorAction SilentlyContinue
    throw "Приложение не запустилось"
}

Write-Host "Сайт запущен: http://127.0.0.1:$AppPort"