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

## Setup

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

## Run

Start the development server:

```powershell
fastapi dev main.py
```

The API is available at:

- API root: http://127.0.0.1:8000/
- Swagger documentation: http://127.0.0.1:8000/docs

## API Endpoints

### `GET /`

Health check endpoint.

### `GET /courses`

Returns the list of courses.

Supported query parameters:

- `is_elective=true/false` — filter courses by elective status
- `sort=popular` — sort by popularity
- `sort=title` — sort alphabetically by title
- `page` — page number
- `page_size` — number of courses per page

Examples:

```text
/courses
/courses?is_elective=true
/courses?is_elective=false
/courses?sort=title
/courses?page=2&page_size=2
```

### `GET /courses/{course_id}`

Returns a single course by its ID.

Example:

```text
/courses/web-security
```

If the course does not exist, the API returns `404 Not Found`.

### `POST /courses/{course_id}/like`

Increments the like count of a course and returns the updated course.

Example:

```text
POST /courses/web-security/like
```

Returns `404 Not Found` if the course does not exist.

### `POST /enrollments`

Creates an enrollment for an existing course.

Example request body:

```json
{
  "courseId": "web-security",
  "studentName": "Aigerim"
}
```

The `studentName` field must contain at least two characters. The `courseId` must reference an existing course.

- `201 Created` — enrollment created successfully
- `404 Not Found` — course does not exist
- `422 Unprocessable Entity` — request validation failed

### `GET /enrollments`

Returns the enrollments stored in the running application.

## CORS Configuration

The API allows browser requests from the frontend development origin:

```text
http://localhost:3000
```

The FastAPI application uses `CORSMiddleware` with the following settings:

```python
allow_origins=["http://localhost:3000"]
allow_methods=["*"]
allow_headers=["*"]
```

The frontend must use the allowed origin exactly. For example, `http://127.0.0.1:3000` is a different origin from `http://localhost:3000`.

CORS controls whether browser JavaScript can access cross-origin responses. It does not prevent server-to-server requests from Next.js to FastAPI.

## Data Models and JSON Naming

Pydantic models use a shared `CamelModel` configuration with `to_camel` as the alias generator.

Python code uses snake_case attributes such as:

- `is_elective`
- `course_id`
- `student_name`

JSON requests and responses use camelCase aliases, such as:

- `isElective`
- `courseId`
- `studentName`

The API accepts field names and aliases during validation.

## Storage

Courses are loaded from the project's data module. Likes are updated in application memory.

Enrollments are also stored in an in-memory list. They are not persisted to a database, and the list resets when the application restarts.

## What Was Verified

- `GET /` returns `200 OK`
- `GET /courses` returns six courses
- `GET /courses/web-security` returns the requested course
- `GET /courses/nope` returns `404 Not Found`
- `is_elective=true` returns two courses
- `is_elective=false` returns four courses
- `sort=title` sorts courses alphabetically
- `page=2&page_size=2` returns the second page
- Swagger documentation is available at `/docs`
- CORS allows the configured frontend origin
- Course responses use camelCase JSON aliases
- `POST /courses/{course_id}/like` increments the like count
- `POST /enrollments` validates and creates an enrollment
- `GET /enrollments` returns created enrollments
- Invalid enrollment data returns `422`
- Enrollment for an unknown course returns `404`
