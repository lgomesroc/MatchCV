
from io import BytesIO

from MatchCV.Application.DTOs.AnalyzeResumeRequest import AnalyzeResumeRequest


class TestAnalyzeResumeRequest:
    def test_creates_request_with_pasted_resume_text(self):
        request = AnalyzeResumeRequest(
            job_description="Vaga para desenvolvedor Python.",
            resume_text="Experiência profissional com Python e desenvolvimento de APIs.",
        )

        assert request.job_description == "Vaga para desenvolvedor Python."
        assert request.resume_text == (
            "Experiência profissional com Python e desenvolvimento de APIs."
        )
        assert request.file_stream is None
        assert request.file_name is None
        assert request.file_size_bytes is None

    def test_creates_request_with_uploaded_file(self):
        file_stream = BytesIO(b"conteudo do curriculo")

        request = AnalyzeResumeRequest(
            job_description="Vaga para desenvolvedor Python.",
            file_stream=file_stream,
            file_name="curriculo.pdf",
            file_size_bytes=20,
        )

        assert request.job_description == "Vaga para desenvolvedor Python."
        assert request.file_stream is file_stream
        assert request.file_name == "curriculo.pdf"
        assert request.file_size_bytes == 20
        assert request.resume_text is None

    def test_creates_request_with_all_fields(self):
        file_stream = BytesIO(b"conteudo do curriculo")

        request = AnalyzeResumeRequest(
            job_description="Vaga para desenvolvedor Python.",
            file_stream=file_stream,
            file_name="curriculo.pdf",
            file_size_bytes=20,
            resume_text="Experiência profissional com Python.",
        )

        assert request.job_description == "Vaga para desenvolvedor Python."
        assert request.file_stream is file_stream
        assert request.file_name == "curriculo.pdf"
        assert request.file_size_bytes == 20
        assert request.resume_text == "Experiência profissional com Python."

    def test_optional_fields_default_to_none(self):
        request = AnalyzeResumeRequest(
            job_description="Vaga para desenvolvedor Java."
        )

        assert request.file_stream is None
        assert request.file_name is None
        assert request.file_size_bytes is None
        assert request.resume_text is None

    def test_preserves_zero_file_size_without_validating_it(self):
        request = AnalyzeResumeRequest(
            job_description="Vaga para desenvolvedor Java.",
            file_stream=BytesIO(b""),
            file_name="curriculo.pdf",
            file_size_bytes=0,
        )

        assert request.file_size_bytes == 0

    def test_preserves_empty_resume_text_without_validating_it(self):
        request = AnalyzeResumeRequest(
            job_description="Vaga para desenvolvedor Java.",
            resume_text="",
        )

        assert request.resume_text == ""
