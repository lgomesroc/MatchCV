import json
from urllib import error
from urllib import request

from MatchCV.AI.Exceptions.AIProviderException import (
    AIProviderException,
)


class AIHttpClient:
    """Cliente HTTP simples para comunicação com APIs de IA."""

    @staticmethod
    def post_json(
        url: str,
        headers: dict[str, str],
        payload: dict,
        timeout_seconds: int,
    ) -> dict:
        body = json.dumps(payload).encode("utf-8")

        http_request = request.Request(
            url=url,
            data=body,
            headers={
                **headers,
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with request.urlopen(
                http_request,
                timeout=timeout_seconds,
            ) as response:
                response_body = response.read().decode(
                    "utf-8"
                )

        except error.HTTPError as exception:
            error_body = ""

            try:
                error_body = exception.read().decode(
                    "utf-8",
                    errors="replace",
                )
            except Exception:
                error_body = ""

            retryable = (
                exception.code >= 500
                or exception.code == 429
            )

            if error_body:
                message = (
                    f"O provedor de IA retornou HTTP "
                    f"{exception.code}: {error_body}"
                )
            else:
                message = (
                    f"O provedor de IA retornou HTTP "
                    f"{exception.code}."
                )

            raise AIProviderException(
                message,
                retryable=retryable,
            ) from exception

        except error.URLError as exception:
            reason = str(exception.reason)

            raise AIProviderException(
                "Não foi possível comunicar com o provedor de IA. "
                f"Motivo: {reason}",
                retryable=True,
            ) from exception

        except TimeoutError as exception:
            raise AIProviderException(
                "A comunicação com o provedor de IA excedeu "
                f"o tempo limite de {timeout_seconds} segundos.",
                retryable=True,
            ) from exception

        try:
            data = json.loads(response_body)
        except json.JSONDecodeError as exception:
            raise AIProviderException(
                "O provedor retornou uma resposta JSON inválida.",
                retryable=False,
            ) from exception

        if not isinstance(data, dict):
            raise AIProviderException(
                "O provedor retornou uma resposta inválida.",
                retryable=False,
            )

        return data
