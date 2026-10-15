"""🧩 信息采集 Agent：多轮对话收集出行参数，校验完整性。"""

from __future__ import annotations

import re
from datetime import date, timedelta

from pydantic import ValidationError

from tubai.agents.base import BaseAgent
from tubai.models import (
    BudgetLevel,
    Companion,
    CompanionType,
    TravelRequest,
    TravelStyle,
)

WELCOME = (
    "你好，我是途备 Agent，你的智能旅行规划助手。\n"
    "告诉我你的目的地、出行天数、同行人员和游玩偏好，"
    "我将为你生成全套行程、每日穿搭和出行打包清单。\n\n"
    "你可以一次性说清楚，例如：\n"
    "「5 月中旬去成都玩 3 天，两大一小，喜欢逛吃，中端预算」"
)

FIELD_ORDER = [
    "destination",
    "days",
    "companions",
    "style",
    "budget",
    "constraints",
]


class CollectorAgent(BaseAgent):
    name = "collector"
    prompt_file = "collector.md"

    def parse(self, text: str) -> tuple[TravelRequest | None, list[str]]:
        """从自然语言解析出行参数。返回 (部分/完整请求, 待补齐字段)。"""
        data: dict = {}

        dest = self._extract_destination(text)
        if dest:
            data["destination"] = dest

        days = self._extract_days(text)
        if days:
            data["days"] = days

        start, end = self._extract_dates(text, days)
        if start:
            data["start_date"] = start
        if end:
            data["end_date"] = end

        companions = self._extract_companions(text)
        if companions:
            data["companions"] = companions

        style = self._extract_style(text)
        if style:
            data["style"] = style

        budget = self._extract_budget(text)
        if budget:
            data["budget"] = budget

        constraints = self._extract_constraints(text)
        data.update(constraints)

        missing = self._missing_fields(data)
        if missing:
            return None, missing

        # 补默认值以便通过校验
        data.setdefault("days", 3)
        data.setdefault("start_date", date.today() + timedelta(days=14))
        if data.get("start_date") and "end_date" not in data:
            data["end_date"] = data["start_date"] + timedelta(days=data["days"] - 1)
        if data["end_date"] and "start_date" not in data:
            data["start_date"] = data["end_date"] - timedelta(days=data["days"] - 1)
        try:
            return TravelRequest(**data), []
        except ValidationError:
            return None, self._missing_fields(data)

    def follow_up(self, missing: list[str]) -> str:
        questions = {
            "destination": "请问目的地是哪里？（城市或景区都可以）",
            "days": "计划出行几天呢？",
            "companions": "同行人员情况？（例如：2 成人 / 1 老人 1 儿童）",
            "style": "更偏好哪种玩法？城市逛吃 / 自然风光徒步 / 海岛休闲 / 人文古迹",
            "budget": "预算档位：经济型 / 中端舒适 / 轻奢？",
            "constraints": "有体力限制、饮食禁忌、过敏或需要自驾吗？没有可回复「无」",
        }
        parts = [questions[m] for m in missing if m in questions]
        if not parts:
            return "还差一点信息，可以补充一下出行日期或备注吗？"
        return "为了给你更准确的方案，还需要确认：\n" + "\n".join(
            f"{i}. {p}" for i, p in enumerate(parts, 1)
        )

    def missing(self, text: str) -> list[str]:
        _, missing = self.parse(text)
        return missing

    # ---- 抽取器 ----

    def _extract_destination(self, text: str) -> str | None:
        from tubai.services.knowledge import DESTINATIONS

        # 1) 优先匹配已知城市，最稳
        for d in DESTINATIONS:
            if d.city in text:
                return d.city

        stopwords = {
            "今天",
            "明天",
            "后天",
            "几天",
            "多少",
            "怎么",
            "什么",
            "我们",
            "自己",
            "预算",
            "穿搭",
            "行李",
            "清单",
            "行程",
            "规划",
            "帮我",
            "一下",
            "出去",
            "我想",
            "准备",
            "打算",
            "请问",
            "可以",
            "需要",
            "一个",
            "两人",
            "单人",
            "城市",
            "自然",
            "风光",
            "海岛",
            "休闲",
            "人文",
            "古迹",
            "徒步",
            "逛吃",
        }
        patterns = [
            r"(?:去|到|前往|目的地是?|想去)\s*([\u4e00-\u9fff]{2,10}?)(?:市|省|县|镇|区)?(?=[\s，。,.]?|$|\d|天|日|玩|旅|游|出发|和|跟|与|，)",
            r"([\u4e00-\u9fff]{2,8}?)(?:出发|旅游|旅行|游玩|度假)",
        ]
        for pat in patterns:
            m = re.search(pat, text)
            if not m:
                continue
            cand = m.group(1).strip("的了啊呢吧玩游旅")
            cand = re.sub(r"(玩|去|到|旅游|旅行|游玩|度假)$", "", cand)
            if (
                cand
                and cand not in stopwords
                and len(cand) >= 2
                and not re.fullmatch(r"\d+", cand)
            ):
                return cand
        return None

    def _extract_days(self, text: str) -> int | None:
        m = re.search(r"(\d{1,2})\s*(?:天|日)", text)
        if m:
            return max(1, min(30, int(m.group(1))))
        m = re.search(r"(?:半|一|两|二|三|四|五|六|七|八|九|十)\s*天", text)
        if m:
            cn = {
                "半": 1,
                "一": 1,
                "两": 2,
                "二": 2,
                "三": 3,
                "四": 4,
                "五": 5,
                "六": 6,
                "七": 7,
                "八": 8,
                "九": 9,
                "十": 10,
            }
            for k, v in cn.items():
                if m.group(0).startswith(k):
                    return v
        return None

    def _extract_dates(
        self, text: str, days: int | None
    ) -> tuple[date | None, date | None]:
        today = date.today()
        m = re.search(r"(\d{1,2})\s*月\s*(\d{1,2})\s*日?", text)
        if m:
            month, day = int(m.group(1)), int(m.group(2))
            year = today.year
            try:
                start = date(year, month, day)
            except ValueError:
                return None, None
            if start < today:
                try:
                    start = date(year + 1, month, day)
                except ValueError:
                    return None, None
            end = start + timedelta(days=(days or 3) - 1)
            return start, end
        # 仅月份：取该月 1 号（若已过则次年）
        m = re.search(r"(\d{1,2})\s*月", text)
        if m:
            month = int(m.group(1))
            if 1 <= month <= 12:
                year = today.year
                try:
                    start = date(year, month, 1)
                except ValueError:
                    return None, None
                if start < today:
                    start = date(year + 1, month, 1)
                end = start + timedelta(days=(days or 3) - 1)
                return start, end
        m = re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})", text)
        if m:
            start = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            end = start + timedelta(days=(days or 3) - 1)
            return start, end
        return None, None

    def _extract_companions(self, text: str) -> list[Companion]:
        result: list[Companion] = []
        cn_num = {
            "一": 1, "两": 2, "二": 2, "三": 3, "四": 4, "五": 5,
            "六": 6, "七": 7, "八": 8, "九": 9, "十": 10,
        }

        def parse_count(pattern: str) -> int | None:
            m = re.search(pattern, text)
            if not m:
                return None
            raw = m.group(1)
            return int(raw) if raw.isdigit() else cn_num.get(raw)

        # 口语：两大一小 / 两大两小 / 三老一小
        for m in re.finditer(r"([一两二三四五六七八九十\d]+)(大|小|老)", text):
            raw, kind = m.group(1), m.group(2)
            n = int(raw) if raw.isdigit() else cn_num.get(raw, 0)
            if n <= 0:
                continue
            if kind == "大":
                result.append(Companion(type=CompanionType.ADULT, count=n))
            elif kind == "小":
                result.append(Companion(type=CompanionType.INFANT, count=n))
            else:
                result.append(Companion(type=CompanionType.ELDERLY, count=n))

        adult_count = parse_count(r"(\d+|[一两二三四五六七八九十])\s*(?:个|位)?(?:成人|大人|成年人|情侣|人)")
        if "情侣" in text and adult_count is None and not any(
            c.type == CompanionType.ADULT for c in result
        ):
            result.append(Companion(type=CompanionType.ADULT, count=2))
        elif adult_count and not any(c.type == CompanionType.ADULT for c in result):
            result.append(Companion(type=CompanionType.ADULT, count=adult_count))
        elif re.search(r"单人|一个人|独自|自己一人", text) and not result:
            result.append(Companion(type=CompanionType.ADULT, count=1))

        elder_count = parse_count(r"(\d+|[一两二三四五六七八九十])\s*(?:个|位)?(?:老人|长辈|爸妈|父母|老年人)")
        if elder_count and not any(c.type == CompanionType.ELDERLY for c in result):
            result.append(Companion(type=CompanionType.ELDERLY, count=elder_count))
        elif re.search(r"带老人|老人小孩|老人孩子|亲子|家庭", text) and not any(
            c.type == CompanionType.ELDERLY for c in result
        ):
            result.append(Companion(type=CompanionType.ELDERLY, count=1))

        infant_count = parse_count(
            r"(\d+|[一两二三四五六七八九十])\s*(?:个|位)?(?:婴幼儿|宝宝|婴儿|小孩|儿童|孩子)"
        )
        if infant_count and not any(c.type == CompanionType.INFANT for c in result):
            result.append(Companion(type=CompanionType.INFANT, count=infant_count))
        elif re.search(r"带孩子|亲子|家庭|小孩", text) and not any(
            c.type == CompanionType.INFANT for c in result
        ):
            result.append(Companion(type=CompanionType.INFANT, count=1))
        return result

    def _extract_style(self, text: str) -> TravelStyle | None:
        mapping = [
            (("海岛", "海边", "沙滩", "度假", "潜水"), TravelStyle.ISLAND),
            (("徒步", "自然", "登山", "山野", "户外", "风光"), TravelStyle.NATURE),
            (("人文", "古迹", "历史", "博物馆", "古建筑", "文化"), TravelStyle.CULTURE),
            (("逛吃", "美食", "城市", "都市", "逛街", "打卡"), TravelStyle.CITY),
        ]
        for keys, style in mapping:
            if any(k in text for k in keys):
                return style
        return None

    def _extract_budget(self, text: str) -> BudgetLevel | None:
        if any(k in text for k in ("轻奢", "豪华", "高端", "奢侈")):
            return BudgetLevel.LUXURY
        if any(k in text for k in ("经济", "穷游", "便宜", "节省")):
            return BudgetLevel.ECONOMY
        if any(k in text for k in ("舒适", "中端", "中档", "适中", "一般")):
            return BudgetLevel.COMFORT
        return None

    def _extract_constraints(self, text: str) -> dict:
        out: dict = {
            "physical_limit": bool(
                re.search(r"体力有限|腿脚|不要太累|轻松|慢节奏|有老人小孩|轮椅", text)
            ),
            "self_drive": bool(re.search(r"自驾|开车|租车自驾", text)),
            "diet_restrictions": [],
            "allergies": [],
        }
        if re.search(r"不吃辣|忌辣|清淡", text):
            out["diet_restrictions"].append("清淡/不吃辣")
        if re.search(r"素食|吃素", text):
            out["diet_restrictions"].append("素食")
        if re.search(r"清真|回族|不吃猪肉", text):
            out["diet_restrictions"].append("清真")
        for a in ("海鲜", "花生", "芒果", "牛奶", "鸡蛋", "花粉"):
            if a in text:
                out["allergies"].append(a)
        return out

    def _missing_fields(self, data: dict) -> list[str]:
        missing = []
        if not data.get("destination"):
            missing.append("destination")
        if not data.get("days"):
            missing.append("days")
        if not data.get("companions"):
            missing.append("companions")
        if not data.get("style"):
            missing.append("style")
        if not data.get("budget"):
            missing.append("budget")
        # constraints 可选，不强制
        return missing
