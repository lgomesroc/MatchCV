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
            retryable = exception.code >= 500 or exception.code == 429

            raise AIProviderException(
                f"O provedor de IA retornou HTTP {exception.code}.",
                retryable=retryable,
            ) from exception

        except (
            error.URLError,
            TimeoutError,
        ) as exception:
            raise AIProviderException(
                "Não foi possível comunicar com o provedor de IA.",
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
