
import re
import unicodedata

from MatchCV.Domain.Exceptions.DomainException import DomainException


class ProfanityValidator:
    """Detecta palavrões e termos inadequados sem bloquear palavras legítimas."""

    DEFAULT_TERMS = {
        "caralho",
        "puta",
        "piru",
        "piroca",
        "pica",
        "buceta",
        "vagina",
        "penis",
        "porra",
        "cuzinho",
        "cusinho",
        "cuzao",
        "cusao",
        "foda",
        "foda se",
        "fodasse",
        "fuder",
        "fode",
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
        obfuscated_value = cls._normalize_obfuscated(value)

        configured_terms = cls.DEFAULT_TERMS if terms is None else terms

        # "Pica-pau" é um composto legítimo. A exceção só se aplica
        # à lista padrão, sem desativar termos personalizados.
        legitimate_pica_pau = (
            terms is None
            and cls._contains_term(normalized_value, "pica pau")
        )

        for term in configured_terms:
            normalized_term = cls._normalize(term)

            if (
                legitimate_pica_pau
                and normalized_term == "pica"
            ):
                continue

            if (
                cls._contains_term(normalized_value, normalized_term)
                or cls._contains_term(obfuscated_value, normalized_term)
            ):
                raise DomainException(
                    f"{field_name} contém conteúdo inadequado."
                )

        # "cocô" é proibido, mas "coco" sem acento pode aparecer
        # em nomes próprios e empresas, como Coco Bambu.
        if terms is None and re.search(
            r"(?<!\w)cocô(?!\w)",
            value,
            flags=re.IGNORECASE,
        ):
            raise DomainException(
                f"{field_name} contém conteúdo inadequado."
            )

    @classmethod
    def _normalize(cls, value: str) -> str:
        """Remove acentos e normaliza separadores, caixa e espaços."""
        normalized = unicodedata.normalize("NFKD", value)
        normalized = "".join(
            character
            for character in normalized
            if not unicodedata.combining(character)
        )
        normalized = normalized.lower()
        normalized = normalized.translate(cls.LEET_TRANSLATION)
        normalized = cls.SEPARATOR_PATTERN.sub(" ", normalized)
        normalized = cls.NON_ALPHANUMERIC_PATTERN.sub(" ", normalized)
        normalized = cls.WHITESPACE_PATTERN.sub(" ", normalized)

        return normalized.strip()

    @classmethod
    def _normalize_obfuscated(cls, value: str) -> str:
        """Detecta termos disfarçados com separadores entre letras."""
        normalized = unicodedata.normalize("NFKD", value)
        normalized = "".join(
            character
            for character in normalized
            if not unicodedata.combining(character)
        )
        normalized = normalized.lower()
        normalized = normalized.translate(cls.LEET_TRANSLATION)

        normalized = re.sub(
            r"(?<=[a-z0-9])[*_.\-/\\|]+(?=[a-z0-9])",
            "",
            normalized,
        )
        normalized = cls.NON_ALPHANUMERIC_PATTERN.sub(" ", normalized)
        normalized = cls.WHITESPACE_PATTERN.sub(" ", normalized)

        return normalized.strip()

    @staticmethod
    def _contains_term(
        normalized_text: str,
        normalized_term: str,
    ) -> bool:
        """Verifica um termo isolado, respeitando os limites das palavras."""
        if not normalized_term:
            return False

        pattern = (
            rf"(?<![a-z0-9])"
            rf"{re.escape(normalized_term)}"
            rf"(?![a-z0-9])"
        )

        return re.search(pattern, normalized_text) is not None
