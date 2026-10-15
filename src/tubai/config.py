"""运行配置。"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """支持 OpenAI 兼容接口；无 key 时启用离线规则引擎。"""

    api_key: str = ""
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4o-mini"
    timeout: float = 60.0
    offline: bool = False

    @classmethod
    def from_env(cls) -> Settings:
        api_key = os.getenv("TUBAI_API_KEY") or os.getenv("OPENAI_API_KEY") or ""
        offline = (
            os.getenv("TUBAI_OFFLINE", "").lower() in {"1", "true", "yes"}
            or not api_key
        )
        return cls(
            api_key=api_key,
            base_url=os.getenv(
                "TUBAI_BASE_URL", os.getenv("OPENAI_BASE_URL", cls.base_url)
            ),
            model=os.getenv("TUBAI_MODEL", cls.model),
            timeout=float(os.getenv("TUBAI_TIMEOUT", cls.timeout)),
            offline=offline,
        )
