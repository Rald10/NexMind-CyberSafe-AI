
import sqlite3


class UpdateTracker:
    def __init__(self, db_path):
        self.db_path = str(db_path)
        self.initialize()

    def connect(self):
        connection = sqlite3.connect(
            self.db_path,
            timeout=30
        )
        connection.execute("PRAGMA busy_timeout=30000")
        return connection

    def initialize(self):
        with self.connect() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS telegram_updates (
                    update_id INTEGER PRIMARY KEY,
                    status TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def claim(self, update_id):
        if type(update_id) is not int:
            raise ValueError("update_id must be an integer")

        with self.connect() as connection:
            cursor = connection.execute(
                """
                INSERT OR IGNORE INTO telegram_updates
                    (update_id, status)
                VALUES (?, 'processing')
                """,
                (update_id,)
            )

            return cursor.rowcount == 1

    def mark_processed(self, update_id):
        with self.connect() as connection:
            cursor = connection.execute(
                """
                UPDATE telegram_updates
                SET status = 'processed'
                WHERE update_id = ?
                  AND status = 'processing'
                """,
                (update_id,)
            )

            return cursor.rowcount == 1

    def release(self, update_id):
        with self.connect() as connection:
            cursor = connection.execute(
                """
                DELETE FROM telegram_updates
                WHERE update_id = ?
                  AND status = 'processing'
                """,
                (update_id,)
            )

            return cursor.rowcount == 1

    def get_status(self, update_id):
        with self.connect() as connection:
            result = connection.execute(
                """
                SELECT status
                FROM telegram_updates
                WHERE update_id = ?
                """,
                (update_id,)
            ).fetchone()

        return result[0] if result else None


    def recover_stale(self, timeout_seconds=300):
        """
        Release processing claims older than timeout_seconds.

        Only processing records are removed.
        Successfully processed records are preserved.
        """
        if timeout_seconds <= 0:
            raise ValueError(
                "timeout_seconds must be positive"
            )

        with self.connect() as connection:
            cursor = connection.execute(
                """
                DELETE FROM telegram_updates
                WHERE status = 'processing'
                  AND created_at <= datetime(
                      'now',
                      ? || ' seconds'
                  )
                """,
                (str(-timeout_seconds),)
            )

            return cursor.rowcount
