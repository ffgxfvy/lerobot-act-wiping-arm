#!/usr/bin/env bash
# AutoDL 云端 ACT 端到端训练脚本（离线 Hugging Face 模式）
set -euo pipefail

HF_ROOT="${HF_HOME:-/root/autodl-tmp/huggingface}"
LEROBOT_DIR="${LEROBOT_DIR:-/root/autodl-tmp/lerobot}"
DATASET_REPO="${DATASET_REPO:-user/dataset_three_new}"
JOB_NAME="${JOB_NAME:-act_wiping_100k}"
BATCH_SIZE="${BATCH_SIZE:-16}"
STEPS="${STEPS:-100000}"

export HF_HOME="${HF_ROOT}"
export HF_LEROBOT_HOME="${HF_ROOT}/lerobot"
export HF_HUB_OFFLINE=1
unset OMP_NUM_THREADS || true

cd "${LEROBOT_DIR}"

lerobot-train \
  --dataset.repo_id="${DATASET_REPO}" \
  --policy.type=act \
  --output_dir="outputs/train/${JOB_NAME}" \
  --job_name="${JOB_NAME}" \
  --policy.device=cuda \
  --batch_size="${BATCH_SIZE}" \
  --steps="${STEPS}" \
  --save_freq=10000 \
  --log_freq=100 \
  --policy.push_to_hub=false \
  --wandb.enable=false
