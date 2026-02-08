# Phase V: Oracle Cloud Deployment (OKE)

This guide covers deploying the Chronos Todo application on Oracle Cloud Infrastructure (OCI) using Oracle Kubernetes Engine (OKE).

## Prerequisites

1. **Oracle Cloud Account** with free tier
   - Sign up at: https://www.oracle.com/cloud/free/
   - OKE Always Free: 4 OCPUs, 24GB RAM

2. **OCI CLI** - Oracle Cloud Infrastructure Command Line Interface
   ```bash
   # Install OCI CLI
   bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)"

   # Configure
   oci setup config
   ```

3. **kubectl** - Kubernetes CLI
   ```bash
   # Install kubectl
   curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
   sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
   ```

4. **Helm** - Kubernetes package manager
   ```bash
   # Install Helm
   curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
   ```

5. **Dapr** - Distributed Application Runtime
   ```bash
   # Install Dapr CLI
   wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash -s 1.0.0

   # Initialize Dapr on Kubernetes
   dapr init -k
   ```

## Creating an OKE Cluster

### Option 1: Using OCI Console

1. Navigate to **Developer Services** > **Kubernetes Clusters (OKE)**
2. Click **Create Cluster**
3. Choose **Quick Create**
4. Select **Always Free Eligible** option
5. Name your cluster: `chronos-todo-cluster`
6. Click **Create**

### Option 2: Using OCI CLI

```bash
# Get compartment OCID
oci iam compartment list

# Create OKE cluster (Always Free)
oci ce cluster create \
  --name chronos-todo-cluster \
  --compartment-id $COMPARTMENT_OCID \
  --kubernetes-version "1.29.1" \
  --name chronos-todo-cluster \
  --options '{
    "serviceLbConfig": {"isEnabled": true},
    "addons": [{"addonName": "KubeDash"}]
  }'
```

## Connecting to the Cluster

```bash
# Get cluster OCID
oci ce cluster list --compartment-id $COMPARTMENT_OCID

# Generate kubeconfig
oci ce cluster create-kubeconfig \
  --cluster-id $CLUSTER_OCID \
  --file $HOME/.kube/config-chronos \
  --region us-ashburn-1

# Set KUBECONFIG
export KUBECONFIG=$HOME/.kube/config-chronos

# Verify connection
kubectl get nodes
```

## Building and Pushing Images

### Option 1: Use Oracle Container Registry (OCIR)

```bash
# Create repository in OCIR
oci artifacts container repository create \
  --compartment-id $COMPARTMENT_OCID \
  --display-name chronos-todo-backend \
  --is-public true

oci artifacts container repository create \
  --compartment-id $COMPARTMENT_OCID \
  --display-name chronos-todo-frontend \
  --is-public true

# Login to OCIR
docker login phx.ocir.io

# Tag images
docker tag chronos-backend:latest phx.ocir.io/$TENANCY/chronos-todo-backend:latest
docker tag chronos-frontend:latest phx.ocir.io/$TENANCY/chronos-todo-frontend:latest

# Push images
docker push phx.ocir.io/$TENANCY/chronos-todo-backend:latest
docker push phx.ocir.io/$TENANCY/chronos-todo-frontend:latest
```

### Option 2: Use Docker Hub (simpler for hackathon)

```bash
# Tag images
docker tag chronos-backend:latest YOUR_USERNAME/chronos-backend:latest
docker tag chronos-frontend:latest YOUR_USERNAME/chronos-frontend:latest

# Push to Docker Hub
docker push YOUR_USERNAME/chronos-backend:latest
docker push YOUR_USERNAME/chronos-frontend:latest
```

## Deploying with Helm

### Create Secrets

```bash
# Create namespace
kubectl create namespace chronos

# Create secret with all sensitive values
kubectl create secret generic chronos-secrets \
  --from-literal=database-password='npg_cXY2EI8DAqhx' \
  --from-literal=openai-api-key='sk-proj-...' \
  --from-literal=qdrant-api-key='eyJhbGci...' \
  --from-literal=resend-api-key='re_MycPDamK...' \
  --from-literal=resend-webhook-secret='whsec_TrpKkW...' \
  --from-literal=better-auth-secret='mlHt/eQkNbw8oSExN56WdGS0dxwBdNGtMtG0XJ7jveE=' \
  --from-literal=vapid-public-key='BLnlI3_WvJ6cDbDuyen07L4GOcqxPZFAoJJ4z48mvaK3VC2XMSylx6xlTTUTFWTuMyvIoVMZRe43PHubaZXEysY' \
  --from-literal=vapid-private-key='J4fh6gilYWT5RXJdm211piusPnlRsVVF2-vqwS3yGpA' \
  --namespace=chronos
```

### Install Helm Chart

```bash
helm install chronos-todo ./helm/chronos-todo \
  --namespace chronos \
  --set global.environment=production \
  --set oracle.enabled=true \
  --set frontend.image.repository=YOUR_USERNAME/chronos-frontend \
  --set backend.image.repository=YOUR_USERNAME/chronos-backend \
  --set frontend.buildArgs.NEXT_PUBLIC_API_URL=https://api.YOUR_DOMAIN.com \
  --set frontend.buildArgs.NEXT_PUBLIC_APP_URL=https://YOUR_DOMAIN.com \
  --create-namespace
```

### Configure Load Balancers

Oracle Cloud provides Load Balancers with the Always Free tier. The Helm chart includes annotations for OCI load balancers:

