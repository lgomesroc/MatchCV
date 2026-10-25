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
    persisted_states = []
    worker._analysis_repository.update.side_effect = (
        lambda saved_analysis: persisted_states.append(
            saved_analysis.status
        )
    )
    worker._queue_repository = MagicMock()
    worker._encryption = MagicMock()
    worker._encryption.decrypt.return_value = payload.to_json()
    worker._ai_provider = MagicMock()
    worker._ai_provider.analyze.return_value = result

    worker._process_item(queue_item, threading.Event())

    assert analysis.status == AnalysisStatus.COMPLETED
    assert analysis.user_id == user_id
    assert worker._analysis_repository.update.call_count == 2
    assert persisted_states == [
        AnalysisStatus.PROCESSING,
        AnalysisStatus.COMPLETED,
    ]
    worker._queue_repository.mark_completed.assert_called_once_with(
        queue_item.id
    )
    worker._ai_provider.analyze.assert_called_once_with(
        resume_text=payload.resume_text,
        job_description=payload.job_description,
    )



def test_worker_does_not_call_ai_for_already_completed_analysis():
    analysis = Analysis(
        id=uuid4(),
        user_id=uuid4(),
        resume_id=uuid4(),
        job_description_id=uuid4(),
        status=AnalysisStatus.COMPLETED,
    )
    queue_item = AnalysisQueueItem(
        id=uuid4(),
        analysis_id=analysis.id,
        payload_ciphertext=b"unused",
        status="PROCESSING",
        attempts=2,
        created_at=datetime.now(timezone.utc),
        started_at=datetime.now(timezone.utc),
        finished_at=None,
        last_error=None,
    )
    worker = AnalysisWorker.__new__(AnalysisWorker)
    worker._analysis_repository = MagicMock()
    worker._analysis_repository.get_by_id.return_value = analysis
    worker._queue_repository = MagicMock()
    worker._encryption = MagicMock()
    worker._ai_provider = MagicMock()

    worker._process_item(queue_item, threading.Event())

    worker._ai_provider.analyze.assert_not_called()
    worker._analysis_repository.update.assert_not_called()
    worker._queue_repository.mark_completed.assert_called_once_with(queue_item.id)


def test_worker_does_not_persist_result_after_lease_is_lost():
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
        resume_text="Experiência profissional em desenvolvimento de sistemas e APIs REST.",
        job_description="Vaga para pessoa desenvolvedora com experiência em APIs e testes automatizados.",
    )
    result = MagicMock()
    result.evidenced_requirements = []
    result.unevidenced_requirements = []
    result.gaps = []
    result.resume_issues = []
    result.suggestions = []

    worker = AnalysisWorker.__new__(AnalysisWorker)
    worker._analysis_repository = MagicMock()
    worker._analysis_repository.get_by_id.return_value = analysis
    worker._queue_repository = MagicMock()
    worker._encryption = MagicMock()
    worker._encryption.decrypt.return_value = payload.to_json()
    worker._ai_provider = MagicMock()
    worker._ai_provider.analyze.return_value = result
    lease_lost = threading.Event()
    lease_lost.set()

    try:
        worker._process_item(queue_item, lease_lost)
    except RuntimeError as exc:
        assert "Lease perdido" in str(exc)
    else:
        raise AssertionError("Era esperado impedir a persistência após perder o lease.")

    worker._analysis_repository.update.assert_called_once_with(analysis)
    assert analysis.status == AnalysisStatus.PROCESSING
    worker._queue_repository.mark_completed.assert_not_called()
