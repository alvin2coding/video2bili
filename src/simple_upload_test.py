#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简化版Bilibili视频上传测试脚本
用于验证基本的上传功能
"""

import asyncio
from bilibili_api import video_uploader, Credential

# 显示bilibili_api版本信息
import bilibili_api
print(f"bilibili-api-python版本: {bilibili_api.__version__ if hasattr(bilibili_api, '__version__') else '未知'}")

# 查看VideoUploader类的文档
print("\n=== VideoUploader类信息 ===")
print(f"类文档: {video_uploader.VideoUploader.__doc__}")

# 查看VideoUploaderPage类的文档
print("\n=== VideoUploaderPage类信息 ===")
print(f"类文档: {video_uploader.VideoUploaderPage.__doc__}")

# 查看VideoMeta的结构
print("\n=== VideoMeta结构 ===")
# 通过查看源码我们知道VideoMeta是一个字典，包含以下字段：
video_meta_fields = [
    "title",        # 视频标题
    "desc",         # 视频描述
    "tid",          # 分区ID
    "tag",          # 标签
    "copyright",    # 版权标志
    "source",       # 转载来源
    "cover",        # 封面URL
    "no_reprint",   # 是否禁止转载
    "open_elec",    # 是否开启充电面板
    "dynamic",      # 粉丝动态
]

print("VideoMeta应包含以下字段:")
for field in video_meta_fields:
    print(f"  - {field}")

# 查看Credential类的文档
print("\n=== Credential类信息 ===")
print(f"类文档: {Credential.__doc__}")

# 显示使用说明
print("\n=== 使用说明 ===")
print("要使用此脚本上传视频，您需要:")
print("1. 获取Bilibili账号的登录凭据（SESSDATA, BILI_JCT, BUVID3, DEDEUSERID）")
print("2. 准备要上传的视频文件")
print("3. 填写视频元数据（标题、描述、标签等）")
print("4. 运行上传脚本")

# 示例代码结构
example_code = '''
# 示例代码结构:
import asyncio
from bilibili_api import video_uploader, Credential

# 创建凭据
credential = Credential(
    sessdata="你的SESSDATA",
    bili_jct="你的BILI_JCT", 
    buvid3="你的BUVID3",
    dedeuserid="你的DEDEUSERID"
)

# 创建分P
page = video_uploader.VideoUploaderPage(
    path="视频文件路径.mp4",
    title="分P标题",
    description="分P描述"
)

# 创建视频元数据
meta = {
    "title": "视频标题",
    "desc": "视频描述",
    "tid": 17,  # 分区ID
    "tag": "标签1,标签2,标签3",
    "copyright": 1,
    "source": "",
    "cover": "",
    "no_reprint": 1,
    "open_elec": 1,
    "dynamic": ""
}

# 创建上传器
uploader = video_uploader.VideoUploader(
    pages=[page],
    meta=meta,
    credential=credential
)

# 添加事件监听器
@uploader.on("PREUPLOAD")
async def on_pre_upload(data):
    print("准备上传...")

@uploader.on("UPLOADING")
async def on_uploading(data):
    print(f"上传进度: {data['percentage']:.2f}%")

# 启动上传
asyncio.run(uploader.start())
'''

print("\n=== 示例代码 ===")
print(example_code)

if __name__ == "__main__":
    print("\n此脚本仅用于展示bilibili-api-python的视频上传功能结构")
    print("请根据实际需求修改并使用完整版上传脚本")
