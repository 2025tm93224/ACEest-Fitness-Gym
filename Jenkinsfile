pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }

    environment {
        PIP_DISABLE_PIP_VERSION_CHECK = '1'
        PYTHONDONTWRITEBYTECODE = '1'
        PYTHONUNBUFFERED = '1'
        DOCKER_IMAGE = 'aceest-fitness'
    }

    stages {
        stage('Checkout') {
            steps {
                // For a Pipeline-from-SCM or Multibranch Pipeline job, Jenkins checks out SCM here.
                checkout scm
                sh 'git --no-pager log -1 --oneline'
            }
        }

        stage('Clean Python Build Environment') {
            steps {
                sh '''
                    set -eu
                    python3 --version
                    rm -rf .venv
                    python3 -m venv .venv
                    .venv/bin/python -m pip install --upgrade pip
                    .venv/bin/python -m pip install -r requirements-dev.txt
                '''
            }
        }

        stage('Compile / Validate') {
            steps {
                sh '''
                    set -eu
                    .venv/bin/python -m compileall -q app run.py config.py
                    .venv/bin/python -m pip check
                '''
            }
        }

        stage('Unit Tests - Quality Gate') {
            steps {
                sh '''
                    set -eu
                    mkdir -p reports
                    .venv/bin/python -m pytest -v --junitxml=reports/pytest-results.xml
                '''
            }
            post {
                always {
                    junit testResults: 'reports/pytest-results.xml', allowEmptyResults: true
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    set -eu
                    docker build --pull --target runtime \
                      --tag "${DOCKER_IMAGE}:${BUILD_NUMBER}" \
                      --tag "${DOCKER_IMAGE}:latest" .
                '''
            }
        }
    }

    post {
        success {
            echo 'BUILD SUCCESS: checkout, dependency installation, compile checks, tests, and Docker image build passed.'
        }
        failure {
            echo 'BUILD FAILED: inspect the stage logs and Pytest report before merging or deploying.'
        }
        always {
            archiveArtifacts artifacts: 'reports/*.xml', allowEmptyArchive: true
        }
    }
}
