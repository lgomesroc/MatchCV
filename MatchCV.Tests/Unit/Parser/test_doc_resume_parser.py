from io import BytesIO

import pytest

from MatchCV.Parser.Exceptions.ParserException import ParserException
from MatchCV.Parser.Parsers.DocResumeParser import DocResumeParser


class TestDocResumeParser:
    def setup_method(self):
        self.parser = DocResumeParser()

    def test_rejects_legacy_doc_file(self):
        with pytest.raises(
            ParserException,
            match="Arquivos DOC legados não podem ser processados",
        ):
            self.parser.parse(
                file_stream=BytesIO(b"legacy doc content"),
                file_name="curriculo.doc",
                file_size_bytes=1024,
            )

    def test_rejects_unsupported_extension_before_doc_error(self):
        with pytest.raises(
            ParserException,
            match="Formato de currículo não suportado",
        ):
            self.parser.parse(
                file_stream=BytesIO(b"content"),
                file_name="curriculo.txt",
                file_size_bytes=1024,
            )

    def test_rejects_empty_file_before_doc_error(self):
        with pytest.raises(
            ParserException,
            match="tamanho maior que zero",
        ):
            self.parser.parse(
                file_stream=BytesIO(b""),
                file_name="curriculo.doc",
                file_size_bytes=0,
            )
