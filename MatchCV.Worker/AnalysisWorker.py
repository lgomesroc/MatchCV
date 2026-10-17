import logging
import threading
import time
from uuid import UUID

from MatchCV.Application.Queue.AnalysisQueuePayload import (
    AnalysisQueuePayload,
)
from MatchCV.Domain.Enums.AnalysisStatus import AnalysisStatus
from MatchCV.Infrastructure.Config.AISettings import AISettings
from MatchCV.Infrastructure.Config.AppSettings import AppSettings
from MatchCV.Infrastructure.Database.DatabaseConnection import (
    DatabaseConnection,
)
from MatchCV.Infrastructure.Encryption.AnalysisPayloadEncryption import (
    AnalysisPayloadEncryption,
)
from MatchCV.Infrastructure.Repositories.SqlServerAnalysisQueueRepository import (
    SqlServerAnalysisQueueRepository,
)
from MatchCV.Infrastructure.Repositories.SqlServerAnalysisRepository import (
    SqlServerAnalysisRepository,
)
from MatchCV.Infrastructure.Services.AIProviderService import (
    AIProviderService,
)
from MatchCV.Infrastructure.Providers.OpenAICompatibleProvider import (
    OpenAICompatibleProvider,
)
from MatchCV.Infrastructure.Providers.SecondaryAIProvider import (
    SecondaryAIProvider,
)


logger = logging.getLogger(__name__)


