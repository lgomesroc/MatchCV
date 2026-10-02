from io import BytesIO
from typing import BinaryIO

from pypdf import PdfReader

from MatchCV.Domain.Enums.FileType import FileType
from MatchCV.Parser.Exceptions.ParserException import ParserException
from MatchCV.Parser.Interfaces.IResumeParser import IResumeParser
from MatchCV.Parser.Models.ParsedResume import ParsedResume
from MatchCV.Parser.Validation.ResumeFileValidator import (
    ResumeFileValidator,
)


class PdfResumeParser(IResumeParser):
    """Parser de currículos em formato PDF."""

    def parse(
        self,
        file_stream: BinaryIO,
        file_name: str,
        file_size_bytes: int,
    ) -> ParsedResume:
        ResumeFileValidator.validate(
            file_name=file_name,
            file_size_bytes=file_size_bytes,
        )

        try:
            file_stream.seek(0)
            file_bytes = file_stream.read()

            reader = PdfReader(BytesIO(file_bytes))

        except Exception as exception:
            raise ParserException(
                "Não foi possível ler o arquivo PDF."
            ) from exception

        is_password_protected = bool(reader.is_encrypted)

        if is_password_protected:
            return ParsedResume(
                file_name=file_name,
                file_type=FileType.PDF,
                file_size_bytes=file_size_bytes,
                page_count=len(reader.pages),
                extracted_text="",
                is_text_extractable=False,
                is_single_column=None,
                has_images=False,
                is_password_protected=True,
            )

        page_count = len(reader.pages)

        extracted_pages: list[str] = []
        has_images = False

        try:
            for page in reader.pages:
                text = page.extract_text() or ""
                extracted_pages.append(text)

                if "/XObject" in page.get("/Resources", {}):
                    has_images = True

        except Exception as exception:
            raise ParserException(
                "Não foi possível extrair o texto do arquivo PDF."
            ) from exception

        extracted_text = "\n".join(extracted_pages).strip()

        is_text_extractable = bool(
            extracted_text.strip()
        )

        return ParsedResume(
            file_name=file_name,
            file_type=FileType.PDF,
            file_size_bytes=file_size_bytes,
            page_count=page_count,
            extracted_text=extracted_text,
            is_text_extractable=is_text_extractable,
            is_single_column=self._detect_single_column(
                extracted_pages
            ),
            has_images=has_images,
            is_password_protected=False,
        )

    @staticmethod
    def _detect_single_column(
        pages_text: list[str],
    ) -> bool | None:
        """
        Faz uma heurística simples para detectar múltiplas colunas.

        A análise visual perfeita de layout não é responsabilidade
        deste parser na V1. Quando não houver evidência suficiente,
        retorna None.
        """

        if not pages_text:
            return None

        for page_text in pages_text:
            lines = [
                line.strip()
                for line in page_text.splitlines()
                if line.strip()
            ]

            if not lines:
                continue

            suspicious_lines = 0

            for line in lines:
                if "    " in line or "\t" in line:
                    suspicious_lines += 1

            if suspicious_lines >= 3:
                return False

        return True
