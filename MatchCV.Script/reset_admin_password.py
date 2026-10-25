
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
MAX_RECOVERIES = 3
BLOCK_DURATION_DAYS = 15


def main() -> None:
    print("=== Recuperação local da senha administrativa ===")
    print("Use este procedimento somente no computador autorizado.")

    new_password = getpass("Nova senha administrativa: ")
    confirm_password = getpass("Confirme a nova senha: ")

    if new_password != confirm_password:
        raise ValueError("As senhas informadas não são iguais.")

    PasswordPolicy.validate(new_password)

    database = DatabaseConnection(AppSettings.from_environment())

    with database.connection() as connection:
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                SELECT id
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

            admin_id = admin[0]

            cursor.execute(
                """
                SELECT id, admin_user_id, reset_count, reset_blocked_until
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
                reset_count = 0
                blocked_until = None
            else:
                if str(policy[1]).lower() != str(admin_id).lower():
                    raise RuntimeError(
                        "O registro de política não corresponde "
                        "ao administrador esperado."
                    )

                reset_count = policy[2]
                blocked_until = policy[3]

            now = datetime.now(timezone.utc)

            if blocked_until is not None:
                if blocked_until.tzinfo is None:
                    blocked_until = blocked_until.replace(
                        tzinfo=timezone.utc
                    )

                if now < blocked_until:
                    remaining = blocked_until - now
                    days = max(1, (remaining.days + 1))
                    raise ValueError(
                        "Recuperação bloqueada. "
                        f"Tente novamente em aproximadamente {days} dia(s)."
                    )

                # O bloqueio expirou: inicia um novo ciclo de recuperações.
                reset_count = 0
                blocked_until = None

            if reset_count >= MAX_RECOVERIES:
                raise RuntimeError(
                    "O limite de recuperações foi atingido, "
                    "mas não há uma data de desbloqueio registrada. "
                    "Verifique a política no banco."
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

            new_count = reset_count + 1
            new_blocked_until = (
                now + timedelta(days=BLOCK_DURATION_DAYS)
                if new_count >= MAX_RECOVERIES
                else None
            )

            cursor.execute(
                """
                UPDATE dbo.admin_password_policy
                SET reset_count = ?,
                    last_reset_at = SYSUTCDATETIME(),
                    reset_blocked_until = ?,
                    updated_at = SYSUTCDATETIME()
                WHERE id = 1 AND admin_user_id = ?
                """,
                new_count,
                new_blocked_until.replace(tzinfo=None)
                if new_blocked_until is not None
                else None,
                str(admin_id),
            )

            if cursor.rowcount != 1:
                raise RuntimeError(
                    "Não foi possível atualizar o controle de recuperação."
                )

            connection.commit()

            print("Senha administrativa recuperada com sucesso.")
            print(f"Recuperações usadas neste ciclo: {new_count}/{MAX_RECOVERIES}")

            if new_blocked_until is not None:
                print(
                    "O limite foi atingido. Novas recuperações estarão "
                    "bloqueadas por 15 dias."
                )

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
