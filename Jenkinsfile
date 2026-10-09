
pipeline {
    agent any

    environment {
        PYTHON_EXE = 'C:/Users/perfi/AppData/Local/Programs/Python/Python313/python.exe'
    }

    triggers {
        githubPush()
    }

    stages {
        stage('Setup') {
            steps {
                script {
                    env.BRANCH = (env.BRANCH_NAME ?: env.GIT_BRANCH ?: 'unknown').replaceFirst('^origin/', '')
                    env.IMAGE_TAG = "${env.BRANCH.replaceAll('[^A-Za-z0-9_.-]', '-')}-${env.BUILD_NUMBER}"
                    env.COMPOSE_PROJECT_NAME = 'my-fastapi-prod'
                }
                powershell '''
                    $p = "./.venv/Scripts/python.exe"
                    if (!(Test-Path $p)) {
                        & $env:PYTHON_EXE -m venv .venv
                        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
                    }
                    & $p -m pip install -q -r requirements.txt
                    exit $LASTEXITCODE
                '''
            }
        }

        stage('Tests') {
            steps {
                powershell '& "./.venv/Scripts/python.exe" -m pytest -q tests/; exit $LASTEXITCODE'
            }
        }

        stage('Registry') {
            steps {
                powershell '''
                    $r = docker ps -a --filter "name=^registry$" --format "{{.Names}}"
                    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

                    if ($r -eq "registry") {
                        docker start registry | Out-Null
                    } else {
                        docker run -d --restart=always -p 5000:5000 -v registry_data:/var/lib/registry --name registry registry:2 | Out-Null
                    }
                    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

                    for ($i = 0; $i -lt 15; $i++) {
                        try {
                            if ((Invoke-WebRequest http://localhost:5000/v2/ -UseBasicParsing -TimeoutSec 2).StatusCode -eq 200) { exit 0 }
                        } catch {}
                        Start-Sleep 2
                    }
                    exit 1
                '''
            }
        }

        stage('Build and Push') {
            steps {
                powershell '''
                    docker compose build -q
                    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

                    docker compose push -q
                    exit $LASTEXITCODE
                '''
            }
        }

        stage('Deploy') {
            when {
                expression { env.BRANCH == 'main' }
            }
            steps {
                powershell '''
                    docker compose pull -q
                    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

                    docker compose up -d --no-build --remove-orphans
                    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

                    for ($i = 0; $i -lt 20; $i++) {
                        try {
                            if ((Invoke-WebRequest http://localhost:8100/ -UseBasicParsing -TimeoutSec 3).StatusCode -eq 200) { exit 0 }
                        } catch {}
                        Start-Sleep 3
                    }
                    exit 1
                '''
            }
        }
    }
}
