
import sys
from datetime import datetime, timedelta, timezone
from getpass import getpass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env.somee", override=True)

from MatchCV.Infrastructure.Config.AppSettings import AppSettings
from MatchCV.Infrastructure.Database.DatabaseConnection import DatabaseConnection
from MatchCV.Login.Authentication.PasswordHasher import PasswordHasher
from MatchCV.Login.Authentication.PasswordPolicy import PasswordPolicy


ADMIN_EMAIL = "admin@admin.com"
MIN_CHANGE_INTERVAL_DAYS = 30


def main() -> None:
    print("=== Alteração da senha administrativa do MatchCV ===")

    current_password = getpass("Senha atual: ")
    new_password = getpass("Nova senha: ")
    confirm_password = getpass("Confirme a nova senha: ")

    if new_password != confirm_password:
        raise ValueError("As senhas informadas não são iguais.")

    PasswordPolicy.validate(new_password)

    if current_password == new_password:
        raise ValueError("A nova senha deve ser diferente da atual.")

    database = DatabaseConnection(AppSettings.from_environment())

    with database.connection() as connection:
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                SELECT id, password_hash
                FROM dbo.users WITH (UPDLOCK, HOLDLOCK)
                WHERE email = ? AND role = 'ADMIN'
                """,
                ADMIN_EMAIL,
            )
            admin = cursor.fetchone()

            if admin is None:
                raise RuntimeError(
                    "O administrador admin@admin.com não foi encontrado."
                )

            admin_id, current_hash = admin

            if not PasswordHasher.verify_password(
                current_password, current_hash
            ):
                raise ValueError("A senha atual está incorreta.")

            cursor.execute(
                """
                SELECT id, admin_user_id, last_normal_change_at
                FROM dbo.admin_password_policy WITH (UPDLOCK, HOLDLOCK)
                WHERE id = 1
                """
            )
            policy = cursor.fetchone()

            if policy is None:
                cursor.execute(
                    """
                    INSERT INTO dbo.admin_password_policy (
                        id, admin_user_id, last_normal_change_at,
                        reset_count
                    )
                    VALUES (1, ?, NULL, 0)
                    """,
                    str(admin_id),
                )
                last_change = None
            else:
                if str(policy[1]).lower() != str(admin_id).lower():
                    raise RuntimeError(
                        "O registro de política não corresponde "
                        "ao administrador esperado."
                    )
                last_change = policy[2]

            now = datetime.now(timezone.utc)

            if last_change is not None:
                if last_change.tzinfo is None:
                    last_change = last_change.replace(tzinfo=timezone.utc)

                allowed_at = last_change + timedelta(
                    days=MIN_CHANGE_INTERVAL_DAYS
                )

                if now < allowed_at:
                    remaining = allowed_at - now
                    days = max(1, (remaining.days + 1))
                    raise ValueError(
                        "A troca normal ainda não está liberada. "
                        f"Tente novamente em aproximadamente {days} dia(s)."
                    )

            new_hash = PasswordHasher.hash_password(new_password)

            cursor.execute(
                """
                UPDATE dbo.users
                SET password_hash = ?
                WHERE id = ? AND role = 'ADMIN'
                """,
                new_hash,
                str(admin_id),
            )

            if cursor.rowcount != 1:
                raise RuntimeError("Não foi possível atualizar a senha.")

            cursor.execute(
                """
                UPDATE dbo.admin_password_policy
                SET last_normal_change_at = SYSUTCDATETIME(),
                    updated_at = SYSUTCDATETIME()
                WHERE id = 1 AND admin_user_id = ?
                """,
                str(admin_id),
            )

            if cursor.rowcount != 1:
                raise RuntimeError(
                    "Não foi possível atualizar o histórico da senha."
                )

            connection.commit()
            print("Senha administrativa alterada com sucesso.")

        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError) as error:
        print(f"Erro: {error}")
    except Exception as error:
        print(f"Falha inesperada: {error}")
        sys.exit(1)
