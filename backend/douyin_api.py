"""
抖音 API 调用模块 - 使用 Douyin 开放接口
优先使用 API 方式提取视频 share_url
"""

import requests
import time
from typing import List, Dict, Optional
import json


def extract_sec_user_id(user_url: str) -> Optional[str]:
    """
    从用户主页 URL 中提取 sec_user_id
    
    Args:
        user_url: 用户主页 URL，例如: https://www.douyin.com/user/MS4wLjABAAAA...
        
    Returns:
        sec_user_id 或 None
    """
    try:
        if not user_url or not user_url.strip():
            return None
            
        # 如果是完整的 URL
        if user_url.startswith('http'):
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(user_url)
            
            # 从查询参数中获取
            params = parse_qs(parsed.query)
            if 'sec_user_id' in params:
                return params['sec_user_id'][0]
            
            # 从路径中提取
            path_parts = parsed.path.split('/')
            if 'user' in path_parts:
                user_index = path_parts.index('user')
                if user_index + 1 < len(path_parts):
                    sec_user_id = path_parts[user_index + 1]
                    # 移除可能的查询参数
                    if '?' in sec_user_id:
                        sec_user_id = sec_user_id.split('?')[0]
                    return sec_user_id
        else:
            # 直接是 sec_user_id
            return user_url.strip()
            
    except Exception as e:
        print(f"提取 sec_user_id 失败: {e}")
        
    return None


