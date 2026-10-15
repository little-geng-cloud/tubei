"""子 Agent 基类。"""

from __future__ import annotations

from pathlib import Path

from tubai.services.llm import LLMClient

PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"


class BaseAgent:
    name: str = "base"
    prompt_file: str = ""

    def __init__(self, llm: LLMClient | None = None) -> None:
        self.llm = llm or LLMClient()

    def system_prompt(self) -> str:
        path = PROMPT_DIR / self.prompt_file
        if path.exists():
            return path.read_text(encoding="utf-8")
        return f"你是 {self.name} 子 Agent。"
