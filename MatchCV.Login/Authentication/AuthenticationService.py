from uuid import UUID

from MatchCV.Application.Repositories.IUserRepository import IUserRepository
from MatchCV.Domain.Entities.User import User
from MatchCV.Domain.Exceptions.DomainException import DomainException
from MatchCV.Login.Authentication.PasswordHasher import PasswordHasher
from MatchCV.Login.Authentication.PasswordPolicy import PasswordPolicy
from MatchCV.Login.Tokens.TokenService import TokenService


class AuthenticationService:
    """Regras de cadastro e autenticação de usuários."""

    def __init__(
        self,
        user_repository: IUserRepository,
        token_service: TokenService,
    ) -> None:
        self._user_repository = user_repository
        self._token_service = token_service

    def register(
        self,
        name: str,
        email: str,
        password: str,
    ) -> User:
        normalized_email = email.strip().lower()

        if "@" not in normalized_email or normalized_email.startswith("@"):
            raise DomainException("Informe um e-mail válido.")

        try:
            PasswordPolicy.validate(password)
        except ValueError as exception:
            raise DomainException(str(exception)) from exception

        if self._user_repository.get_by_email(normalized_email) is not None:
            raise DomainException("Já existe uma conta com esse e-mail.")

        password_hash = PasswordHasher.hash_password(password)

        user = User.create(
            name=name,
            email=normalized_email,
            password_hash=password_hash,
        )

        try:
            return self._user_repository.add(user)
        except Exception as exception:
            if self._user_repository.get_by_email(normalized_email) is not None:
                raise DomainException(
                    "Já existe uma conta com esse e-mail."
                ) from exception
            raise

    def authenticate(self, email: str, password: str) -> User:
        normalized_email = email.strip().lower()
        user = self._user_repository.get_by_email(normalized_email)

        if user is None or not PasswordHasher.verify_password(
            password,
            user.password_hash,
        ):
            raise ValueError("E-mail ou senha inválidos.")

        return user

    def change_password(
        self,
        user_id: UUID,
        current_password: str,
        new_password: str,
    ) -> User:
        user = self._user_repository.get_by_id(user_id)

        if user is None:
            raise ValueError("Usuário não encontrado.")

        if not PasswordHasher.verify_password(
            current_password,
            user.password_hash,
        ):
            raise ValueError("A senha atual está incorreta.")

        try:
            PasswordPolicy.validate(new_password)
        except ValueError as exception:
            raise DomainException(str(exception)) from exception

        if PasswordHasher.verify_password(
            new_password,
            user.password_hash,
        ):
            raise DomainException(
                "A nova senha deve ser diferente da senha atual."
            )

        new_hash = PasswordHasher.hash_password(new_password)

        if not self._user_repository.update_password_hash(user.id, new_hash):
            raise ValueError("Não foi possível atualizar a senha.")

        updated_user = self._user_repository.get_by_id(user.id)

        if updated_user is None:
            raise ValueError(
                "A senha foi atualizada, mas não foi possível carregar a conta."
            )

        return updated_user

    def create_access_token(self, user: User) -> str:
        return self._token_service.create_access_token(
            str(user.id),
            user.password_hash,
        )
