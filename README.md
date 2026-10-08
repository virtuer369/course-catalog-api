# Course Catalog API

Backend API for the Course Catalog project built with FastAPI and Pydantic.

## Technologies

- Python
- FastAPI
- Pydantic
- Uvicorn

## Project Structure

```text
course-catalog-api/
├── .gitignore
├── README.md
├── requirements.txt
├── models.py
├── data.py
└── main.py
```

Setup
Create a virtual environment:
python -m venv .venv

Activate it:
.venv\Scripts\Activate.ps1

Install dependencies:
pip install -r requirements.txt

Run
Start the development server:
fastapi dev main.py

Swagger documentation:
http://127.0.0.1:8000/docs

API Endpoints
GET /
Health check endpoint.
GET /courses
Returns the list of courses.
Supported query parameters:
- is_elective=true/false
- sort=popular
- sort=title
- page
- page_size
Examples:
/courses
/courses?is_elective=true
/courses?is_elective=false
/courses?sort=title
/courses?page=2&page_size=2

GET /courses/{course_id}
Returns a single course by its ID.
Example:
/courses/web-security

If the course does not exist, the API returns 404.
What Was Verified
- GET / returns 200 OK
- GET /courses returns 6 courses
- GET /courses/web-security returns the course
- GET /courses/nope returns 404
- is_elective=true returns 2 courses
- is_elective=false returns 4 courses
- sort=title sorts courses alphabetically
- page=2&page_size=2 returns the second page
- Swagger documentation is available at /docs