class AnalysisWorker:
    """Worker responsável por processar a fila de análises."""

    POLL_INTERVAL_SECONDS = 2
    LEASE_RENEW_INTERVAL_SECONDS = 60
    RECOVERY_INTERVAL_SECONDS = 60

    def __init__(self) -> None:
        settings = AppSettings.from_environment()

        database_connection = DatabaseConnection(settings)

        self._queue_repository = SqlServerAnalysisQueueRepository(
            database_connection
        )

        self._analysis_repository = SqlServerAnalysisRepository(
            database_connection
        )

        self._encryption = AnalysisPayloadEncryption(
            encryption_key=settings.analysis_queue_encryption_key
        )

        primary_provider = OpenAICompatibleProvider(
            AISettings.primary(settings)
        )

        fallback_provider = SecondaryAIProvider(
            AISettings.fallback(settings)
        )

        self._ai_provider = AIProviderService(
            primary_provider=primary_provider,
            fallback_provider=fallback_provider,
        )

        self._last_recovery = 0.0

    def run(self) -> None:
        """Executa o loop de processamento da fila."""

        logger.info("Worker de análises iniciado.")

        while True:
            try:
                self._recover_expired_leases_if_due()

                processed = self.process_next()

                if not processed:
                    time.sleep(self.POLL_INTERVAL_SECONDS)

            except KeyboardInterrupt:
                logger.info("Worker encerrado pelo operador.")
                break

            except Exception as exc:
                logger.error(
                    "Erro no loop do worker: %s",
                    type(exc).__name__,
                )
                time.sleep(self.POLL_INTERVAL_SECONDS)

    def _recover_expired_leases_if_due(self) -> None:
        """
        Executa a recuperação periodicamente.

        A recuperação só é segura se o worker renovar o lease
        enquanto estiver processando a tarefa.
        """

        now = time.monotonic()

        if (
            now - self._last_recovery
            < self.RECOVERY_INTERVAL_SECONDS
        ):
            return

        recovered = self._queue_repository.recover_processing()
        self._last_recovery = now

        if recovered:
            logger.warning(
                "Tarefas recuperadas após expiração do lease: %s",
                recovered,
            )

    def process_next(self) -> bool:
        """
        Reserva e processa uma tarefa.

        Retorna True quando uma tarefa foi reservada.
        """

        queue_item = self._queue_repository.get_next_pending()

        if queue_item is None:
            return False

        stop_heartbeat = threading.Event()
        lease_lost = threading.Event()

        heartbeat_thread = threading.Thread(
            target=self._renew_lease,
            args=(
                queue_item.id,
                stop_heartbeat,
                lease_lost,
            ),
            name=f"lease-{queue_item.id}",
            daemon=True,
        )

        heartbeat_thread.start()

        try:
            self._process_item(queue_item, lease_lost)

        except Exception as exc:
            if lease_lost.is_set():
                logger.error(
                    "Lease perdido para a tarefa %s. "
                    "O resultado não será persistido por este worker.",
                    queue_item.id,
                )
            else:
                logger.error(
                    "Falha ao processar a tarefa %s: %s",
                    queue_item.id,
                    type(exc).__name__,
                )
                self._handle_failure(
                    queue_item.id,
                    queue_item.analysis_id,
                    exc,
                )

        finally:
            stop_heartbeat.set()
            heartbeat_thread.join(
                timeout=self.LEASE_RENEW_INTERVAL_SECONDS + 5
            )

        return True

    def _renew_lease(
        self,
        queue_id: UUID,
        stop_event: threading.Event,
        lease_lost: threading.Event,
    ) -> None:
        """
        Renova o lease enquanto a tarefa estiver ativa.

        Uma falha de renovação é tratada conservadoramente:
        este worker não deve persistir o resultado depois disso.
        """

        while not stop_event.wait(
            self.LEASE_RENEW_INTERVAL_SECONDS
        ):
            try:
                renewed = self._queue_repository.renew_processing(
                    queue_id
                )

                if not renewed:
                    lease_lost.set()

                    logger.error(
                        "Não foi possível renovar o lease da tarefa %s.",
                        queue_id,
                    )
                    return

            except Exception as exc:
                lease_lost.set()

                logger.error(
                    "Falha na renovação do lease da tarefa %s: %s",
                    queue_id,
                    type(exc).__name__,
                )
                return

    def _process_item(
        self,
        queue_item,
        lease_lost: threading.Event,
    ) -> None:
        """Executa a análise e persiste seu resultado."""

        analysis = self._analysis_repository.get_by_id(
            queue_item.analysis_id
        )

        if analysis is None:
            raise RuntimeError(
                "Análise associada à tarefa não encontrada."
            )

        if analysis.status == AnalysisStatus.COMPLETED:
            if lease_lost.is_set():
                return

            self._queue_repository.mark_completed(queue_item.id)
            return

        if analysis.status == AnalysisStatus.FAILED:
            if lease_lost.is_set():
                return

            self._queue_repository.mark_failed(
                queue_item.id,
                "A análise já estava marcada como falha.",
            )
            return

        decrypted_payload = self._encryption.decrypt(
            queue_item.payload_ciphertext
        )

        payload = AnalysisQueuePayload.from_json(
            decrypted_payload
        )

        result = self._ai_provider.analyze(
            resume_text=payload.resume_text,
            job_description=payload.job_description,
        )

        if lease_lost.is_set():
            raise RuntimeError(
                "Lease perdido durante a execução da análise."
            )

        analysis.complete(
            evidenced_requirements=result.evidenced_requirements,
            unevidenced_requirements=result.unevidenced_requirements,
            gaps=result.gaps,
            resume_issues=result.resume_issues,
            suggestions=result.suggestions,
        )

        if lease_lost.is_set():
            raise RuntimeError(
                "Lease perdido antes da persistência do resultado."
            )

        self._analysis_repository.update(analysis)

        if lease_lost.is_set():
            logger.error(
                "Lease perdido após atualizar a análise %s.",
                queue_item.analysis_id,
            )
            return

        self._queue_repository.mark_completed(queue_item.id)

        logger.info(
            "Análise concluída: %s",
            queue_item.analysis_id,
        )

    def _handle_failure(
        self,
        queue_id: UUID,
        analysis_id: UUID,
        exception: Exception,
    ) -> None:
        """
        Registra a falha sem armazenar detalhes potencialmente
        sensíveis da exceção na fila.
        """

        safe_error = (
            f"{type(exception).__name__}: "
            "falha durante o processamento."
        )

        try:
            analysis = self._analysis_repository.get_by_id(
                analysis_id
            )

            if analysis is not None:
                if analysis.status in (
                    AnalysisStatus.PENDING,
                    AnalysisStatus.PROCESSING,
                ):
                    analysis.fail()
                    self._analysis_repository.update(analysis)

                elif analysis.status == AnalysisStatus.COMPLETED:
                    self._queue_repository.mark_completed(queue_id)
                    return

                elif analysis.status == AnalysisStatus.FAILED:
                    self._queue_repository.mark_failed(
                        queue_id,
                        safe_error,
                    )
                    return

            self._queue_repository.mark_failed(
                queue_id,
                safe_error,
            )

        except Exception as handling_error:
            logger.error(
                "Falha ao registrar o erro da tarefa %s: %s",
                queue_id,
                type(handling_error).__name__,
            )


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    worker = AnalysisWorker()
    worker.run()


if __name__ == "__main__":
    main()
