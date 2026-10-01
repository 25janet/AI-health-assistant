pipeline {

    agent any

    stages {

        stage('Bash Check') {
            steps {

                echo 'Checkout repository code'
                checkout scm

                echo 'Check Bash version'
                sh 'bash --version'

                echo 'Check Bash syntax'
                sh 'bash -n health_check.sh'

                echo 'Make health_check.sh executable'
                sh 'chmod +x health_check.sh'

                echo 'Create log directory'
                sh 'mkdir -p log'

                echo 'Run health check'
                sh './health_check.sh > log/health.log 2>&1'

                echo 'Archive health log'
                archiveArtifacts artifacts: 'log/health.log'
            }
        }


        stage('Python Check') {
            steps {

                echo 'Check Python version'
                sh 'python3 --version'

                echo 'Run the Python parser'
                sh 'python3 health_parser.py'

                echo 'Validate generated JSON file'
                sh 'python3 -m json.tool json/health_report.json'
            }
        }


        stage('Build Docker Image') {
            steps {

                echo 'Building Docker image'
                sh 'docker compose build'

                echo 'Running health check container'
                sh 'docker compose run --rm health-check'
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