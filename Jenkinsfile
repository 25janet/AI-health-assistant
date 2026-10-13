pipeline {
    agent any

    stages {

        stage('Checkout and Validate Bash') {
            steps {
                echo 'Checking out repository code'
                checkout scm

                echo 'Checking Bash version'
                sh 'bash --version'

                echo 'Checking health-check script syntax'
                sh 'bash -n monitoring/health_check.sh'

                echo 'Making health-check script executable'
                sh 'chmod +x monitoring/health_check.sh'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Linux Health Check Docker image'
                sh 'docker compose build'
            }
        }

        stage('Run Health Check in Docker') {
            steps {
                echo 'Running health check inside Docker'
                sh 'docker compose run --rm health-check'
            }
        }

        stage('Parse Health Report') {
            steps {
                echo 'Checking Python version'
                sh 'python3 --version'

                echo 'Running the Python health-log parser'
                sh 'python3 monitoring/health_parser.py'

                echo 'Validating generated JSON report'
                sh 'python3 -m json.tool data/processed/health_report.json'

                echo 'Archiving health logs and reports'
                archiveArtifacts(
                    artifacts: 'data/raw/health.log,data/processed/health_report.json',
                    allowEmptyArchive: false
                )
            }
        }
    }

    post {
        success {
            echo 'Linux Health Check pipeline completed successfully!'

            githubNotify(
                context: 'Jenkins',
                description: 'Linux Health Check pipeline passed',
                status: 'SUCCESS',
                account: '25janet',
                repo: 'AI-health-assistant',
                credentialsId: 'github-ai-health-assistant',
                sha: env.GIT_COMMIT
            )
        }

        failure {
            echo 'Linux Health Check pipeline failed!'

            githubNotify(
                context: 'Jenkins',
                description: 'Linux Health Check pipeline failed',
                status: 'FAILURE',
                account: '25janet',
                repo: 'AI-health-assistant',
                credentialsId: 'github-ai-health-assistant',
                sha: env.GIT_COMMIT
            )
        }
    }
}

