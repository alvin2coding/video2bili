# Bilibili视频上传工具

这是一个基于`bilibili-api-python`库的视频上传工具，支持视频下载、翻译、烧录后的上传至B站功能。

## 项目结构

```
video2bili/
├── src/
│   ├── bili_cookie.txt          # Bilibili账号凭据文件
│   ├── simple_upload_test.py    # API参考脚本
│   └── upload_test_video.py     # 视频上传主脚本
├── videos/
│   └── video_name/              # 视频文件夹（以视频文件名命名）
│       ├── video_name.mp4       # 视频文件（文件名与文件夹名相同）
│       └── video_name_cover.jpg # 封面文件（以视频文件名_cover开头）
├── logs/                        # 日志文件夹
│   ├── video_name_upload.log    # 详细日志文件（以视频文件名命名）
│   └── video_name_result.txt    # 上传结果文件（以视频文件名命名）
├── bin/                         # 虚拟环境可执行文件
└── lib/                         # 虚拟环境库文件
└── README.md                    # 项目说明文档
```

## 环境要求

- Python 3.13.1
- bilibili-api-python库
- aiohttp库（用于网络请求）

## 安装步骤

1. 创建虚拟环境：
   ```bash
   cd /Users/yangchao/cursor/video2bili
   python3.13 -m venv video2bili
   ```

2. 激活虚拟环境：
   ```bash
   cd video2bili
   source bin/activate
   ```

3. 安装依赖：
   ```bash
   pip install bilibili-api-python
   pip install aiohttp
   ```

## 使用方法

### 1. 准备凭据文件

在`src/bili_cookie.txt`文件中填入您的Bilibili账号凭据：

```json
{
    "SESSDATA": "your_sessdata",
    "bili_jct": "your_bili_jct",
    "buvid3": "your_buvid3",
    "DedeUserID": "your_dedeuserid"
}
```

### 2. 准备视频文件

按照以下命名规则准备视频文件和封面文件：
- 视频文件夹名应与视频文件名相同
- 视频文件应放在对应的文件夹中
- 封面文件应以`视频文件名_cover`开头，例如`video_name_cover.jpg`

示例：
```
videos/
└── my_video/
    ├── my_video.mp4
    └── my_video_cover.jpg
```

### 3. 运行上传脚本

```bash
cd /Users/yangchao/cursor/video2bili/video2bili
source bin/activate
cd src
python upload_test_video.py video_folder_name video_file_name
```

示例：
```bash
python upload_test_video.py my_video my_video.mp4
```

## 功能特点

1. **完整的视频上传流程**：支持视频文件上传至B站
2. **进度显示**：动态显示上传进度百分比
3. **元数据支持**：支持填写标题、描述、标签等元数据
4. **错误处理**：包含完整的错误处理机制
5. **模块化设计**：易于扩展和维护
6. **日志记录**：详细的日志记录功能
7. **灵活的文件组织**：支持按视频名称组织文件夹和文件

## 命名规则

### 视频文件夹命名
- 文件夹名应与视频文件名相同（不包含扩展名）

### 封面文件命名
- 封面文件应以`视频文件名_cover`开头
- 支持的图片格式：.jpg, .jpeg, .png, .gif, .bmp, .webp

### 示例
对于视频文件`my_video.mp4`：
```
videos/
└── my_video/                 # 文件夹名与视频文件名相同（不含扩展名）
    ├── my_video.mp4          # 视频文件
    └── my_video_cover.jpg    # 封面文件
```

## 日志功能说明

### 日志级别
- INFO: 一般信息，如上传开始、进度更新、上传完成等
- WARNING: 警告信息，如文件不存在等
- ERROR: 错误信息，如上传失败、异常等

### 日志输出
- 控制台实时显示
- `logs/视频文件名_upload.log` 文件持久化存储

### 日志内容包括
1. **上传过程信息**：
   - 准备上传阶段
   - 分P上传开始和完成
   - 上传进度（每1%显示一次）
   - 详细进度（每10秒显示一次）
   - 进度摘要（每分钟显示一次）
   - 上传完成/失败

2. **文件信息**：
   - 视频文件路径和大小
   - 封面文件路径
   - 上传结果（AV号、BV号等）

3. **时间信息**：
   - 上传开始时间
   - 上传结束时间
   - 总用时
   - 预计剩余时间

4. **错误信息**：
   - 详细的错误堆栈信息
   - 异常处理记录

### 进度显示机制
- **动态进度**：每增加1%显示一次进度
- **详细进度**：每10秒显示一次详细进度，包括预计剩余时间
- **进度摘要**：每分钟显示一次进度摘要

### 结果记录
上传完成后会生成`logs/视频文件名_result.txt`文件，包含：
- 上传时间
- AV号和BV号
- 视频文件和封面文件信息
- 上传用时

## 分区ID参考

常用分区ID：
- 1: 动画
- 13: 番剧
- 167: 国创
- 3: 音乐
- 129: 舞蹈
- 4: 游戏
- 17: 单机游戏
- 36: 知识
- 188: 科技
- 95: 数码

## 注意事项

1. 确保凭据文件中的信息有效且未过期
2. 大视频上传可能需要较长时间，请耐心等待
3. 上传过程中会动态显示进度百分比
4. 请遵守B站的上传规范和版权要求
5. 视频文件夹名应与视频文件名相同
6. 封面文件应以视频文件名_cover开头

## 脚本说明

- `src/upload_test_video.py`：主上传脚本，使用实际凭据和视频文件，包含完整的日志功能
- `src/simple_upload_test.py`：API参考脚本，用于了解bilibili-api的使用方法
- `src/bili_cookie.txt`：Bilibili账号凭据文件
