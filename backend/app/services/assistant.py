import json

from openai import APIError, AsyncOpenAI
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.services.queue_engine import QueueEngine, QueueNotFoundError


class AssistantError(Exception):
    status_code = 503

    def __init__(self, detail: str):
        super().__init__(detail)
        self.detail = detail


class AssistantConfigurationError(AssistantError):
    status_code = 503


class AssistantProviderError(AssistantError):
    status_code = 502


class QueueOperationsAssistant:
    _client: AsyncOpenAI | None = None
    _client_api_key: str | None = None

    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()

    async def answer(self, queue_entry_id: int, question: str) -> str:
        if not self.settings.openai_api_key:
            raise AssistantConfigurationError(
                "The Queue Operations Assistant is not configured."
            )

        engine = QueueEngine(self.db)
        queue_entry = engine.get_queue_entry(queue_entry_id)
        try:
            recommended_branch = engine.recommend_branch()
            recommendation = {
                "name": recommended_branch.name,
                "id": recommended_branch.id,
            }
        except QueueNotFoundError:
            recommendation = None

        prompt = self._build_prompt(question, queue_entry, recommendation)
        try:
            response = await self._get_client().chat.completions.create(
                model=self.settings.openai_model,
                temperature=0,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are QueuePilot's read-only Queue Operations Assistant. "
                            "Answer only questions about queue position, ETA, READY status, "
                            "queue behavior, branch recommendations, skipped customers, "
                            "or expected waiting time. Politely explain that you only "
                            "support QueuePilot queue operations for unrelated questions. "
                            "Use only the supplied Queue Engine data. Never invent values, "
                            "and never suggest that you changed queue state."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
            )
        except APIError:
            raise AssistantProviderError(
                "The Queue Operations Assistant provider is unavailable."
            ) from None

        answer = response.choices[0].message.content if response.choices else None
        if not answer:
            raise AssistantProviderError("The assistant returned no answer.")
        return answer.strip()

    @classmethod
    def _get_client(cls) -> AsyncOpenAI:
        settings = get_settings()
        api_key = settings.openai_api_key
        if not api_key:
            raise AssistantConfigurationError(
                "The Queue Operations Assistant is not configured."
            )
        if cls._client is None or cls._client_api_key != api_key:
            cls._client = AsyncOpenAI(api_key=api_key)
            cls._client_api_key = api_key
        return cls._client

    @staticmethod
    def _build_prompt(
        question: str,
        queue_entry: dict[str, object],
        recommendation: dict[str, object] | None,
    ) -> str:
        return (
            "Answer the customer's question using this current Queue Engine snapshot.\n\n"
            f"Customer question: {question}\n"
            f"Queue snapshot: {json.dumps(queue_entry, sort_keys=True)}\n"
            "Lowest-ETA branch recommendation: "
            f"{json.dumps(recommendation, sort_keys=True) if recommendation else 'Unavailable'}\n\n"
            "If the snapshot does not contain enough information, say so plainly."
        )
