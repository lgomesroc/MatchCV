
from uuid import uuid4

from MatchCV.Domain.Entities.User import User
from MatchCV.Domain.Enums.UserRole import UserRole
from MatchCV.Infrastructure.Database.DatabaseConnection import DatabaseConnection
from MatchCV.Infrastructure.Repositories.SqlServerUserRepository import (
    SqlServerUserRepository,
)


class TestSqlServerUserRepository:
    def test_add_and_get_by_id(
        self,
        test_database_connection: DatabaseConnection,
        cleanup_registry,
    ):
        repository = SqlServerUserRepository(
            database_connection=test_database_connection,
        )
        user = User.create(
            name="Usuario Teste",
            email=f"usuario-{uuid4()}@example.com",
            password_hash="hash-de-senha-de-teste",
            role=UserRole.USER,
        )
        cleanup_registry["user_ids"].append(user.id)

        added = repository.add(user)

        assert added.id == user.id

        retrieved = repository.get_by_id(user.id)

        assert retrieved is not None
        assert retrieved.id == user.id
        assert retrieved.name == user.name
        assert retrieved.email == user.email
        assert retrieved.password_hash == user.password_hash
        assert retrieved.role == user.role

    def test_get_by_email_returns_user(
        self,
        test_database_connection: DatabaseConnection,
        cleanup_registry,
    ):
        repository = SqlServerUserRepository(
            database_connection=test_database_connection,
        )
        user = User.create(
            name="Usuario por Email",
            email=f"busca-{uuid4()}@example.com",
            password_hash="hash-de-senha-de-teste",
            role=UserRole.ADMIN,
        )
        cleanup_registry["user_ids"].append(user.id)

        repository.add(user)

        retrieved = repository.get_by_email(user.email)

        assert retrieved is not None
        assert retrieved.id == user.id
        assert retrieved.email == user.email
        assert retrieved.role == UserRole.ADMIN

    def test_get_by_id_returns_none_when_record_does_not_exist(
        self,
        test_database_connection: DatabaseConnection,
    ):
        repository = SqlServerUserRepository(
            database_connection=test_database_connection,
        )

        result = repository.get_by_id(uuid4())

        assert result is None

    def test_get_by_email_returns_none_when_email_does_not_exist(
        self,
        test_database_connection: DatabaseConnection,
    ):
        repository = SqlServerUserRepository(
            database_connection=test_database_connection,
        )

        result = repository.get_by_email(
            f"inexistente-{uuid4()}@example.com"
        )

        assert result is None
