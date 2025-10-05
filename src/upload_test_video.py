#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bilibili测试视频上传脚本
使用实际的cookie信息和测试视频文件
"""

import asyncio
import os
import json
import logging
import argparse
import sys
from datetime import datetime
from bilibili_api import video_uploader, Credential
import time

def setup_logging(video_name):
    """
    配置日志，保存在logs文件夹下，以视频名称命名日志文件
    
    Args:
        video_name (str): 视频名称，用于日志文件命名
    """
    # 创建logs目录
    log_dir = "../logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # 配置日志
    log_filename = os.path.join(log_dir, f'{video_name}_upload.log')
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

class BilibiliVideoUploader:
    def __init__(self, sessdata, bili_jct, buvid3, dedeuserid):
        """
        初始化Bilibili视频上传器
        
        Args:
            sessdata (str): Bilibili账号的SESSDATA
            bili_jct (str): Bilibili账号的BILI_JCT
            buvid3 (str): Bilibili账号的BUVID3
            dedeuserid (str): Bilibili账号的DEDEUSERID
        """
        self.credential = Credential(
            sessdata=sessdata,
            bili_jct=bili_jct,
            buvid3=buvid3,
            dedeuserid=dedeuserid
        )
        self.uploader = None
        self.start_time = None
        self.total_chunks = 0
        self.uploaded_chunks = 0
        
    def prepare_video(self, video_path, title="", description=""):
        """
        准备视频文件
        
        Args:
            video_path (str): 视频文件路径
            title (str): 分P标题
            description (str): 分P描述
            
        Returns:
            VideoUploaderPage: 视频分P对象
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"视频文件不存在: {video_path}")
            
        # 获取文件大小
        file_size = os.path.getsize(video_path)
        logging.info(f"准备上传视频文件: {video_path}, 大小: {file_size} 字节 ({file_size/1024/1024:.2f} MB)")
            
        page = video_uploader.VideoUploaderPage(
            path=video_path,
            title=title,
            description=description
        )
        return page
    
    def create_video_meta(self, title, desc, tags, tid=17, **kwargs):
        """
        创建视频元数据
        
        Args:
            title (str): 视频标题
            desc (str): 视频描述
            tags (list or str): 视频标签，可以是列表或逗号分隔的字符串
            tid (int): 分区ID，默认为17（单机游戏）
            **kwargs: 其他可选参数
            
        Returns:
            dict: 视频元数据字典
        """
        # 处理标签
        if isinstance(tags, list):
            tag_str = ",".join(tags)
        else:
            tag_str = tags
            
        meta = {
            "title": title,           # 视频标题
            "desc": desc,             # 视频描述
            "tid": tid,               # 分区ID
            "tag": tag_str,           # 视频标签
            "copyright": kwargs.get("copyright", 1),      # 版权标志，1为原创，2为转载
            "source": kwargs.get("source", ""),           # 转载来源
            "no_reprint": kwargs.get("no_reprint", 1),    # 是否禁止转载，1为禁止
            "open_elec": kwargs.get("open_elec", 1),      # 是否开启充电面板，1为开启
            "dynamic": kwargs.get("dynamic", ""),         # 粉丝动态
        }
        
        logging.info(f"创建视频元数据: 标题='{title}', 分区ID={tid}, 标签='{tag_str}'")
        return meta
    
    def find_cover_file(self, video_path):
        """
        根据视频文件路径查找对应的封面文件
        封面文件命名规则：视频文件名_cover.后缀名
        
        Args:
            video_path (str): 视频文件路径
            
        Returns:
            str or None: 封面文件路径，如果找不到则返回None
        """
        # 获取视频文件的目录和文件名
        video_dir = os.path.dirname(video_path)
        video_filename = os.path.basename(video_path)
        video_name, video_ext = os.path.splitext(video_filename)
        
        # 常见的图片后缀名
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        
        # 查找封面文件
        for ext in image_extensions:
            cover_filename = f"{video_name}_cover{ext}"
            cover_path = os.path.join(video_dir, cover_filename)
            if os.path.exists(cover_path):
                logging.info(f"找到封面文件: {cover_path}")
                return cover_path
                
        logging.warning(f"未找到视频 {video_filename} 对应的封面文件")
        return None
    
    def create_uploader(self, pages, meta, cover_path=None):
        """
        创建视频上传器
        
        Args:
            pages (list): 视频分P列表
            meta (dict): 视频元数据
            cover_path (str, optional): 封面图片路径
            
        Returns:
            VideoUploader: 视频上传器对象
        """
        # 处理封面参数
        if cover_path and os.path.exists(cover_path):
            # 如果提供了封面路径且文件存在，则使用该路径
            logging.info(f"使用封面文件: {cover_path}")
            self.uploader = video_uploader.VideoUploader(
                pages=pages,
                meta=meta,
                credential=self.credential,
                cover=cover_path
            )
        else:
            # 不传递cover参数，使用默认值
            logging.info("未提供封面文件或文件不存在，将不使用封面")
            self.uploader = video_uploader.VideoUploader(
                pages=pages,
                meta=meta,
                credential=self.credential
            )
        return self.uploader
    
    async def upload_with_progress(self):
        """
        上传视频并显示进度
        
        Returns:
            dict: 上传结果
        """
        if not self.uploader:
            raise ValueError("请先创建上传器")
            
        # 记录开始时间
        self.start_time = time.time()
        logging.info("开始上传视频...")
        
        # 用于存储上传进度
        self.upload_progress = 0
        self.last_progress_time = time.time()
        self.last_displayed_progress = 0  # 上次显示的进度
        self.last_detailed_progress_time = time.time()  # 上次详细进度显示时间
        
        # 添加事件监听器
        @self.uploader.on(video_uploader.VideoUploaderEvents.PREUPLOAD.value)
        async def on_pre_upload(data):
            logging.info("[准备上传] 正在准备上传...")
            
        @self.uploader.on(video_uploader.VideoUploaderEvents.PRE_PAGE.value)
        async def on_pre_page(data):
            # 安全地获取page_number
            page_number = data.get('page_number', '未知')
            logging.info(f"[分P上传] 正在上传第 {page_number} 个分P...")
            
        @self.uploader.on(video_uploader.VideoUploaderEvents.AFTER_PAGE.value)
        async def on_after_page(data):
            # 安全地获取page_number
            page_number = data.get('page_number', '未知')
            logging.info(f"[分P完成] 第 {page_number} 个分P上传完成!")
            
        @self.uploader.on(video_uploader.VideoUploaderEvents.PRE_CHUNK.value)
        async def on_pre_chunk(data):
            # 记录总块数
            if 'total' in data:
                self.total_chunks = data['total']
                
        @self.uploader.on(video_uploader.VideoUploaderEvents.AFTER_CHUNK.value)
        async def on_after_chunk(data):
            # 更新进度
            if 'percentage' in data:
                self.upload_progress = data["percentage"]
                
                # 动态显示进度（每增加1%显示一次）
                if self.upload_progress - self.last_displayed_progress >= 1:
                    elapsed_time = time.time() - self.start_time
                    logging.info(f"[上传进度] 当前进度: {self.upload_progress:.2f}%, 已用时: {elapsed_time:.1f}秒")
                    self.last_displayed_progress = self.upload_progress
                
                # 更详细的进度显示（每10秒显示一次详细进度）
                current_time = time.time()
                if current_time - self.last_detailed_progress_time >= 10:
                    elapsed_time = current_time - self.start_time
                    # 计算预计剩余时间
                    if self.upload_progress > 0:
                        estimated_total_time = elapsed_time / (self.upload_progress / 100)
                        estimated_remaining_time = estimated_total_time - elapsed_time
                        logging.info(f"[详细进度] 进度: {self.upload_progress:.2f}%, 已用时: {elapsed_time:.1f}秒, 预计剩余: {estimated_remaining_time:.1f}秒")
                    else:
                        logging.info(f"[详细进度] 进度: {self.upload_progress:.2f}%, 已用时: {elapsed_time:.1f}秒")
                    self.last_detailed_progress_time = current_time
                
                # 每隔1分钟显示一次进度摘要
                if current_time - self.last_progress_time >= 60:
                    elapsed_time = current_time - self.start_time
                    logging.info(f"[上传进度摘要] 当前进度: {self.upload_progress:.2f}%, 已用时: {elapsed_time:.1f}秒")
                    self.last_progress_time = current_time
                    
        @self.uploader.on(video_uploader.VideoUploaderEvents.COMPLETED.value)
        async def on_completed(data):
            elapsed_time = time.time() - self.start_time
            logging.info(f"[上传完成] 视频上传完成! 总用时: {elapsed_time:.1f}秒")
            
        @self.uploader.on(video_uploader.VideoUploaderEvents.FAILED.value)
        async def on_failed(data):
            error_msg = data.get('error', '未知错误')
            logging.error(f"[上传失败] 视频上传失败: {error_msg}")
            
        # 启动上传
        try:
            result = await self.uploader.start()
            elapsed_time = time.time() - self.start_time
            logging.info(f"视频上传结束! 总用时: {elapsed_time:.1f}秒")
            return result
        except Exception as e:
            logging.error(f"上传过程中发生错误: {e}")
            raise

