pipeline {
    agent any

    environment {
    PYTHON_EXE = 'C:/Users/perfi/AppData/Local/Programs/Python/Python313/python.exe'
    DEPLOY_ROOT = 'C:/JenkinsDeploy/my-fastapi'
    DEPLOY_URL = 'http://127.0.0.1:8000'
    APP_PORT = '8000'
}

    triggers {
        githubPush()
    }

    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    stages {
        stage('Check environment') {
            steps {
                powershell '''
                    git --version
                    & $env:PYTHON_EXE --version
                '''
            }
        }

        stage('Install dependencies') {
            steps {
                powershell '''
                    $Python = ".venv/Scripts/python.exe"

                    if (-not (Test-Path $Python)) {
                        & $env:PYTHON_EXE -m venv .venv
                    }

                    & $Python -m pip install --upgrade pip

                    if ($LASTEXITCODE -ne 0) {
                        exit $LASTEXITCODE
                    }

                    & $Python -m pip install -r requirements.txt

                    if ($LASTEXITCODE -ne 0) {
                        exit $LASTEXITCODE
                    }
                '''
            }
        }

        stage('Tests') {
            steps {
                powershell '''
                    & ".venv/Scripts/python.exe" -m pytest tests/
                    exit $LASTEXITCODE
                '''
            }
        }

        stage('Deploy') {
            when {
                branch 'main'
            }

            steps {
                powershell '''
                    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
                    & "./scripts/deploy.ps1"
                '''
            }
        }

        stage('Health check') {
            when {
                branch 'main'
            }

            steps {
                powershell '''
                    $Success = $false

                    for ($Attempt = 1; $Attempt -le 15; $Attempt++) {
                        try {
                            $Response = Invoke-WebRequest `
                                -Uri $env:DEPLOY_URL `
                                -UseBasicParsing `
                                -TimeoutSec 3

                            if ($Response.StatusCode -eq 200) {
                                $Success = $true
                                break
                            }
                        }
                        catch {
                            Start-Sleep -Seconds 2
                        }
                    }

                    if (-not $Success) {
                        throw "Сайт не запустился"
                    }

                    Write-Host "Сайт успешно развёрнут"
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline завершён успешно'
        }

        failure {
            echo 'Pipeline завершился с ошибкой'
        }
    }
}