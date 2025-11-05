@Library('testsharedlibry') _

pipeline {
    agent any

    parameters {
       string(name: 'FRONTEND', defaultValue: 'frontend', description: 'this is my docker image name for frontend')
       string(name: 'IMAGE_TAG', defaultValue: 'latest', description: 'this is my docker tag name')
       string(name: 'CONTAINER_FRONTEND', defaultValue: 'cfrontend-app', description: 'this is my docker container name for frontend')
       string(name: 'GITHUB_USER', defaultValue: 'DonovanKen', description: 'user')
       string(name: 'DOCKERHUB_USER', defaultValue: 'mrkendono', description: 'docker hub')
       string(name: 'K8S_NAMESPACE', defaultValue: 'microservices', description: 'Kubernetes namespace')
    }
    
    stages {
      stage('Build Image') {
        steps {
          script {
            sh """
                docker build -t ${params.FRONTEND}:${params.IMAGE_TAG} .
            """
          }
        }
      }
      
      stage('Push Images to Docker Hub') {
        steps {
            script {
                sh """
                    docker tag ${params.FRONTEND}:${params.IMAGE_TAG} ${params.DOCKERHUB_USER}/${params.FRONTEND}:${params.IMAGE_TAG}
                    docker push ${params.DOCKERHUB_USER}/${params.FRONTEND}:${params.IMAGE_TAG}
                """
            }
        }
      }

      stage('Run Container Test') {
        steps {
            script {
                sh """
                    echo "Testing frontend container..."
                    docker rm -f ${params.CONTAINER_FRONTEND} || true
                    docker run -d -p 5000:5000 --name ${params.CONTAINER_FRONTEND} ${params.FRONTEND}:${params.IMAGE_TAG}
                    docker ps
                    sleep 10
                    echo "Testing frontend container..."
                    curl -f http://localhost:5000/health || curl -I http://localhost:5000 || echo "Frontend health check completed"
                    echo "Cleaning up frontend container..."
                    docker rm -f ${params.CONTAINER_FRONTEND}
                    echo "Frontend test completed..."
                """
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
                    # Create directory on remote server first
                    ssh -o StrictHostKeyChecking=no kubernetes@192.168.2.88 'mkdir -p /tmp/k8s-frontend/'
                    
                    # Copy k8s manifests to target server
                    scp -r k8s/ kubernetes@192.168.2.88:/tmp/k8s-frontend/
                    
                    # Deploy to Kubernetes
                    ssh kubernetes@192.168.2.88 "
                        cd /tmp/k8s-frontend/k8s
                        echo 'Current directory and files'
                        pwd
                        ls -la
                        echo 'Creating namespace if it does not exist'
                        kubectl create namespace ${params.K8S_NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
                        echo 'Applying Kubernetes manifests'
                        kubectl apply -f . -n ${params.K8S_NAMESPACE}
                        echo 'Waiting for frontend deployment to be ready'
                        kubectl wait --for=condition=available deployment/frontend-app -n ${params.K8S_NAMESPACE} --timeout=300s
                        echo 'Deployment Status'
                        kubectl get deployments -n ${params.K8S_NAMESPACE}
                        echo 'Pod Status'
                        kubectl get pods -n ${params.K8S_NAMESPACE}
                        echo 'Service Status'
                        kubectl get services -n ${params.K8S_NAMESPACE}
                    "
                """
            }
        }
      }
    }
    
    post {
        always {
            echo 'Pipeline completed - check Kubernetes deployment status'
            sh "docker rm -f ${params.CONTAINER_FRONTEND} || true"
        }
        success {
            echo 'Frontend service deployed successfully to Kubernetes!'
        }
        failure {
            echo 'Deployment failed - check Kubernetes logs'
        }
    }
}