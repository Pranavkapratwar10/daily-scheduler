pipeline {

    agent any

    stages {

        stage('Install Dependencies') {
            steps {
                bat 'C:\\Users\\Pratik\\AppData\\Local\\Programs\\Python\\Python311\\python.exe -m pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                bat 'C:\\Users\\Pratik\\AppData\\Local\\Programs\\Python\\Python311\\python.exe -m pytest -v'
            }
        }

        stage('Check Docker') {
            steps {
                bat 'C:\\Users\\Pratik\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe version'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'C:\\Users\\Pratik\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe build -t daily-scheduler:latest .'
            }
        }

        stage('Deploy Container') {
            steps {
                bat '''
                C:\\Users\\Pratik\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe stop daily-scheduler || exit 0
                C:\\Users\\Pratik\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe rm daily-scheduler || exit 0
                C:\\Users\\Pratik\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe run -d --name daily-scheduler -p 5000:5000 daily-scheduler:latest
                '''
            }
        }

    }

    post {

        success {
            echo 'CI/CD pipeline completed successfully!'
        }

        failure {
            echo 'CI/CD pipeline failed. Check the logs.'
        }

    }
}