
from uuid import uuid4

import pytest

from MatchCV.Application.Interfaces.IAnalysisProvider import IAnalysisProvider
from MatchCV.Application.Interfaces.IResumeParserService import IResumeParserService
from MatchCV.Application.Repositories.IAnalysisRepository import IAnalysisRepository
from MatchCV.Application.Repositories.IJobDescriptionRepository import (
    IJobDescriptionRepository,
)
from MatchCV.Application.Repositories.IUserRepository import IUserRepository


class TestApplicationInterfaces:
    @pytest.mark.parametrize(
        "interface",
        [
            IAnalysisProvider,
            IResumeParserService,
            IAnalysisRepository,
            IJobDescriptionRepository,
            IUserRepository,
        ],
    )
    def test_abstract_interfaces_cannot_be_instantiated(self, interface):
        with pytest.raises(TypeError):
            interface()

    def test_analysis_provider_requires_analyze_implementation(self):
        class Provider(IAnalysisProvider):
            pass

        with pytest.raises(TypeError):
            Provider()

    def test_resume_parser_service_requires_parse_implementation(self):
        class ParserService(IResumeParserService):
            pass

        with pytest.raises(TypeError):
            ParserService()

    def test_analysis_repository_requires_abstract_methods(self):
        class Repository(IAnalysisRepository):
            pass

        with pytest.raises(TypeError):
            Repository()

    def test_job_description_repository_requires_abstract_methods(self):
        class Repository(IJobDescriptionRepository):
            pass

        with pytest.raises(TypeError):
            Repository()

    def test_user_repository_requires_abstract_methods(self):
        class Repository(IUserRepository):
            pass

        with pytest.raises(TypeError):
            Repository()
