# ML Inference Service

## Purpose

This is a **standalone ML inference service** that provides AI-powered expense categorization. It is completely isolated from the backend application and communicates only via REST API.

## Architecture Principles

### Service Boundaries
- ✅ **DOES:** Load models, perform inference, return predictions
- ❌ **DOES NOT:** Handle auth, access databases, implement business logic

### Independence
- Can deploy, restart, and scale without backend
- Backend can deploy and run without this service
- No shared code or dependencies

---

## Quick Start

### Installation

```bash
# Navigate to ML service directory
cd ml-service

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create `.env` file:

```bash
ML_SERVICE_HOST=0.0.0.0
ML_SERVICE_PORT=8000
MODEL_PATH=models/expense_category_model.pkl
VECTORIZER_PATH=models/tfidf_vectorizer.pkl
LOG_LEVEL=INFO
```

### Run Service

```bash
# Development
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## API Endpoints

### Health Check
```bash
GET /health
```

### Predict Category
```bash
POST /api/v1/predict/category
Content-Type: application/json

{
  "description": "Zomato food order"
}
```

### Model Info
```bash
GET /api/v1/model/info
```

See [API_CONTRACT.md](./API_CONTRACT.md) for full specification.

---

## Project Structure

```
ml-service/
├── main.py                 # FastAPI application
├── models.py               # ML model loading and inference
├── preprocessing.py        # Text preprocessing functions
├── schemas.py              # Pydantic request/response schemas
├── config.py               # Configuration management
├── requirements.txt        # Dependencies
├── models/                 # Model files (not in repo)
│   ├── expense_category_model.pkl
│   └── tfidf_vectorizer.pkl
├── tests/                  # Unit and integration tests
│   ├── test_inference.py
│   └── test_api.py
└── README.md
```

---

## Model Files

Model files are **NOT stored in this repository** for these reasons:
1. Large file size (50MB+)
2. Frequent updates
3. Environment-specific

### How to Get Models

**Option 1: Copy from Training**
```bash
# After training, copy models to ml-service
cp ../ml/expense_category_model.pkl models/
cp ../ml/tfidf_vectorizer.pkl models/
```

**Option 2: Download from Storage**
```bash
# Production: Download from cloud storage
aws s3 cp s3://your-bucket/models/ models/ --recursive
```

**Option 3: Mount Volume (Docker)**
```yaml
volumes:
  - ./models:/app/models:ro
```

---

## Testing

```bash
# Run unit tests
pytest tests/

# Test API manually
curl http://localhost:8000/health

# Load test
ab -n 1000 -c 10 -p request.json -T application/json \
   http://localhost:8000/api/v1/predict/category
```

---

## Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Model files mounted as volume or copied separately
VOLUME /app/models

# Expose port
EXPOSE 8000

# Run service
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t ml-service:latest .
docker run -p 8000:8000 -v $(pwd)/models:/app/models ml-service:latest
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-service
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: ml-service
        image: ml-service:latest
        ports:
        - containerPort: 8000
        volumeMounts:
        - name: models
          mountPath: /app/models
          readOnly: true
        resources:
          limits:
            memory: "512Mi"
            cpu: "500m"
      volumes:
      - name: models
        persistentVolumeClaim:
          claimName: ml-models-pvc
```

---

## Performance

### Expected Metrics
- **Startup Time:** < 5 seconds
- **Inference Time (P50):** < 50ms
- **Inference Time (P95):** < 150ms
- **Memory Usage:** ~300MB
- **Throughput:** > 100 req/sec

### Optimization Tips
1. **Preload Models:** Load at startup, not on first request
2. **Use Workers:** Multiple Uvicorn workers for parallelism
3. **Cache Preprocessing:** Reuse vectorizer transformations
4. **Batch Predictions:** Process multiple requests together
5. **Monitor Memory:** Ensure models fit in available RAM

---

## Monitoring

### Health Checks
```bash
# Kubernetes liveness probe
GET /health

# Expected: 200 OK with {"status": "healthy"}
```

### Metrics to Track
- Request latency (P50, P95, P99)
- Error rate
- Model load status
- Memory usage
- CPU usage
- Throughput (req/sec)

### Logging
```python
# Structured logging format
{
  "timestamp": "2026-01-05T10:30:00Z",
  "level": "INFO",
  "service": "ml-inference",
  "event": "prediction",
  "duration_ms": 45,
  "category": "Food",
  "confidence": 0.85
}
```

---

## Troubleshooting

### Model Not Found
```
Error: Model files not found at models/
```
**Solution:** Copy model files or mount volume with models

### Out of Memory
```
Error: MemoryError during model loading
```
**Solution:** Increase container memory limit or reduce model size

### Slow Inference
```
Warning: Inference time > 200ms
```
**Solution:** Check if models are loaded in memory, not reading from disk

---

## Model Updates

### How to Update Models

1. **Train New Model** (in ml/ directory)
2. **Copy New Model Files**
   ```bash
   cp new_model.pkl models/expense_category_model.pkl
   ```
3. **Restart Service** (zero-downtime with rolling update)
4. **Verify** with test requests

### Zero-Downtime Updates (Kubernetes)
```bash
# Rolling update
kubectl rollout restart deployment/ml-service

# Monitor rollout
kubectl rollout status deployment/ml-service
```

---

## Security

### What This Service Receives
- ✅ Transaction descriptions (text only)
- ❌ NO user credentials
- ❌ NO financial amounts
- ❌ NO personal information

### Best Practices
1. **No Authentication Required:** Lightweight internal service
2. **Network Isolation:** Only accessible from backend service
3. **Input Validation:** Strict schema validation with Pydantic
4. **Rate Limiting:** Implement in API gateway/load balancer
5. **Audit Logging:** Log all predictions for debugging

---

## FAQ

### Q: Why separate service?
**A:** To keep backend lightweight, reduce deployment size, and allow independent scaling.

### Q: What if ML service is down?
**A:** Backend continues working with graceful fallback (null category or default).

### Q: Can I run multiple instances?
**A:** Yes! Service is stateless and can scale horizontally.

### Q: How do I add a new model?
**A:** Train model, copy to `models/`, restart service. No code changes needed.

### Q: What about real-time retraining?
**A:** Not in this service. Retrain offline, then hot-swap model files.

---

## Contributing

### Adding New Features
1. Keep service focused on inference only
2. No database connections
3. No business logic
4. Maintain API contract

### Code Style
- Follow PEP 8
- Type hints required
- Docstrings for all functions
- Unit tests for new features

---

## License

Same as parent project.

---

## Contact

For issues or questions, see main project documentation.
