# LeRobot 环境搭建与仿真流程记录

> 记录 SO-101 主从机械臂的完整搭建过程：环境安装、端口识别、标定、遥操作、相机配置、示教数据采集与 ACT 模型训练。
>
> 本文由 Word 文档自动提取转换，**公式与图片未嵌入**，保留原文结构与图注文字。

---

环境：
python3.10、anaconda、anaconda powershell prompt
创建环境指令：
conda create -n lerobot
python=3.10 conda activate lerobot
克隆库：git clone https://github.com/JoyandAI/lerobot.git
Lerobot目录中添加飞特舵机驱动：
pip install -e ".[feetech]"
安装ffmpeg
conda install -c conda-forge ffmpeg=7.1.1
报错尝试输入：
chcp 65001
conda install -c conda-forge gdk-pixbuf=2.44.5
conda install -c conda-forge ffmpeg

标定：
确定从臂主臂对应的端口号：
lerobot-find-port
中立位置：

开始标定：
从臂标定：
lerobot-calibrate `
    --robot.type=so101_follower `
    --robot.port=COM3 `                   从臂对应的端口COM7
    --robot.id=R12252801                  自己取的从臂名字my_follower
主臂标定：
lerobot-calibrate `
    --teleop.type=so101_leader `
    --teleop.port=COM4 `             COM8
    --teleop.id=R07252801            my_leader

遥操作：
处于rest位进行遥操作：

标定后第一次示教，从臂要断电一次，不然会卡死
lerobot-teleoperate `
    --robot.type=so101_follower `
    --robot.port=COM28 `                    从臂对应端口
    --robot.id=R12252801 `                   从臂标定文件名称
    --teleop.type=so101_leader `
    --teleop.port=COM27 `                  主臂对应端口
--teleop.id=R07252801                  主臂标定文件名称

安装相机：
两个摄像头分别接到电脑上不同的usb口上
确定摄像头的序号，在lerobot/output/captured_images目录下查看拍到的图片，插拔或重启电脑后对应关系可能变化：
lerobot-find-cameras
示教：
设置为用户名：
set HF_USER=your_user_name
开始录制，数据集在./cache/huggingface/lerobot/${HF_USER}/，键盘左键重录，右键提前结束，esc退出：
lerobot-record `
    --robot.disable_torque_on_disconnect=true `
    --robot.type=so101_follower `
    --robot.port=COM4 `                根据实际改
    --robot.id=R12252801 `               根据实际改
    --robot.cameras="{'wrist': {'type':'opencv', 'index_or_path':0, 'width':640, 'height':360, 'fps':30}, 'front': {'type':'opencv', 'index_or_path':1, 'width':640, 'height':360, 'fps':30}}" `              选择使用的相机编号和相机参数，根据实际改
    --teleop.type=so101_leader `
    --teleop.port=COM3 `
    --teleop.id=R07252801 `
    --display_data=true `
    --dataset.repo_id=${HF_USER}/so101_test `                 给这次的数据集起个名字
    --dataset.num_episodes=50 --dataset.episode_time_s=30 `             分别设置录制视频数和录制时间
--dataset.single_task="Grab the black cube"
Ai给的录制指令：
lerobot-record --config record_task.yaml
record_task.yaml内容：
robot:
  type: so101_follower
  port: COM7
  id: my_follower
  cameras:
    cam_high:
      type: opencv
      index_or_path: 1
      width: 640
      height: 480
      fps: 30
    cam_wrist:
      type: opencv
      index_or_path: 2
      width: 640
      height: 480
      fps: 30

teleop:
  type: so101_leader
  port: COM8
  id: my_leader

dataset:
  repo_id: user/my_first_dataset
  single_task: "Pick up the object and move it to the right"
  fps: 30
  episode_time_s: 40
  push_to_hub: false

display_data: true

示教视角：

模型训练：
可以使用的方法：
act, Action Chunking Transformers
diffusion, Diffusion Policy
tdmpc, TDMPC Policy
vqbet, VQ-BeT
smolvla, SmolVLA             pip install -e ".[smolvla]"
pi0, A Vision-Language-Action Flow Model for General Robot Control          使用需要额外下载依赖：pip install "lerobot[pi]"
pi0-fast
sac
reward_classifier
开始训练：
lerobot-train \
  --dataset.repo_id=${HF_USER}/so101_test \           选择数据集
  --policy.type=act \                      选择模型
  --output_dir=outputs/train/act_so101_test \
  --job_name=act_so101_test \
  --policy.device=cuda \
  --policy.push_to_hub=false \
  --wandb.enable=false
继续之前中断的训练：
lerobot-train \
  --config_path=outputs/train/act_so101_test/checkpoints/last/pretrained_model/train_config.json \
  --resume=true
测试模型：