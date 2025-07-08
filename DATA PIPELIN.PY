import pandas as pd
from sqlalchemy import create_engine
import sqlite3

class DataPipeline:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)

    def extract(self, query):
        return pd.read_sql(query, self.engine)

    def transform(self, df, transformations):
        for transformation in transformations:
            df = transformation(df)
        return df

    def load(self, df, table_name):
        df.to_sql(table_name, self.engine, if_exists='replace', index=False)

    def run(self, query, transformations, table_name):
        data = self.extract(query)
        transformed_data = self.transform(data, transformations)
        self.load(transformed_data, table_name)

def initialize_database(db_path):
    # Connect using sqlite3 to create a table with dummy data
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS source_table (
            id INTEGER PRIMARY KEY,
            column INTEGER,
            name TEXT
        )
    """)

    # Check if table has data
    cursor.execute("SELECT COUNT(*) FROM source_table")
    if cursor.fetchone()[0] == 0:
        # Insert some sample data
        sample_data = [
            (1, 10, 'Alice'),
            (2, -5, 'Bob'),
            (3, 15, 'Charlie'),
            (4, None, 'Dana'),
            (5, 0, 'Eve')
        ]
        cursor.executemany("INSERT INTO source_table (id, column, name) VALUES (?, ?, ?)", sample_data)
        conn.commit()

    conn.close()

if __name__ == "__main__":
    db_url = 'sqlite:///example.db'
    db_path = 'example.db'

    initialize_database(db_path)

    pipeline = DataPipeline(db_url)

    query = 'SELECT * FROM source_table'
    transformations = [
        lambda df: df.dropna(),               # Remove rows with NaN
        lambda df: df[df['column'] > 0]       # Keep rows where column > 0
    ]
    table_name = 'destination_table'

    pipeline.run(query, transformations, table_name)

    # Show result
    engine = create_engine(db_url)
    result_df = pd.read_sql(f"SELECT * FROM {table_name}", engine)
    print("Transformed Data:")
    print(result_df)
