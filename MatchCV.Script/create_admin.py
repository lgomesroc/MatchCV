
import getpass
import sys
from pathlib import Path

from dotenv import load_dotenv

# Permite importar os módulos do projeto quando o script é executado.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from MatchCV.Domain.Entities.User import User
from MatchCV.Domain.Enums.UserRole import UserRole
from MatchCV.Infrastructure.Config.AppSettings import AppSettings
from MatchCV.Infrastructure.Database.DatabaseConnection import (
    DatabaseConnection,
)
from MatchCV.Infrastructure.Repositories.SqlServerUserRepository import (
    SqlServerUserRepository,
)
from MatchCV.Login.Authentication.PasswordHasher import PasswordHasher
from MatchCV.Login.Authentication.PasswordPolicy import PasswordPolicy


ADMIN_EMAIL = "admin@admin.com"
EXPECTED_DATABASE_HOST = "matchcv.mssql.somee.com"
EXPECTED_DATABASE_NAME = "MatchCV"
CONFIRMATION_TEXT = "CRIAR ADMIN NO SOMEE"


def main() -> int:
    print("=== MatchCV | Criação local do administrador ===")
    print("O script será executado localmente.")
    print("A gravação será feita no SQL Server do Somee.\n")

    # Usa um arquivo de configuração exclusivo para o banco remoto.
    env_file = PROJECT_ROOT / ".env.somee"

    if not env_file.is_file():
        print("ERRO: arquivo .env.somee não encontrado.")
        print("Crie o arquivo na raiz do projeto e configure")
        print("as credenciais de acesso ao SQL Server do Somee.")
        print("Nenhuma alteração foi realizada.")
        return 1

    # Sobrescreve as variáveis previamente carregadas do .env local.
    load_dotenv(dotenv_path=env_file, override=True)

    try:
        settings = AppSettings.from_environment()
    except (TypeError, ValueError):
        print("ERRO: configurações de ambiente inválidas.")
        print("Verifique a porta e as configurações de .env.somee.")
        print("Nenhuma alteração foi realizada.")
        return 1

    host = settings.database_host.strip().lower().rstrip(".")
    database_name = settings.database_name.strip()

    # Falha fechada: impede gravar em um servidor diferente do esperado.
    if host != EXPECTED_DATABASE_HOST:
        print("ERRO: DATABASE_HOST não corresponde ao host esperado.")
        print(f"Host configurado: {settings.database_host}")
        print("Nenhuma alteração foi realizada.")
        return 1

    if database_name.casefold() != EXPECTED_DATABASE_NAME.casefold():
        print("ERRO: DATABASE_NAME não corresponde ao banco esperado.")
        print(f"Banco configurado: {settings.database_name}")
        print("Nenhuma alteração foi realizada.")
        return 1

    if not settings.database_user or not settings.database_password:
        print(
            "ERRO: configure DATABASE_USER e DATABASE_PASSWORD "
            "no arquivo .env.somee."
        )
        print("Nenhuma alteração foi realizada.")
        return 1

    if not settings.database_port:
        print("ERRO: DATABASE_PORT não está configurada corretamente.")
        print("Nenhuma alteração foi realizada.")
        return 1

    print(f"Servidor: {settings.database_host}")
    print(f"Porta: {settings.database_port}")
    print(f"Banco: {settings.database_name}")
    print(f"E-mail administrativo: {ADMIN_EMAIL}")
    print("\nA senha não será exibida nem armazenada em texto puro.")

    confirmation = input(
        f'\nPara autorizar a gravação, digite "{CONFIRMATION_TEXT}": '
    ).strip()

    if confirmation != CONFIRMATION_TEXT:
        print("Operação cancelada. Nenhuma alteração foi realizada.")
        return 0

    name = input("\nNome do administrador: ").strip()

    if not name:
        print("ERRO: o nome não pode ficar vazio.")
        return 1

    password = ""
    confirm_password = ""

    try:
        password = getpass.getpass("Senha do administrador: ")
        confirm_password = getpass.getpass("Confirme a senha: ")

        if password != confirm_password:
            print("ERRO: as senhas não coincidem.")
            return 1

        try:
            PasswordPolicy.validate(password)
        except ValueError as exc:
            print(f"ERRO na senha: {exc}")
            return 1

        database = DatabaseConnection(settings)
        repository = SqlServerUserRepository(database)

        # Confirma que o banco remoto pode ser acessado e verifica
        # se o e-mail reservado já está cadastrado.
        existing_user = repository.get_by_email(ADMIN_EMAIL)

        if existing_user is not None:
            print(
                f"ERRO: já existe uma conta com o e-mail {ADMIN_EMAIL}. "
                "Nenhuma alteração foi realizada."
            )
            return 1

        # Utiliza o mesmo mecanismo de hash da aplicação.
        password_hash = PasswordHasher.hash_password(password)

        admin = User.create(
            name=name,
            email=ADMIN_EMAIL,
            password_hash=password_hash,
            role=UserRole.ADMIN,
        )

        # A implementação do repositório deve verificar a existência
        # de outro administrador e inserir dentro de uma transação.
        repository.add_admin_if_none_exists(admin)

    except ValueError as exc:
        print(f"Não foi possível criar o administrador: {exc}")
        return 1
    except Exception:
        # Não exibe detalhes da conexão, credenciais ou exceções SQL.
        print(
            "ERRO: não foi possível concluir a operação. "
            "Verifique a conexão com o Somee, a porta configurada "
            "e as permissões do usuário do banco. "
            "Não compartilhe credenciais nos logs."
        )
        return 1
    finally:
        # Remove as referências locais às senhas o quanto antes.
        password = ""
        confirm_password = ""

    print("\nAdministrador criado com sucesso.")
    print(f"E-mail: {ADMIN_EMAIL}")
    print("Perfil: ADMIN")
    print("A senha foi armazenada como hash.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nOperação cancelada.")
        raise SystemExit(130)
