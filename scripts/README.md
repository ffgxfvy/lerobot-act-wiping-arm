# 配置与工程脚本清单

本目录已按脱敏、可校验原则补齐核心工程配置与脚本：

| 文件 | 用途 | 备注 |
|---|---|---|
| `record_task.yaml` | 主从遥操作示教采集配置 | 使用 `${FOLLOWER_PORT}` / `${LEADER_PORT}` / `${HF_USER}` 环境变量占位 |
| `deploy_task.yaml` | 本地实机推理部署配置 | 适配 SO-101 从臂 + 双视角 OpenCV 相机 + ACT |
| `train_act.sh` | AutoDL 云端 ACT 离线训练命令 | 已统一离线环境变量与 checkpoint 频次 |
| `finetune.sh` | 失败样本共训练（Co-training）微调脚本 | 基于上一轮权重低步数微调 |
| `merge_datasets.sh` | 多批次示教数据集合并脚本 | 调用 `lerobot-edit-dataset --operation.type merge` |
| `eval_checkpoint.sh` | 本地实机评测启动命令 | 遵循 LeRobot v0.4 `draccus` 等号与小写布尔值规范 |
| `check_env.py` | 本地部署前环境与硬件自检 | 支持 `--json` 与 `--probe-cameras` |
| `dataset_stats.py` | 201 episodes 多工况构成与消融实验校验 | 支持核对本地 Hugging Face LeRobot 数据目录 |

> 本地真机串口与权重目录请在运行时通过环境变量传入，禁止把个人 `COM` 口或本地绝对路径硬编码进仓库。
