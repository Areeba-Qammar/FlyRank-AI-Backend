# Task API (FastAPI)

A lightweight RESTful Task Management API built line-by-line using Python and FastAPI.

## How to Install & Run

1. Clone the repository and navigate to the project directory:
   ```bash
   cd task-api
   pip install fastapi uvicorn pydantic
   uvicorn main:app --reload
   Method,Endpoint,Description,Status Code
GET,/,API details & endpoints,200 OK
GET,/health,Server health check,200 OK
GET,/tasks,Get list of all tasks,200 OK
GET,/tasks/{id},Get task by ID,200 OK / 404
POST,/tasks,Create a new task,201 Created
PUT,/tasks/{id},Update an existing task,200 OK / 404
DELETE,/tasks/{id},Delete a task by ID,204 No Content / 404
HTTP/1.1 200 OK
content-type: application/json

[
  {"id": 1, "title": "Setup development environment", "completed": true},
  {"id": 2, "title": "Build FastAPI endpoints", "completed": false}
]
AI vs Me
Prompt Used
"Create a Python FastAPI Task Management API using in-memory list storage. Include endpoints for GET /, GET /health, GET /tasks, GET /tasks/{id}, POST /tasks (201), PUT /tasks/{id}, and DELETE /tasks/{id} (204). Use Pydantic models for validation and handling 404 errors."

Differences Found:
Pydantic Type Hinting: The AI used explicit Pydantic response models (response_model=List[Task]) for automatic data serialization, which added cleaner schema documentation in Swagger UI compared to manual dictionary returns.

Data Structure Types: The AI instantiated Pydantic objects (Task(...)) inside the memory list instead of raw Python dictionaries ({"id": 1, ...}).

Root Response Spec: My manual version returned explicit endpoints metadata ("endpoints": ["/tasks"]), while the AI defaulted to a generic welcome message ({"message": "..."}) because it wasn't specified in the prompt