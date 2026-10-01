pipeline {
	agent {
		docker {
			image 'ubuntu:latest'
		}
	}
	stages {
		stage('bash-check') {
			steps {
				echo 'Checkout repository code'
				checkout scm

				echo 'Check bash version'
				sh 'bash --version'

				echo 'Check Bash syntax'
				sh 'bash -n heath_check.sh'
			
				sh 'chmod +x health_check.sh'

				echo 'Run health check file'
				sh './health_check.sh'

				archiveArtifacts artifacts: 'log/health.log'
			}
		}
		
		stage('Python-check'){
			steps {
				echo 'Check python version'
				sh 'python3 --version'

				echo 'Run the python parser'
				sh 'python3 health_parser.py'

				echo 'Validate generated json file'
				sh 'python3 -m json.tool json/health_report.json'
			}
		}
		stage ('Build Docker Image'){
			steps {
				echo 'Building an image'
				sh 'docker compose build'

				echo 'Running health check container'
				sh 'docker compose run --rm health_check'
			}
		}
	}
	post {
		success {
			echo 'Linux Health Check pipeline completed successfully!'
			githubNotify(
					context: 'Jenkins',
					description: 'Linux Health check pipeine passed',
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
					description: 'Linux Health check pipeline failed',
					status: 'FAILURE',
					account: '25janet',
					repo: 'AI-health-assistant',
					credentialsId: 'github-ai-health-assistant',
					sha: env.GIT_COMMIT
			)

		}
		
	}
}



