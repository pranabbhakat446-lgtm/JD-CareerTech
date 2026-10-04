import os
import psycopg
from psycopg.rows import dict_row


# =========================================================
# SUPABASE POSTGRESQL CONNECTION
# =========================================================

DATABASE_URL = os.getenv("SUPABASE_DB_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "SUPABASE_DB_URL environment variable is not set."
    )


class DatabaseConnection:
    """
    Compatibility wrapper for the existing Flask application.

    Existing app.py uses SQLite-style '?' placeholders.
    This wrapper automatically converts them to PostgreSQL
    '%s' placeholders, so app.py does not need hundreds of
    manual query changes.
    """

    def __init__(self):
        self._connection = psycopg.connect(
            DATABASE_URL,
            row_factory=dict_row,
            prepare_threshold=None,
        )

    def execute(self, query, params=None):
        """
        Convert SQLite '?' placeholders to psycopg '%s'
        placeholders and execute the query.
        """

        query = query.replace("?", "%s")

        if params is None:
            return self._connection.execute(query)

        return self._connection.execute(query, params)

    def commit(self):
        self._connection.commit()

    def rollback(self):
        self._connection.rollback()

    def close(self):
        self._connection.close()

    def __getattr__(self, name):
        return getattr(self._connection, name)


def get_db_connection():
    """
    Return a PostgreSQL connection compatible with
    the existing app.py code.
    """

    return DatabaseConnection()


def create_tables():
    """
    Tables already exist in Supabase.

    We only test the connection here and do not recreate
    or seed any tables.
    """

    connection = get_db_connection()

    try:
        connection.execute("SELECT 1")
    finally:
        connection.close()