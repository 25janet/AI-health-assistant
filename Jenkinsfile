pipeline {
	agent any
	stages {
		stage('Checkout') {
			steps {
				checkout scm
			}
		}
		stage('Validate Script'){
			steps {
				sh 'bash -n health_check.sh'
			}
		}
		stage('Run Health Check'){
			steps {
				sh 'chmod +x health_check.sh'
				sh './health_check.sh'
			}
		}
		stage ('Build Docker Image'){
			steps {
				sh 'docker build -t linux-health-check:v1 .'
			}
		}
	}
	post {
		success {
			echo 'Linux Health Check pipeline completed successfully!'
			githubNotify(
					context: 'Jenkins'
					description: 'Linux Health check pipeine passed'
					status: 'SUCCESS'
			)

		}
		failure {
			echo 'Linux Health Check pipeline failed!'
			githubNotify(
					context: 'Jenkins'
					description: 'Linux Health check pipeline failed'
					status: 'FAILED'
			)
		}
	}
}