async def main(video_folder_name, video_filename):
    """
    主函数 - 上传指定的视频
    
    Args:
        video_folder_name (str): 视频文件夹名称（应与视频文件名相同）
        video_filename (str): 视频文件名
    """
    # 设置日志
    logger = setup_logging(video_filename)
    logger.info(f"=== Bilibili视频上传工具开始运行 ===")
    logger.info(f"视频文件夹: {video_folder_name}")
    logger.info(f"视频文件: {video_filename}")
    
    # 读取cookie信息
    try:
        with open("bili_cookie.txt", "r", encoding="utf-8") as f:
            cookies = json.load(f)
        logger.info("成功读取cookie文件")
    except Exception as e:
        logger.error(f"读取cookie文件失败: {e}")
        return
    
    # 获取凭据信息
    SESSDATA = cookies.get("SESSDATA", "")
    BILI_JCT = cookies.get("bili_jct", "")
    BUVID3 = cookies.get("buvid3", "")
    DEDEUSERID = cookies.get("DedeUserID", "")
    
    # 构建视频文件路径（文件夹名与视频文件名相同）
    VIDEO_FOLDER_PATH = f"../videos/{video_folder_name}"
    VIDEO_PATH = os.path.join(VIDEO_FOLDER_PATH, video_filename)
    
    # 查找封面文件（以视频文件名_cover开头）
    uploader_instance = BilibiliVideoUploader(SESSDATA, BILI_JCT, BUVID3, DEDEUSERID)
    COVER_PATH = uploader_instance.find_cover_file(VIDEO_PATH)
    
    # 检查凭据和文件是否存在
    if not all([SESSDATA, BILI_JCT, BUVID3, DEDEUSERID]):
        logger.error("错误: 请提供完整的Bilibili账号凭据")
        return
        
    if not os.path.exists(VIDEO_PATH):
        logger.error(f"错误: 视频文件不存在: {VIDEO_PATH}")
        return
    
    # 检查视频文件夹是否存在
    if not os.path.exists(VIDEO_FOLDER_PATH):
        logger.error(f"错误: 视频文件夹不存在: {VIDEO_FOLDER_PATH}")
        return
    
    try:
        # 准备视频
        page = uploader_instance.prepare_video(
            video_path=VIDEO_PATH,
            title=f"视频上传测试 - {video_filename}",
            description=f"这是一个使用Python脚本上传的测试视频 - {video_filename}"
        )
        
        # 创建视频元数据
        meta = uploader_instance.create_video_meta(
            title=f"测试视频上传 - {video_filename}",
            desc=f"这是一个使用bilibili-api-python库上传的测试视频，用于验证上传功能是否正常工作。({video_filename})",
            tags=["测试", "Python", "API", "上传", video_filename.split('.')[0]],
            tid=17,  # 单机游戏分区
            copyright=1,  # 原创
            no_reprint=1,  # 禁止转载
            open_elec=1,   # 开启充电
        )
        
        # 创建上传器，使用封面文件
        uploader_instance.create_uploader(pages=[page], meta=meta, cover_path=COVER_PATH)
        
        # 开始上传并显示进度
        result = await uploader_instance.upload_with_progress()
        
        # 输出结果
        logger.info("\n=== 上传结果 ===")
        av_id = result.get('aid', '未知')
        bv_id = result.get('bvid', '未知')
        logger.info(f"AV号: {av_id}")
        logger.info(f"BV号: {bv_id}")
        # CID可能不存在于返回结果中
        if 'cid' in result:
            logger.info(f"CID: {result['cid']}")
        logger.info("视频上传成功!")
        
        # 记录上传结果到文件（保存在logs文件夹下）
        log_dir = "../logs"
        result_file_path = os.path.join(log_dir, f'{video_filename}_result.txt')
        with open(result_file_path, 'w', encoding='utf-8') as f:
            f.write(f"上传时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"AV号: {av_id}\n")
            f.write(f"BV号: {bv_id}\n")
            if 'cid' in result:
                f.write(f"CID: {result['cid']}\n")
            f.write(f"视频文件: {VIDEO_PATH}\n")
            f.write(f"封面文件: {COVER_PATH if COVER_PATH else '无'}\n")
            f.write(f"上传用时: {time.time() - uploader_instance.start_time:.1f}秒\n")
        
        logger.info("=== Bilibili视频上传工具运行结束 ===")
        
    except Exception as e:
        logger.error(f"上传过程中发生错误: {e}")
        import traceback
        logger.error(f"详细错误信息:\n{traceback.format_exc()}")
        return False

def parse_args():
    """
    解析命令行参数
    """
    parser = argparse.ArgumentParser(description="Bilibili视频上传工具")
    parser.add_argument("video_folder", help="视频文件夹名称（应与视频文件名相同）")
    parser.add_argument("video_file", help="视频文件名")
    return parser.parse_args()

# 常用分区ID参考
VIDEO_ZONES = {
    1: "动画",
    13: "番剧",
    167: "国创",
    3: "音乐",
    129: "舞蹈",
    4: "游戏",
    17: "单机游戏",
    36: "知识",
    188: "科技",
    95: "数码",
    189: "运动",
    190: "汽车",
    119: "生活",
    191: "美食",
    192: "动物圈",
    193: "鬼畜",
    194: "时尚",
    195: "资讯",
    196: "娱乐",
    197: "影视",
    198: "纪录片",
    199: "电影",
    200: "电视剧"
}

if __name__ == "__main__":
    # 解析命令行参数
    args = parse_args()
    
    print("Bilibili测试视频上传工具")
    print("注意事项:")
    print(f"1. 确保bili_cookie.txt文件包含有效的Bilibili账号凭据")
    print(f"2. 确保videos/{args.video_folder}/{args.video_file}文件存在")
    print("3. 大视频上传可能需要较长时间，请耐心等待")
    print("4. 上传过程中每1%进度会显示一次，每10秒显示详细进度，每分钟显示进度摘要")
    print("5. 日志将同时输出到控制台和logs/视频名_upload.log文件")
    print("6. 上传结果将保存在logs/视频名_result.txt文件中")
    
    # 运行上传任务
    asyncio.run(main(args.video_folder, args.video_file))
