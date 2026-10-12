
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

    def add(self, user: User) -> User:
        with self._database_connection.connection() as connection:
            cursor = connection.cursor()

            try:
                cursor.execute(
                    """
                    INSERT INTO dbo.users (
                        id, name, email, password_hash, role
                    )
                    VALUES (?, ?, ?, ?, ?)
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

    def add_admin_if_none_exists(self, user: User) -> User:
        """Cria o administrador inicial dentro de uma transação serializável."""
        if user.role is not UserRole.ADMIN:
            raise ValueError("Esta operação aceita apenas administradores.")

        with self._database_connection.connection() as connection:
            cursor = connection.cursor()

            try:
                cursor.execute(
                    "SET TRANSACTION ISOLATION LEVEL SERIALIZABLE"
                )
                cursor.execute(
                    """
                    SELECT TOP (1) id
                    FROM dbo.users WITH (UPDLOCK, HOLDLOCK)
                    WHERE role = 'ADMIN'
                    """
                )

                if cursor.fetchone() is not None:
                    raise ValueError(
                        "O administrador inicial já foi criado."
                    )

                cursor.execute(
                    """
                    INSERT INTO dbo.users (
                        id, name, email, password_hash, role
                    )
                    VALUES (?, ?, ?, ?, 'ADMIN')
                    """,
                    str(user.id),
                    user.name,
                    user.email,
                    user.password_hash,
                )
                connection.commit()
            except Exception:
                connection.rollback()
                raise
            finally:
                cursor.close()

        return user

    def update_password_hash(self, user_id: UUID, password_hash: str) -> bool:
        with self._database_connection.connection() as connection:
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "UPDATE dbo.users SET password_hash = ? WHERE id = ?",
                    password_hash,
                    str(user_id),
                )
                updated = cursor.rowcount > 0
                connection.commit()
                return updated
            except Exception:
                connection.rollback()
                raise
            finally:
                cursor.close()

    def get_by_id(self, user_id: UUID) -> Optional[User]:
        with self._database_connection.connection() as connection:
            cursor = connection.cursor()

            try:
                cursor.execute(
                    """
                    SELECT id, name, email, password_hash, role, created_at
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

        return self._to_entity(self._to_record(row))

    def get_by_email(self, email: str) -> Optional[User]:
        with self._database_connection.connection() as connection:
            cursor = connection.cursor()

            try:
                cursor.execute(
                    """
                    SELECT id, name, email, password_hash, role, created_at
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

        return self._to_entity(self._to_record(row))

    @staticmethod
    def _to_record(row: tuple) -> UserRecord:
        return UserRecord(
            id=UUID(str(row[0])),
            name=row[1],
            email=row[2],
            password_hash=row[3],
            role=UserRole(row[4]),
            created_at=row[5],
        )

    @staticmethod
    def _to_entity(record: UserRecord) -> User:
        return User(
            id=record.id,
            name=record.name,
            email=record.email,
            password_hash=record.password_hash,
            role=record.role,
        )
