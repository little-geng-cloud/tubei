"""Markdown 方案导出。"""

from __future__ import annotations

from tubai.models import TravelPlan


def export_markdown(plan: TravelPlan) -> str:
    req = plan.request
    lines: list[str] = []
    lines.append("# 【途备Agent旅行方案】")
    lines.append("")
    lines.append("## 基础出行信息")
    lines.append("")
    lines.append(f"- **目的地**：{req.destination}")
    if req.start_date and req.end_date:
        lines.append(f"- **出行时间**：{req.start_date} ~ {req.end_date}")
    lines.append(f"- **天数**：{req.days} 天")
    companions = (
        "、".join(f"{c.type.value}×{c.count}" for c in req.companions) or "未填写"
    )
    lines.append(f"- **同行人员**：{companions}（共约 {req.total_people} 人）")
    lines.append(f"- **出行偏好**：{req.style.value}")
    lines.append(f"- **预算档位**：{req.budget.value}")
    if req.self_drive:
        lines.append("- **出行方式**：自驾")
    if req.physical_limit or req.diet_restrictions or req.allergies:
        limits = []
        if req.physical_limit:
            limits.append("有体力限制")
        if req.diet_restrictions:
            limits.append("饮食禁忌：" + "、".join(req.diet_restrictions))
        if req.allergies:
            limits.append("过敏：" + "、".join(req.allergies))
        lines.append(f"- **特殊限制**：{'；'.join(limits)}")
    if req.notes:
        lines.append(f"- **备注**：{req.notes}")
    lines.append("")

    lines.append("## 一、每日行程规划")
    lines.append("")
    for day in plan.itinerary:
        lines.append(f"### Day{day.day}｜{day.theme}")
        lines.append("")
        if day.pace_note:
            lines.append(f"> 节奏提示：{day.pace_note}")
            lines.append("")
        if day.spots:
            lines.append("**景点安排**")
            lines.append("")
            for i, s in enumerate(day.spots, 1):
                lines.append(f"{i}. **{s.name}**（{s.duration}）")
                if s.intro:
                    lines.append(f"   - 简介：{s.intro}")
                if s.reservation:
                    lines.append(f"   - 预约：{s.reservation}")
                if s.closure_tip:
                    lines.append(f"   - 提醒：{s.closure_tip}")
            lines.append("")
        if day.transport:
            lines.append(f"**交通**：{day.transport}")
            lines.append("")
        if day.meals:
            lines.append("**美食**")
            lines.append("")
            for m in day.meals:
                tip = f"（{m.tip}）" if m.tip else ""
                lines.append(f"- {m.name}：{m.dish}{tip}")
            lines.append("")

    lines.append("## 二、每日穿搭推荐")
    lines.append("")
    for day in plan.outfits:
        o = day.outfit
        lines.append(f"### Day{day.day}")
        lines.append("")
        if day.weather_hint:
            lines.append(f"> {day.weather_hint}")
            lines.append("")
        if o.top or o.bottom or o.outerwear:
            lines.append(f"- **上衣**：{o.top or '—'}")
            lines.append(f"- **下装**：{o.bottom or '—'}")
            lines.append(f"- **外套**：{o.outerwear or '—'}")
            lines.append(f"- **鞋子**：{o.shoes or '—'}")
            if o.accessories:
                lines.append(f"- **配饰**：{'、'.join(o.accessories)}")
            if o.carry_on:
                lines.append(f"- **随身穿**：{'、'.join(o.carry_on)}")
            if o.packed:
                lines.append(f"- **行李箱**：{'、'.join(o.packed)}")
            if o.tip:
                lines.append(f"- **判断依据**：{o.tip}")
        else:
            lines.append("- 穿搭建议见下方打包清单综合搭配")
        lines.append("")

    lines.append("## 三、出行打包清单")
    lines.append("")
    required = [(c.category, i) for c in plan.packing for i in c.items if i.required]
    optional = [
        (c.category, i) for c in plan.packing for i in c.items if not i.required
    ]
    lines.append("### ✅ 必带物品")
    lines.append("")
    for cat, item in required:
        reason = f"（{item.reason}）" if item.reason else ""
        lines.append(f"- [{cat}] **{item.name}**{reason}")
    lines.append("")
    lines.append("### ⭕ 可选物品")
    lines.append("")
    for cat, item in optional:
        reason = f"（{item.reason}）" if item.reason else ""
        lines.append(f"- [{cat}] **{item.name}**{reason}")
    lines.append("")

    lines.append("## 四、出行提示 & 避坑指南")
    lines.append("")
    if plan.risks:
        lines.append("### 风险提示")
        lines.append("")
        for r in plan.risks:
            lines.append(f"- {r}")
        lines.append("")
    if plan.tips:
        lines.append("### 避坑提醒")
        lines.append("")
        for t in plan.tips:
            lines.append(f"- {t}")
        lines.append("")
    if plan.alternatives:
        lines.append("### 备选方案")
        lines.append("")
        for a in plan.alternatives:
            lines.append(f"- {a}")
        lines.append("")

    lines.append("## 五、预算预估")
    lines.append("")
    b = plan.budget
    lines.append("| 分项 | 预估费用 |")
    lines.append("| --- | --- |")
    lines.append(f"| 交通 | {b.transport or '—'} |")
    lines.append(f"| 住宿 | {b.lodging or '—'} |")
    lines.append(f"| 门票 | {b.tickets or '—'} |")
    lines.append(f"| 餐饮 | {b.meals or '—'} |")
    lines.append(f"| 其他 | {b.other or '—'} |")
    lines.append(f"| **合计** | **{b.total or '—'}** |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(
        "> 本方案由 **途备 Agent** 生成，天气为历史同期参考，"
        "景点开放与预约政策以官方最新公告为准。出行前请再次核对实时信息。"
    )
    lines.append("")
    return "\n".join(lines)
