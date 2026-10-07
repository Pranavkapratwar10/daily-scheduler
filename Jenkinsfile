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


        stage('Build Docker Image') {

            steps {

                bat 'C:\\Users\\Pratik\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe build -t daily-scheduler:latest .'

            }

        }

    }

    post {

        success {

            echo 'CI pipeline completed successfully!'

        }

        failure {

            echo 'CI pipeline failed. Check the logs.'

        }

    }

}