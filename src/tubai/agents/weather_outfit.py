"""🌤 天气 & 穿搭 Agent：按日生成穿搭方案。"""

from __future__ import annotations

from tubai.agents.base import BaseAgent
from tubai.models import DayOutfit, OutfitItem, TravelRequest
from tubai.services.weather import estimate_weather


class WeatherOutfitAgent(BaseAgent):
    name = "weather_outfit"
    prompt_file = "weather_outfit.md"

    def run(self, req: TravelRequest) -> list[DayOutfit]:
        month = req.start_date.month if req.start_date else 5
        results: list[DayOutfit] = []
        for day in range(1, req.days + 1):
            weather = estimate_weather(req.destination, day=day, start_month=month)
            outfit = self._build_outfit(req, weather, day)
            results.append(
                DayOutfit(day=day, weather_hint=weather["hint"], outfit=outfit)
            )
        return results

    def _build_outfit(self, req: TravelRequest, weather: dict, day: int) -> OutfitItem:
        special = weather.get("special") or ""
        rainy = weather.get("rainy") == "是"
        temp = weather.get("temp", "")
        cold = self._is_cold(temp)
        hot = self._is_hot(temp)
        need_modest = req.has_child_or_elderly or req.physical_limit

        if special == "海岛":
            top = "速干短袖 / 泳装上衣"
            bottom = "轻薄短裤 / 裙装 / 沙滩裤"
            outerwear = "防晒薄外套（空调房/晚间）"
            shoes = "防滑凉鞋 / 溯溪鞋"
            accessories = ["墨镜", "防晒帽", "高倍防晒霜", "防晒衣"]
            tip = "海岛高温暴晒，优先防晒与速干；下水后及时更换干衣。"
        elif special == "高原":
            top = "长袖速干衣 + 保暖中层（抓绒/薄羽绒）"
            bottom = "耐磨长裤（冲锋裤更佳）"
            outerwear = "防风防雨冲锋衣"
            shoes = "防滑登山鞋 / 徒步鞋"
            accessories = ["墨镜", "防晒帽", "高倍防晒霜", "保湿唇膏", "魔术头巾"]
            tip = "高原昼夜温差大且紫外线强，采用三层穿衣（排汗+保暖+防风）。"
        elif cold:
            top = "保暖内衣 + 毛衣/卫衣"
            bottom = "加绒长裤"
            outerwear = "羽绒服 / 厚大衣"
            shoes = "保暖防滑靴"
            accessories = ["围巾", "手套", "保温杯", "润肤霜"]
            tip = "气温偏低，注意防风保暖；室内外温差大，方便穿脱。"
        elif hot:
            top = "透气短袖 / 亚麻衬衫"
            bottom = "轻薄长裤 / 裙装"
            outerwear = "防晒薄外套（防晒+空调）"
            shoes = "透气运动鞋 / 凉鞋"
            accessories = ["墨镜", "遮阳帽", "防晒霜", "小风扇"]
            tip = "高温注意补水防暑，避免正午长时间暴晒。"
        else:
            top = "长袖衬衫 / 薄卫衣"
            bottom = "休闲长裤 / 牛仔裤"
            outerwear = "轻薄风衣 / 针织开衫"
            shoes = "舒适运动鞋"
            accessories = ["遮阳帽", "薄围巾"]
            tip = "气温舒适，叠穿方便应对早晚温差。"

        if rainy:
            accessories += ["折叠伞", "防水鞋套"]
            tip += " 同期多雨，防水与速干面料优先。"
        if req.self_drive:
            accessories.append("偏光驾驶镜")

        carry_on = [top, bottom, outerwear, shoes] + accessories[:3]
        packed = ["备用上衣", "备用下装", "换洗内衣袜", "睡衣"]
        if day >= 3:
            packed.append("备用鞋")
        if need_modest:
            tip += " 同行含老人/儿童或体力有限，优先舒适好走、易穿脱的衣物。"

        return OutfitItem(
            top=top,
            bottom=bottom,
            outerwear=outerwear,
            shoes=shoes,
            accessories=accessories,
            carry_on=carry_on,
            packed=packed,
            tip=tip,
        )

    @staticmethod
    def _is_cold(temp: str) -> bool:
        try:
            low = int(temp.split("~")[0])
            return low <= 8
        except (ValueError, IndexError):
            return False

    @staticmethod
    def _is_hot(temp: str) -> bool:
        try:
            high = int(temp.replace("°C", "").split("~")[1])
            return high >= 28
        except (ValueError, IndexError):
            return False
