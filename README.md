# Course Catalog API

Backend REST API for managing courses, students, and enrollments. Built with FastAPI, PostgreSQL, SQLAlchemy 2.0, and Alembic.

## Lab 8: REST and GraphQL

The API now exposes both REST and Strawberry GraphQL over the same PostgreSQL database and SQLAlchemy services. Expected application errors are raised from `services.py`; REST converts them to `application/problem+json`, while GraphQL returns them in `userErrors`. GraphQL query errors remain in the top-level `errors` array even when the HTTP status is 200.

### Run

Install the requirements in the project virtual environment, copy `.env.example` to `.env`, set `DATABASE_URL`, and confirm the Lab 7 schema is at Alembic head with the seed data loaded. Start the API with:

```powershell
fastapi dev main.py
```

REST docs are at `http://localhost:8000/docs`; GraphiQL is at `http://localhost:8000/graphql`. Set `GRAPHQL_INTROSPECTION=false` in `.env` to disable schema introspection. `SQL_ECHO=true` logs SQL during the N+1 exercise. Every response includes the `X-SQL-Queries` header.

To reset a local training database to the six courses, three students, and six enrollments, run `psql -h localhost -U catalog_app -d course_catalog -v ON_ERROR_STOP=1 -f seed.sql` from this folder. This intentionally clears the catalog tables before inserting the fixture.

### GraphQL examples

The `MyCourses` query returns exactly the fields used by the screen:

```graphql
query MyCourses($id: ID!) {
  student(id: $id) {
    name
    enrollments { id course { title credits level } }
  }
}
```

Variables: `{ "id": "2" }`.

Enrollments use a payload so expected business errors are part of the normal response:

```graphql
mutation Enroll($input: EnrollInput!) {
  enroll(input: $input) {
    enrollment { id }
    userErrors { code message }
  }
}
```

Variables: `{ "input": { "courseId": "web-security", "studentId": "3" } }`.
The schema SDL can be printed with `python print_schema.py`.

### REST vs GraphQL measurement

`python measure.py` reproduces the two server-side frontend data paths for student 2. With the supplied seed data and DataLoaders, the lab's reference measurements are:

| API | Requests | Network rounds | Response bytes | SQL queries |
|---|---:|---:|---:|---:|
| REST | 5 | 2 | about 1,160 | 5 |
| GraphQL | 1 | 1 | about 339 | 3 |

The byte counts vary slightly with the data. REST needs a second round because the course IDs arrive in the enrollment response; GraphQL returns the selected course fields in one response. DataLoaders batch related records and bring the nested GraphQL query cost down from 7 queries (3 students) or 27 (20 students) to 3. The `more_students.sql` fixture adds students 4–20 and should only be run once before reseeding.

### Experiment log

The following are the outcomes the lab exercises are designed to demonstrate. Run the scripts against the local seeded database to record machine-specific timings and confirm the responses before a live demonstration.

| Experiment | Observation | Explanation |
|---|---|---|
| 1. Query validation | A typo such as `titel` returns HTTP 200, `data: null`, and a GraphQL `errors` entry with a “Did you mean” hint. | GraphQL query errors are in the response body; HTTP success alone does not mean the query succeeded. |
| 2. Nullability | Removing `| None` from `course` makes a missing course bubble to `data: null`; restoring it returns that field as `null` while preserving sibling data. | A non-null schema field is a promise; a null violation propagates to the nearest nullable parent. |
| 3. Mutation over GET | A GraphQL query works over GET; a mutation over GET receives HTTP 400 and does not change likes. | GET must remain safe to repeat, prefetch, and cache. |
| 4. N+1 growth | Before loaders, the nested query takes 7 SQL statements for 3 students and 27 for 20; GraphiQL may still look quick. | Lazy relationship access issues separate statements for each parent and related object. |
| 5. Broken batch result | Returning rows in database order can first raise `WrongNumberOfResultsReturned`; when key and row counts happen to match, it can silently associate the wrong course with an enrollment. | A DataLoader batch must return one result per input key in the same key order. |
| 6. Query protections | Depth over 5 and more than 10 aliases are rejected; invalid limits and nonnumeric IDs receive clear errors; unexpected database errors are masked. Twelve aliased likes are rejected before SQL execution. | Depth and alias limits constrain one request; argument validation helps clients fix input; `MaskErrors` hides internal details. |
| 7. Introspection | With `GRAPHQL_INTROSPECTION=false`, `__schema` is rejected, ordinary queries still work, and typo hints can still reveal field names. | Disabling introspection hides schema browsing, but it is not authorization. |
| 8. Frontend error handling | A bad GraphQL field becomes `GraphQLRequestError`; without the `errors` check the page instead crashes while reading null data; a stopped API causes `fetch failed`. | GraphQL errors can arrive with status 200, so the client must inspect `errors`; network failures have no GraphQL response. |

The detailed response and SQL counts are produced by `try_graphql.py`, `try_n_plus_1.py`, `try_protection.py`, `flood_likes.py`, and `measure.py`. Restore the seed data after write experiments before comparing the reference measurements.

### Project structure additions

`services.py`, `problem.py`, `graphql_api.py`, and `counter.py` implement shared services, REST errors, GraphQL schema/resolvers, and per-request SQL counting. `try_errors.py`, `try_graphql.py`, `try_n_plus_1.py`, `try_protection.py`, `flood_likes.py`, `measure.py`, `more_students.sql`, and `print_schema.py` are lab exercises and measurement helpers.

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
