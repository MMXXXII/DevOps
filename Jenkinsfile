pipeline {
    agent any

    environment {
        PATH = "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
        DEPLOY_URL = "http://127.0.0.1:8000"
        APP_PORT = "8000"
    }

    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: "10"))
    }

    stages {
        stage("Install dependencies & Test") {
            steps {
                sh '''
                    python3 -m venv .venv
                    .venv/bin/python -m pip install --upgrade pip
                    .venv/bin/python -m pip install -r requirements.txt
                    .venv/bin/python -m pytest tests/
                '''
            }
        }

        stage("Deploy") {
            when {
                branch "main"
            }
            steps {
                sh '''
                    chmod +x scripts/deploy.sh
                    scripts/deploy.sh
                '''
            }
        }
        
        stage("Health check") {
            when {
                branch "main"
            }
            steps {
                sh '''
                    for attempt in $(seq 1 15); do
                        if curl --fail --silent "$DEPLOY_URL"; then
                            exit 0
                        fi
                        sleep 2
                    done
                    exit 1
                '''
            }
        }
    }
}