from app.database import Base
import app.models

for table_name, table in Base.metadata.tables.items():
    print(f"\nTABLE: {table_name}")

    for column in table.columns:
        print(f"  - {column.name}")