Streamlit Application Deployment on Kubernetes

1)Project Overview:

   This repository contains all necessary files to deploy a Streamlit-based document chat application using Kubernetes and Minikube. The                
   application supports document uploads, vector storage with FAISS, and uses Google Gemini for AI-based responses.

2)Prerequisites:

Before deploying, ensure you have the following installed:
   Docker
   Minikube
   Kubectl
   Python 3.9+

3)Steps to Deploy

->Build and Push Docker Image:

   sh
   Copy
   Edit
  # Navigate to the project folder
   cd path/to/project

  # Build the Docker image
   docker build -t <your-dockerhub-username>/streamlit-app:v1 .

  # Push to Docker Hub (or private registry)
   docker push <your-dockerhub-username>/streamlit-app:v1

->Start Minikube:

   sh
   Copy
   Edit
   minikube start
 Ensure Minikube is running with:

   sh
   Copy
   Edit
   kubectl get nodes

4)Apply Kubernetes Manifests:

->Create Persistent Storage:

   sh
   Copy
   Edit
   kubectl apply -f pv.yaml
   kubectl apply -f pvc.yaml

->Deploy ConfigMap and Secret:

   sh
   Copy
   Edit
   kubectl apply -f configmap.yaml
   kubectl apply -f secret.yaml

->Deploy the Application:

   sh
   Copy
   Edit
   kubectl apply -f deployment.yaml
   kubectl apply -f service.yaml
   kubectl apply -f hpa.yaml

5)Verify Deployment:

->Check running pods:

   sh
   Copy
   Edit
   kubectl get pods

->Check services:

   sh
   Copy
   Edit
   kubectl get services

->Access the application:

   sh
   Copy
   Edit
   minikube service streamlit-service --url

  Copy the URL and open it in your browser.

6)Scaling and Auto-scaling Tests:

->Test 1: Application Availability

   sh
   Copy
   Edit
   kubectl get services
 curl http://<EXTERNAL-IP>:<PORT>

Expected output: The Streamlit homepage or API response.

->Test 2: Horizontal Pod Autoscaler

   sh
   Copy
   Edit
   kubectl get hpa
   kubectl run --rm -it --image=busybox stress-test -- /bin/sh

Inside BusyBox shell:

   sh
   Copy
   Edit
   while true; do wget -q -O- http://<SERVICE-IP>:<PORT>; done

Expected output: Number of pods should increase dynamically.

->Test 3: Rolling Update

   sh
   Copy
   Edit
   kubectl set image deployment/streamlit-app streamlit=<your-dockerhub-username>/streamlit-app:v2
   kubectl rollout status deployment/streamlit-app
Expected output: New version is deployed with zero downtime.

->Test 4: Rollback

   sh
   Copy
   Edit
   kubectl rollout undo deployment/streamlit-app
Expected output: Application reverts to the previous working version.

->Test 5: Self-healing

   sh
   Copy
   Edit
   kubectl delete pod <POD_NAME>

Expected output: A new pod should be automatically created.

->Test 6: Logging

   sh
   Copy
   Edit
   kubectl logs <POD_NAME>

Expected output: Application logs should be displayed.

7)Deliverables:

->GitHub repository containing:
   Dockerfile
   Kubernetes YAML manifests (deployment.yaml, service.yaml, hpa.yaml, etc.)
   Step-by-step README.md
->Demo Video (3-5 minutes) explaining the deployment
->Screenshots of running Minikube cluster & auto-scaling in action
->Test Case Documentation for all six tests above


8)Troubleshooting:

->How to Restart a Pod:

   sh
   Copy
   Edit
   kubectl rollout restart deployment/streamlit-app

->How to Delete Everything:

   sh
   Copy
   Edit
   kubectl delete -f .

->Check Pod Logs:

   sh
   Copy
   Edit
   kubectl logs -f <POD_NAME>
