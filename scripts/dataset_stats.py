"""201 条工业仪表擦拭示教数据集与五阶段消融指标统计工具。

说明：
- 默认输出技术报告与数据集设计文档中已核对的多工况构成与消融实验汇总；
- 若通过 `--dataset-dir` 指定本地 Hugging Face / LeRobot 数据集目录（含 `meta/episodes.jsonl` 或 `meta/info.json`），
  则额外统计真实本地 episode 数量与总帧数。
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

# 与 docs/dataset-design.md 严格一致的 8 类工况分布（共 201 episodes）
DATASET_CONDITIONS = [
    {"id": 1, "name": "标准污渍擦拭", "episodes": 27, "focus": "基础抓取-擦拭-复位链路"},
    {"id": 2, "name": "仪表位置偏移", "episodes": 26, "focus": "工作空间位置泛化"},
    {"id": 3, "name": "仪表尺寸变化", "episodes": 24, "focus": "大小表盘视觉尺度适应"},
    {"id": 4, "name": "污渍状态判断", "episodes": 28, "focus": "有污渍擦拭 vs 干净跳过"},
    {"id": 5, "name": "海绵抓取偏差", "episodes": 25, "focus": "柔性工具夹持偏移容错"},
    {"id": 6, "name": "光照/反光扰动", "episodes": 23, "focus": "玻璃反光与照度变化鲁棒性"},
    {"id": 7, "name": "真实厂房采集", "episodes": 24, "focus": "非结构化工业现场背景泛化"},
    {"id": 8, "name": "失败样本补录", "episodes": 24, "focus": "部署回补与共训练（Co-training）"},
]

# 与 docs/technical-report.md 表 4-2 严格一致的消融实测成功率
ABLATION_RESULTS = [
    {"stage": "单全局视角模型", "inputs": "全局图像", "success_rate": 76.8},
    {"stage": "双视角模型", "inputs": "全局图像 + 腕部图像", "success_rate": 84.5},
    {"stage": "双视角 + 关节状态模型", "inputs": "双相机 + 6DoF 关节与夹爪状态", "success_rate": 88.1},
    {"stage": "ACT 动作分块模型", "inputs": "多模态输入 + Action Chunking", "success_rate": 89.4},
    {"stage": "ACT + 失败样本微调", "inputs": "动作分块 + 失败样本 Co-training", "success_rate": 91.2},
]


def summarize_dataset() -> dict:
    total = sum(item["episodes"] for item in DATASET_CONDITIONS)
    breakdown = [
        {**item, "ratio_pct": round(item["episodes"] * 100.0 / total, 1)}
        for item in DATASET_CONDITIONS
    ]
    return {
        "total_episodes": total,
        "num_conditions": len(DATASET_CONDITIONS),
        "min_episodes_per_condition": min(item["episodes"] for item in DATASET_CONDITIONS),
        "max_episodes_per_condition": max(item["episodes"] for item in DATASET_CONDITIONS),
        "conditions": breakdown,
        "ablation": ABLATION_RESULTS,
        "net_gain_pct_points": round(
            ABLATION_RESULTS[-1]["success_rate"] - ABLATION_RESULTS[0]["success_rate"], 1
        ),
    }


def inspect_local_lerobot_dir(dataset_dir: Path) -> dict:
    meta_dir = dataset_dir / "meta"
    info_file = meta_dir / "info.json"
    ep_file = meta_dir / "episodes.jsonl"
    result: dict = {"path": str(dataset_dir), "exists": dataset_dir.exists()}
    if info_file.exists():
        info = json.loads(info_file.read_text(encoding="utf-8"))
        result["info_total_episodes"] = info.get("total_episodes")
        result["info_total_frames"] = info.get("total_frames")
        result["fps"] = info.get("fps")
    if ep_file.exists():
        lines = [line for line in ep_file.read_text(encoding="utf-8").splitlines() if line.strip()]
        episodes = [json.loads(line) for line in lines]
        lengths = [ep.get("length", 0) for ep in episodes]
        result["episodes_jsonl_count"] = len(episodes)
        if lengths:
            result["avg_frames_per_episode"] = round(sum(lengths) / len(lengths), 1)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="LeRobot 仪表擦拭数据集与消融结果汇总")
    parser.add_argument("--dataset-dir", type=Path, default=None, help="可选：本地 LeRobot 数据集目录")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    args = parser.parse_args(argv)

    summary = summarize_dataset()
    if args.dataset_dir is not None:
        summary["local_dataset"] = inspect_local_lerobot_dir(args.dataset_dir)

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0

    print(f"数据集总规模: {summary['total_episodes']} episodes / {summary['num_conditions']} 类工况")
    for item in summary["conditions"]:
        print(f"  {item['id']}. {item['name']:<10} | {item['episodes']:>2} eps ({item['ratio_pct']:>4.1f}%) | {item['focus']}")
    print("\n五阶段消融实验任务完成率（技术报告 表 4-2）：")
    for row in summary["ablation"]:
        print(f"  - {row['stage']:<16} | {row['success_rate']:>4.1f}% | {row['inputs']}")
    print(f"\n端到端总体增益: +{summary['net_gain_pct_points']} 个百分点（76.8% -> 91.2%）")
    if "local_dataset" in summary:
        print("\n本地目录统计:", json.dumps(summary["local_dataset"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
