"""途备 Agent 单元测试。"""

from __future__ import annotations

from datetime import date

import pytest

from tubai.agents.collector import CollectorAgent
from tubai.agents.itinerary import ItineraryAgent
from tubai.agents.packing import PackingAgent
from tubai.agents.weather_outfit import WeatherOutfitAgent
from tubai.models import (
    BudgetLevel,
    Companion,
    CompanionType,
    TravelRequest,
    TravelStyle,
)
from tubai.orchestrator import TubaiOrchestrator
from tubai.services.exporter import export_markdown


@pytest.fixture
def collector() -> CollectorAgent:
    return CollectorAgent()


@pytest.fixture
def sample_req() -> TravelRequest:
    return TravelRequest(
        destination="成都",
        start_date=date(2026, 5, 1),
        end_date=date(2026, 5, 3),
        days=3,
        companions=[Companion(type=CompanionType.ADULT, count=2)],
        style=TravelStyle.CITY,
        budget=BudgetLevel.COMFORT,
    )


def test_collector_parses_one_shot(collector: CollectorAgent) -> None:
    req, missing = collector.parse("单人去成都玩 2 天，城市逛吃，经济型预算，5 月出发")
    assert req is not None
    assert not missing
    assert req.destination == "成都"
    assert req.days == 2
    assert req.style == TravelStyle.CITY
    assert req.budget == BudgetLevel.ECONOMY


def test_collector_asks_when_missing(collector: CollectorAgent) -> None:
    req, missing = collector.parse("我想出去玩")
    assert req is None
    assert "destination" in missing
    follow = collector.follow_up(missing)
    assert "目的地" in follow


def test_itinerary_days_and_pace(sample_req: TravelRequest) -> None:
    plans = ItineraryAgent().run(sample_req)
    assert len(plans) == 3
    assert plans[0].spots
    family = sample_req.model_copy(
        update={
            "companions": [
                Companion(type=CompanionType.ADULT, count=2),
                Companion(type=CompanionType.ELDERLY, count=1),
                Companion(type=CompanionType.INFANT, count=1),
            ],
            "physical_limit": True,
        }
    )
    family_plans = ItineraryAgent().run(family)
    assert "放缓" in family_plans[1].pace_note or "休息" in family_plans[1].pace_note


def test_weather_outfit_island() -> None:
    req = TravelRequest(
        destination="三亚",
        days=2,
        companions=[Companion(type=CompanionType.ADULT, count=2)],
        style=TravelStyle.ISLAND,
        budget=BudgetLevel.LUXURY,
    )
    outfits = WeatherOutfitAgent().run(req)
    assert len(outfits) == 2
    text = (
        outfits[0].outfit.top
        + outfits[0].outfit.shoes
        + "".join(outfits[0].outfit.accessories)
    )
    assert any(k in text for k in ("防晒", "短袖", "凉鞋", "泳"))


def test_packing_special_items() -> None:
    req = TravelRequest(
        destination="丽江",
        days=3,
        companions=[Companion(type=CompanionType.ADULT, count=2)],
        style=TravelStyle.NATURE,
        budget=BudgetLevel.COMFORT,
    )
    packing = PackingAgent().run(req)
    names = [i.name for c in packing for i in c.items]
    assert any("氧气" in n or "防晒" in n for n in names)


def test_export_markdown_structure(sample_req: TravelRequest) -> None:
    orch = TubaiOrchestrator()
    plan = orch.generate(sample_req)
    md = export_markdown(plan)
    for section in [
        "# 【途备Agent旅行方案】",
        "## 基础出行信息",
        "## 一、每日行程规划",
        "## 二、每日穿搭推荐",
        "## 三、出行打包清单",
        "## 四、出行提示",
        "## 五、预算预估",
    ]:
        assert section in md


def test_regenerate_updates_days(sample_req: TravelRequest) -> None:
    orch = TubaiOrchestrator()
    plan = orch.generate(sample_req)
    new_plan = orch.regenerate(plan, days=5)
    assert new_plan.request.days == 5
    assert len(new_plan.itinerary) == 5
    assert len(new_plan.outfits) == 5
