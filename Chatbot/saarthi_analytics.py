# import duckdb
# from datetime import datetime


# import duckdb

# # Initialize DuckDB connection
# def init_duckdb_connection():
#     return duckdb.connect('saarthi_conversation.db')

# # Create table if it doesn't exist
# def create_table(conn):
#     conn.execute("""
#          CREATE TABLE IF NOT EXISTS saarthi_talks (
#              conversation_id TEXT,
#              name TEXT,
#              rating INT,
#              summary TEXT,
#              feedback TEXT,
#              message_count INT,
#              summary_timestamp TIMESTAMP,
#          );
#      """)

# # Function to insert text into the database
# def insert_text(conn, conversation_id, extracted_preference, msg):
#     # conversation_id = str(uuid.uuid4())
#     summary_timestamp = datetime.now()
#     conn.execute(
#         "INSERT INTO saarthi_talks (conversation_id, summary, message_count, summary_timestamp) VALUES (?, ?, ?, ?)",
#         (conversation_id, extracted_preference, msg, summary_timestamp)
#     )
#     conn.commit()

# def update_text(conn, conversation_id, feedback, rating, name):
#     conn.execute("""
#         UPDATE saarthi_talks
#         SET feedback = ?,
#             rating = ?,
#             name = ?
#         WHERE conversation_id = ?
#     """, (feedback, rating, name, conversation_id))
#     conn.commit()

# # Initialize connection and create table
# conn = init_duckdb_connection()
# create_table(conn)

import duckdb
import pandas as pd
from datetime import datetime

def init_duckdb_connection():
    return duckdb.connect('saarthi_conversation.db')

def create_table(conn):
    conn.execute("""
         CREATE TABLE IF NOT EXISTS saarthi_talks (
             conversation_id TEXT,
             name TEXT,
             rating INT,
             summary TEXT,
             feedback TEXT,
             message_count INT,
             summary_timestamp TIMESTAMP
         );
     """)

def get_all_records(conn):
    return conn.execute("SELECT * FROM saarthi_talks").fetchdf()

def get_filtered_records(conn, rating, date):
    query = """
    SELECT * FROM saarthi_talks
    WHERE rating = ?
    AND CAST(summary_timestamp as DATE) = ?
    """
    return conn.execute(query, [rating, date]).fetchdf()

def insert_text(conn, conversation_id, extracted_preference, msg):
    summary_timestamp = datetime.now()
    conn.execute(
        "INSERT INTO saarthi_talks (conversation_id, summary, message_count, summary_timestamp) VALUES (?, ?, ?, ?)",
        (conversation_id, extracted_preference, msg, summary_timestamp)
    )
    conn.commit()

def update_text(conn, conversation_id, feedback, rating, name):
    conn.execute("""
        UPDATE saarthi_talks
        SET feedback = ?,
            rating = ?,
            name = ?
        WHERE conversation_id = ?
    """, (feedback, rating, name, conversation_id))
    conn.commit()