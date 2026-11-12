import requests

BASE_URL = "http://127.0.0.1:8000"

tests = [
    {
        "name": "Duplicate email",
        "method": "POST",
        "url": "/students",
        "json": {
            "name": "Another Aigerim",
            "email": "aigerim@example.com"
        },
        "expected": 409,
    },
    {
        "name": "Duplicate enrollment",
        "method": "POST",
        "url": "/enrollments",
        "json": {
            "courseId": "ai-integration",
            "studentId": 3
        },
        "expected": 409,
    },
    {
        "name": "Unknown course",
        "method": "POST",
        "url": "/enrollments",
        "json": {
            "courseId": "nope",
            "studentId": 3
        },
        "expected": 404,
    },
    {
        "name": "Unknown student",
        "method": "POST",
        "url": "/enrollments",
        "json": {
            "courseId": "web-security",
            "studentId": 999
        },
        "expected": 404,
    },
    {
        "name": "Name too short",
        "method": "POST",
        "url": "/students",
        "json": {
            "name": "A",
            "email": "short@example.com"
        },
        "expected": 422,
    },
]

passed = 0

for test in tests:
    response = requests.request(
        test["method"],
        BASE_URL + test["url"],
        json=test["json"],
    )

    success = response.status_code == test["expected"]

    if success:
        passed += 1

    status = "PASS" if success else "FAIL"

    print(
        f"{status}: {test['name']} "
        f"(expected {test['expected']}, got {response.status_code})"
    )

print(f"\nResult: {passed}/{len(tests)} tests passed")