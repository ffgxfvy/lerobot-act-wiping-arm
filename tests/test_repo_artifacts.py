"""验证 lerobot-act-wiping-arm 仓库中的脱敏配置、脚本语法卫生及数据集统计一致性。"""
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
DOCS = ROOT / "docs"

sys.path.insert(0, str(SCRIPTS))
import check_env  # noqa: E402
import dataset_stats  # noqa: E402


def test_yaml_configs_exist_and_are_sanitized():
    for name in ("record_task.yaml", "deploy_task.yaml"):
        path = SCRIPTS / name
        assert path.exists(), f"Missing {name}"
        text = path.read_text(encoding="utf-8")
        assert "robot:" in text and "cameras:" in text and "dataset:" in text
        assert "COM7" not in text and "COM8" not in text
        assert "D:\\Project" not in text


def test_shell_scripts_have_no_html_entities_or_crlf():
    for sh in sorted(SCRIPTS.glob("*.sh")):
        raw = sh.read_bytes()
        assert b"\r\n" not in raw, f"{sh.name} contains CRLF line endings"
        text = raw.decode("utf-8")
        assert text.startswith("#!/usr/bin/env bash"), f"{sh.name} missing bash shebang"
        assert "&amp;" not in text and "&lt;" not in text and "&gt;" not in text


def test_docs_have_no_html_entity_leaks_or_local_paths():
    for md in sorted(DOCS.glob("*.md")):
        text = md.read_text(encoding="utf-8")
        assert "&amp;&amp;" not in text, f"{md.name} contains unescaped &amp;&amp;"
        assert "D:\\Project" not in text, f"{md.name} leaks hardcoded local path"


def test_dataset_statistics_match_technical_report():
    summary = dataset_stats.summarize_dataset()
    assert summary["total_episodes"] == 201
    assert summary["num_conditions"] == 8
    assert summary["min_episodes_per_condition"] >= 23
    rates = [row["success_rate"] for row in summary["ablation"]]
    assert rates == [76.8, 84.5, 88.1, 89.4, 91.2]
    assert rates == sorted(rates)
    assert summary["net_gain_pct_points"] == 14.4


def test_dataset_stats_local_inspection_fixture(tmp_path):
    meta = tmp_path / "meta"
    meta.mkdir()
    (meta / "info.json").write_text(
        json.dumps({"total_episodes": 3, "total_frames": 900, "fps": 30}),
        encoding="utf-8",
    )
    (meta / "episodes.jsonl").write_text(
        "\n".join(json.dumps({"episode_index": i, "length": 300}) for i in range(3)),
        encoding="utf-8",
    )
    info = dataset_stats.inspect_local_lerobot_dir(tmp_path)
    assert info["episodes_jsonl_count"] == 3
    assert info["avg_frames_per_episode"] == 300.0


def test_check_env_cli_runs_cleanly():
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / "check_env.py"), "--json"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=str(ROOT),
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert "python" in payload and "torch" in payload and "cache" in payload
