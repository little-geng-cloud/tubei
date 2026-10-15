"""📦 物资清单 Agent：分类打包清单 + 风险/避坑/预算。"""

from __future__ import annotations

from tubai.agents.base import BaseAgent
from tubai.models import (
    BudgetBreakdown,
    BudgetLevel,
    PackCategory,
    PackItem,
    TravelPlan,
    TravelRequest,
    TravelStyle,
)
from tubai.services.knowledge import get_destination
from tubai.services.weather import estimate_weather


class PackingAgent(BaseAgent):
    name = "packing"
    prompt_file = "packing.md"

    def run(self, req: TravelRequest) -> list[PackCategory]:
        month = req.start_date.month if req.start_date else 5
        weather = estimate_weather(req.destination, start_month=month)
        special = weather.get("special") or ""
        rainy = weather.get("rainy") == "是"

        categories: list[PackCategory] = [
            PackCategory(
                category="证件类",
                items=[
                    PackItem(name="身份证/护照", required=True),
                    PackItem(
                        name="学生证/老年证/优待证",
                        required=False,
                        reason="可享门票优惠",
                    ),
                    PackItem(name="电子行程单/酒店确认单", required=True),
                ],
            ),
            PackCategory(
                category="电子设备",
                items=[
                    PackItem(name="手机+充电器", required=True),
                    PackItem(name="充电宝（≤100Wh）", required=True),
                    PackItem(name="数据线/转换头", required=True),
                    PackItem(name="相机/运动相机", required=False, reason="记录旅途"),
                ],
            ),
            PackCategory(
                category="洗漱用品",
                items=[
                    PackItem(name="牙刷牙膏/旅行装洗漱", required=True),
                    PackItem(name="护肤基础套装", required=True),
                    PackItem(name="湿巾/免洗洗手液", required=True),
                    PackItem(name="剃须刀/化妆品", required=False, reason="按个人习惯"),
                ],
            ),
            PackCategory(
                category="药品",
                items=[
                    PackItem(name="感冒药/肠胃药", required=True),
                    PackItem(name="创可贴/消毒棉片", required=True),
                    PackItem(
                        name="个人常用药", required=True, reason="慢性病/处方药随身"
                    ),
                    PackItem(name="晕车药", required=False, reason="山路/船班备用"),
                ],
            ),
            PackCategory(
                category="衣物配件",
                items=[
                    PackItem(name="内衣袜（按天数+1）", required=True),
                    PackItem(name="睡衣", required=True),
                    PackItem(name="舒适步行鞋", required=True),
                    PackItem(
                        name="防晒帽/墨镜", required=False, reason="户外强光时必备"
                    ),
                ],
            ),
        ]

        # 场景专项
        if special == "高原" or req.style == TravelStyle.NATURE:
            categories.append(
                PackCategory(
                    category="专项物品（高原/徒步）",
                    items=[
                        PackItem(
                            name="高倍防晒霜（SPF50+）",
                            required=True,
                            reason="高原紫外线强",
                        ),
                        PackItem(
                            name="唇膏/保湿面霜", required=True, reason="干燥防裂"
                        ),
                        PackItem(name="便携氧气瓶", required=True, reason="缓解高反"),
                        PackItem(
                            name="红景天（提前服用）",
                            required=False,
                            reason="部分人有效",
                        ),
                        PackItem(
                            name="登山杖/护膝",
                            required=req.style == TravelStyle.NATURE,
                            reason="护膝保护关节",
                        ),
                        PackItem(
                            name="头灯/手电", required=False, reason="夜路/停电备用"
                        ),
                    ],
                )
            )
        if special == "海岛" or req.style == TravelStyle.ISLAND:
            categories.append(
                PackCategory(
                    category="专项物品（海边）",
                    items=[
                        PackItem(name="泳衣/泳镜", required=True),
                        PackItem(name="防水袋/手机防水套", required=True),
                        PackItem(name="速干浴巾", required=True),
                        PackItem(name="浮潜面镜", required=False, reason="自备更卫生"),
                        PackItem(name="防蚊液", required=True),
                    ],
                )
            )
        if rainy:
            categories.append(
                PackCategory(
                    category="雨天备用",
                    items=[
                        PackItem(name="折叠伞/雨衣", required=True, reason="同期多雨"),
                        PackItem(name="防水鞋套", required=False),
                        PackItem(name="速干替换衣物", required=True),
                    ],
                )
            )
        if req.has_elderly:
            categories.append(
                PackCategory(
                    category="长辈关怀",
                    items=[
                        PackItem(name="常用药+药盒分装", required=True),
                        PackItem(name="轻便折叠凳/拐杖", required=False),
                        PackItem(name="保温杯", required=True),
                        PackItem(name="宽松防滑鞋", required=True),
                    ],
                )
            )
        if req.has_infant:
            categories.append(
                PackCategory(
                    category="婴幼儿专项",
                    items=[
                        PackItem(name="尿不湿/湿巾", required=True),
                        PackItem(name="奶粉/辅食/餐具", required=True),
                        PackItem(name="儿童常备药", required=True),
                        PackItem(name="轻便推车/腰凳", required=False),
                        PackItem(name="换洗衣物（多备）", required=True),
                    ],
                )
            )
        return categories

    def risks_and_tips(
        self, req: TravelRequest
    ) -> tuple[list[str], list[str], list[str]]:
        dest = get_destination(req.destination, req.style.value)
        month = req.start_date.month if req.start_date else 5
        weather = estimate_weather(req.destination, start_month=month)

        risks = list(dest.risks)
        if weather.get("rainy") == "是":
            risks.append("出行同期降雨概率较高，备好雨具并关注道路/船班信息")
        if weather.get("special") == "高原":
            risks.append("高海拔地区注意高反，首日勿洗澡洗头、勿剧烈运动")
        if weather.get("special") == "海岛":
            risks.append("海上项目关注风浪预警，下水务必穿救生衣")
        if req.has_elderly:
            risks.append("老人同行：避免长时间暴晒与连续爬坡，每日步行控制在合理范围")
        if req.has_infant:
            risks.append("婴幼儿同行：注意防晒防蚊与作息，景点选择室内+户外结合")

        tips = list(dest.anti_pitfalls)
        tips.append("热门景点尽量开门即入园，避开 10:00-14:00 高峰")
        tips.append("消费前确认计价方式（按份/按只/按克），索要小票")

        alternatives = list(dest.alternatives)
        return risks, tips, alternatives

    def budget(self, req: TravelRequest) -> BudgetBreakdown:
        people = req.total_people
        days = req.days
        unit = {
            BudgetLevel.ECONOMY: 400,
            BudgetLevel.COMFORT: 800,
            BudgetLevel.LUXURY: 1600,
        }[req.budget]
        # 人均每日粗算
        meals = int(unit * 0.25 * people * days)
        lodging = int(unit * 0.35 * people * days)
        tickets = int(unit * 0.15 * people * days)
        transport = int(unit * 0.2 * people * days)
        other = int(unit * 0.05 * people * days)
        total = meals + lodging + tickets + transport + other
        fmt = lambda n: f"约 ¥{n:,}"
        return BudgetBreakdown(
            transport=fmt(transport),
            lodging=fmt(lodging),
            tickets=fmt(tickets),
            meals=fmt(meals),
            other=fmt(other),
            total=fmt(total),
        )

    def enrich_plan(self, plan: TravelPlan) -> TravelPlan:
        risks, tips, alternatives = self.risks_and_tips(plan.request)
        plan.risks = risks
        plan.tips = tips
        plan.alternatives = alternatives
        plan.budget = self.budget(plan.request)
        return plan
