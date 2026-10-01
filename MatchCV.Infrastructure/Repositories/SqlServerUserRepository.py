from typing import Optional
from uuid import UUID

from MatchCV.Application.Repositories.IUserRepository import (
    IUserRepository,
)
from MatchCV.Domain.Entities.User import User
from MatchCV.Domain.Enums.UserRole import UserRole
from MatchCV.Infrastructure.Database.DatabaseConnection import (
    DatabaseConnection,
)
from MatchCV.Infrastructure.Models.UserRecord import UserRecord


class SqlServerUserRepository(IUserRepository):
    """Implementação SQL Server do repositório de usuários."""

    def __init__(
        self,
        database_connection: DatabaseConnection,
    ) -> None:
        self._database_connection = database_connection

    def add(
        self,
        user: User,
    ) -> User:
        with self._database_connection.connection() as connection:
            cursor = connection.cursor()

            try:
                cursor.execute(
                    """
                    INSERT INTO dbo.users (
                        id,
                        name,
                        email,
                        password_hash,
                        role
                    )
                    VALUES (
                        ?,
                        ?,
                        ?,
                        ?,
                        ?
                    )
                    """,
                    str(user.id),
                    user.name,
                    user.email,
                    user.password_hash,
                    user.role.value,
                )

                connection.commit()
            except Exception:
                connection.rollback()
                raise
            finally:
                cursor.close()

        return user

    def get_by_id(
        self,
        user_id: UUID,
    ) -> Optional[User]:
        with self._database_connection.connection() as connection:
            cursor = connection.cursor()

            try:
                cursor.execute(
                    """
                    SELECT
                        id,
                        name,
                        email,
                        password_hash,
                        role,
                        created_at
                    FROM dbo.users
                    WHERE id = ?
                    """,
                    str(user_id),
                )

                row = cursor.fetchone()
            finally:
                cursor.close()

        if row is None:
            return None

        record = self._to_record(row)

        return self._to_entity(record)

    def get_by_email(
        self,
        email: str,
    ) -> Optional[User]:
        with self._database_connection.connection() as connection:
            cursor = connection.cursor()

            try:
                cursor.execute(
                    """
                    SELECT
                        id,
                        name,
                        email,
                        password_hash,
                        role,
                        created_at
                    FROM dbo.users
                    WHERE email = ?
                    """,
                    email,
                )

                row = cursor.fetchone()
            finally:
                cursor.close()

        if row is None:
            return None

        record = self._to_record(row)

        return self._to_entity(record)

    @staticmethod
    def _to_record(
        row: tuple,
    ) -> UserRecord:
        return UserRecord(
            id=UUID(str(row[0])),
            name=row[1],
            email=row[2],
            password_hash=row[3],
            role=UserRole(row[4]),
            created_at=row[5],
        )

    @staticmethod
    def _to_entity(
        record: UserRecord,
    ) -> User:
        return User(
            id=record.id,
            name=record.name,
            email=record.email,
            password_hash=record.password_hash,
            role=record.role,
        )
