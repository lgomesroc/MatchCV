import threading
from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import uuid4

from MatchCV.Application.Queue.AnalysisQueueItem import AnalysisQueueItem
from MatchCV.Application.Queue.AnalysisQueuePayload import AnalysisQueuePayload
from MatchCV.Domain.Entities.Analysis import Analysis
from MatchCV.Domain.Enums.AnalysisStatus import AnalysisStatus
from MatchCV.Worker.AnalysisWorker import AnalysisWorker


def test_worker_moves_pending_analysis_to_processing_before_completion():
    user_id = uuid4()
    analysis = Analysis(
        id=uuid4(),
        user_id=user_id,
        resume_id=uuid4(),
        job_description_id=uuid4(),
    )
    queue_item = AnalysisQueueItem(
        id=uuid4(),
        analysis_id=analysis.id,
        payload_ciphertext=b"encrypted",
        status="PROCESSING",
        attempts=1,
        created_at=datetime.now(timezone.utc),
        started_at=datetime.now(timezone.utc),
        finished_at=None,
        last_error=None,
    )
    payload = AnalysisQueuePayload(
        resume_text=(
            "Experiência profissional em desenvolvimento de sistemas, "
            "criação de APIs e testes automatizados."
        ),
        job_description=(
            "Vaga para desenvolvedor com experiência em APIs REST "
            "e desenvolvimento de aplicações."
        ),
    )
    result = MagicMock()
    result.evidenced_requirements = ["Python"]
    result.unevidenced_requirements = ["Docker"]
    result.gaps = ["Experiência em cloud"]
    result.resume_issues = []
    result.suggestions = ["Detalhar projetos"]

    worker = AnalysisWorker.__new__(AnalysisWorker)
    worker._analysis_repository = MagicMock()
    worker._analysis_repository.get_by_id.return_value = analysis
    worker._queue_repository = MagicMock()
    worker._encryption = MagicMock()
    worker._encryption.decrypt.return_value = payload.to_json()
    worker._ai_provider = MagicMock()
    worker._ai_provider.analyze.return_value = result

    worker._process_item(queue_item, threading.Event())

    assert analysis.status == AnalysisStatus.COMPLETED
    assert analysis.user_id == user_id
    assert worker._analysis_repository.update.call_count == 2
    first_saved_state = (
        worker._analysis_repository.update.call_args_list[0].args[0].status
    )
    second_saved_state = (
        worker._analysis_repository.update.call_args_list[1].args[0].status
    )
    assert first_saved_state == AnalysisStatus.COMPLETED
    assert second_saved_state == AnalysisStatus.COMPLETED
    worker._queue_repository.mark_completed.assert_called_once_with(
        queue_item.id
    )
    worker._ai_provider.analyze.assert_called_once_with(
        resume_text=payload.resume_text,
        job_description=payload.job_description,
    )
