"""主 Agent：途备 Agent 统筹调度 4 个子 Agent。"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from tubai.agents.collector import WELCOME, CollectorAgent
from tubai.agents.itinerary import ItineraryAgent
from tubai.agents.packing import PackingAgent
from tubai.agents.weather_outfit import WeatherOutfitAgent
from tubai.models import TravelPlan, TravelRequest
from tubai.services.exporter import export_markdown
from tubai.services.llm import LLMClient


class TubaiOrchestrator:
    """Kiro Crew 风格编排：采集 → 并行子 Agent → 汇总导出。"""

    def __init__(self, llm: LLMClient | None = None) -> None:
        self.llm = llm or LLMClient()
        self.collector = CollectorAgent(self.llm)
        self.weather_outfit = WeatherOutfitAgent(self.llm)
        self.itinerary = ItineraryAgent(self.llm)
        self.packing = PackingAgent(self.llm)

    @property
    def welcome(self) -> str:
        return WELCOME

    def parse_input(
        self, text: str
    ) -> tuple[TravelRequest | None, list[str], str | None]:
        """解析用户输入。返回 (请求, 缺失字段, 追问文案)。"""
        req, missing = self.collector.parse(text)
        if req is not None:
            return req, [], None
        return None, missing, self.collector.follow_up(missing)

    def generate(self, req: TravelRequest) -> TravelPlan:
        """并行生成行程、穿搭，再由物资清单 Agent 补充风险与预算。"""
        with ThreadPoolExecutor(max_workers=3) as pool:
            f_itin = pool.submit(self.itinerary.run, req)
            f_outfit = pool.submit(self.weather_outfit.run, req)
            f_pack = pool.submit(self.packing.run, req)
            itinerary = f_itin.result()
            outfits = f_outfit.result()
            packing = f_pack.result()

        plan = TravelPlan(
            request=req,
            itinerary=itinerary,
            outfits=outfits,
            packing=packing,
        )
        return self.packing.enrich_plan(plan)

    def regenerate(self, plan: TravelPlan, **changes) -> TravelPlan:
        """根据变更字段动态重新生成整套方案。"""
        data = plan.request.model_dump()
        data.update(changes)
        new_req = TravelRequest(**data)
        return self.generate(new_req)

    def export(self, plan: TravelPlan) -> str:
        return export_markdown(plan)

    def run_text(self, user_text: str) -> str:
        """端到端：输入自然语言 → Markdown 方案或追问。"""
        req, _missing, follow_up = self.parse_input(user_text)
        if req is None:
            return follow_up or "信息还不完整，请补充目的地与出行天数。"
        plan = self.generate(req)
        return self.export(plan)
