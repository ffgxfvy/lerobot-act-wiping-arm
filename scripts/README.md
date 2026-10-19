# 待补充的脚本清单

本目录目前为空。以下脚本需要从本地工程中整理后放入，补全后本仓库即为完整可复现状态。

## 优先级 P0（缺了这些，仓库无法自证"我真的训练过"）

| 文件名 | 内容 | 来源 |
|---|---|---|
| `record_task.yaml` | 示教采集配置：机器人类型、端口、双相机参数、数据集命名、episode 数与时长 | `机械臂.docx` 中记录了该文件的字段结构 |
| `deploy_task.yaml` | 部署推理配置：模型路径、标定文件、相机参数、单次任务设置 | `本地部署.docx` |
| `train_act.sh` | ACT 训练启动命令（含 `HF_LEROBOT_HOME` / `HF_HUB_OFFLINE` 环境变量与全部参数） | `云端训练.docx` 第三、四阶段 |
| `finetune.sh` | 失败样本微调命令（`--policy.path` 指向上一版 checkpoint，低学习率、`steps=20000`） | `云端训练.docx` |
| `eval_checkpoint.sh` | 实机评测启动命令（`lerobot-record` + `--policy.pretrained_path`） | `本地部署.docx` |

## 优先级 P1（提升可复现性）

| 文件名 | 内容 |
|---|---|
| `merge_datasets.sh` | 多批数据集合并（`combined_datasets`）的命令序列 |
| `check_env.py` | 环境自检：`torch.cuda.is_available()`、torch/torchvision 版本、相机枚举、串口枚举 |
| `plot_training.py` | 从训练日志画 loss 曲线（报告里的收敛图） |
| `analyze_failures.py` | 统计实机失败类型分布与阶段耗时（报告 4.2 / 4.3 节的数据来源） |

## 优先级 P2（面向他人复用）

| 文件名 | 内容 |
|---|---|
| `dataset_stats.py` | 统计 201 episodes 的分布（按工况）与每条时长 |
| `README.md`（本文件升级版） | 每个脚本的一行用法说明 |

---

## 整理时注意

1. **删除所有个人信息**：COM 口号（`COM3`/`COM7`/`COM28`…）、HF 用户名、AutoDL 实例信息、API token；
2. **标注占位符**：把端口写成 `COM_PORT_FOLLOWER` / `COM_PORT_LEADER`，把用户名写成 `${HF_USER}`；
3. **保留踩坑注释**：那些"为什么必须这样写"的注释是这个仓库最有价值的部分，不要为了整洁删掉；
4. **`.gitignore` 已排除** `*.mp4`、`*.pth`、`*.safetensors`、`*.zip`、`*.docx`，脚本可以放心提交。
