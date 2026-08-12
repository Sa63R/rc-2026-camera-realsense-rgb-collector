# RealSense RGB 数据采集工具

这是 2026 赛季相机采集脚本的清理公开版。它使用 Intel RealSense 获取彩色画面，支持人工按键把干净 RGB 帧保存为 real / fake 两类；两个实验脚本还可将深度对齐到彩色画面，并查询鼠标点击像素的三维坐标和距离。

仓库只包含代码与文档，不包含历史图片、YOLO 标注、ZIP、深度录像或模型权重。数据为什么不应直接进入 Git，见 [DATASET_POLICY.md](DATASET_POLICY.md)；发布前的权利确认见 [LEGAL_NOTICE.md](LEGAL_NOTICE.md)；依赖的许可边界与官方来源见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

> real / fake 只是历史按键和目录名，不是已经定义好的业务标签。正式采集前，算法负责人必须书面定义两类的含义、边界样本和验收规则。

## 程序的输入与输出

输入：

- 一台能提供彩色流的 Intel RealSense；turn1.py 和 turn2.py 还需要深度流。
- OpenCV 图形窗口中的键盘与鼠标输入。
- 可选命令行参数：输出目录、设备序列号、分辨率和帧率等。
- turn1.py / turn2.py 使用的手动旋转角，单位为度。

输出：

- RGB 图片。默认写到启动目录下的 captures/real 和 captures/fake。
- turn1.py / turn2.py 在终端打印点击点的相机坐标和实验性旋转坐标；turn2.py 还打印三维距离与相对光轴的径向偏移。
- 不保存深度帧、点云、标注、相机内外参、ROS 消息或 CAN 数据。

所有脚本将提示文字画在预览副本上，保存的是未叠加 UI、红点或距离文本的原始 RGB 帧。文件名使用微秒时间戳和随机后缀；每次写盘都检查 OpenCV 返回值。

## 应该运行哪个脚本

| 文件 | 用途 | 流 | 按键 | 建议 |
| --- | --- | --- | --- | --- |
| collect_new.py | 普通双类 RGB 采集 | RGB，默认 640×480@30 | r / f / q | 新人首选 |
| collect_images.py | 带计数、帧超时与重试的双类采集 | RGB | r / f / q | USB 偶发超时时使用 |
| collect_only.py | 低带宽单类拍照 | RGB，默认 640×480@15 | 空格 / Esc | 只采一种类别或链路不稳时 |
| collect_simple.py | 最小教学版本 | RGB | r / f / q | 阅读流程、排查基础问题 |
| turn.py | 历史 RGB-only 变体 | RGB | r / f / q | 兼容留档，不含转角功能 |
| turn1.py | 点击查询三维点 | RGB + 深度 | 鼠标、a / r / f / q | 实验用途 |
| turn2.py | 点击查询三维点和距离 | RGB + 深度 | 鼠标、a / r / f / q | 测距实验首选 |

## 快速开始

### 1. 环境

建议 Python 3.10 或更高版本，并使用有桌面显示环境的 Linux/Windows 主机：

~~~bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
~~~

这些脚本需要 cv2.imshow，不能用 opencv-python-headless。Linux 还需要与相机、系统和 Python 匹配的 librealsense、USB 权限规则和图形环境。某些 ARM/Jetson 平台没有可直接安装的 pyrealsense2 wheel。

可先检查：

