# FastAPI Math Operations API

A simple REST API built with FastAPI that provides basic math operations: addition, subtraction, and multiplication.

## Features

- **Add**: Add two numbers
- **Subtract**: Subtract two numbers
- **Multiply**: Multiply two numbers
- Comprehensive test coverage with pytest
   
## Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone or navigate to the project directory:
```bash
cd codecov
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up Git hooks (optional but recommended):
```bash
# Linux/macOS
chmod +x setup-git-hooks.sh
./setup-git-hooks.sh

# Windows
setup-git-hooks.bat
```

The Git hooks will run tests before allowing pushes. See [BRANCH_PROTECTION.md](BRANCH_PROTECTION.md) for details on the two-layer enforcement system.

## Running the API

Start the development server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Interactive API Documentation

Once the server is running, you can access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

All endpoints accept POST requests with a JSON body containing two numbers.

### Request Format

```json
{
  "a": 10.5,
  "b": 5.2
}
```

### Response Format

```json
{
  "result": 15.7
}
```

### Endpoints

#### POST /add
Adds two numbers together.

**Example Request:**
```bash
curl -X POST "http://localhost:8000/add" \
  -H "Content-Type: application/json" \
  -d '{"a": 10, "b": 5}'
```

**Example Response:**
```json
{
  "result": 15
}
```

#### POST /subtract
Subtracts the second number from the first.

**Example Request:**
```bash
curl -X POST "http://localhost:8000/subtract" \
  -H "Content-Type: application/json" \
  -d '{"a": 10, "b": 5}'
```

**Example Response:**
```json
{
  "result": 5
}
```

#### POST /multiply
Multiplies two numbers together.

**Example Request:**
```bash
curl -X POST "http://localhost:8000/multiply" \
  -H "Content-Type: application/json" \
  -d '{"a": 10, "b": 5}'
```

**Example Response:**
```json
{
  "result": 50
}
```

## Running Tests

Run all tests:
```bash
pytest
```

Run tests with verbose output:
```bash
pytest -v
```

Run tests with coverage:
```bash
pytest --cov=app
```

## Project Structure

```
codecov/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application and routes
│   └── models.py        # Request/response models
├── tests/
│   ├── __init__.py
│   └── test_api.py      # Test cases for all endpoints
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Error Handling

The API validates input and returns HTTP 422 (Unprocessable Entity) for:
- Missing required fields (`a` or `b`)
- Invalid data types (non-numeric values)

