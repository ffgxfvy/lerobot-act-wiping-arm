#!/usr/bin/env bash
# 本地实机 ACT 模型推理与评测启动命令（遵循 LeRobot v0.4 draccus 等号+全小写语法约束）
set -euo pipefail

FOLLOWER_PORT="${FOLLOWER_PORT:-/dev/ttyACM0}"
FOLLOWER_ID="${FOLLOWER_ID:-my_follower}"
MODEL_PATH="${MODEL_PATH:-outputs/model_act/pretrained_model}"
EVAL_REPO="${EVAL_REPO:-eval/wipe_run_01}"

lerobot-record \
  --robot.type=so101_follower \
  --robot.id="${FOLLOWER_ID}" \
  --robot.port="${FOLLOWER_PORT}" \
  --robot.cameras="{cam_high: {type: opencv, index_or_path: 2, width: 640, height: 480, fps: 30}, cam_wrist: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30}}" \
  --policy.type=act \
  --policy.pretrained_path="${MODEL_PATH}" \
  --dataset.repo_id="${EVAL_REPO}" \
  --dataset.single_task="wipe the board" \
  --dataset.push_to_hub=false \
  --policy.device=cuda \
  --dataset.episode_time_s=120 \
  --dataset.num_episodes=1 \
  --display_data=true
