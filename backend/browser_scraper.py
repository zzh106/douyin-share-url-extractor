"""
浏览器自动化备用方案 - 使用 Playwright 提取视频 share_url
当 API 方式不可用时使用此方案
"""

from typing import List, Dict, Optional
import re
import time
from urllib.parse import urljoin, urlparse


def extract_sec_user_id_from_url(user_url: str) -> Optional[str]:
    """从用户主页 URL 中提取 sec_user_id"""
    try:
        if not user_url or not user_url.strip():
            return None
        
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
                    if '?' in sec_user_id:
                        sec_user_id = sec_user_id.split('?')[0]
                    return sec_user_id
        else:
            return user_url.strip()
    except Exception as e:
        print(f"提取 sec_user_id 失败: {e}")
    
    return None


def fetch_user_videos_browser(
    sec_user_id: str,
    cookies: Optional[str] = None,
    headless: bool = True,
    max_scroll: int = 50
) -> List[Dict[str, str]]:
    """
    使用 Playwright 浏览器自动化提取用户视频
    
    Args:
        sec_user_id: 用户的 sec_user_id 或用户主页 URL
        cookies: 浏览器 Cookie 字符串（可选，用于保持登录状态）
        headless: 是否使用无头模式
        max_scroll: 最大滚动次数
        
    Returns:
        视频列表，格式: [{"title": "...", "share_url": "...", "create_time": "..."}, ...]
    """
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
    except ImportError:
        raise Exception("Playwright 未安装，请运行: pip install playwright && playwright install chromium")
    
    # 如果输入是 URL，先提取 sec_user_id
    if sec_user_id.startswith('http'):
        sec_user_id = extract_sec_user_id_from_url(sec_user_id) or sec_user_id
    
    if not sec_user_id:
        raise Exception("无法提取 sec_user_id")
    
    all_videos = []
    video_urls = set()  # 用于去重
    
    try:
        with sync_playwright() as p:
            # 启动浏览器
            browser = p.chromium.launch(headless=headless)
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            # 如果有 Cookie，添加到浏览器上下文
            if cookies:
                try:
                    # 解析 Cookie 字符串
                    cookie_list = []
                    for item in cookies.split(';'):
                        item = item.strip()
                        if '=' in item:
                            key, value = item.split('=', 1)
                            cookie_list.append({
                                'name': key.strip(),
                                'value': value.strip(),
                                'domain': '.douyin.com',
                                'path': '/'
                            })
                    if cookie_list:
                        context.add_cookies(cookie_list)
                except Exception as e:
                    print(f"添加 Cookie 失败: {e}")
            
            page = context.new_page()
            
            # 构建用户主页 URL
            user_url = f"https://www.douyin.com/user/{sec_user_id}"
            
            print(f"正在访问用户主页: {user_url}")
            page.goto(user_url, wait_until='networkidle', timeout=30000)
            
            # 等待页面加载
            time.sleep(2)
            
            # 滚动页面加载所有视频
            print("正在滚动页面加载所有视频...")
            scroll_count = 0
            last_height = 0
            
            while scroll_count < max_scroll:
                # 获取当前页面高度
                current_height = page.evaluate("document.body.scrollHeight")
                
                # 滚动到底部
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                
                # 等待新内容加载
                time.sleep(2)
                
                # 检查是否已经到底
                new_height = page.evaluate("document.body.scrollHeight")
                if new_height == last_height:
                    # 尝试点击"加载更多"按钮（如果有）
                    try:
                        load_more = page.query_selector('text=加载更多')
                        if load_more:
                            load_more.click()
                            time.sleep(2)
                    except:
                        pass
                    
                    # 如果高度没有变化，可能已经加载完
                    if new_height == current_height:
                        break
                
                last_height = new_height
                scroll_count += 1
                print(f"已滚动 {scroll_count} 次，当前高度: {new_height}")
            
            # 提取所有视频链接
            print("正在提取视频链接...")
            
            # 方法1: 查找所有指向 /video/ 的链接
            video_links = page.query_selector_all('a[href*="/video/"]')
            
            for link in video_links:
                try:
                    href = link.get_attribute('href')
                    if href:
                        # 转换为完整 URL
                        if href.startswith('/'):
                            full_url = urljoin('https://www.douyin.com', href)
                        elif href.startswith('http'):
                            full_url = href
                        else:
                            continue
                        
                        # 提取视频 ID
                        match = re.search(r'/video/(\d+)', full_url)
                        if match:
                            video_id = match.group(1)
                            if full_url not in video_urls:
                                video_urls.add(full_url)
                                
                                # 尝试获取视频标题
                                title = "无标题"
                                try:
                                    # 查找标题元素（根据实际页面结构调整）
                                    title_elem = link.query_selector('text')
                                    if title_elem:
                                        title = title_elem.inner_text()
                                except:
                                    pass
                                
                                all_videos.append({
                                    "title": title,
                                    "share_url": full_url,
                                    "create_time": "",
                                    "aweme_id": video_id
                                })
                except Exception as e:
                    print(f"提取链接失败: {e}")
                    continue
            
            # 方法2: 从页面中提取所有视频 URL（通过 JavaScript）
            try:
                js_videos = page.evaluate("""
                    () => {
                        const videos = [];
                        const links = document.querySelectorAll('a[href*="/video/"]');
                        links.forEach(link => {
                            const href = link.getAttribute('href');
                            if (href) {
                                const fullUrl = href.startsWith('/') 
                                    ? 'https://www.douyin.com' + href 
                                    : href;
                                videos.push({
                                    url: fullUrl,
                                    title: link.textContent || '无标题'
                                });
                            }
                        });
                        return videos;
                    }
                """)
                
                for video in js_videos:
                    url = video.get('url', '')
                    if url and url not in video_urls:
                        video_urls.add(url)
                        match = re.search(r'/video/(\d+)', url)
                        video_id = match.group(1) if match else ''
                        
                        all_videos.append({
                            "title": video.get('title', '无标题'),
                            "share_url": url,
                            "create_time": "",
                            "aweme_id": video_id
                        })
            except Exception as e:
                print(f"JavaScript 提取失败: {e}")
            
            browser.close()
            
    except PlaywrightTimeoutError:
        raise Exception("页面加载超时，请检查网络连接或 sec_user_id 是否正确")
    except Exception as e:
        raise Exception(f"浏览器自动化失败: {str(e)}")
    
    # 去重并返回
    unique_videos = []
    seen_urls = set()
    for video in all_videos:
        url = video.get('share_url', '')
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_videos.append(video)
    
    return unique_videos


def get_user_videos_browser_fallback(
    sec_user_id: str,
    cookies: Optional[str] = None
) -> List[Dict[str, str]]:
    """
    浏览器自动化备用方案入口
    
    Args:
        sec_user_id: 用户的 sec_user_id 或用户主页 URL
        cookies: 浏览器 Cookie 字符串（可选）
        
    Returns:
        视频列表，格式: [{"title": "...", "share_url": "...", "create_time": "..."}, ...]
    """
    return fetch_user_videos_browser(sec_user_id, cookies, headless=True)

