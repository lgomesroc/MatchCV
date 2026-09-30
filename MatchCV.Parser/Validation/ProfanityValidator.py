import re
import unicodedata

from MatchCV.Parser.Exceptions.ParserException import ParserException


class ProfanityValidator:
    """Detecta palavras chulas, palavrões e conteúdo inadequado."""

    DEFAULT_TERMS = {
        "caralho",
        "puta",
        "piru",
        "piroca",
        "pica",
        "buceta",
        "vagina",
        "penis",
        "cueca",
        "calcinha",
        "porra",
        "cuzinho",
        "sexo",
        "sex",
        "fuck",
    }

    LEET_TRANSLATION = str.maketrans(
        {
            "0": "o",
            "1": "i",
            "3": "e",
            "4": "a",
            "5": "s",
            "7": "t",
        }
    )

    @classmethod
    def validate(
        cls,
        value: str | None,
        field_name: str,
        terms: set[str] | None = None,
    ) -> None:
        if value is None:
            return

        normalized = cls._normalize(value)

        configured_terms = terms or cls.DEFAULT_TERMS

        for term in configured_terms:
            normalized_term = cls._normalize(term)

            if cls._contains_term(normalized, normalized_term):
                raise ParserException(
                    f"{field_name} contém conteúdo inadequado."
                )

    @classmethod
    def _normalize(cls, value: str) -> str:
        normalized = unicodedata.normalize(
            "NFKD",
            value,
        )

        normalized = "".join(
            character
            for character in normalized
            if not unicodedata.combining(character)
        )

        normalized = normalized.lower()

        normalized = normalized.translate(
            cls.LEET_TRANSLATION
        )

        normalized = re.sub(
            r"[*_\-./\\|]+",
            " ",
            normalized,
        )

        normalized = re.sub(
            r"[^a-z0-9\s]",
            " ",
            normalized,
        )

        normalized = re.sub(
            r"\s+",
            " ",
            normalized,
        )

        return normalized.strip()

    @staticmethod
    def _contains_term(
        normalized_text: str,
        normalized_term: str,
    ) -> bool:
        if not normalized_term:
            return False

        pattern = rf"(?<![a-z0-9]){re.escape(normalized_term)}(?![a-z0-9])"

        return re.search(
            pattern,
            normalized_text,
        ) is not None
