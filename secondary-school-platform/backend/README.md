# API starter

Local smoke-test API for the separate secondary-school product.

## Local run
```bash
cd secondary-school-platform/backend
python -m venv .venv
# Activate the virtual environment, then:
pip install -r requirements.txt
python -m unittest -v
python app.py
```

Health endpoint: `GET /health`
Illustrative catalogue: `GET /api/v1/catalogue`

## Deliberate limitations
This is not production-ready. It has no database connection, authentication, admin authorisation, payment processing, webhook, media delivery or student data. The catalogue is sample data only. Do not connect it to live payments or publish it as the student service until the security and persistence phases are implemented and tested.
