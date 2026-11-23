pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
        timestamps()
    }

    environment {
        IMAGE_NAME = 'cicd-assignment-web'
        TEST_IMAGE_NAME = 'cicd-assignment-tests'
        DOCKER_NETWORK = 'cicd-assignment-net'

        STAGING_CONTAINER = 'cicd-assignment-staging'
        PRODUCTION_CONTAINER = 'cicd-assignment-production'
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out GitHub repository...'
                checkout scm
            }
        }

        stage('Package') {
            steps {
                echo 'Building website and Selenium Docker images...'

                sh '''
                    docker network inspect "$DOCKER_NETWORK" \
                    >/dev/null 2>&1 || docker network create "$DOCKER_NETWORK"

                    docker build \
                    -t "$IMAGE_NAME:$BUILD_NUMBER" .

                    docker build \
                    -t "$TEST_IMAGE_NAME:$BUILD_NUMBER" \
                    -f tests/Dockerfile tests
                '''
            }
        }

        stage('Start Staging') {
            steps {
                echo 'Starting staging website...'

                sh '''
                    docker rm -f "$STAGING_CONTAINER" \
                    >/dev/null 2>&1 || true

                    docker run -d \
                    --name "$STAGING_CONTAINER" \
                    --network "$DOCKER_NETWORK" \
                    -p 8081:80 \
                    "$IMAGE_NAME:$BUILD_NUMBER"

                    for i in $(seq 1 20); do
                        if curl -fsS http://127.0.0.1:8081 \
                        >/dev/null; then
                            echo "Staging website is ready!"
                            exit 0
                        fi

                        sleep 2
                    done

                    echo "Staging website failed to start."
                    exit 1
                '''
            }
        }

        stage('Test') {
            steps {
                echo 'Running Selenium tests inside Docker test agent...'

                script {
                    sh 'mkdir -p tests/screenshots test-results'
                    sh 'rm -f test-results/results.xml'
                    sh 'rm -f tests/screenshots/homepage.png'

                    def testStatus = sh(
                        returnStatus: true,
                        script: '''
                            docker run --rm \
                            --network "$DOCKER_NETWORK" \
                            -e BASE_URL=http://cicd-assignment-staging \
                            -v "$WORKSPACE/tests/screenshots:/app/screenshots" \
                            -v "$WORKSPACE/test-results:/app/test-results" \
                            "$TEST_IMAGE_NAME:$BUILD_NUMBER"
                        '''
                    )

                    junit(
                        testResults: 'test-results/results.xml',
                        allowEmptyResults: true
                    )

                    archiveArtifacts(
                        artifacts: 'tests/screenshots/*.png',
                        allowEmptyArchive: true
                    )

                    if (testStatus != 0) {
                        error('Selenium tests failed! Deployment cancelled.')
                    }

                    echo 'All Selenium tests passed!'
                }
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deploying tested website to production...'

                sh '''
                    docker rm -f "$PRODUCTION_CONTAINER" \
                    >/dev/null 2>&1 || true

                    docker tag \
                    "$IMAGE_NAME:$BUILD_NUMBER" \
                    "$IMAGE_NAME:latest"

                    docker run -d \
                    --name "$PRODUCTION_CONTAINER" \
                    --restart unless-stopped \
                    -p 80:80 \
                    "$IMAGE_NAME:$BUILD_NUMBER"

                    echo "Production deployment successful!"
                '''
            }
        }
    }

    post {
        always {
            echo 'Cleaning up staging container...'

            sh '''
                docker rm -f "$STAGING_CONTAINER" \
                >/dev/null 2>&1 || true
            '''
        }

        success {
            echo 'Pipeline completed successfully!'
        }

        failure {
            echo 'Pipeline failed. Check the console output.'
        }
    }
}
