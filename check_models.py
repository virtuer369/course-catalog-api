
from sqlalchemy import inspect

from db import engine
import models


inspector = inspect(engine)

for table_name in ["courses", "students", "enrollments"]:
    print(f"\nTable: {table_name}")

    columns = inspector.get_columns(table_name)
    for column in columns:
        print(f"  {column['name']}: {column['type']}")

    print("  Constraints:")
    for constraint in inspector.get_unique_constraints(table_name):
        print(f"    UNIQUE: {constraint['name']}")
