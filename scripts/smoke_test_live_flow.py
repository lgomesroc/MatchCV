"""Opt-in smoke test for the real MatchCV API, queue, worker and AI integration.

This creates a real analysis and may consume quota. Use only a dedicated test
account and synthetic text. No credentials are printed.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

BASE = os.getenv("MATCHCV_API_BASE_URL", "https://matchcv-api-0oi5.onrender.com").rstrip("/")
EMAIL = os.getenv("MATCHCV_LIVE_E2E_EMAIL", "")
PASSWORD = os.getenv("MATCHCV_LIVE_E2E_PASSWORD", "")
CONFIRM = os.getenv("MATCHCV_LIVE_E2E_CONFIRM_PRODUCTION") == "YES"


def call(path, method="GET", token=None, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    headers = {"Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = "Bearer " + token
    request = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            raw = response.read().decode()
            return response.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"{method} {path} retornou HTTP {exc.code}") from None
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(f"Falha de conexão em {path}: {type(exc).__name__}") from None


def submit_analysis(token):
    boundary = "----MatchCVLiveSmokeBoundary"
    fields = {
        "job_description": "Desenvolvedor backend com experiência em APIs REST, Python, testes automatizados e SQL.",
        "resume_text": "Desenvolvedor com experiência em APIs REST com Python, testes automatizados e bancos SQL.",
    }
    chunks = []
    for name, value in fields.items():
        chunks.extend([
            f"--{boundary}\r\n".encode(),
            f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode(),
            value.encode(),
            b"\r\n",
        ])
    chunks.append(f"--{boundary}--\r\n".encode())
    request = urllib.request.Request(
        BASE + "/api/v1/analysis/resume",
        data=b"".join(chunks),
        headers={
            "Accept": "application/json",
            "Authorization": "Bearer " + token,
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.status, json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"POST /api/v1/analysis/resume retornou HTTP {exc.code}") from None


def main():
    if not CONFIRM:
        print("Defina MATCHCV_LIVE_E2E_CONFIRM_PRODUCTION=YES para autorizar uma análise real.", file=sys.stderr)
        return 2
    if not EMAIL or not PASSWORD:
        print("Configure MATCHCV_LIVE_E2E_EMAIL e MATCHCV_LIVE_E2E_PASSWORD com uma conta de teste.", file=sys.stderr)
        return 2
    timeout = int(os.getenv("MATCHCV_LIVE_E2E_TIMEOUT_SECONDS", "300"))
    if not 30 <= timeout <= 900:
        print("O timeout deve estar entre 30 e 900 segundos.", file=sys.stderr)
        return 2
    try:
        print("1/5 Health da API")
        status, health = call("/health")
        if status != 200 or health.get("status") != "ok":
            raise RuntimeError("O endpoint de saúde não confirmou status ok.")
        print("2/5 Login real")
        _, login = call("/api/v1/auth/login", "POST", payload={"email": EMAIL, "password": PASSWORD})
        token = login.get("access_token")
        if not token:
            raise RuntimeError("Login não retornou token.")
        print("3/5 Validação da sessão")
        _, user = call("/api/v1/auth/me", token=token)
        if not user.get("id"):
            raise RuntimeError("A sessão autenticada não retornou usuário.")
        print("4/5 Criando análise sintética real")
        status, queued = submit_analysis(token)
        if status != 202 or not queued.get("analysis_id"):
            raise RuntimeError("A API não confirmou o enfileiramento com HTTP 202.")
        analysis_id = queued["analysis_id"]
        print("5/5 Aguardando worker e resultado")
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            _, result = call("/api/v1/analysis/" + analysis_id, token=token)
            state = result.get("status")
            if state == "completed":
                expected = {"evidenced_requirements", "unevidenced_requirements", "gaps", "resume_issues", "suggestions"}
                if not expected.issubset(result):
                    raise RuntimeError("A análise concluiu sem todos os campos de resultado esperados.")
                print("SUCESSO: API, autenticação, persistência/fila, worker, provedor de IA e consulta do resultado.")
                print("ID da análise:", analysis_id)
                return 0
            if state == "failed":
                raise RuntimeError("A análise falhou; verifique os logs sanitizados da API, worker e provedores.")
            time.sleep(3)
        raise RuntimeError(f"Timeout após {timeout}s; último status: {state}. Verifique worker, banco e chave de criptografia.")
    except (RuntimeError, ValueError) as exc:
        print("FALHA:", exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
