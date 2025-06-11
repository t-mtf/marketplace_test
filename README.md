# Marketplace Orders API

This project is a technical test build with **Django**, which involves parsing an XML file containing orders, saving them to a database, and exposing this data through a REST API.

## Tech Stack

- Python 3.12
- Django 5.2
- Django REST Framework
- SQLite 
- Docker + Docker Compose
- Uvicorn
- uv (project and dependency manager)
- Ruff (linting PEP8)
- Pytest (unit tests)

## Main directories and files

- `config/` — Django project (settings, urls, asgi)
- `orders/` — Django application containing the `Order` model, views, orders import command and unit tests
- `docker-entrypoint.sh` — Docker startup script 
- `Dockerfile` — Docker image definition 
- `compose.yml` — Docker compose configuration 
- `pyproject.toml` — Dependencies managed with `uv`
- `README.md`

## Running the app with Docker

The following commands should be run from the project root folder `marketplace_test`.   

### Environment variables file

Before launching the app, you must create an environment variable file named `.env` at the root of the project (i.e `marketplace_test`) and include the following 3 variables: 

```bash
SECRET_KEY = "you-generated-key" 
DEBUG = False 
ALLOWED_HOSTS=localhost,127.0.0.1
```
If needed, you can generate the key using:
```bash
python generate_secret_key.py
``` 

### Build and start the app

```bash
docker compose build --no-cache
docker compose up -d
```
This will:
- Install dependencies using `uv` 
- Apply database migrations and call orders import command
- Start the server using `uvicorn`

The application will be available at [localhost:8000](http://localhost:8000/orders/)

## API endpoints

The API exposes two endpoints:

### 1. List orders
```bash
GET /orders/
```

Response:

```json
[
    {
        "id": 1,
        "order_id": "111-2222222-3333333",
        "marketplace": "amazon",
        "order_amount": "34.50",
        "order_currency": "EUR",
        "delivery_full_address": "014 rue de la poupée   75000 Paris FR"
    },
    ...
]
```

### 2. Order details
```bash
GET /orders/{id}
```
Response:

```json
{
    "id": 2,
    "order_id": "123-4567890-1112131",
    "marketplace": "amazon",
    "order_amount": "115.50",
    "order_currency": "EUR",
    "delivery_full_address": "1512 Rue de l'Impasse   44000 Nantes FR"
}
```
## Tests and coverage 

Unit tests are available in `orders/tests/`:

```bash
docker exec order_api uv run pytest --cov=./ --cov-config=coverage.ini 
```

## Linting with default rules

This project uses **Ruff** for code linting:

```bash
docker exec order_api uv run ruff check .
```