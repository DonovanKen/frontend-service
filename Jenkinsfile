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
           dockerBuildSingle("$FRONTEND", "$IMAGE_TAG")
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
                testimageSingle("$FRONTEND", "$IMAGE_TAG", "$CONTAINER_FRONTEND")
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
                        echo 'Applying Kubernetes manifests'
                        kubectl apply -f .
                        echo 'Waiting for frontend deployment to be ready'
                        kubectl wait --for=condition=available deployment/frontend-app --timeout=300s
                        echo 'Deployment Status'
                        kubectl get deployment/frontend-app
                        echo 'Pod Status'
                        kubectl get pods -l app=frontend-app
                        echo 'Service Status'
                        kubectl get service/frontend-app
                    "
                """
            }
        }
      }
    }
    
    post {
        always {
            echo 'Pipeline completed - check Kubernetes deployment status'
        }
        success {
            echo 'Frontend service deployed successfully to Kubernetes!'
        }
        failure {
            echo 'Deployment failed - check Kubernetes logs'
        }
    }
}