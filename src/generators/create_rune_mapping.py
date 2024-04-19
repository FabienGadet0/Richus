from src.db.db import execute_query_from_file

def main():
    try:
        execute_query_from_file("src/sql/rune_mapping.sql")
    except Exception as e:
        print(f"Failed to create rune mapping: {e}")
        raise
    finally:
        print("rune mapping done")
