"""途备 Agent 核心数据模型。"""

from __future__ import annotations

from datetime import date
from enum import StrEnum

from pydantic import BaseModel, Field


class TravelStyle(StrEnum):
    CITY = "城市逛吃"
    NATURE = "自然风光徒步"
    ISLAND = "海岛休闲"
    CULTURE = "人文古迹"


class BudgetLevel(StrEnum):
    ECONOMY = "经济型"
    COMFORT = "中端舒适"
    LUXURY = "轻奢"


class CompanionType(StrEnum):
    ADULT = "成人"
    ELDERLY = "老人"
    INFANT = "婴幼儿"


class Companion(BaseModel):
    type: CompanionType
    count: int = Field(ge=1)


class TravelRequest(BaseModel):
    """信息采集 Agent 的结构化输出。"""

    destination: str
    start_date: date | None = None
    end_date: date | None = None
    days: int = Field(ge=1, le=30)
    companions: list[Companion] = Field(default_factory=list)
    style: TravelStyle = TravelStyle.CITY
    budget: BudgetLevel = BudgetLevel.COMFORT
    physical_limit: bool = False
    diet_restrictions: list[str] = Field(default_factory=list)
    allergies: list[str] = Field(default_factory=list)
    self_drive: bool = False
    notes: str = ""

    @property
    def has_elderly(self) -> bool:
        return any(c.type == CompanionType.ELDERLY for c in self.companions)

    @property
    def has_infant(self) -> bool:
        return any(c.type == CompanionType.INFANT for c in self.companions)

    @property
    def has_child_or_elderly(self) -> bool:
        return self.has_elderly or self.has_infant

    @property
    def total_people(self) -> int:
        return sum(c.count for c in self.companions) or 1


class Spot(BaseModel):
    name: str
    duration: str = "2-3 小时"
    intro: str = ""
    reservation: str = ""
    closure_tip: str = ""


class Meal(BaseModel):
    name: str
    dish: str = ""
    tip: str = ""


class DayPlan(BaseModel):
    day: int
    theme: str = ""
    spots: list[Spot] = Field(default_factory=list)
    transport: str = ""
    meals: list[Meal] = Field(default_factory=list)
    pace_note: str = ""


class OutfitItem(BaseModel):
    top: str = ""
    bottom: str = ""
    outerwear: str = ""
    shoes: str = ""
    accessories: list[str] = Field(default_factory=list)
    carry_on: list[str] = Field(default_factory=list)
    packed: list[str] = Field(default_factory=list)
    tip: str = ""


class DayOutfit(BaseModel):
    day: int
    weather_hint: str = ""
    outfit: OutfitItem = Field(default_factory=OutfitItem)


class PackItem(BaseModel):
    name: str
    required: bool = True
    reason: str = ""


class PackCategory(BaseModel):
    category: str
    items: list[PackItem] = Field(default_factory=list)


class BudgetBreakdown(BaseModel):
    transport: str = ""
    lodging: str = ""
    tickets: str = ""
    meals: str = ""
    other: str = ""
    total: str = ""


class TravelPlan(BaseModel):
    """主 Agent 汇总后的完整方案。"""

    request: TravelRequest
    itinerary: list[DayPlan] = Field(default_factory=list)
    outfits: list[DayOutfit] = Field(default_factory=list)
    packing: list[PackCategory] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    tips: list[str] = Field(default_factory=list)
    budget: BudgetBreakdown = Field(default_factory=BudgetBreakdown)
    alternatives: list[str] = Field(default_factory=list)