```yaml
# In values.yaml
oracle:
  enabled: true
  loadBalancerAnnotations:
    service.beta.kubernetes.io/oci-load-balancer-shape: "flexible"
    service.beta.kubernetes.io/oci-load-balancer-shape-flex-min: "10"
    service.beta.kubernetes.io/oci-load-balancer-shape-flex-max: "100"
```

## Getting External IPs

```bash
# Get LoadBalancer IPs
kubectl get svc -n chronos

# Wait for EXTERNAL-IP to be assigned (may take a few minutes)
watch kubectl get svc -n chronos
```

## Setting Up DNS (Optional)

1. Create DNS A records pointing to the LoadBalancer IPs:
   ```
   chronos.YOUR_DOMAIN.com → Frontend LB IP
   api.chronos.YOUR_DOMAIN.com → Backend LB IP
   ```

2. Update frontend environment variables with the new URLs:
   ```bash
   helm upgrade chronos-todo ./helm/chronos-todo \
     --namespace chronos \
     --set frontend.buildArgs.NEXT_PUBLIC_API_URL=https://api.chronos.YOUR_DOMAIN.com \
     --set frontend.buildArgs.NEXT_PUBLIC_APP_URL=https://chronos.YOUR_DOMAIN.com
   ```

## Verifying Deployment

```bash
# Check all pods are running
kubectl get pods -n chronos

# Check services
kubectl get svc -n chronos

# Check Dapr components
kubectl get components -n chronos
kubectl get configurations -n chronos

# View logs
kubectl logs -f deployment/chronos-todo-backend -n chronos
```

## Testing the Application

1. Access the frontend at `https://chronos.YOUR_DOMAIN.com`
2. Sign up for a new account
3. Create a task via the UI
4. Test the AI chatbot
5. Verify Kafka events are being published:
   ```bash
   # Port forward to Redpanda
   kubectl port-forward -n chronos svc/chronos-todo-redpanda 9644:9644

   # Check topics
   curl http://localhost:9644/v1/topics
   ```

## Dapr Dashboard (Optional)

```bash
# Install Dapr dashboard
dapr dashboard -k -n chronos

# Access at http://localhost:8080
```

## Monitoring with OCI Logging

Enable OCI Logging for OKE:

```bash
# Enable logging
oci logging service enable \
  --compartment-id $COMPARTMENT_OCID \
  --service-id $CLUSTER_OCID

# View logs
oci logging log list --compartment-id $COMPARTMENT_OCID
```

## Troubleshooting

### Pod Not Starting

```bash
# Describe pod for events
kubectl describe pod <pod-name> -n chronos

# Check logs
kubectl logs <pod-name> -n chronos
```

### Load Balancer Not Provisioning

```bash
# Check OCI load balancer
oci lb load-balancer list --compartment-id $COMPARTMENT_OCID

# Verify annotations
kubectl get svc chronos-todo-backend -n chronos -o yaml
```

### Dapr Sidecar Issues

```bash
# Check Dapr installation
dapr status -k -n chronos

# Check Dapr sidecar logs
kubectl logs <pod-name> -c daprd -n chronos
```

### Database Connection

```bash
# Test connectivity from pod
kubectl run -it --rm debug --image=nicolaka/netshoot --restart=Never -n chronos
# Inside pod:
# telnet ep-fragrant-firefly-ahri4549.c-3.us-east-1.aws.neon.tech 5432
```

## Cleanup

```bash
# Uninstall Helm release
helm uninstall chronos-todo -n chronos

# Delete namespace
kubectl delete namespace chronos

# Delete OKE cluster (via Console or CLI)
oci ce cluster delete --cluster-id $CLUSTER_OCID --force
```

## Cost Optimization (Always Free)

- Use Always Free OKE cluster (4 OCPUs, 24GB RAM)
- Use flexible load balancer (10-100 Mbps)
- Keep Redpanda replica at 1
- Set resource limits appropriately
- Delete cluster when not in use

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   Oracle Cloud Infrastructure                   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Oracle Kubernetes Engine (OKE)              │   │
│  │                                                          │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │   │
│  │  │  Frontend    │  │  Backend     │  │   Redpanda  │  │   │
│  │  │  (Next.js)   │  │  (FastAPI)   │  │   (Kafka)   │  │   │
│  │  │              │  │              │  │             │  │   │
│  │  │  + Dapr      │  │  + Dapr      │  │             │  │   │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬──────┘  │   │
│  │         │                 │                 │          │   │
│  │         └─────────────────┴─────────────────┘          │   │
│  │                           │                             │   │
│  └───────────────────────────┼─────────────────────────────┘   │
│                              │                                  │
│  ┌───────────────────────────┼─────────────────────────────┐   │
│  │        OCI Load Balancer  │                              │   │
│  └───────────────────────────┴─────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    External Cloud Services                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │
│  │  Neon    │  │  Qdrant  │  │  OpenAI  │  │   Resend     │   │
│  │  Postgres│  │  Cloud   │  │   API    │  │   Email      │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## CI/CD with GitHub Actions (Optional)

Create `.github/workflows/deploy-oke.yml`:

```yaml
name: Deploy to Oracle OKE

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Configure Kubeconfig
        run: |
          echo "${{ secrets.OCI_KUBECONFIG }}" > kubeconfig
          export KUBECONFIG=kubeconfig

      - name: Deploy with Helm
        run: |
          helm upgrade --install chronos-todo ./helm/chronos-todo \
            --namespace chronos \
            --create-namespace \
            --set oracle.enabled=true
```

## Congratulations!

You have successfully deployed the Chronos Todo application to Oracle Cloud Infrastructure using Kubernetes, Dapr, and Kafka!
