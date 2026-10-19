# 本地实机部署与模型推理

> 记录训练好的 ACT 权重在本地实机部署推理的过程，含 GPU 环境治理、模型/标定文件挂载、LeRobot v0.4 语法约束与安全操作规范。
>
> 本文由 Word 文档自动提取转换，**公式与图片未嵌入**，保留原文结构与图注文字。

---

解压tar.gz文件
tar -zxvf model_60k.tar.gz
开始：
lerobot-record --config_path deploy_task.yaml
一、 环境搭建与显卡排雷
默认环境极易混入 CPU 版本的 PyTorch，导致无显卡加速（出现 Switching to 'cpu' 警告）或 torchvision 版本不兼容 。
卸载残缺依赖：必须先彻底清理旧版环境，执行 pip uninstall torch torchvision torchaudio -y 。
安装满血引擎：推荐跨代升级至 CUDA 12.4 以完美兼容 v0.4 框架，执行 pip install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124 。
强制核验：启动前务必执行 python -c "import torch; print('CUDA 状态:', torch.cuda.is_available())"，必须看到输出为 True 。

二、 模型与硬件挂载规范
在实机推理时，底层逻辑依然是“录制数据集”，因此对模型路径和硬件参数的挂载要求极度严格 。
模型路径避雷：启动指令中的路径不能只指向外层，必须精准指向包含 config.json 和 .safetensors 的最深层文件夹（如 .../pretrained_model），否则系统会因找不到特征而报 ValueError 。
标定文件挂载：将记录了电机物理极限的标定文件（如 my_follower.json）放入 D:\Project\huggingface_cache\lerobot\calibration\robots\so101_follower\ 。使用 --robot.id=my_follower 挂载即可完美跳过手动示教环节 。
感官配置注入：放弃外部 .yaml 传参，采用字典内联写法直接在命令行中声明双摄像头参数 。

三、 启动指令与语法铁律
LeRobot v0.4 的底层解析器 draccus 对语法极其敏感，以下是必须遵守的语法红线 ：
等号赋值：参数与值之间必须使用等号（如 --dataset.push_to_hub=false），严禁使用空格分隔 。
全小写布尔值：布尔参数必须严格全小写（true/false），首字母大写会导致解析崩溃 。
指令防冲突：指令末尾严禁携带特殊符号（如 \） 。若程序中断后重跑，必须更改 --dataset.repo_id 的名称以防触发 FileExistsError 文件夹冲突 。
逻辑规避参数：
添加 -p 强制指定模型路径，避免框架陷入 No policy 的死循环误判 。
添加 --dataset.push_to_hub=false 切断云端同步，防止 Hugging Face 未登录引发 401 Unauthorized 崩溃 。
添加 --dataset.episode_time_s=120 与 --dataset.num_episodes=1 以打破默认的 60 秒上限，并确保单次任务优雅退出，防止重置死循环 。
指令模板 ：
DOS
lerobot-record --robot.type=so101_follower --robot.id=my_follower --robot.port=COM7 --robot.cameras="{cam_high: {type: opencv, index_or_path: 2, width: 640, height: 480, fps: 30}, cam_wrist: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30}}" --policy.type=act --policy.pretrained_path=outputs\model_act01\100000\pretrained_model --dataset.repo_id=my_eval/eval_test_04 --dataset.single_task="wipe the board" --dataset.push_to_hub=false --policy.device=cuda --dataset.episode_time_s=120 --dataset.num_episodes=1 --display_data=true

四、 物理安全与进阶迭代
物理防线：预训练模型对视角敏感，回车运行前，操作者的手必须停留在急停开关或电源处，遇轨迹漂移需在 1 秒内断电 。
原环境兼容：经过优化的满血 GPU 环境完全可以继续使用 lerobot-record --config record_task.yaml 指令进行录制示教，且张量计算将获得显卡加速 。
录制 vs 部署：录制示教（Teleop）是利用主臂积累专家数据“教”AI；而本机部署（Inference）则剥离主臂，仅靠显卡内的大脑和摄像头控制从臂来“考”试 。
数据飞轮启动：模型部署成功后，后续需通过改变光线和物体位置等方式评估模型的鲁棒性并寻找失败案例（Fail Cases） 。针对失败场景切回录制模式补录数据，混合旧数据重新云端训练（Co-training），并尝试调整 chunk_size 等超参数优化动作流畅度 。