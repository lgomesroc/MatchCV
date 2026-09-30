from MatchCV.Parser.Exceptions.ParserException import ParserException
from MatchCV.Parser.Models.ParsedResume import ParsedResume


class ResumeStructureValidator:
    """Valida a estrutura extraída do currículo."""

    MIN_USEFUL_CHARACTERS = 30
    MAX_PAGE_COUNT = 2

    @classmethod
    def validate(cls, parsed_resume: ParsedResume) -> None:
        if parsed_resume.page_count <= 0:
            raise ParserException(
                "O currículo deve possuir pelo menos uma página."
            )

        if parsed_resume.page_count > cls.MAX_PAGE_COUNT:
            raise ParserException(
                "O currículo não pode possuir mais de duas páginas."
            )

        if not parsed_resume.is_text_extractable:
            raise ParserException(
                "Não foi possível extrair texto do currículo."
            )

        useful_characters = len(
            "".join(
                character
                for character in parsed_resume.extracted_text
                if character.isalnum()
            )
        )

        if useful_characters < cls.MIN_USEFUL_CHARACTERS:
            raise ParserException(
                "O currículo deve possuir pelo menos 30 caracteres úteis."
            )

        if parsed_resume.is_password_protected:
            raise ParserException(
                "Não é possível processar um currículo protegido por senha."
            )

        if parsed_resume.is_single_column is False:
            raise ParserException(
                "O currículo deve utilizar uma estrutura de coluna única."
            )
