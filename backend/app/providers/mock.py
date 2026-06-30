import hashlib

from app.providers.base import GenerationResult, JudgeResult, LLMProvider

# Relative "quality" of each model, used to shape the mock outcome distribution
# so that comparing models/configs produces realistic, repeatable differences.
MODEL_QUALITY = {
    "gpt-4.1": 0.93,
    "claude": 0.95,
    "gemini": 0.90,
    "llama": 0.85,
    "mistral": 0.86,
}

# Rough latency (ms) and price ($ per 1K tokens) characteristics per model.
MODEL_LATENCY_MS = {
    "gpt-4.1": 1800,
    "claude": 2000,
    "gemini": 1500,
    "llama": 1200,
    "mistral": 1100,
}
MODEL_PRICE_PER_1K = {
    "gpt-4.1": 0.010,
    "claude": 0.012,
    "gemini": 0.007,
    "llama": 0.002,
    "mistral": 0.002,
}


def _unit(*parts) -> float:
    """Deterministic pseudo-random float in [0, 1) from the given parts."""
    h = hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()
    return int(h[:8], 16) / 0xFFFFFFFF


def model_price_per_1k(model: str) -> float:
    return MODEL_PRICE_PER_1K.get(model, 0.005)


class MockProvider(LLMProvider):
    """A deterministic, offline LLM stand-in.

    Outcomes depend on (question, model, temperature, prompt version, retriever,
    chunk size) so that changing the configuration produces realistic, reproducible
    shifts in accuracy/latency/cost — which is exactly what the Compare Runs view needs.
    No network calls, no API keys, no cost.
    """

    name = "mock"

    def __init__(self, model: str):
        self.model = model
        self.quality = MODEL_QUALITY.get(model, 0.88)

    def generate(self, system_prompt: str, question: str, config: dict) -> GenerationResult:
        temperature = float(config.get("temperature", 0.2))
        prompt_version = config.get("prompt_version", "")
        chunk_size = int(config.get("chunk_size", 512))
        top_k = int(config.get("top_k", 5))
        retriever = config.get("retriever", "hybrid")

        seed = _unit(question, self.model, prompt_version, retriever, chunk_size)

        # Token usage scales with question length, top_k retrieved chunks, and chunk size.
        prompt_tokens = 40 + len(question.split()) * 3 + top_k * (chunk_size // 32)
        completion_tokens = 60 + int(seed * 200)

        # Latency: base per-model + variance + extra for larger retrieval contexts.
        base = MODEL_LATENCY_MS.get(self.model, 1500)
        latency = base * (0.7 + 0.6 * seed) + top_k * 25 + (chunk_size / 512) * 100

        answer = (
            f"[{self.model}] Answer to: {question[:80]} "
            f"(prompt={prompt_version or 'default'}, retriever={retriever})"
        )

        retrieved = []
        if config.get("task_type", "rag") == "rag":
            retrieved = [f"doc_{int(_unit(question, i) * 1000)}" for i in range(top_k)]

        return GenerationResult(
            text=answer,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            latency_ms=round(latency, 1),
            retrieved_docs=retrieved,
        )

    def judge(self, question: str, ground_truth: str, answer: str, config: dict) -> JudgeResult:
        temperature = float(config.get("temperature", 0.2))
        prompt_version = config.get("prompt_version", "")
        retriever = config.get("retriever", "hybrid")

        # Higher temperature slightly reduces reliability; hybrid retrieval helps.
        retriever_bonus = 0.03 if retriever == "hybrid" else 0.0
        threshold = self.quality + retriever_bonus - temperature * 0.08

        roll = _unit("judge", question, self.model, prompt_version, retriever, ground_truth)
        is_correct = roll < threshold
        confidence = round(0.6 + 0.39 * _unit("conf", question, self.model, roll), 2)

        faithfulness = round(min(1.0, threshold + 0.05 * _unit("faith", question)), 2)
        # Hallucinations are a small fraction of the incorrect cases.
        is_hallucination = (not is_correct) and (
            _unit("hall", question, self.model) < 0.5
        )
        toxicity = round(_unit("tox", question, answer) * 0.02, 4)

        if is_correct:
            reasoning = "The response aligns with the ground truth on the key facts."
        elif is_hallucination:
            reasoning = "The response asserts details not supported by the reference — likely hallucinated."
        else:
            reasoning = "The response is incomplete or diverges from the expected answer."

        return JudgeResult(
            is_correct=is_correct,
            confidence=confidence,
            reasoning=reasoning,
            faithfulness=faithfulness,
            is_hallucination=is_hallucination,
            toxicity=toxicity,
        )
