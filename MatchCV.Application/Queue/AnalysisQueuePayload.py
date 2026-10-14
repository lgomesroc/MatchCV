from dataclasses import dataclass
import json


@dataclass
class AnalysisQueuePayload:
    resume_text: str
    job_description: str

    def to_json(self) -> str:
        return json.dumps(
            {
                "resume_text": self.resume_text,
                "job_description": self.job_description,
            },
            ensure_ascii=False,
        )

    @classmethod
    def from_json(
        cls,
        value: str,
    ) -> "AnalysisQueuePayload":
        data = json.loads(value)

        return cls(
            resume_text=data["resume_text"],
            job_description=data["job_description"],
        )