def fetch_user_post_videos_api(
    sec_user_id: str,
    access_token: Optional[str] = None,
    cookie: Optional[str] = None,
    max_retries: int = 3
) -> List[Dict[str, str]]:
    """
    使用 Douyin API 获取用户发布的所有视频
    
    Args:
        sec_user_id: 用户的 sec_user_id
        access_token: Douyin 开放平台 access_token（可选）
        cookie: 浏览器 Cookie（可选）
        max_retries: 最大重试次数
        
    Returns:
        视频列表，格式: [{"title": "...", "share_url": "...", "create_time": "..."}, ...]
    """
    all_videos = []
    max_cursor = 0
    has_more = 1
    retry_count = 0
    
    # 创建 Session 以保持 Cookie
    session = requests.Session()
    
    # 构建请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.douyin.com/',
        'Origin': 'https://www.douyin.com',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }
    
    # 添加 access_token 到请求头
    if access_token:
        headers['access_token'] = access_token
        # 或者添加到 URL 参数
        # 根据 Douyin API 文档调整
    
    # 添加 Cookie
    if cookie:
        headers['Cookie'] = cookie
    
    try:
        # 先访问主页以获取 Cookie（如果需要）
        if not cookie:
            try:
                session.get('https://www.douyin.com/', headers=headers, timeout=5)
            except:
                pass
        
        while has_more and retry_count < max_retries:
            try:
                # 构建 API 请求 URL
                # 使用 Douyin Web API
                url = (
                    f"https://www.douyin.com/aweme/v1/web/aweme/post/"
                    f"?device_platform=webapp"
                    f"&aid=6383"
                    f"&channel=channel_pc_web"
                    f"&sec_user_id={sec_user_id}"
                    f"&count=20"
                    f"&max_cursor={max_cursor}"
                    f"&version_code=170400"
                    f"&version_name=17.4.0"
                )
                
                # 如果使用 access_token，可能需要不同的端点
                if access_token:
                    # 根据 Douyin 开放平台文档调整 URL
                    # 这里假设 access_token 可以作为参数或请求头
                    pass
                
                # 发送请求
                response = session.get(url, headers=headers, timeout=15, allow_redirects=True)
                response.raise_for_status()
                
                # 检查响应内容
                if not response.text or response.text.strip() == '':
                    if max_cursor == 0:
                        # 提供更详细的错误信息
                        raise Exception("抖音 API 返回空响应。这可能是因为：1) 需要登录 Cookie；2) API 端点已变更；3) 网络问题。建议使用浏览器自动化方式或提供有效的 Cookie。")
                    else:
                        break
                
                # 解析 JSON 响应
                try:
                    data = response.json()
                except ValueError as e:
                    if response.text.startswith('<!DOCTYPE') or response.text.startswith('<html'):
                        raise Exception("抖音 API 返回了错误页面，可能需要登录或 Cookie")
                    raise Exception(f"JSON 解析失败: {str(e)}")
                
                # 检查响应状态
                status_code = data.get('status_code', 0)
                if status_code != 0:
                    error_msg = data.get('status_msg', '未知错误')
                    
                    if status_code == 10000:
                        raise Exception("参数错误，请检查 sec_user_id 是否正确")
                    elif status_code == 10001:
                        raise Exception("用户不存在或已注销")
                    elif status_code == 10002:
                        raise Exception("用户设置了隐私，无法访问")
                    else:
                        raise Exception(f"API 返回错误 (code: {status_code}): {error_msg}")
                
                # 提取视频列表
                aweme_list = data.get('aweme_list', [])
                
                if not aweme_list:
                    has_more = data.get('has_more', 0)
                    if not has_more:
                        break
                    max_cursor = data.get('max_cursor', 0)
                    continue
                
                # 处理每个视频
                for aweme in aweme_list:
                    # 提取 share_url（优先使用 share_info.share_url）
                    share_url = None
                    
                    # 方式1: 从 share_info 中获取
                    share_info = aweme.get('share_info', {})
                    if share_info:
                        share_url = share_info.get('share_url') or share_info.get('shareUrl')
                    
                    # 方式2: 直接从 aweme 中获取
                    if not share_url:
                        share_url = aweme.get('share_url') or aweme.get('shareUrl')
                    
                    # 方式3: 从 video 对象中获取
                    if not share_url:
                        video = aweme.get('video', {})
                        if video:
                            share_url = video.get('share_url') or video.get('shareUrl')
                    
                    # 方式4: 如果都没有，构建 share_url
                    if not share_url:
                        aweme_id = aweme.get('aweme_id', '')
                        if aweme_id:
                            share_url = f"https://www.douyin.com/video/{aweme_id}"
                    
                    # 提取其他信息
                    title = aweme.get('desc', '无标题')
                    create_time = aweme.get('create_time', 0)
                    
                    # 格式化创建时间
                    create_time_str = ""
                    if create_time:
                        try:
                            from datetime import datetime
                            dt = datetime.fromtimestamp(create_time)
                            create_time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                        except:
                            create_time_str = str(create_time)
                    
                    if share_url:
                        all_videos.append({
                            "title": title,
                            "share_url": share_url,
                            "create_time": create_time_str,
                            "aweme_id": aweme.get('aweme_id', '')
                        })
                
                # 检查是否还有更多数据
                has_more = data.get('has_more', 0)
                max_cursor = data.get('max_cursor', 0)
                
                # 如果还有更多数据，等待一下再请求
                if has_more:
                    time.sleep(1)
                
                # 重置重试计数（成功请求后）
                retry_count = 0
                
            except requests.exceptions.RequestException as e:
                retry_count += 1
                if retry_count >= max_retries:
                    raise Exception(f"网络请求失败，已重试 {max_retries} 次: {str(e)}")
                print(f"请求失败，重试 {retry_count}/{max_retries}: {e}")
                time.sleep(2)
            except Exception as e:
                # 其他错误直接抛出
                raise
        
        return all_videos
        
    except Exception as e:
        raise Exception(f"获取视频列表失败: {str(e)}")
    finally:
        session.close()


def get_user_all_videos(
    sec_user_id: str,
    access_token: Optional[str] = None,
    cookie: Optional[str] = None
) -> List[Dict[str, str]]:
    """
    获取用户的所有公开视频（主入口函数）
    
    Args:
        sec_user_id: 用户的 sec_user_id 或用户主页 URL
        access_token: Douyin 开放平台 access_token（可选）
        cookie: 浏览器 Cookie（可选）
        
    Returns:
        视频列表，格式: [{"title": "...", "share_url": "...", "create_time": "..."}, ...]
    """
    # 如果输入是 URL，先提取 sec_user_id
    if sec_user_id.startswith('http'):
        sec_user_id = extract_sec_user_id(sec_user_id) or sec_user_id
    
    if not sec_user_id:
        raise Exception("无法提取 sec_user_id，请提供有效的用户主页 URL 或 sec_user_id")
    
    # 使用 API 方式获取
    return fetch_user_post_videos_api(sec_user_id, access_token, cookie)
