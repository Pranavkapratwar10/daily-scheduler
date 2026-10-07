pipeline {

    agent any

    stages {

        stage('Install Dependencies') {

            steps {

                bat 'python -m pip install -r requirements.txt'

            }

        }


        stage('Run Tests') {

            steps {

                bat 'python -m pytest -v'

            }

        }


        stage('Build Docker Image') {

            steps {

                bat 'docker build -t daily-scheduler:latest .'

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