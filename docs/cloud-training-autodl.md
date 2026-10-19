# AutoDL 云端训练全流程（含踩坑记录）

> 记录在 AutoDL 租用 RTX 4090 实例完成 ACT 模型云端训练的全过程，含环境绑定、数据集寻址、缓存路径设置与训练命令。
>
> 本文由 Word 文档自动提取转换，**公式与图片未嵌入**，保留原文结构与图注文字。

---

第一阶段：基础设施准备（云端开机）
租用实例： 在 AutoDL 租用合适的显卡（如 RTX 4090），并选择带有 lerobot 环境的社区镜像。
连接终端： 开机后，通过“快捷工具”打开 JupyterLab，点击蓝色的“+”号新建一个 Terminal（终端）。
环境激活： 进入系统自带的魔法环境。
Bash
conda activate lerobot

第二阶段：代码拉取与环境绑定（避开版本地雷）
核心教训：绝对不要盲目拉取 Hugging Face 官方最新代码，会导致 Python 版本不兼容（3.10 vs 3.12）。
进入数据盘并开启加速：
Bash
cd /root/autodl-tmp
source /etc/network_turbo
拉取定制版稳定代码：
Bash
git clone https://github.com/JoyandAI/lerobot.git
安装并绑定依赖：
Bash
cd lerobot
pip install -e .

第三阶段：数据寻址与“防吞”布置（最容易翻车的一步）
核心教训：程序极其死板，只会去系统默认缓存路径找数据；且 Linux 的 mv 命令在目标文件夹不存在时，会把你的文件夹“改名”而不是“移入”。
设定全局缓存路径（骗过程序）：
Bash
cd ~
mkdir -p ./autodl-tmp/huggingface
export HF_HOME=/root/autodl-tmp/huggingface
建立精准的嵌套目录：
Bash
mkdir -p /root/autodl-tmp/huggingface/lerobot
安全转移数据（假设你刚上传并解压出 user 文件夹）：
Bash
mv /root/autodl-tmp/user /root/autodl-tmp/huggingface/lerobot/

本地数据集压缩成tar文件或tar.gz文件：
tar -cvf act_02.tar act_02或
tar -czvf combined_datasets.tar.gz dataset_02 dataset_03
已经配置好的环境，上传tar文件到autodl-tmp
cd /root/autodl-tmp
解压命令:
tar -xvf act_three_02.tar或tar -xzvf ‘文件名’.tar.gz
移动:
mv dataset_three_add_04 /root/autodl-tmp/huggingface/lerobot/user/
mv dataset_03 /root/autodl-tmp/huggingface/lerobot/user/
指定数据集位置：
export HF_HOME=/root/autodl-tmp/huggingface
合并数据集：
export HF_LEROBOT_HOME=/root/autodl-tmp/huggingface/lerobot &amp;&amp; export HF_HUB_OFFLINE=1 &amp;&amp; lerobot-edit-dataset --repo_id user/dataset_three_added_04 --operation.type merge --operation.repo_ids "['user/dataset_three_added_02', 'user/dataset_three_add_04']" --push_to_hub false
预模型训练：
cd /root/autodl-tmp/lerobot &amp;&amp; export HF_LEROBOT_HOME=/root/autodl-tmp/huggingface/lerobot &amp;&amp; export HF_HUB_OFFLINE=1 &amp;&amp; unset OMP_NUM_THREADS &amp;&amp; lerobot-train --dataset.repo_id=user/dataset_three_added_04 --policy.path=/root/autodl-tmp/lerobot/outputs/train/act_three_added_02/checkpoints/020000/pretrained_model --output_dir=/root/autodl-tmp/lerobot/outputs/train/act_three_added_04 --job_name=act_three_added_04 --batch_size=16 --steps=20000 --save_freq=5000 --log_freq=100 --policy.device=cuda --wandb.enable=false
第四阶段：终极点火与监控
回到代码大本营：
Bash
cd /root/autodl-tmp/lerobot
执行训练指令：
Bash
export HF_HOME=/root/autodl-tmp/huggingface &amp;&amp; export HF_HUB_OFFLINE=1 &amp;&amp; lerobot-train --dataset.repo_id=user/dataset_three_new --policy.type=act --output_dir=outputs/train/act_three_new --job_name=act_three_new --policy.device=cuda --batch_size=16 --steps=100000 --policy.push_to_hub=false --wandb.enable=false
挂机与验收： 看到 Loss 值开始下降后，保持实例运行。训练中途（如 2 万步时）或彻底结束后，前往 /root/autodl-tmp/lerobot/outputs/train/act_so101_test/checkpoints/ 目录下下载对应的模型权重文件至本地。
到保存权重的文件夹中：
cd /root/autodl-tmp/lerobot/outputs/train/
打包命令：
tar -czvf act_three.tar.gz dataset_three/