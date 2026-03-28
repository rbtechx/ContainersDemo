# ContainersDemo — AWS IP Ranges API

A lightweight Python REST API (FastAPI) that fetches
[`https://ip-ranges.amazonaws.com/ip-ranges.json`](https://ip-ranges.amazonaws.com/ip-ranges.json)
and returns filtered IPv4/IPv6 prefixes.  
The default filter is **region `us-east-1` (North Virginia)** and **service `EC2`**.

---

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness probe |
| GET | `/ip-ranges` | Filtered prefix list |

### Query parameters for `/ip-ranges`

| Parameter | Default | Example |
|-----------|---------|---------|
| `region` | `us-east-1` | `eu-west-1` |
| `service` | `EC2` | `S3`, `CLOUDFRONT` |

### Example response

```json
{
  "sync_token": "1711929439",
  "create_date": "2024-04-01-00-00-00",
  "region": "us-east-1",
  "service": "EC2",
  "ipv4_prefixes": ["3.80.0.0/12", "52.2.0.0/15", "..."],
  "ipv6_prefixes": ["2600:1f18::/36", "..."],
  "ipv4_count": 42,
  "ipv6_count": 5
}
```

Interactive docs are available at `http://localhost:8000/docs` when the server is running.

---

## Running locally

### Python (virtual environment)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Docker

```bash
docker build -t ip-ranges-api .
docker run -p 8000:8000 ip-ranges-api
```

### Docker Compose

```bash
docker compose up --build
```

---

## Tests

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

---

## Deployment

### Prerequisites

- A container registry (ECR for EKS, ACR for AKS).
- Build and push the image:

  ```bash
  # Example for ECR
  docker build -t <account>.dkr.ecr.<region>.amazonaws.com/ip-ranges-api:latest .
  docker push <account>.dkr.ecr.<region>.amazonaws.com/ip-ranges-api:latest
  ```

- Update the `image:` field in `k8s/deployment.yaml` with your registry path.

### AWS EKS

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress-eks.yaml   # requires AWS Load Balancer Controller
```

### Azure AKS

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress-aks.yaml   # requires NGINX Ingress Controller
```

---

## Project structure

```
.
├── app/
│   ├── main.py                # FastAPI application
│   └── services/
│       └── ip_ranges.py       # Fetch & filter logic
├── tests/
│   └── test_api.py
├── k8s/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress-eks.yaml       # AWS EKS (ALB)
│   └── ingress-aks.yaml       # Azure AKS (NGINX)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── requirements-dev.txt
```
