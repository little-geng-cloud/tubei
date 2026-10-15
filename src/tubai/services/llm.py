"""LLM 客户端：OpenAI 兼容 Chat Completions + 离线规则引擎。"""

from __future__ import annotations

import json
import re
from typing import Any

import httpx

from tubai.config import Settings


class LLMClient:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings.from_env()

    @property
    def offline(self) -> bool:
        return self.settings.offline

    def chat(self, system: str, user: str, *, temperature: float = 0.4) -> str:
        if self.offline:
            return self._offline_reply(system, user)

        payload = {
            "model": self.settings.model,
            "temperature": temperature,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        headers = {"Authorization": f"Bearer {self.settings.api_key}"}
        resp = httpx.post(
            f"{self.settings.base_url.rstrip('/')}/chat/completions",
            json=payload,
            headers=headers,
            timeout=self.settings.timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    def chat_json(
        self, system: str, user: str, *, temperature: float = 0.2
    ) -> dict[str, Any]:
        raw = self.chat(
            system + "\n\n请只输出合法 JSON，不要输出其他内容。",
            user,
            temperature=temperature,
        )
        return extract_json(raw)

    def _offline_reply(self, system: str, user: str) -> str:
        """无 API key 时的确定性占位回复，保证流水线可跑通。"""
        if "JSON" in system or "json" in system:
            return json.dumps(
                {
                    "note": "offline-mode-placeholder",
                    "echo_keywords": _keywords(user),
                },
                ensure_ascii=False,
            )
        return (
            "【离线模式】未配置 TUBAI_API_KEY / OPENAI_API_KEY，"
            "当前为规则引擎占位输出。配置 API Key 后可获得完整智能规划。"
        )


def extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.DOTALL)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            raise ValueError(f"无法解析 JSON: {text[:200]}") from None
        return json.loads(match.group(0))


def _keywords(text: str, limit: int = 12) -> list[str]:
    tokens = re.findall(r"[\w\u4e00-\u9fff]{2,}", text)
    seen: list[str] = []
    for t in tokens:
        if t not in seen:
            seen.append(t)
        if len(seen) >= limit:
            break
    return seen
