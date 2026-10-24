from unittest.mock import MagicMock
from uuid import uuid4

from MatchCV.Application.DTOs.AnalyzeResumeRequest import AnalyzeResumeRequest
from MatchCV.Application.UseCases.AnalyzeResumeUseCase import AnalyzeResumeUseCase


def test_enqueue_persists_pending_analysis_and_encrypted_payload_without_calling_ai():
    parser = MagicMock()
    ai_provider = MagicMock()
    job_repository = MagicMock()
    analysis_repository = MagicMock()
    queue_repository = MagicMock()
    encryption = MagicMock()
    encryption.encrypt.return_value = b"encrypted-payload"

    use_case = AnalyzeResumeUseCase(
        resume_parser_service=parser,
        analysis_provider=ai_provider,
        job_description_repository=job_repository,
        analysis_repository=analysis_repository,
        queue_repository=queue_repository,
        payload_encryption=encryption,
    )
    request = AnalyzeResumeRequest(
        job_description=(
            "Vaga para pessoa desenvolvedora com experiência em APIs REST "
            "e testes automatizados."
        ),
        resume_text=(
            "Experiência profissional em desenvolvimento de sistemas, "
            "criação de APIs e testes automatizados."
        ),
    )
    user_id = uuid4()

    analysis = use_case.enqueue(request, user_id=user_id)

    assert analysis.status.value == "PENDING"
    job_repository.add.assert_called_once()
    analysis_repository.add.assert_called_once_with(analysis, user_id)
    encryption.encrypt.assert_called_once()
    queue_repository.enqueue.assert_called_once_with(
        analysis_id=analysis.id,
        payload_ciphertext=b"encrypted-payload",
    )
    ai_provider.analyze.assert_not_called()
