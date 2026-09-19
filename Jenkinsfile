pipeline {
    agent any
    
    environment {
        PYTHON = 'C:\\Users\\Eger\\AppData\\Local\\Programs\\Python\\Python310\\python.exe'
    }
    
    stages {
        stage('Получение кода') {
            steps {
                checkout scm
                echo "Код получен. Ветка: ${env.GIT_BRANCH}"
            }
        }

        stage('Установка зависимостей') {
            steps {
                bat '''
                    echo "Создание venv в workspace Jenkins..."
                    if exist venv rmdir /s /q venv
                    "C:\\Users\\perfi\\AppData\\Local\\Programs\\Python\\Python313\\python.exe" -m venv venv
                    
                    echo "Обновление pip и установка пакетов..."
                    venv\\Scripts\\python -m pip install --upgrade pip
                    venv\\Scripts\\python -m pip install -r requirements.txt
                '''
            }
        }

        stage('Запуск тестов') {
            steps {
                bat '''
                    echo "Запуск тестов..."
                    venv\\Scripts\\python -m pytest tests/ -v
                '''
            }
        }
        
        stage('Деплой') {
            when { 
                expression { env.GIT_BRANCH?.endsWith('main') || env.GIT_BRANCH?.endsWith('master') } 
            }
            steps {
                bat '''
                    echo "Копирование файлов в C:\\apps\\hjfjksd..."
                    if not exist C:\\apps\\hjfjksd mkdir C:\\apps\\hjfjksd
                    robocopy . C:\\apps\\hjfjksd /E /XD .git venv __pycache__ .pytest_cache /NFL /NDL /NJH /NJS /NC /NS

                    echo "Запуск приложения FastAPI..."
                    cd /d C:\\apps\\hjfjksd
                    start /b venv\\Scripts\\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
                    echo "Сервер запущен на http://127.0.0.1:8000"
                '''
            }
        }
        
        stage('Инфо для веток разработки') {
            when { 
                expression { !(env.GIT_BRANCH?.endsWith('main') || env.GIT_BRANCH?.endsWith('master')) } 
            }
            steps {
                echo "Ветка ${env.GIT_BRANCH}: деплой пропущен (выполнены только сборка и тесты)."
            }
        }
    }
    
    post {
        success { echo "Успешно! Ветка: ${env.GIT_BRANCH}" }
        failure { echo "Ошибка! Ветка: ${env.GIT_BRANCH}" }
    }
}