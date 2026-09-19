pipeline {
    agent any

    environment {
        PYTHON = 'C:\\Users\\perfi\\AppData\\Local\\Programs\\Python\\Python313\\python.exe'
        DEPLOY_DIR = 'C:\\apps'
    }

    stages {
        stage('Получение кода') {
            steps {
                checkout scm
            }
        }

        stage('Установка зависимостей') {
            steps {
                bat '''
                    if exist venv rmdir /s /q venv
                    "%PYTHON%" -m venv venv
                    venv\\Scripts\\python.exe -m pip install --upgrade pip
                    venv\\Scripts\\python.exe -m pip install -r requirements.txt
                '''
            }
        }

        stage('Запуск тестов') {
            steps {
                bat '''
                    venv\\Scripts\\python.exe -m pytest tests/ -v
                '''
            }
        }

        stage('Деплой') {
            when {
                expression {
                    env.GIT_BRANCH?.endsWith('main') ||
                    env.GIT_BRANCH?.endsWith('master')
                }
            }
            steps {
                bat '''
                    if not exist "%DEPLOY_DIR%" mkdir "%DEPLOY_DIR%"

                    robocopy . "%DEPLOY_DIR%" /E /XD .git venv __pycache__ .pytest_cache /XF app.db /NFL /NDL /NJH /NJS /NC /NS

                    if errorlevel 8 exit /b %ERRORLEVEL%

                    cd /d "%DEPLOY_DIR%"

                    if not exist venv (
                        "%PYTHON%" -m venv venv
                    )

                    venv\\Scripts\\python.exe -m pip install -r requirements.txt

                    net stop FastAPI 2>nul

                    net start FastAPI
                '''
            }
        }
    }

    post {
        success {
            echo "Деплой успешно завершён"
        }
        failure {
            echo "Сборка или деплой завершились ошибкой"
        }
    }
}