#!/usr/bin/env bash
# 失败样本补录后混合微调（Co-training Finetune）脚本
set -euo pipefail

HF_ROOT="${HF_HOME:-/root/autodl-tmp/huggingface}"
LEROBOT_DIR="${LEROBOT_DIR:-/root/autodl-tmp/lerobot}"
MERGED_REPO="${MERGED_REPO:-user/dataset_three_added_04}"
BASE_CKPT="${BASE_CKPT:-${LEROBOT_DIR}/outputs/train/act_three_added_02/checkpoints/020000/pretrained_model}"
JOB_NAME="${JOB_NAME:-act_three_added_04}"
BATCH_SIZE="${BATCH_SIZE:-16}"
STEPS="${STEPS:-20000}"

export HF_HOME="${HF_ROOT}"
export HF_LEROBOT_HOME="${HF_ROOT}/lerobot"
export HF_HUB_OFFLINE=1
unset OMP_NUM_THREADS || true

cd "${LEROBOT_DIR}"

lerobot-train \
  --dataset.repo_id="${MERGED_REPO}" \
  --policy.path="${BASE_CKPT}" \
  --output_dir="outputs/train/${JOB_NAME}" \
  --job_name="${JOB_NAME}" \
  --batch_size="${BATCH_SIZE}" \
  --steps="${STEPS}" \
  --save_freq=5000 \
  --log_freq=100 \
  --policy.device=cuda \
  --wandb.enable=false