~~~bash
python -c "import cv2, numpy, pyrealsense2; print('imports OK')"
rs-enumerate-devices
python -m py_compile *.py tools/*.py
~~~

关闭 RealSense Viewer、ROS 相机节点和其他会独占设备的程序。

### 2. 做少量 RGB 冒烟测试

~~~bash
python collect_new.py --output-dir ../private-captures/session-001
~~~

点击图像窗口使它获得焦点，然后：

- 小写 r：保存到 session-001/real。
- 小写 f：保存到 session-001/fake。
- 小写 q：正常退出并释放相机。

先各拍 3～5 张，打开磁盘中的图片，确认它们清晰、类别正确、没有预览文字且路径符合预期，再开始整批采集。

如果连接多台 RealSense，应固定设备：

~~~bash
python collect_new.py \
  --device-serial YOUR_CAMERA_SERIAL \
  --output-dir ../private-captures/session-001
~~~

运行 python collect_new.py --help 可查看分辨率、帧率和超时参数。

### 3. 低带宽单类采集

~~~bash
python collect_only.py \
  --output-dir ../private-captures/session-002/real \
  --fps 15 \
  --format jpg \
  --jpeg-quality 80
~~~

默认启用自动曝光。如果确实需要固定曝光，显式提供 --manual-exposure；程序会先关闭自动曝光再设置该值。不同设备支持的曝光范围不同，必须做现场验证。

### 4. 点击测距实验

~~~bash
python turn2.py \
  --output-dir ../private-captures/session-003 \
  --angles 0 0 0
~~~

- 左键点击 Color Stream 中的像素：读取对齐深度并打印结果。
- a：切回终端重新输入 roll、pitch、yaw。
- r / f：只保存原始 RGB，不保存深度或屏幕标注。
- q：退出。

turn1.py / turn2.py 所称的旋转坐标只应用了一个历史旋转矩阵，没有相机到机器人基座的平移、外参标定、时间同步或 TF。因此它不是可直接发送给控制组的世界坐标。turn2.py 的“光轴径向偏移”是 sqrt(X²+Y²)，不是地面平面上的水平距离。

## 常用命令行参数

双类脚本通常支持：

| 参数 | 默认值 | 含义 |
| --- | --- | --- |
| --output-dir | captures | 输出根目录，程序在其中创建 real / fake |
| --device-serial | 未指定 | 多相机时选择固定设备 |
| --width / --height | 640 / 480 | 彩色流尺寸；深度脚本同时用于深度流 |
| --fps | 30 | 流帧率 |

参数是否可用取决于相机型号、USB 带宽和固件。SDK 报 “Couldn't resolve requests” 时，应先恢复默认 profile，再逐项改变。

## 仓库结构

~~~text
.
├── collect_new.py          # 推荐的普通 RGB 采集器
├── collect_images.py       # 超时重试与计数版本
├── collect_only.py         # 低带宽单类版本
├── collect_simple.py       # 最小版本
├── turn.py                 # 历史 RGB-only 版本
├── turn1.py                # 点击三维点实验
├── turn2.py                # 点击坐标与距离实验
├── capture_utils.py        # 唯一文件名、目录和安全写盘公共函数
├── tools/build_manifest.py # 外部采集目录的 SHA-256 清单工具
├── DATASET_POLICY.md       # 数据准入、隐私、去重与托管政策
├── LEGAL_NOTICE.md         # 公开发布前的权利检查
├── THIRD_PARTY_NOTICES.md  # 第三方依赖许可与官方来源
├── note.md                 # 面向新人的详细原理与协作说明
└── requirements.txt
~~~

captures、常见数据目录、图片、录包和 ZIP 默认被 .gitignore 排除。若确需提交一张演示图，必须先通过权利与隐私审查，再由维护者明确使用 git add -f；不要为了方便删掉保护规则。

## 生成数据清单

对仓库外的一次采集生成相对路径、大小和 SHA-256：

~~~bash
python tools/build_manifest.py \
  ../private-captures/session-001 \
  --output ../private-captures/session-001-manifest.csv
~~~

class_hint 只是根据 real / fake 路径推断，不能代替人工确认或正式标签。哈希能发现完全相同的文件，不能发现连续帧、重压缩或裁剪后的近重复。

## 与其他组的接口

1. 算法/训练组先给出目标、类别、负样本、标注格式、场景覆盖和验收指标。
2. 采集组按 session 保存干净图片和元数据，完成隐私、许可和基础质量检查。
3. 标注组按版本化规范生成标签；训练集、验证集和测试集按 session/物体/场景隔离。
4. 训练组交付数据版本、切分清单、指标和失败样例，而不只交付模型权重。
5. 硬件/机械/控制组共同提供相机安装外参、物体尺寸、坐标系、单位、时间戳和失效行为。

本仓库只覆盖第 2 步中的采集工具和一个深度点击实验。完整新人流程、数学边界与故障排查见 [note.md](note.md)。

## 发布状态

这是待发布的干净副本，不代表已经完成法律审批。公开前至少要：

- 由权利人添加明确的 LICENSE；
- 确认项目/赛事/学校规则允许公开；
- 保证提交历史中也没有数据或敏感路径；
- 在无相机和真实相机环境各做一次检查；
- 单独建立经过审查的数据集卡和托管地址。
