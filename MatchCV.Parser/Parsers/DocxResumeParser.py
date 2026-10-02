from io import BytesIO
from typing import BinaryIO

from docx import Document

from MatchCV.Domain.Enums.FileType import FileType
from MatchCV.Parser.Exceptions.ParserException import ParserException
from MatchCV.Parser.Interfaces.IResumeParser import IResumeParser
from MatchCV.Parser.Models.ParsedResume import ParsedResume
from MatchCV.Parser.Validation.ResumeFileValidator import (
    ResumeFileValidator,
)


class DocxResumeParser(IResumeParser):
    """Parser de currículos em formato DOCX."""

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

            document = Document(BytesIO(file_bytes))

        except Exception as exception:
            raise ParserException(
                "Não foi possível ler o arquivo DOCX."
            ) from exception

        paragraphs = [
            paragraph.text.strip()
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        ]

        table_text: list[str] = []

        for table in document.tables:
            for row in table.rows:
                cells = [
                    cell.text.strip()
                    for cell in row.cells
                    if cell.text.strip()
                ]

                if cells:
                    table_text.append(" | ".join(cells))

        extracted_parts = paragraphs + table_text

        extracted_text = "\n".join(
            extracted_parts
        ).strip()

        has_images = bool(
            document.inline_shapes
        )

        page_count = self._estimate_page_count(
            extracted_text
        )

        return ParsedResume(
            file_name=file_name,
            file_type=FileType.DOCX,
            file_size_bytes=file_size_bytes,
            page_count=page_count,
            extracted_text=extracted_text,
            is_text_extractable=bool(extracted_text),
            is_single_column=self._detect_single_column(
                document
            ),
            has_images=has_images,
            is_password_protected=False,
        )

    @staticmethod
    def _estimate_page_count(
        extracted_text: str,
    ) -> int:
        """
        Estimativa de páginas para DOCX.

        O python-docx não fornece paginação física confiável,
        pois a quantidade real de páginas depende do mecanismo
        de renderização do Word.

        Quebras de página explícitas são consideradas.
        """

        if not extracted_text:
            return 1

        return max(
            1,
            extracted_text.count("\f") + 1,
        )

    @staticmethod
    def _detect_single_column(
        document: Document,
    ) -> bool | None:
        """
        Detecta estruturas obviamente baseadas em tabelas.

        Tabelas podem representar tanto layout legítimo quanto
        múltiplas colunas. Por isso, nesta V1 não rejeitamos
        automaticamente documentos que possuem tabelas.
        """

        if not document.paragraphs and not document.tables:
            return None

        return True
