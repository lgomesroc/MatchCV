#!/usr/bin/env python3
"""Apply only test migrations to the isolated MatchCVTest SQL Server database."""

import os
import re
import sys
import time
from pathlib import Path

import pyodbc


ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS = ROOT / "MatchCV.Db" / "Migrations" / "Test"
EXPECTED_HOST = "127.0.0.1"
EXPECTED_PORT = 1435
EXPECTED_DATABASE = "MatchCVTest"


def required_environment(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if not value or not value.strip():
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value.strip()


def main() -> int:
    host = required_environment("MATCHCV_TEST_DATABASE_HOST", EXPECTED_HOST)
    port = int(required_environment("MATCHCV_TEST_DATABASE_PORT", str(EXPECTED_PORT)))
    database = required_environment("MATCHCV_TEST_DATABASE_NAME", EXPECTED_DATABASE)
    password = required_environment("TEST_DATABASE_PASSWORD")

    if host not in {"127.0.0.1", "localhost"}:
        raise RuntimeError(f"Refusing non-local SQL Server host: {host}")
    if port != EXPECTED_PORT:
        raise RuntimeError(f"Refusing SQL Server port {port}; expected {EXPECTED_PORT}")
    if database != EXPECTED_DATABASE:
        raise RuntimeError(
            f"Refusing database {database}; expected isolated {EXPECTED_DATABASE}"
        )

    connection_string = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={host},{port};DATABASE=master;UID=sa;PWD={password};"
        "Encrypt=no;TrustServerCertificate=yes;"
    )

    connection = None
    last_error: Exception | None = None
    for _ in range(60):
        try:
            connection = pyodbc.connect(
                connection_string,
                autocommit=True,
                timeout=3,
            )
            break
        except pyodbc.Error as error:
            last_error = error
            time.sleep(2)
    if connection is None:
        raise RuntimeError("Test SQL Server did not become ready after 120 seconds") from last_error

    try:
        files = sorted(MIGRATIONS.glob("*.sql"))
        if not files:
            raise RuntimeError(f"No test migrations found in {MIGRATIONS}")

        cursor = connection.cursor()
        try:
            for migration in files:
                sql = migration.read_text(encoding="utf-8-sig")
                batches = re.split(r"(?im)^\s*GO\s*(?:--.*)?$", sql)
                for batch in batches:
                    if batch.strip():
                        cursor.execute(batch)
                print(f"Applied {migration.name}")
            cursor.execute("SELECT DB_NAME()")
            cursor.fetchone()
            cursor.execute(
                "SELECT DB_ID(?)",
                EXPECTED_DATABASE,
            )
            if cursor.fetchone()[0] is None:
                raise RuntimeError("Test database was not created by migrations")

            cursor.execute(
                "SELECT TABLE_NAME FROM MatchCVTest.INFORMATION_SCHEMA.TABLES "
                "WHERE TABLE_SCHEMA = 'dbo' AND TABLE_TYPE = 'BASE TABLE'"
            )
            tables = {row[0] for row in cursor.fetchall()}
            expected_tables = {
                "users",
                "job_descriptions",
                "analyses",
                "analysis_queue",
                "analysis_quota_reservations",
                "user_analysis_usage",
                "password_reset_tokens",
                "admin_password_policy",
            }
            missing = expected_tables - tables
            if missing:
                raise RuntimeError(f"Migration validation failed; missing tables: {sorted(missing)}")
            print(f"Validated database {EXPECTED_DATABASE}: {len(tables)} tables")
        finally:
            cursor.close()
    finally:
        connection.close()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"TEST DATABASE SETUP FAILED: {error}", file=sys.stderr)
        raise SystemExit(1)
