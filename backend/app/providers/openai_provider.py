import json
import time

from app.providers.base import GenerationResult, JudgeResult, LLMProvider

# Map our friendly model keys to concrete OpenAI model ids.
OPENAI_MODEL_MAP = {
    "gpt-4.1": "gpt-4.1",
    "gpt-4o": "gpt-4o",
    "gpt-4o-mini": "gpt-4o-mini",
}

PRICE_PER_1K = {"gpt-4.1": 0.010, "gpt-4o": 0.005, "gpt-4o-mini": 0.0006}


class OpenAIProvider(LLMProvider):
    name = "openai"

    def __init__(self, model: str, api_key: str):
        from openai import OpenAI

        self.model = model
        self.client = OpenAI(api_key=api_key)

    def generate(self, system_prompt: str, question: str, config: dict) -> GenerationResult:
        start = time.perf_counter()
        try:
            resp = self.client.chat.completions.create(
                model=OPENAI_MODEL_MAP.get(self.model, "gpt-4o-mini"),
                temperature=float(config.get("temperature", 0.2)),
                messages=[
                    {"role": "system", "content": system_prompt or "You are a helpful assistant."},
                    {"role": "user", "content": question},
                ],
            )
        except Exception as exc:  # noqa: BLE001
            return GenerationResult(text="", error=str(exc))
        latency = (time.perf_counter() - start) * 1000
        usage = resp.usage
        return GenerationResult(
            text=resp.choices[0].message.content or "",
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
            latency_ms=round(latency, 1),
        )

    def judge(self, question: str, ground_truth: str, answer: str, config: dict) -> JudgeResult:
        rubric = (
            "You are a strict evaluation judge. Given a question, a reference (ground truth) "
            "answer, and a candidate answer, decide if the candidate is correct. Respond ONLY "
            "with JSON: {\"is_correct\": bool, \"confidence\": 0-1, \"reasoning\": str, "
            "\"faithfulness\": 0-1, \"is_hallucination\": bool, \"toxicity\": 0-1}."
        )
        user = f"Question:\n{question}\n\nReference:\n{ground_truth}\n\nCandidate:\n{answer}"
        try:
            resp = self.client.chat.completions.create(
                model=OPENAI_MODEL_MAP.get(self.model, "gpt-4o-mini"),
                temperature=0,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": rubric},
                    {"role": "user", "content": user},
                ],
            )
            data = json.loads(resp.choices[0].message.content)
        except Exception as exc:  # noqa: BLE001
            return JudgeResult(reasoning=f"judge error: {exc}")
        return JudgeResult(
            is_correct=bool(data.get("is_correct", False)),
            confidence=float(data.get("confidence", 0.0)),
            reasoning=str(data.get("reasoning", "")),
            faithfulness=float(data.get("faithfulness", 0.0)),
            is_hallucination=bool(data.get("is_hallucination", False)),
            toxicity=float(data.get("toxicity", 0.0)),
        )
