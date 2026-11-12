# Course Catalog API

Backend REST API for managing courses, students, and enrollments. Built with FastAPI, PostgreSQL, SQLAlchemy 2.0, and Alembic.

## Technologies

- Python
- FastAPI
- Pydantic
- SQLAlchemy 2.0
- PostgreSQL
- Alembic
- Uvicorn

## Project Structure

```text
course-catalog-api/
├── alembic/
│   ├── versions/
│   │   ├── 0001_*.py
│   │   └── 0002_*.py
│   └── env.py
├── .env.example
├── .gitignore
├── requirements.txt
├── config.py
├── db.py
├── models.py
├── schemas.py
├── main.py
├── check_db.py
├── check_models.py
├── try_errors.py
└── README.md
```

## Setup

### 1. Create a virtual environment

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure the database

Create a PostgreSQL database and a database user.

Copy `.env.example` to `.env` and configure the connection:

```env
DATABASE_URL=postgresql+psycopg://catalog_app:YOUR_PASSWORD@localhost:5432/course-catalog-db
```

Do not commit `.env` or database credentials.

### 4. Apply migrations

```powershell
alembic upgrade head
```

For a fresh database, sample data can be inserted separately using the project's seed SQL script, if provided.

## Run

Start the development server:

```powershell
uvicorn main:app --reload
```

The API is available at:

- API root: http://127.0.0.1:8000/
- Swagger documentation: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## API Endpoints

### Courses

**`GET /courses`**

Returns a list of courses.

Supported query parameters:

- `is_elective=true/false` — filter by elective status.
- `level=beginner/intermediate` — filter by course level.
- `sort=popular` — sort by popularity.
- `sort=title` — sort alphabetically by title.
- `page` — page number.
- `page_size` — number of courses per page.

Examples:

```text
/courses
/courses?is_elective=true
/courses?level=beginner
/courses?level=intermediate
/courses?sort=title
/courses?page=2&page_size=2
```

**`GET /courses/{course_id}`**

Returns a single course by its ID.

Example:

```text
/courses/web-security
```

Returns `404 Not Found` if the course does not exist.

**`POST /courses/{course_id}/like`**

Increments the course like count and returns the updated course.

The increment is performed directly in the database using an SQL UPDATE operation.

Example:

```text
POST /courses/web-security/like
```

Returns `404 Not Found` if the course does not exist.

### Students

Student records are stored in PostgreSQL.

The API supports student creation and retrieval using SQLAlchemy models and Pydantic schemas.

### Enrollments

**`POST /enrollments`**

Creates an enrollment for an existing course and student.

Example request body:

```json
{
  "courseId": "web-security",
  "studentId": 11
}
```

**`GET /enrollments`**

Returns enrollment records.

Enrollment data is persisted in PostgreSQL.

Duplicate enrollments and references to nonexistent courses or students are handled through database constraints and application-level error handling.

## Database and Models

The project uses SQLAlchemy 2.0 ORM.

Main database models:

- `Course`
- `Student`
- `Enrollment`

The models define database tables, columns, relationships, and constraints.

Database sessions are configured centrally and injected into API routes.

PostgreSQL is used for persistent storage.

## Migrations

Alembic manages database schema changes.

The project contains two migrations:

- `0001` — creates the initial catalog tables.
- `0002` — adds the `level` column to courses.

Migration 0002 uses a three-step approach:

1. Add the column in a way that supports existing records.
2. Populate existing records with appropriate values.
3. Apply the final NOT NULL constraint.

Useful commands:

```powershell
alembic current
alembic history
alembic heads
alembic check
alembic upgrade head
```

The expected current revision is `08d83362f614`.

The project should have one migration head and no pending schema changes.

## Error Handling

Database integrity errors are mapped to appropriate HTTP responses using constraint names.

Examples:

- Duplicate student email — `409 Conflict`.
- Duplicate enrollment — `409 Conflict`.
- Unknown course — `404 Not Found`.
- Unknown student — `404 Not Found`.
- Invalid request data — `422 Unprocessable Entity`.

## Verification

Run the project verification scripts:

```powershell
python check_db.py
python check_models.py
python try_errors.py
alembic check
alembic heads
```

The error-handling test script checks five cases:

1. Duplicate email.
2. Duplicate enrollment.
3. Unknown course.
4. Unknown student.
5. Student name validation.

Previously observed result: 5/5 tests passed.

## Experiment Log

| Experiment | Description and result |
|---|---|
| 1. Naming convention | Examined how constraint naming conventions affect generated constraint names. |
| 2. Pydantic validation | Tested removing `min_length` from the student input schema. |
| 3. Constraint name typo | Examined error mapping when a constraint name does not match. |
| 4. Nullable title | Checked schema differences when the database column does not have the expected NOT NULL constraint. |
| 5. Migration 0002 | Examined adding the course level field while preserving existing records. |
| 6. Missing model import | Generated an experimental revision with no operations in this run. Restored the import and verified that `alembic check` passed. |
| 7. Model without migration | Added `phone` to the Student model temporarily. Alembic detected the missing `students.phone` column. Removed the field and verified the schema again. |
| 8. Multiple migration heads | Created two independent migration branches, observed the multiple-head error, merged the branches, and removed the experimental migration files. |

## Technical Decisions

### Why map database errors by constraint name instead of SQLSTATE?

Constraint names identify the specific business rule that was violated. This allows the application to distinguish errors such as duplicate email and duplicate enrollment and return appropriate HTTP responses.

SQLSTATE identifies a general database error category but does not always identify the specific application-level constraint.

### Why catch integrity errors after commit instead of checking with SELECT first?

A preliminary SELECT does not guarantee that the data will remain unchanged before insertion. Another transaction could insert the same value between the check and the commit.

Database constraints provide reliable protection against such race conditions. The application catches the resulting integrity error and converts it into an HTTP response.

### Why increment likes using UPDATE instead of reading and updating in Python?

A database-side operation:

```sql
UPDATE courses
SET likes = likes + 1
WHERE id = :course_id
RETURNING likes;
```

avoids a separate read-modify-write sequence in application code. It also reduces the risk of lost updates when multiple requests increment likes concurrently.

## Migration 0002 Self-Check

| Check | Result |
|---|---|
| Migration goal and steps | Reviewed |
| Existing data | Existing records preserved |
| Renames and drops | No unintended table or column deletion in the final migration |
| Rollback | Not tested against the actual database to protect existing data |
| Verification | `alembic check` passed |
| History | One head, migrations 0001 and 0002 |
| Application | API supports the course `level` field |

## Git

The `.env` file contains local database credentials and must not be committed.

The repository should contain `.env.example` with placeholder configuration instead.