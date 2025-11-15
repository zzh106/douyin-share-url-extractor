"""
抖音 API 调用模块
用于获取用户的所有公开视频
"""

import requests
import time
from typing import List, Dict


def get_user_all_videos(sec_user_id: str) -> List[Dict[str, str]]:
    """
    获取用户的所有公开视频
    
    Args:
        sec_user_id: 抖音用户的 sec_user_id
        
    Returns:
        视频列表，格式: [{"title": "...", "url": "..."}, ...]
    """
    all_videos = []
    max_cursor = 0
    has_more = 1
    
    # 模拟浏览器请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.douyin.com/',
        'Origin': 'https://www.douyin.com',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
    }
    
    try:
        while has_more:
            # 构建 API 请求 URL
            url = f"https://www.douyin.com/aweme/v1/web/aweme/post/?device_platform=webapp&aid=6383&channel=channel_pc_web&sec_user_id={sec_user_id}&count=20&max_cursor={max_cursor}"
            
            # 发送请求
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # 解析 JSON 响应
            data = response.json()
            
            # 检查响应状态
            if data.get('status_code') != 0:
                error_msg = data.get('status_msg', '未知错误')
                raise Exception(f"API 返回错误: {error_msg}")
            
            # 提取视频列表
            aweme_list = data.get('aweme_list', [])
            
            for aweme in aweme_list:
                # 提取视频标题
                title = aweme.get('desc', '无标题')
                # 提取视频 ID
                aweme_id = aweme.get('aweme_id', '')
                # 构建视频链接
                video_url = f"https://www.douyin.com/video/{aweme_id}"
                
                all_videos.append({
                    "title": title,
                    "url": video_url
                })
            
            # 检查是否还有更多数据
            has_more = data.get('has_more', 0)
            max_cursor = data.get('max_cursor', 0)
            
            # 如果还有更多数据，等待一下再请求（避免请求过快）
            if has_more:
                time.sleep(0.5)
        
        return all_videos
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"网络请求失败: {str(e)}")
    except KeyError as e:
        raise Exception(f"响应数据格式错误: {str(e)}")
    except Exception as e:
        raise Exception(f"获取视频列表失败: {str(e)}")

