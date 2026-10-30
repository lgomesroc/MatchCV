from typing import Callable
from uuid import UUID, uuid4

from MatchCV.Application.DTOs.AnalysisResult import AnalysisResult
from MatchCV.Application.DTOs.AnalyzeResumeRequest import (
    AnalyzeResumeRequest,
)
from MatchCV.Application.Interfaces.IAnalysisProvider import (
    IAnalysisProvider,
)
from MatchCV.Application.Interfaces.IResumeParserService import (
    IResumeParserService,
)
from MatchCV.Application.Repositories.IAnalysisRepository import (
    IAnalysisRepository,
)
from MatchCV.Application.Repositories.IJobDescriptionRepository import (
    IJobDescriptionRepository,
)
from MatchCV.Application.Queue.AnalysisQueuePayload import AnalysisQueuePayload
from MatchCV.Application.Queue.IAnalysisQueueRepository import IAnalysisQueueRepository
from MatchCV.Infrastructure.Security.AnalysisPayloadEncryption import AnalysisPayloadEncryption
from MatchCV.Domain.Entities.Analysis import Analysis
from MatchCV.Domain.Entities.JobDescription import JobDescription
from MatchCV.Domain.Entities.Resume import Resume
from MatchCV.Domain.Exceptions.DomainException import DomainException
from MatchCV.Domain.Validation.ProfanityValidator import (
    ProfanityValidator,
)
from MatchCV.Domain.Validation.TextContentValidator import (
    TextContentValidator,
)


