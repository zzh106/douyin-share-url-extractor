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
    
    # 创建 Session 以保持 Cookie
    session = requests.Session()
    
    # 模拟浏览器请求头（更完整的请求头）
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
    
    try:
        # 先访问主页以获取 Cookie（如果需要）
        try:
            session.get('https://www.douyin.com/', headers=headers, timeout=5)
        except:
            pass  # 忽略主页访问错误，继续尝试 API
        
        while has_more:
            # 构建 API 请求 URL（尝试不同的参数组合）
            url = f"https://www.douyin.com/aweme/v1/web/aweme/post/?device_platform=webapp&aid=6383&channel=channel_pc_web&sec_user_id={sec_user_id}&count=20&max_cursor={max_cursor}&version_code=170400&version_name=17.4.0"
            
            # 发送请求
            response = session.get(url, headers=headers, timeout=15, allow_redirects=True)
            response.raise_for_status()
            
            # 检查响应内容
            if not response.text or response.text.strip() == '':
                # 如果是第一次请求且返回空，可能是需要 Cookie 或 API 限制
                if max_cursor == 0:
                    raise Exception("抖音 API 返回空响应。可能的原因：1) 需要登录 Cookie；2) API 访问被限制；3) sec_user_id 不正确。请尝试在浏览器中登录抖音后，从浏览器开发者工具中复制 Cookie 并配置。")
                else:
                    raise Exception("抖音 API 返回空响应，请稍后重试")
            
            # 解析 JSON 响应
            try:
                data = response.json()
            except ValueError as e:
                # 如果不是 JSON，可能是 HTML 错误页面
                if response.text.startswith('<!DOCTYPE') or response.text.startswith('<html'):
                    raise Exception("抖音 API 返回了错误页面，可能是请求被限制或需要登录。请尝试在浏览器中登录抖音。")
                raise Exception(f"抖音 API 返回的数据格式错误: {str(e)}")
            
            # 检查响应状态
            if data.get('status_code') != 0:
                error_msg = data.get('status_msg', '未知错误')
                status_code = data.get('status_code')
                
                # 常见错误码处理
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
                # 如果没有视频，检查是否真的没有更多数据
                has_more = data.get('has_more', 0)
                if not has_more:
                    break
                # 如果有 has_more 但没有数据，可能是分页问题
                break
            
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
                time.sleep(1)  # 增加等待时间
        
        return all_videos
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"网络请求失败: {str(e)}")
    except KeyError as e:
        raise Exception(f"响应数据格式错误: {str(e)}")
    except Exception as e:
        raise Exception(f"获取视频列表失败: {str(e)}")
    finally:
        session.close()

