import re
import unicodedata

from MatchCV.Parser.Exceptions.ParserException import ParserException


class ProfanityValidator:
    """Detecta palavrões, palavras chulas e conteúdo inadequado."""

    DEFAULT_TERMS = {
        # Português
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
        "cusinho",
        "cuzao",
        "cusao",
        "pau",
        "foda",
        "foda se",
        "fodasse",
        "fuder",
        "fode",
        "sexo",

        # Inglês
        "sex",
        "fuck",
        "cock",
        "asshole",
        "pussy",
        "dick",
        "bastard",
        "bitch",
        "bullshit",
        "crap",
        "damn",
        "douche",
        "douchebag",
        "fag",
        "faggot",
        "jerk",
        "motherfucker",
        "shit",
        "shitty",
        "slut",
        "whore",
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

    SEPARATOR_PATTERN = re.compile(r"[\s*_.\-/\\|]+")

    NON_ALPHANUMERIC_PATTERN = re.compile(r"[^a-z0-9\s]")

    WHITESPACE_PATTERN = re.compile(r"\s+")

    @classmethod
    def validate(
        cls,
        value: str | None,
        field_name: str,
        terms: set[str] | None = None,
    ) -> None:
        if value is None:
            return

        normalized_value = cls._normalize(value)
        configured_terms = terms or cls.DEFAULT_TERMS

        for term in configured_terms:
            normalized_term = cls._normalize(term)

            if cls._contains_term(
                normalized_value,
                normalized_term,
            ):
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

        normalized = cls.SEPARATOR_PATTERN.sub(
            " ",
            normalized,
        )

        normalized = cls.NON_ALPHANUMERIC_PATTERN.sub(
            " ",
            normalized,
        )

        normalized = cls.WHITESPACE_PATTERN.sub(
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

        pattern = (
            rf"(?<![a-z0-9])"
            rf"{re.escape(normalized_term)}"
            rf"(?![a-z0-9])"
        )

        return re.search(
            pattern,
            normalized_text,
        ) is not None