class AnalyzeResumeUseCase:
    """
    Caso de uso responsável por processar um currículo e realizar
    a análise em relação a uma descrição de vaga.
    """

    MIN_USEFUL_CHARACTERS = 30

    def __init__(
        self,
        resume_parser_service: IResumeParserService,
        analysis_provider: IAnalysisProvider,
        job_description_repository: IJobDescriptionRepository,
        analysis_repository: IAnalysisRepository,
        queue_repository: IAnalysisQueueRepository | None = None,
        payload_encryption: AnalysisPayloadEncryption | None = None,
    ) -> None:
        self._resume_parser_service = resume_parser_service
        self._analysis_provider = analysis_provider
        self._job_description_repository = job_description_repository
        self._analysis_repository = analysis_repository
        self._queue_repository = queue_repository
        self._payload_encryption = payload_encryption

    def enqueue(
        self,
        request: AnalyzeResumeRequest,
        user_id: UUID,
        on_analysis_created: Callable[[UUID], None] | None = None,
    ) -> Analysis:
        """Valida e persiste uma análise pendente sem chamar o provedor de IA."""
        if self._queue_repository is None or self._payload_encryption is None:
            raise RuntimeError("A fila assíncrona não foi configurada.")

        if not user_id:
            raise DomainException(
                "O usuário é obrigatório para realizar a análise."
            )

        job_description = JobDescription.create(request.job_description)

        if request.resume_text is not None:
            resume_text = self._validate_resume_text(request.resume_text)
            resume_id = uuid4()
        else:
            if (
                request.file_stream is None
                or request.file_name is None
                or request.file_size_bytes is None
            ):
                raise DomainException(
                    "Os dados do arquivo do currículo são obrigatórios."
                )

            parsed_resume = self._resume_parser_service.parse(
                file_stream=request.file_stream,
                file_name=request.file_name,
                file_size_bytes=request.file_size_bytes,
            )
            resume_text = self._validate_resume_text(
                parsed_resume.extracted_text
            )
            resume = Resume.create(
                file_name=parsed_resume.file_name,
                file_type=parsed_resume.file_type,
                file_size_bytes=parsed_resume.file_size_bytes,
                page_count=parsed_resume.page_count,
                extracted_text=resume_text,
            )
            resume_id = resume.id

        self._job_description_repository.add(job_description)
        analysis = Analysis.create(
            user_id=user_id,
            resume_id=resume_id,
            job_description_id=job_description.id,
        )
        self._analysis_repository.add(analysis, user_id)

        if on_analysis_created is not None:
            on_analysis_created(analysis.id)

        payload = AnalysisQueuePayload(
            resume_text=resume_text,
            job_description=job_description.content,
        )
        encrypted_payload = self._payload_encryption.encrypt(payload.to_json())
        try:
            self._queue_repository.enqueue(
                analysis_id=analysis.id,
                payload_ciphertext=encrypted_payload,
            )
        except Exception:
            # A análise não deve ficar indefinidamente pendente sem tarefa.
            analysis.start_processing()
            analysis.fail()
            self._analysis_repository.update(analysis)
            raise

        return analysis

    def execute(
        self,
        request: AnalyzeResumeRequest,
        user_id: UUID,
    ) -> AnalysisResult:
        """
        Executa a análise completa.

        Este método ainda representa o processamento síncrono atual.
        A próxima etapa moverá a chamada da IA para o worker.
        """

        if not user_id:
            raise DomainException(
                "O usuário é obrigatório para realizar a análise."
            )

        job_description = JobDescription.create(
            request.job_description,
        )

        if request.resume_text is not None:
            resume_text = self._validate_resume_text(
                request.resume_text,
            )

            resume_id = uuid4()

        else:
            if (
                request.file_stream is None
                or request.file_name is None
                or request.file_size_bytes is None
            ):
                raise DomainException(
                    "Os dados do arquivo do currículo são obrigatórios."
                )

            parsed_resume = self._resume_parser_service.parse(
                file_stream=request.file_stream,
                file_name=request.file_name,
                file_size_bytes=request.file_size_bytes,
            )

            resume_text = self._validate_resume_text(
                parsed_resume.extracted_text,
            )

            resume = Resume.create(
                file_name=parsed_resume.file_name,
                file_type=parsed_resume.file_type,
                file_size_bytes=parsed_resume.file_size_bytes,
                page_count=parsed_resume.page_count,
                extracted_text=resume_text,
            )

            resume_id = resume.id

        self._job_description_repository.add(
            job_description,
        )

        analysis = Analysis.create(
            user_id=user_id,
            resume_id=resume_id,
            job_description_id=job_description.id,
        )

        self._analysis_repository.add(
            analysis,
            user_id,
        )

        analysis.start_processing()

        self._analysis_repository.update(
            analysis,
        )

        try:
            result = self._analysis_provider.analyze(
                resume_text=resume_text,
                job_description=job_description.content,
            )

            analysis.complete(
                evidenced_requirements=result.evidenced_requirements,
                unevidenced_requirements=result.unevidenced_requirements,
                gaps=result.gaps,
                resume_issues=result.resume_issues,
                suggestions=result.suggestions,
            )

            self._analysis_repository.update(
                analysis,
            )

            return result

        except Exception:
            analysis.fail()

            self._analysis_repository.update(
                analysis,
            )

            raise

    @classmethod
    def _validate_resume_text(
        cls,
        resume_text: str,
    ) -> str:
        if not resume_text or not resume_text.strip():
            raise DomainException(
                "O currículo deve possuir texto."
            )

        normalized_text = resume_text.strip()

        if len(normalized_text) > Resume.MAX_CHARACTERS:
            raise DomainException(
                "O currículo não pode ultrapassar 15000 caracteres."
            )

        useful_characters = len(
            "".join(
                character
                for character in normalized_text
                if character.isalnum()
            )
        )

        if useful_characters < cls.MIN_USEFUL_CHARACTERS:
            raise DomainException(
                "O currículo deve possuir pelo menos "
                "30 caracteres úteis."
            )

        TextContentValidator.validate_no_emoji_or_emoticon(
            normalized_text,
            "O currículo",
        )

        ProfanityValidator.validate(
            normalized_text,
            "O currículo",
        )

        return normalized_text
