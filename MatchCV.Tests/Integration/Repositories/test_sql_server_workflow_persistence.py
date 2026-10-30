from datetime import date
from uuid import uuid4


def test_persists_analysis_queue_quota_and_password_recovery_token(
    test_database_connection,
):
    user_id = uuid4()
    job_id = uuid4()
    analysis_id = uuid4()
    queue_id = uuid4()
    reservation_id = uuid4()
    token_hash = uuid4().hex + uuid4().hex
    month_start = date.today().replace(day=1)
    resume_id = uuid4()

    with test_database_connection.connection() as connection:
        cursor = connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO dbo.users (id, name, email, password_hash, role) "
                "VALUES (?, ?, ?, ?, ?)",
                str(user_id),
                "Integration Test User",
                f"sql-integration-{user_id}@example.test",
                "synthetic-password-hash",
                "USER",
            )
            cursor.execute(
                "INSERT INTO dbo.job_descriptions (id, content) VALUES (?, ?)",
                str(job_id),
                "Synthetic test role: backend APIs and SQL Server.",
            )
            cursor.execute(
                "INSERT INTO dbo.analyses "
                "(id, user_id, resume_id, job_description_id, status) "
                "VALUES (?, ?, ?, ?, ?)",
                str(analysis_id),
                str(user_id),
                str(resume_id),
                str(job_id),
                "PENDING",
            )
            cursor.execute(
                "INSERT INTO dbo.analysis_queue "
                "(id, analysis_id, payload_ciphertext, status) "
                "VALUES (?, ?, ?, ?)",
                str(queue_id),
                str(analysis_id),
                b"synthetic-encrypted-payload",
                "PENDING",
            )
            cursor.execute(
                "INSERT INTO dbo.analysis_quota_reservations "
                "(id, user_id, analysis_id, month_start, status) "
                "VALUES (?, ?, ?, ?, ?)",
                str(reservation_id),
                str(user_id),
                str(analysis_id),
                month_start,
                "RESERVED",
            )
            cursor.execute(
                "INSERT INTO dbo.password_reset_tokens "
                "(token_hash, user_id, created_at, expires_at, used_at) "
                "VALUES (?, ?, SYSUTCDATETIME(), DATEADD(MINUTE, 15, SYSUTCDATETIME()), NULL)",
                token_hash,
                str(user_id),
            )
            connection.commit()

            cursor.execute(
                "UPDATE dbo.analyses SET status = ?, "
                "evidenced_requirements = ?, unevidenced_requirements = ?, "
                "gaps = ?, resume_issues = ?, suggestions = ?, "
                "completed_at = SYSUTCDATETIME() WHERE id = ?",
                "COMPLETED",
                '["REST APIs"]',
                '["Kubernetes"]',
                '["Kubernetes experience"]',
                '["Synthetic resume missing dates"]',
                '["Add measurable outcomes"]',
                str(analysis_id),
            )
            cursor.execute(
                "UPDATE dbo.analysis_queue SET status = ?, "
                "finished_at = SYSUTCDATETIME() WHERE id = ?",
                "COMPLETED",
                str(queue_id),
            )
            cursor.execute(
                "UPDATE dbo.analysis_quota_reservations SET status = ?, "
                "updated_at = SYSUTCDATETIME() WHERE id = ?",
                "COMPLETED",
                str(reservation_id),
            )
            connection.commit()

            cursor.execute(
                "SELECT status, evidenced_requirements, unevidenced_requirements, "
                "gaps, resume_issues, suggestions FROM dbo.analyses WHERE id = ?",
                str(analysis_id),
            )
            analysis = cursor.fetchone()
            assert analysis is not None
            assert analysis[0] == "COMPLETED"
            assert analysis[1] == '["REST APIs"]'
            assert analysis[2] == '["Kubernetes"]'
            assert analysis[3] == '["Kubernetes experience"]'
            assert analysis[4] == '["Synthetic resume missing dates"]'
            assert analysis[5] == '["Add measurable outcomes"]'

            cursor.execute(
                "SELECT status, finished_at FROM dbo.analysis_queue WHERE id = ?",
                str(queue_id),
            )
            queue = cursor.fetchone()
            assert queue is not None
            assert queue[0] == "COMPLETED"
            assert queue[1] is not None

            cursor.execute(
                "SELECT status FROM dbo.analysis_quota_reservations WHERE id = ?",
                str(reservation_id),
            )
            quota = cursor.fetchone()
            assert quota is not None
            assert quota[0] == "COMPLETED"

            cursor.execute(
                "SELECT token_hash, used_at FROM dbo.password_reset_tokens WHERE token_hash = ?",
                token_hash,
            )
            token = cursor.fetchone()
            assert token is not None
            assert token[0].strip() == token_hash
            assert token[1] is None
        finally:
            connection.rollback()
            cursor.execute(
                "DELETE FROM dbo.password_reset_tokens WHERE token_hash = ?",
                token_hash,
            )
            cursor.execute(
                "DELETE FROM dbo.analysis_quota_reservations WHERE id = ?",
                str(reservation_id),
            )
            cursor.execute(
                "DELETE FROM dbo.analysis_queue WHERE id = ?",
                str(queue_id),
            )
            cursor.execute(
                "DELETE FROM dbo.analyses WHERE id = ?",
                str(analysis_id),
            )
            cursor.execute(
                "DELETE FROM dbo.job_descriptions WHERE id = ?",
                str(job_id),
            )
            cursor.execute(
                "DELETE FROM dbo.users WHERE id = ?",
                str(user_id),
            )
            connection.commit()
            cursor.close()
