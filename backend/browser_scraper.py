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
    max_scroll: int = 50,
    max_retries: int = 2
) -> List[Dict[str, str]]:
    """
    使用 Playwright 浏览器自动化提取用户视频
    
    Args:
        sec_user_id: 用户的 sec_user_id 或用户主页 URL
        cookies: 浏览器 Cookie 字符串（可选，用于保持登录状态）
        headless: 是否使用无头模式
        max_scroll: 最大滚动次数
        max_retries: 最大重试次数
        
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
        raise Exception("无法提取 sec_user_id，请检查输入的 URL 或 sec_user_id 是否正确")
    
    all_videos = []
    video_urls = set()  # 用于去重
    
    # 重试机制
    for retry in range(max_retries):
        try:
            with sync_playwright() as p:
                # 启动浏览器，增加启动超时时间
                browser = p.chromium.launch(
                    headless=headless,
                    args=['--disable-blink-features=AutomationControlled']  # 隐藏自动化特征
                )
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    locale='zh-CN',
                    timezone_id='Asia/Shanghai'
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
                            print(f"已添加 {len(cookie_list)} 个 Cookie")
                    except Exception as e:
                        print(f"添加 Cookie 失败: {e}")
                
                page = context.new_page()
                
                # 构建用户主页 URL
                user_url = f"https://www.douyin.com/user/{sec_user_id}"
                
                print(f"正在访问用户主页: {user_url} (尝试 {retry + 1}/{max_retries})")
                
                # 使用更宽松的等待策略，增加超时时间到 60 秒
                # 'load' 等待页面加载完成，比 'networkidle' 更宽松
                try:
                    page.goto(user_url, wait_until='load', timeout=60000)
                except PlaywrightTimeoutError:
                    # 如果 load 超时，尝试使用 domcontentloaded（更宽松）
                    print("load 超时，尝试使用 domcontentloaded...")
                    try:
                        page.goto(user_url, wait_until='domcontentloaded', timeout=60000)
                    except PlaywrightTimeoutError:
                        raise Exception(f"页面加载超时（已等待 60 秒）。可能原因：1) 网络连接慢或不稳定；2) sec_user_id 不正确；3) 需要登录 Cookie；4) 抖音服务器响应慢。建议：检查网络连接、提供有效的 Cookie 或稍后重试。")
            
                # 等待页面加载和内容渲染
                print("等待页面内容加载...")
                time.sleep(3)
                
                # 检查页面是否正常加载（检查是否有错误提示或需要登录）
                page_title = page.title()
                page_url = page.url
                print(f"页面标题: {page_title}")
                print(f"当前 URL: {page_url}")
                
                # 检查是否需要登录
                try:
                    login_required = page.query_selector('text=登录') or page.query_selector('text=请登录')
                    if login_required:
                        print("⚠️ 检测到可能需要登录")
                except:
                    pass
                
                # 滚动页面加载所有视频
                print("正在滚动页面加载所有视频...")
                scroll_count = 0
                last_height = 0
                no_change_count = 0  # 连续无变化次数
                
                while scroll_count < max_scroll:
                    # 获取当前页面高度
                    try:
                        current_height = page.evaluate("document.body.scrollHeight || document.documentElement.scrollHeight")
                    except:
                        current_height = 0
                    
                    # 滚动到底部
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight || document.documentElement.scrollHeight)")
                    
                    # 等待新内容加载（增加等待时间）
                    time.sleep(3)
                    
                    # 检查是否已经到底
                    try:
                        new_height = page.evaluate("document.body.scrollHeight || document.documentElement.scrollHeight")
                    except:
                        new_height = current_height
                    
                    if new_height == last_height:
                        no_change_count += 1
                        # 尝试点击"加载更多"按钮（如果有）
                        try:
                            load_more = page.query_selector('text=加载更多') or page.query_selector('button:has-text("加载更多")')
                            if load_more:
                                load_more.click()
                                time.sleep(3)
                                no_change_count = 0  # 重置计数
                        except:
                            pass
                        
                        # 如果连续3次高度没有变化，可能已经加载完
                        if no_change_count >= 3:
                            print(f"连续 {no_change_count} 次滚动无新内容，停止滚动")
                            break
                    else:
                        no_change_count = 0  # 有变化，重置计数
                    
                    last_height = new_height
                    scroll_count += 1
                    if scroll_count % 5 == 0:  # 每5次打印一次
                        print(f"已滚动 {scroll_count} 次，当前高度: {new_height}")
                
                # 提取所有视频链接
                print("正在提取视频链接...")
                
                # 方法1: 查找所有指向 /video/ 的链接
                try:
                    video_links = page.query_selector_all('a[href*="/video/"]')
                except Exception as e:
                    print(f"查找视频链接失败: {e}")
                    video_links = []
                
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
                
                # 如果成功提取到视频，返回结果
                if all_videos:
                    break
                elif retry < max_retries - 1:
                    print(f"未提取到视频，准备重试 ({retry + 1}/{max_retries})...")
                    time.sleep(2)
                    
        except PlaywrightTimeoutError as e:
            error_msg = f"页面加载超时（已等待 60 秒）。可能原因：1) 网络连接慢或不稳定；2) sec_user_id 不正确；3) 需要登录 Cookie；4) 抖音服务器响应慢。建议：检查网络连接、提供有效的 Cookie 或稍后重试。"
            if retry < max_retries - 1:
                print(f"⚠️ {error_msg}")
                print(f"准备重试 ({retry + 1}/{max_retries})...")
                time.sleep(3)
                continue
            else:
                raise Exception(error_msg)
        except Exception as e:
            error_msg = f"浏览器自动化失败: {str(e)}"
            if retry < max_retries - 1:
                print(f"⚠️ {error_msg}")
                print(f"准备重试 ({retry + 1}/{max_retries})...")
                time.sleep(3)
                continue
            else:
                raise Exception(error_msg)
    
    # 如果所有重试都失败且没有视频，返回空列表而不是抛出异常
    if not all_videos:
        print("⚠️ 未提取到任何视频，返回空列表")
    
    # 去重并返回
    unique_videos = []
    seen_urls = set()
    for video in all_videos:
        url = video.get('share_url', '')
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_videos.append(video)
    
    print(f"✅ 成功提取 {len(unique_videos)} 个视频")
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

