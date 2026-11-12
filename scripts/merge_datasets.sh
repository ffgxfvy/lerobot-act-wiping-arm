#!/usr/bin/env bash
# 合并多批次示教数据集（旧数据集 + 失败补录数据集）
set -euo pipefail

HF_ROOT="${HF_HOME:-/root/autodl-tmp/huggingface}"
OUT_REPO="${OUT_REPO:-user/dataset_three_added_04}"
SRC_REPOS="${SRC_REPOS:-['user/dataset_three_added_02', 'user/dataset_three_add_04']}"

export HF_HOME="${HF_ROOT}"
export HF_LEROBOT_HOME="${HF_ROOT}/lerobot"
export HF_HUB_OFFLINE=1

lerobot-edit-dataset \
  --repo_id "${OUT_REPO}" \
  --operation.type merge \
  --operation.repo_ids "${SRC_REPOS}" \
  --push_to_hub false
