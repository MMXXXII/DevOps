def resolveBranch() {
    def name = env.BRANCH_NAME ?: env.GIT_BRANCH ?: ''
    return name.replaceFirst('^origin/', '')
}

pipeline {
    agent any

    environment {
        PYTHON_EXE = 'C:/Users/perfi/AppData/Local/Programs/Python/Python313/python.exe'
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
        stage('Detect branch') {
            steps {
                script {
                    env.BRANCH = resolveBranch()

                    if (env.BRANCH == 'main') {
                        env.DEPLOY_ENABLED = 'true'
                        env.APP_ENV = 'prod'
                        env.HTTP_PORT = '8100'
                    } else if (env.BRANCH == 'dev') {
                        env.DEPLOY_ENABLED = 'true'
                        env.APP_ENV = 'dev'
                        env.HTTP_PORT = '8101'
                    } else {
                        // feature/* и прочие ветки: только тесты и сборка образов, без деплоя
                        env.DEPLOY_ENABLED = 'false'
                        env.APP_ENV = 'ci'
                        env.HTTP_PORT = '8190'
                    }

                    env.COMPOSE_PROJECT_NAME = "my-fastapi-${env.APP_ENV}"
                    env.DEPLOY_URL = "http://127.0.0.1:${env.HTTP_PORT}"

                    echo "Branch: ${env.BRANCH}, env: ${env.APP_ENV}, deploy: ${env.DEPLOY_ENABLED}, url: ${env.DEPLOY_URL}"
                }
            }
        }

        stage('Check environment') {
            steps {
                powershell '''
                    $ErrorActionPreference = 'Continue'

                    git --version
                    & $env:PYTHON_EXE --version

                    docker --version
                    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

                    docker compose version
                    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

                    # Проверка, что Jenkins видит Docker-демон
                    docker info --format "Docker server: {{.ServerVersion}}"
                    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
                '''
            }
        }

        stage('Install dependencies') {
            steps {
                powershell '''
                    $Python = ".venv/Scripts/python.exe"

                    if (-not (Test-Path $Python)) {
                        & $env:PYTHON_EXE -m venv .venv

                        if ($LASTEXITCODE -ne 0) {
                            exit $LASTEXITCODE
                        }
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

        stage('Build images') {
            steps {
                powershell '''
                    $ErrorActionPreference = 'Continue'

                    docker compose config -q
                    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

                    docker compose build --progress=plain
                    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

                    docker images --filter "reference=$($env:COMPOSE_PROJECT_NAME)-*"
                '''
            }
        }

        stage('Deploy') {
            when {
                expression { env.DEPLOY_ENABLED == 'true' }
            }

            steps {
                powershell '''
                    $ErrorActionPreference = 'Continue'

                    docker compose up -d --build --remove-orphans
                    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

                    docker compose ps
                '''
            }
        }

        stage('Health check') {
            when {
                expression { env.DEPLOY_ENABLED == 'true' }
            }

            steps {
                powershell '''
                    $Success = $false

                    for ($Attempt = 1; $Attempt -le 20; $Attempt++) {
                        try {
                            $Response = Invoke-WebRequest `
                                -Uri $env:DEPLOY_URL `
                                -UseBasicParsing `
                                -TimeoutSec 3

                            if ($Response.StatusCode -eq 200) {
                                Write-Host "Server header: $($Response.Headers['Server'])"
                                $Success = $true
                                break
                            }
                        }
                        catch {
                            Write-Host "Attempt ${Attempt}: site is not available yet"
                        }

                        Start-Sleep -Seconds 3
                    }

                    if (-not $Success) {
                        throw "Site did not start at $env:DEPLOY_URL"
                    }

                    Write-Host "Site is up at $env:DEPLOY_URL (via nginx)"
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully'
            powershell 'docker image prune -f'
        }

        failure {
            echo 'Pipeline failed'
            script {
                if (env.COMPOSE_PROJECT_NAME && env.DEPLOY_ENABLED == 'true') {
                    powershell '''
                        docker compose ps
                        docker compose logs --tail 80
                        exit 0
                    '''
                }
            }
        }
    }
}