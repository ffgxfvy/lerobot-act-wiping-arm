"""LeRobot SO-101 实机部署前环境自检工具。

检查项目：
1. Python 版本（项目实践基于 Python 3.10+）
2. PyTorch 与 CUDA 加速状态（避免静默回退 CPU）
3. 常用串口 / 相机硬件探针（未接入设备时安全降级输出）
4. Hugging Face / LeRobot 本地缓存目录检查
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
from pathlib import Path


def inspect_python() -> dict:
    ver = sys.version_info
    return {
        "python_version": f"{ver.major}.{ver.minor}.{ver.micro}",
        "recommended_ok": (ver.major == 3 and ver.minor >= 10),
        "platform": platform.platform(),
    }


def inspect_torch() -> dict:
    try:
        import torch  # type: ignore

        return {
            "installed": True,
            "version": torch.__version__,
            "cuda_available": bool(torch.cuda.is_available()),
            "device_count": int(torch.cuda.device_count()) if torch.cuda.is_available() else 0,
        }
    except ImportError as exc:
        return {"installed": False, "error": str(exc)}


def inspect_serial_ports() -> dict:
    try:
        from serial.tools import list_ports  # type: ignore

        ports = [{"device": p.device, "description": p.description} for p in list_ports.comports()]
        return {"installed": True, "ports": ports}
    except ImportError as exc:
        return {"installed": False, "ports": [], "note": f"pyserial unavailable ({exc})"}


def inspect_cameras(max_index: int = 3) -> dict:
    try:
        import cv2  # type: ignore

        available = []
        for idx in range(max_index):
            cap = cv2.VideoCapture(idx)
            if cap.isOpened():
                available.append(idx)
            cap.release()
        return {"installed": True, "available_indices": available}
    except ImportError as exc:
        return {"installed": False, "available_indices": [], "note": f"opencv unavailable ({exc})"}


def inspect_hf_cache() -> dict:
    hf_home = Path(os.environ.get("HF_HOME", Path.home() / ".cache" / "huggingface"))
    lerobot_home = Path(os.environ.get("HF_LEROBOT_HOME", hf_home / "lerobot"))
    calib_dir = lerobot_home / "calibration" / "robots" / "so101_follower"
    return {
        "hf_home": str(hf_home),
        "hf_lerobot_home": str(lerobot_home),
        "calibration_dir_exists": calib_dir.exists(),
    }


def run_checks(probe_cameras: bool = False) -> dict:
    report = {
        "python": inspect_python(),
        "torch": inspect_torch(),
        "serial": inspect_serial_ports(),
        "cache": inspect_hf_cache(),
    }
    if probe_cameras:
        report["cameras"] = inspect_cameras()
    else:
        report["cameras"] = {"probed": False, "note": "Pass --probe-cameras to open local webcams."}
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="SO-101 / LeRobot 部署环境前置自检")
    parser.add_argument("--probe-cameras", action="store_true", help="探测前 3 个 OpenCV 相机索引")
    parser.add_argument("--json", action="store_true", help="以 JSON 格式输出检查报告")
    args = parser.parse_args(argv)

    report = run_checks(probe_cameras=args.probe_cameras)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("=== LeRobot SO-101 Environment Pre-flight ===")
        print(f"Python : {report['python']['python_version']} (ok={report['python']['recommended_ok']})")
        t = report["torch"]
        if t.get("installed"):
            print(f"PyTorch: {t['version']} | CUDA={t['cuda_available']} (devices={t['device_count']})")
        else:
            print(f"PyTorch: NOT INSTALLED ({t.get('error')})")
        print(f"Serial : {len(report['serial']['ports'])} ports (installed={report['serial']['installed']})")
        print(f"Cache  : {report['cache']['hf_lerobot_home']} (calib={report['cache']['calibration_dir_exists']})")
        print(f"Cameras: {report['cameras']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
