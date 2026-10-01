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


class PostgresUserRepository(IUserRepository):
    """Implementação PostgreSQL do repositório de usuários."""

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
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO users (
                        id,
                        name,
                        email,
                        password_hash,
                        role
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    """,
                    (
                        user.id,
                        user.name,
                        user.email,
                        user.password_hash,
                        user.role.value,
                    ),
                )

            connection.commit()

        return user

    def get_by_id(
        self,
        user_id: UUID,
    ) -> Optional[User]:
        with self._database_connection.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        id,
                        name,
                        email,
                        password_hash,
                        role,
                        created_at
                    FROM users
                    WHERE id = %s
                    """,
                    (user_id,),
                )

                row = cursor.fetchone()

        if row is None:
            return None

        record = self._to_record(row)

        return self._to_entity(record)

    def get_by_email(
        self,
        email: str,
    ) -> Optional[User]:
        with self._database_connection.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        id,
                        name,
                        email,
                        password_hash,
                        role,
                        created_at
                    FROM users
                    WHERE email = %s
                    """,
                    (email,),
                )

                row = cursor.fetchone()

        if row is None:
            return None

        record = self._to_record(row)

        return self._to_entity(record)

    @staticmethod
    def _to_record(
        row: tuple,
    ) -> UserRecord:
        return UserRecord(
            id=row[0],
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
