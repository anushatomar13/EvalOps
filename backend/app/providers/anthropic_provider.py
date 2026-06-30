import json
import time

from app.providers.base import GenerationResult, JudgeResult, LLMProvider

ANTHROPIC_MODEL_MAP = {
    "claude": "claude-sonnet-4-6",
    "claude-opus": "claude-opus-4-8",
    "claude-haiku": "claude-haiku-4-5-20251001",
}

PRICE_PER_1K = {"claude": 0.012, "claude-opus": 0.020, "claude-haiku": 0.001}


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    def __init__(self, model: str, api_key: str):
        import anthropic

        self.model = model
        self.client = anthropic.Anthropic(api_key=api_key)

    def _model_id(self) -> str:
        return ANTHROPIC_MODEL_MAP.get(self.model, "claude-sonnet-4-6")

    def generate(self, system_prompt: str, question: str, config: dict) -> GenerationResult:
        start = time.perf_counter()
        try:
            resp = self.client.messages.create(
                model=self._model_id(),
                max_tokens=1024,
                temperature=float(config.get("temperature", 0.2)),
                system=system_prompt or "You are a helpful assistant.",
                messages=[{"role": "user", "content": question}],
            )
        except Exception as exc:  # noqa: BLE001
            return GenerationResult(text="", error=str(exc))
        latency = (time.perf_counter() - start) * 1000
        text = "".join(block.text for block in resp.content if block.type == "text")
        return GenerationResult(
            text=text,
            prompt_tokens=resp.usage.input_tokens,
            completion_tokens=resp.usage.output_tokens,
            latency_ms=round(latency, 1),
        )

    def judge(self, question: str, ground_truth: str, answer: str, config: dict) -> JudgeResult:
        rubric = (
            "You are a strict evaluation judge. Respond ONLY with JSON: "
            "{\"is_correct\": bool, \"confidence\": 0-1, \"reasoning\": str, "
            "\"faithfulness\": 0-1, \"is_hallucination\": bool, \"toxicity\": 0-1}."
        )
        user = f"Question:\n{question}\n\nReference:\n{ground_truth}\n\nCandidate:\n{answer}"
        try:
            resp = self.client.messages.create(
                model=self._model_id(),
                max_tokens=512,
                temperature=0,
                system=rubric,
                messages=[{"role": "user", "content": user}],
            )
            text = "".join(b.text for b in resp.content if b.type == "text")
            data = json.loads(text)
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
