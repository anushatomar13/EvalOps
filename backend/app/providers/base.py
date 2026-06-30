from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List


@dataclass
class GenerationResult:
    text: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_ms: float = 0.0
    retrieved_docs: List[str] = field(default_factory=list)
    error: str = ""

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


@dataclass
class JudgeResult:
    is_correct: bool = False
    confidence: float = 0.0
    reasoning: str = ""
    faithfulness: float = 0.0
    is_hallucination: bool = False
    toxicity: float = 0.0


class LLMProvider(ABC):
    """Interface every model provider (mock, OpenAI, Anthropic, ...) implements."""

    name: str = "base"

    @abstractmethod
    def generate(self, system_prompt: str, question: str, config: dict) -> GenerationResult:
        """Produce an answer for a single question under the given config."""

    @abstractmethod
    def judge(self, question: str, ground_truth: str, answer: str, config: dict) -> JudgeResult:
        """Score an answer against the ground truth (LLM-as-a-judge)."""
