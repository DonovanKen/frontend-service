@Library('testsharedlibry') _

pipeline {
    agent any

    parameters {
        string(name: 'IMAGE_NAME', defaultValue: 'frontend', description: 'Docker image name')
        string(name: 'IMAGE_TAG', defaultValue: 'latest', description: 'Docker image tag')
        string(name: 'CONTAINER_NAME', defaultValue: 'cfrontend-app', description: 'Docker container name')  
        string(name: 'DOCKERHUB_USER', defaultValue: 'mrkendono', description: 'Docker Hub username')
        string(name: 'K8S_NAMESPACE', defaultValue: 'microservices', description: 'Kubernetes namespace')
    }
    
    environment {
        SERVICE_NAME = "frontend-app"
        CONTAINER_NAME = "cfrontend-app" 
        FULL_IMAGE_NAME = "${params.DOCKERHUB_USER}/${params.IMAGE_NAME}:${params.IMAGE_TAG}"
        K8S_DIR = "k8s"
        SERVICE_PORT = "5000"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh """
                    echo "=== Building Frontend Service ==="
                    echo "Service: ${SERVICE_NAME}"
                    echo "Container: ${CONTAINER_NAME}"
                    echo "Image: ${FULL_IMAGE_NAME}"
                    echo "Port: ${SERVICE_PORT}"
                """
            }
        }
        
        stage('Code Quality Check') {
            steps {
                sh '''
                    echo "=== Checking Python Code ==="
                    python --version
                    pip --version
                    echo "=== Requirements Check ==="
                    cat requirements.txt || echo "No requirements.txt found"
                '''
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    dockerBuildSingle(
                        imageName: params.IMAGE_NAME,
                        imageTag: params.IMAGE_TAG,
                        contextPath: "."
                    )
                }
            }
        }
        
        stage('Push to Docker Hub') {
            steps {
                script {
                    sh """
                        echo "=== Pushing Image to Docker Hub ==="
                        docker tag ${params.IMAGE_NAME}:${params.IMAGE_TAG} ${FULL_IMAGE_NAME}
                        docker push ${FULL_IMAGE_NAME}
                        echo "Pushed: ${FULL_IMAGE_NAME}"
                    """
                }
            }
        }

        stage('Test Container') {
            steps {
                script {
                    testImageSingle(
                        imageName: params.IMAGE_NAME,
                        imageTag: params.IMAGE_TAG,
                        containerName: "${CONTAINER_NAME}",  //# Using docker-compose container_name
                        port: "${SERVICE_PORT}",
                        healthEndpoint: "/health"
                    )
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sshagent(credentials: ['ssh-cred1']) {
                    sh '''
                        [ -d ~/.ssh ] || mkdir ~/.ssh && chmod 0700 ~/.ssh
                        ssh-keyscan -t rsa,dsa 192.168.2.88 >> ~/.ssh/known_hosts
                    '''
                    
                    sh """
                        echo "=== Deploying Frontend to Kubernetes ==="
                        
                        # Create directory on remote server
                        ssh -o StrictHostKeyChecking=no kubernetes@192.168.2.88 'mkdir -p /tmp/k8s-frontend/'
                        
                        # Copy k8s manifests
                        scp -r ${K8S_DIR}/ kubernetes@192.168.2.88:/tmp/k8s-frontend/
                        
                        # Deploy to Kubernetes
                        ssh kubernetes@192.168.2.88 "
                            cd /tmp/k8s-frontend/${K8S_DIR}
                            echo '=== Deploying ${SERVICE_NAME} ==='
                            echo 'Current directory:'
                            pwd
                            ls -la
                            
                            # Update image in deployment
                            sed -i 's|mrkendono/frontend:latest|${FULL_IMAGE_NAME}|g' deployment.yaml
                            
                            # Create namespace if it doesn't exist
                            kubectl create namespace ${params.K8S_NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
                            
                            # Apply manifests
                            kubectl apply -f . -n ${params.K8S_NAMESPACE}
                            
                            # Wait for rollout
                            echo '=== Waiting for deployment to be ready ==='
                            kubectl rollout status deployment/${SERVICE_NAME} -n ${params.K8S_NAMESPACE} --timeout=300s
                            
                            echo '=== Deployment Status ==='
                            kubectl get deployment -l app=${SERVICE_NAME} -n ${params.K8S_NAMESPACE}
                            echo '=== Pod Status ==='
                            kubectl get pods -l app=${SERVICE_NAME} -n ${params.K8S_NAMESPACE}
                            echo '=== Service Status ==='
                            kubectl get service -l app=${SERVICE_NAME} -n ${params.K8S_NAMESPACE}
                        "
                    """
                }
            }
        }
        
        stage('Health Check') {
            steps {
                script {
                    sleep 10
                    sh """
                        echo "=== Performing Health Check ==="
                        # Test the frontend service internally
                        kubectl run -it --rm frontend-health-check --image=curlimages/curl \
                          --restart=Never -- curl -f http://${SERVICE_NAME}:${SERVICE_PORT}/health || echo "Health check completed"
                    """
                }
            }
        }
    }
    
    post {
        always {
            echo "=== Frontend Pipeline Completed ==="
            sh "docker rm -f ${CONTAINER_NAME} || true"
            
            // Clean up health check pod
            sh """
                kubectl delete pod frontend-health-check --ignore-not-found=true || true
            """
        }
        success {
            echo "Frontend service deployed successfully!"
        }
        failure {
            echo "Frontend service deployment failed!"
        }
    }
}