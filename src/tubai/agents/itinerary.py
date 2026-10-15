"""🗺 行程编排 Agent：生成每日游玩路线、交通、美食与节奏。"""

from __future__ import annotations

from tubai.agents.base import BaseAgent
from tubai.models import DayPlan, Meal, Spot, TravelRequest, TravelStyle
from tubai.services.knowledge import get_destination


class ItineraryAgent(BaseAgent):
    name = "itinerary"
    prompt_file = "itinerary.md"

    def run(self, req: TravelRequest) -> list[DayPlan]:
        dest = get_destination(req.destination, req.style.value)
        spots = list(dest.spots)
        foods = list(dest.foods)
        days: list[DayPlan] = []

        for day in range(1, req.days + 1):
            day_spots = self._pick_spots(spots, day, req)
            day_foods = self._pick_foods(foods, day)
            theme = self._theme(req, day, day_spots)
            pace = self._pace_note(req, day_spots)

            days.append(
                DayPlan(
                    day=day,
                    theme=theme,
                    spots=day_spots,
                    transport=self._transport(req, dest.transport, day_spots),
                    meals=day_foods,
                    pace_note=pace,
                )
            )
        return days

    def _pick_spots(self, spots: list[str], day: int, req: TravelRequest) -> list[Spot]:
        max_spots = 2 if (req.has_child_or_elderly or req.physical_limit) else 3
        if day == 1:
            max_spots = min(max_spots, 2)  # 抵达日轻松
        if day == req.days:
            max_spots = min(max_spots, 2)  # 返程日轻松

        start = (day - 1) * max_spots
        picked = [spots[(start + i) % len(spots)] for i in range(max_spots)]

        result: list[Spot] = []
        for i, name in enumerate(picked):
            is_major = i == 0
            result.append(
                Spot(
                    name=name,
                    duration="3-4 小时" if is_major else "1.5-2.5 小时",
                    intro=f"{req.destination}代表性的{'核心' if is_major else '轻松'}景点，适合当天主题安排。",
                    reservation="建议提前 3-7 天预约/购票"
                    if is_major
                    else "可现场或提前一日购票",
                    closure_tip="出发前核对开放时间与闭馆日" if is_major else "",
                )
            )
        return result

    def _pick_foods(self, foods: list[str], day: int) -> list[Meal]:
        n = min(3, len(foods))
        picked = [foods[(day - 1 + i) % len(foods)] for i in range(n)]
        meals = ["午餐", "晚餐", "下午茶"]
        return [
            Meal(
                name=meals[i] if i < len(meals) else "加餐",
                dish=p,
                tip="本地口碑店优先" if i == 0 else "",
            )
            for i, p in enumerate(picked)
        ]

    def _theme(self, req: TravelRequest, day: int, spots: list[Spot]) -> str:
        if day == 1:
            return "抵达适应 · 轻松初探"
        if day == req.days:
            return "收尾购物 · 返程准备"
        style_theme = {
            TravelStyle.CITY: "城市漫游 · 美食打卡",
            TravelStyle.NATURE: "自然徒步 · 风光摄影",
            TravelStyle.ISLAND: "海岛休闲 · 海边放松",
            TravelStyle.CULTURE: "人文探秘 · 历史巡礼",
        }
        base = style_theme.get(req.style, "主题游玩")
        if spots:
            return f"{base}｜{spots[0].name}"
        return base

    def _transport(self, req: TravelRequest, default: str, spots: list[Spot]) -> str:
        if req.self_drive:
            return "自驾前往景点，注意停车与限行；山区/景区道路谨慎驾驶。"
        if req.has_child_or_elderly:
            return "优先打车/网约车点对点，减少换乘与步行距离。" + (
                f" 参考：{default}" if default else ""
            )
        return default or "市内地铁/公交+步行，远景点打车。"

    def _pace_note(self, req: TravelRequest, spots: list[Spot]) -> str:
        if req.has_child_or_elderly or req.physical_limit:
            return f"今日安排 {len(spots)} 个点位，节奏放缓，预留休息，避免长时间步行。"
        if len(spots) >= 3:
            return f"今日安排 {len(spots)} 个点位，适中偏充实，注意补水与正午休息。"
        return f"今日安排 {len(spots)} 个点位，节奏宽松，可自由加逛。"
