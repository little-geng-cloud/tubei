"""目的地气候参考（历史同期，非实时预报）。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ClimateProfile:
    city: str
    month_temp: dict[int, tuple[int, int]]  # month -> (low, high) °C
    notes: str
    rainy_months: set[int]
    special: str = ""  # 高原 / 海岛 / 干热 等标签


# 覆盖常见目的地的粗粒度气候画像，用于穿搭/打包的规则推断
CLIMATE_DB: list[ClimateProfile] = [
    ClimateProfile(
        city="北京",
        month_temp={
            1: (-8, 2),
            2: (-5, 5),
            3: (1, 13),
            4: (8, 21),
            5: (14, 27),
            6: (19, 31),
            7: (22, 32),
            8: (21, 30),
            9: (15, 26),
            10: (7, 19),
            11: (-1, 10),
            12: (-7, 3),
        },
        notes="四季分明，春秋短，冬冷夏热",
        rainy_months={7, 8},
    ),
    ClimateProfile(
        city="上海",
        month_temp={
            1: (1, 8),
            2: (2, 10),
            3: (6, 14),
            4: (11, 20),
            5: (16, 25),
            6: (21, 28),
            7: (25, 33),
            8: (25, 33),
            9: (21, 29),
            10: (15, 23),
            11: (9, 17),
            12: (3, 11),
        },
        notes="湿润，梅雨季闷热，夏季闷热多雨",
        rainy_months={6, 7, 8, 9},
    ),
    ClimateProfile(
        city="成都",
        month_temp={
            1: (3, 10),
            2: (5, 12),
            3: (9, 17),
            4: (14, 23),
            5: (18, 27),
            6: (21, 29),
            7: (23, 31),
            8: (22, 31),
            9: (19, 26),
            10: (14, 21),
            11: (9, 16),
            12: (4, 11),
        },
        notes="湿润多云，冬季湿冷",
        rainy_months={7, 8, 9},
    ),
    ClimateProfile(
        city="昆明",
        month_temp={
            1: (2, 15),
            2: (4, 17),
            3: (7, 21),
            4: (11, 24),
            5: (14, 25),
            6: (17, 25),
            7: (17, 25),
            8: (17, 25),
            9: (15, 24),
            10: (12, 21),
            11: (7, 17),
            12: (3, 14),
        },
        notes="四季如春，紫外线强",
        rainy_months={6, 7, 8, 9},
        special="高原",
    ),
    ClimateProfile(
        city="丽江",
        month_temp={
            1: (0, 15),
            2: (2, 17),
            3: (5, 20),
            4: (9, 23),
            5: (13, 25),
            6: (16, 25),
            7: (16, 24),
            8: (15, 24),
            9: (13, 23),
            10: (9, 20),
            11: (4, 16),
            12: (0, 13),
        },
        notes="高原气候，昼夜温差大，紫外线强",
        rainy_months={7, 8, 9},
        special="高原",
    ),
    ClimateProfile(
        city="拉萨",
        month_temp={
            1: (-10, 8),
            2: (-7, 10),
            3: (-2, 14),
            4: (1, 17),
            5: (5, 21),
            6: (9, 24),
            7: (10, 24),
            8: (9, 23),
            9: (6, 21),
            10: (0, 16),
            11: (-7, 11),
            12: (-10, 8),
        },
        notes="高海拔强紫外线，昼夜温差极大，干燥",
        rainy_months={7, 8, 9},
        special="高原",
    ),
    ClimateProfile(
        city="三亚",
        month_temp={
            1: (18, 26),
            2: (19, 27),
            3: (21, 29),
            4: (24, 31),
            5: (26, 32),
            6: (26, 32),
            7: (26, 32),
            8: (26, 32),
            9: (25, 31),
            10: (23, 30),
            11: (21, 28),
            12: (19, 26),
        },
        notes="热带海洋性气候，全年高温，夏秋台风",
        rainy_months={8, 9, 10},
        special="海岛",
    ),
    ClimateProfile(
        city="厦门",
        month_temp={
            1: (10, 17),
            2: (10, 18),
            3: (12, 20),
            4: (16, 24),
            5: (20, 27),
            6: (23, 29),
            7: (25, 32),
            8: (25, 32),
            9: (24, 30),
            10: (20, 27),
            11: (16, 23),
            12: (11, 18),
        },
        notes="海洋性气候，夏热冬暖",
        rainy_months={5, 6},
        special="海岛",
    ),
    ClimateProfile(
        city="杭州",
        month_temp={
            1: (1, 8),
            2: (3, 11),
            3: (7, 16),
            4: (12, 22),
            5: (17, 27),
            6: (21, 29),
            7: (25, 34),
            8: (25, 33),
            9: (20, 29),
            10: (14, 23),
            11: (8, 17),
            12: (2, 11),
        },
        notes="梅雨闷热，夏季高温",
        rainy_months={6, 7},
    ),
    ClimateProfile(
        city="西安",
        month_temp={
            1: (-5, 5),
            2: (-2, 9),
            3: (4, 15),
            4: (10, 22),
            5: (15, 27),
            6: (20, 32),
            7: (22, 33),
            8: (21, 31),
            9: (15, 25),
            10: (8, 19),
            11: (2, 12),
            12: (-4, 6),
        },
        notes="干燥，冬冷夏热，春秋适合出行",
        rainy_months={8, 9},
    ),
    ClimateProfile(
        city="桂林",
        month_temp={
            1: (5, 12),
            2: (7, 14),
            3: (11, 18),
            4: (16, 24),
            5: (20, 28),
            6: (23, 30),
            7: (25, 33),
            8: (25, 33),
            9: (22, 30),
            10: (17, 25),
            11: (12, 20),
            12: (7, 15),
        },
        notes="湿润多雨，夏热",
        rainy_months={4, 5, 6},
    ),
    ClimateProfile(
        city="青岛",
        month_temp={
            1: (-3, 4),
            2: (-1, 6),
            3: (3, 11),
            4: (8, 17),
            5: (13, 22),
            6: (18, 26),
            7: (22, 28),
            8: (22, 28),
            9: (18, 25),
            10: (12, 19),
            11: (5, 12),
            12: (-1, 6),
        },
        notes="海滨城市，夏季凉爽多雾，多风",
        rainy_months={7, 8},
        special="海岛",
    ),
]


def find_climate(destination: str) -> ClimateProfile | None:
    for p in CLIMATE_DB:
        if p.city in destination or destination in p.city:
            return p
    # 关键词回退
    keyword_map = {
        "高原": "拉萨",
        "拉萨": "拉萨",
        "丽江": "丽江",
        "香格里拉": "丽江",
        "海南": "三亚",
        "三亚": "三亚",
        "海岛": "三亚",
        "大理": "昆明",
        "鼓浪屿": "厦门",
        "西湖": "杭州",
        "兵马俑": "西安",
        "漓江": "桂林",
    }
    for kw, city in keyword_map.items():
        if kw in destination:
            for p in CLIMATE_DB:
                if p.city == city:
                    return p
    return None


def estimate_weather(
    destination: str, day: int = 1, start_month: int | None = None
) -> dict[str, str]:
    """返回天气提示与温度区间（历史同期参考）。"""
    profile = find_climate(destination)
    month = start_month or 5
    if profile is None:
        return {
            "temp": "温和（参考）",
            "hint": "未收录该目的地精确气候，按季节通用穿搭，出行前请核对实时天气",
            "special": "",
        }
    low, high = profile.month_temp.get(month, profile.month_temp.get(5, (15, 25)))
    # 简单日间波动，保证每日提示略有差异
    swing = (day - 1) % 3 - 1
    rainy = month in profile.rainy_months
    hint_parts = [f"参考气温 {low + swing}~{high + swing}°C"]
    if rainy:
        hint_parts.append("同期多雨概率较高")
    if profile.special:
        hint_parts.append(profile.special)
    hint_parts.append(profile.notes)
    return {
        "temp": f"{low + swing}~{high + swing}°C",
        "hint": "，".join(hint_parts),
        "special": profile.special,
        "rainy": "是" if rainy else "否",
    }
