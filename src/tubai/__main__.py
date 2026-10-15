"""途备 Agent CLI：交互模式 / 单次生成 / 批量测试。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from tubai.orchestrator import TubaiOrchestrator

app = typer.Typer(add_completion=False, help="途备 Agent — 智能旅行规划助手")
console = Console()


@app.command()
def chat() -> None:
    """多轮对话交互模式。"""
    orch = TubaiOrchestrator()
    console.print(Panel(orch.welcome, title="途备 Agent", border_style="cyan"))

    req = None
    while True:
        try:
            user = console.input("\n[bold green]你[/] > ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n再见，旅途愉快！")
            raise typer.Exit() from None
        if not user:
            continue
        if user in {"q", "quit", "exit", "退出"}:
            console.print("再见，旅途愉快！")
            break

        plan_obj = None
        if req is None:
            parsed, _missing, follow_up = orch.parse_input(user)
            if parsed is None:
                console.print(f"[yellow]{follow_up}[/]")
                continue
            req = parsed
            console.print("[dim]信息已收集，正在生成全套方案…[/]")
            plan_obj = orch.generate(req)
        else:
            changes = _detect_changes(user, req)
            if changes:
                console.print(f"[dim]检测到变更 {changes}，重新生成…[/]")
                plan_obj = orch.generate(req.model_copy(update=changes))
                req = plan_obj.request
            else:
                console.print("[dim]正在根据最新需求生成方案…[/]")
                plan_obj = orch.generate(req)

        md = orch.export(plan_obj)
        console.print(Markdown(md))

        out = Path("outputs") / f"plan_{req.destination}_{req.days}d.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(md, encoding="utf-8")
        console.print(f"[dim]已保存：{out}  可继续输入修改指令，或输入 q 退出[/]")


@app.command()
def plan(
    text: Annotated[
        str, typer.Argument(help="一次性出行描述，如：5月去成都玩3天，两人，逛吃")
    ],
    output: Annotated[
        Path | None, typer.Option("--output", "-o", help="导出 Markdown 路径")
    ] = None,
) -> None:
    """单次生成完整旅行方案。"""
    orch = TubaiOrchestrator()
    md = orch.run_text(text)
    console.print(Markdown(md))
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(md, encoding="utf-8")
        console.print(f"[green]已保存：{output}[/]")
    else:
        out = Path("outputs") / "plan_latest.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(md, encoding="utf-8")
        console.print(f"[dim]已保存：{out}[/]")


@app.command()
def batch(
    cases_dir: Annotated[Path, typer.Option("--cases", "-c", help="用例目录")] = Path(
        "cases"
    ),
    output_dir: Annotated[Path, typer.Option("--out", "-o", help="输出目录")] = Path(
        "outputs/batch"
    ),
) -> None:
    """批量执行 cases/ 下的测试用例（Kiro CLI 回归测试）。"""
    orch = TubaiOrchestrator()
    files = sorted(cases_dir.glob("*.json"))
    if not files:
        console.print(f"[red]未找到用例：{cases_dir}[/]")
        raise typer.Exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)
    passed = 0
    results = []
    for f in files:
        case = json.loads(f.read_text(encoding="utf-8"))
        name = case.get("name", f.stem)
        query = case["query"]
        console.print(f"[cyan]▶ {name}[/]")
        try:
            md = orch.run_text(query)
            # 变更场景：二次生成
            if case.get("followup"):
                req, _, follow = orch.parse_input(query)
                if req is None:
                    raise RuntimeError(follow or "parse failed")
                changes = case.get("changes") or {}
                plan_obj = orch.generate(req.model_copy(update=changes))
                md = orch.export(plan_obj)
            out_file = output_dir / f"{f.stem}.md"
            out_file.write_text(md, encoding="utf-8")

            expected = case.get("expect_contains") or []
            missing = [e for e in expected if e not in md]
            ok = not missing
            status = "PASS" if ok else f"FAIL missing={missing}"
            if ok:
                passed += 1
            results.append({"case": name, "status": status, "output": str(out_file)})
            console.print(f"  {'✅' if ok else '❌'} {status}")
        except Exception as exc:  # noqa: BLE001
            results.append({"case": name, "status": f"ERROR {exc}"})
            console.print(f"  ❌ ERROR {exc}")

    console.print(f"\n[bold]结果：{passed}/{len(files)} 通过[/]")
    (output_dir / "report.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    if passed < len(files):
        raise typer.Exit(1)


def _detect_changes(text: str, req) -> dict:
    import re

    changes: dict = {}
    m = re.search(r"(\d{1,2})\s*(?:天|日)", text)
    if m and any(
        k in text for k in ("改成", "改为", "调整为", "缩短", "增加", "变成", "天数")
    ):
        changes["days"] = int(m.group(1))
    for city in (
        "北京",
        "上海",
        "成都",
        "杭州",
        "三亚",
        "丽江",
        "拉萨",
        "西安",
        "厦门",
        "桂林",
        "青岛",
        "昆明",
    ):
        if city in text and any(
            k in text for k in ("换", "改成", "改为", "不去", "改去", "变成")
        ):
            changes["destination"] = city
            break
    return changes


if __name__ == "__main__":
    app()
