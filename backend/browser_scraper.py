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
                
                # 滚动页面加载所有视频（实时提取模式）
                print("=" * 60)
                print("🚀 开始滚动页面加载所有视频...")
                print("=" * 60)
                scroll_count = 0
                last_height = 0
                last_video_count = 0
                no_change_count = 0  # 连续无变化次数
                max_no_change = 10  # 连续无变化次数阈值（增加到10次，更保守）
                
                # 大幅增加最大滚动次数，确保能加载所有视频
                effective_max_scroll = max(max_scroll, 2000)  # 至少2000次，确保能加载2000+视频
                
                print(f"📊 最大滚动次数: {effective_max_scroll}")
                print(f"⏱️  开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                print("-" * 60)
                
                while scroll_count < effective_max_scroll:
                    # 在每次滚动前，先提取当前已加载的视频（实时提取）
                    try:
                        current_videos = page.evaluate("""
                            () => {
                                const videos = [];
                                // 查找所有视频链接
                                const links = document.querySelectorAll('a[href*="/video/"]');
                                
                                links.forEach(link => {
                                    const href = link.getAttribute('href');
                                    if (href) {
                                        const fullUrl = href.startsWith('/') 
                                            ? 'https://www.douyin.com' + href 
                                            : href;
                                        
                                        let title = '无标题';
                                        
                                        // 方法1: 查找视频卡片容器（抖音常见的容器类名）
                                        const card = link.closest('[class*="item"], [class*="card"], [class*="video"], [data-e2e], [class*="VideoItem"], [class*="video-item"]');
                                        
                                        if (card) {
                                            // 在卡片中查找描述文本，使用多种选择器
                                            const selectors = [
                                                '[class*="desc"]',
                                                '[class*="title"]',
                                                '[class*="text"]',
                                                '[class*="content"]',
                                                '[class*="info"]',
                                                'span[class*="text"]',
                                                'div[class*="desc"]',
                                                'p[class*="desc"]',
                                                '[data-e2e*="desc"]',
                                                '[data-e2e*="title"]'
                                            ];
                                            
                                            for (let selector of selectors) {
                                                const elems = card.querySelectorAll(selector);
                                                for (let elem of elems) {
                                                    const text = elem.textContent?.trim();
                                                    // 过滤条件：有文本、长度合理、不是URL、不是纯数字、不是"无标题"
                                                    // 过滤无效文本：登录、热门、关注、点赞、评论等
                                                    const invalidTexts = ['登录', '热门', '关注', '点赞', '评论', '分享', '收藏', 
                                                                          '热门:', '登录:', '关注:', '点赞:', '评论:', '分享:', 
                                                                          '热门推荐', '登录账号', '立即登录', '请登录'];
                                                    const isInvalid = invalidTexts.some(invalid => text.includes(invalid));
                                                    
                                                    if (text && 
                                                        text.length >= 2 && 
                                                        text.length <= 200 && 
                                                        !text.includes('http') && 
                                                        !text.match(/^\\d+$/) &&
                                                        text !== '无标题' &&
                                                        !text.match(/^[\\s\\n\\r]*$/) &&
                                                        !isInvalid) {
                                                        // 检查是否包含太多换行（可能是多个元素合并的文本）
                                                        const lineCount = (text.match(/\\n/g) || []).length;
                                                        if (lineCount <= 3) {
                                                            title = text;
                                                            break;
                                                        }
                                                    }
                                                }
                                                if (title !== '无标题') break;
                                            }
                                            
                                            // 如果还没找到，尝试查找所有文本节点
                                            if (title === '无标题') {
                                                const allText = card.textContent?.trim();
                                                if (allText && allText.length > 0) {
                                                    // 提取第一行或前100个字符作为标题
                                                    const firstLine = allText.split('\\n')[0] || allText.substring(0, 100);
                                                    if (firstLine.length >= 2 && firstLine.length <= 200 && !firstLine.includes('http')) {
                                                        title = firstLine.trim();
                                                    }
                                                }
                                            }
                                        }
                                        
                                        // 方法2: 从链接的父元素向上查找
                                        if (title === '无标题') {
                                            let current = link.parentElement;
                                            let depth = 0;
                                            while (current && depth < 8) {
                                                // 查找当前元素的所有子元素中的文本
                                                const textElems = current.querySelectorAll('span, div, p, h1, h2, h3, h4');
                                                for (let elem of textElems) {
                                                    const text = elem.textContent?.trim();
                                                    // 过滤无效文本
                                                    const invalidTexts = ['登录', '热门', '关注', '点赞', '评论', '分享', '收藏', 
                                                                          '热门:', '登录:', '关注:', '点赞:', '评论:', '分享:', 
                                                                          '热门推荐', '登录账号', '立即登录', '请登录'];
                                                    const isInvalid = invalidTexts.some(invalid => text.includes(invalid));
                                                    
                                                    if (text && 
                                                        text.length >= 2 && 
                                                        text.length <= 200 && 
                                                        !text.includes('http') &&
                                                        !text.match(/^\\d+$/) &&
                                                        text !== '无标题' &&
                                                        !isInvalid) {
                                                        // 确保这个文本不在链接内
                                                        if (!link.contains(elem)) {
                                                            title = text;
                                                            break;
                                                        }
                                                    }
                                                }
                                                if (title !== '无标题') break;
                                                current = current.parentElement;
                                                depth++;
                                            }
                                        }
                                        
                                        // 方法3: 从链接的属性获取
                                        if (title === '无标题') {
                                            title = link.getAttribute('aria-label') || 
                                                   link.getAttribute('title') || 
                                                   link.getAttribute('data-title') ||
                                                   '无标题';
                                            if (title && (title.length < 2 || title.includes('http'))) {
                                                title = '无标题';
                                            }
                                        }
                                        
                                        videos.push({
                                            url: fullUrl,
                                            title: title || '无标题'
                                        });
                                    }
                                });
                                return videos;
                            }
                        """)
                        
                        # 添加新发现的视频
                        for video in current_videos:
                            url = video.get('url', '')
                            if url and url not in video_urls:
                                video_urls.add(url)
                                match = re.search(r'/video/(\d+)', url)
                                video_id = match.group(1) if match else ''
                                
                                all_videos.append({
                                    "title": video.get('title', '无标题').strip() or '无标题',
                                    "share_url": url,
                                    "create_time": "",
                                    "aweme_id": video_id
                                })
                        
                        current_video_count = len(all_videos)
                        if current_video_count > last_video_count:
                            new_videos = current_video_count - last_video_count
                            progress = (current_video_count / 2000 * 100) if current_video_count < 2000 else 100
                            print(f"✅ 滚动 {scroll_count} 次 | 新增 {new_videos} 个 | 总计 {current_video_count} 个视频 | 进度 {progress:.1f}%")
                            last_video_count = current_video_count
                            no_change_count = 0  # 有新视频，重置计数
                        elif scroll_count > 0 and scroll_count % 20 == 0:
                            # 每20次滚动显示一次状态
                            print(f"⏳ 滚动 {scroll_count} 次 | 当前 {current_video_count} 个视频 | 无新视频")
                    except Exception as e:
                        print(f"⚠️ 实时提取视频时出错: {e}")
                    
                    # 获取当前页面高度
                    try:
                        current_height = page.evaluate("document.body.scrollHeight || document.documentElement.scrollHeight")
                    except:
                        current_height = 0
                    
                    # 滚动到底部（使用平滑滚动，更接近真实用户行为）
                    page.evaluate("""
                        () => {
                            window.scrollTo({
                                top: document.body.scrollHeight || document.documentElement.scrollHeight,
                                behavior: 'smooth'
                            });
                        }
                    """)
                    
                    # 等待新内容加载（根据视频数量调整等待时间）
                    wait_time = 2 if current_video_count < 100 else 3
                    time.sleep(wait_time)
                    
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
                        
                        # 如果连续多次高度和视频数量都没有变化，可能已经加载完
                        if no_change_count >= max_no_change:
                            print("-" * 60)
                            print(f"⏹️  连续 {no_change_count} 次滚动无新内容")
                            print(f"📊 当前已提取 {len(all_videos)} 个视频")
                            print(f"🛑 停止滚动")
                            print("-" * 60)
                            break
                    else:
                        # 页面高度有变化，重置无变化计数
                        if no_change_count > 0:
                            print(f"📈 页面高度变化: {last_height} -> {new_height}，继续滚动...")
                        no_change_count = 0  # 有变化，重置计数
                    
                    last_height = new_height
                    scroll_count += 1
                    
                    # 每50次滚动显示一次详细状态
                    if scroll_count % 50 == 0:
                        elapsed_time = time.strftime('%H:%M:%S', time.gmtime(scroll_count * wait_time))
                        print(f"📊 滚动进度: {scroll_count}/{effective_max_scroll} ({scroll_count/effective_max_scroll*100:.1f}%) | 已提取 {len(all_videos)} 个视频 | 页面高度: {new_height}px")
                
                # 最终提取：确保所有视频都被提取（作为补充）
                print("-" * 60)
                print("🔍 正在进行最终提取，确保不遗漏任何视频...")
                print("-" * 60)
                try:
                    final_videos = page.evaluate("""
                        () => {
                            const videos = [];
                            const links = document.querySelectorAll('a[href*="/video/"]');
                            
                            links.forEach(link => {
                                const href = link.getAttribute('href');
                                if (href) {
                                    const fullUrl = href.startsWith('/') 
                                        ? 'https://www.douyin.com' + href 
                                        : href;
                                    
                                    let title = '无标题';
                                    
                                    // 查找视频卡片容器
                                    const card = link.closest('[class*="item"], [class*="card"], [class*="video"], [data-e2e], [class*="VideoItem"], [class*="video-item"]');
                                    
                                    if (card) {
                                        // 在卡片中查找描述文本，使用多种选择器
                                        const selectors = [
                                            '[class*="desc"]',
                                            '[class*="title"]',
                                            '[class*="text"]',
                                            '[class*="content"]',
                                            '[class*="info"]',
                                            'span[class*="text"]',
                                            'div[class*="desc"]',
                                            'p[class*="desc"]',
                                            '[data-e2e*="desc"]',
                                            '[data-e2e*="title"]'
                                        ];
                                        
                                        for (let selector of selectors) {
                                            const elems = card.querySelectorAll(selector);
                                            for (let elem of elems) {
                                                const text = elem.textContent?.trim();
                                                if (text && 
                                                    text.length >= 2 && 
                                                    text.length <= 200 && 
                                                    !text.includes('http') && 
                                                    !text.match(/^\\d+$/) &&
                                                    text !== '无标题' &&
                                                    !text.match(/^[\\s\\n\\r]*$/)) {
                                                    const lineCount = (text.match(/\\n/g) || []).length;
                                                    if (lineCount <= 3) {
                                                        title = text;
                                                        break;
                                                    }
                                                }
                                            }
                                            if (title !== '无标题') break;
                                        }
                                        
                                        // 如果还没找到，尝试查找所有文本节点
                                        if (title === '无标题') {
                                            const allText = card.textContent?.trim();
                                            if (allText && allText.length > 0) {
                                                const firstLine = allText.split('\\n')[0] || allText.substring(0, 100);
                                                if (firstLine.length >= 2 && firstLine.length <= 200 && !firstLine.includes('http')) {
                                                    title = firstLine.trim();
                                                }
                                            }
                                        }
                                    }
                                    
                                    // 从链接的父元素向上查找
                                    if (title === '无标题') {
                                        let current = link.parentElement;
                                        let depth = 0;
                                        while (current && depth < 8) {
                                            const textElems = current.querySelectorAll('span, div, p, h1, h2, h3, h4');
                                            for (let elem of textElems) {
                                                const text = elem.textContent?.trim();
                                                    // 过滤无效文本
                                                    const invalidTexts = ['登录', '热门', '关注', '点赞', '评论', '分享', '收藏', 
                                                                          '热门:', '登录:', '关注:', '点赞:', '评论:', '分享:', 
                                                                          '热门推荐', '登录账号', '立即登录', '请登录'];
                                                    const isInvalid = invalidTexts.some(invalid => text.includes(invalid));
                                                    
                                                    if (text && 
                                                        text.length >= 2 && 
                                                        text.length <= 200 && 
                                                        !text.includes('http') &&
                                                        !text.match(/^\\d+$/) &&
                                                        text !== '无标题' &&
                                                        !isInvalid) {
                                                        if (!link.contains(elem)) {
                                                            title = text;
                                                            break;
                                                        }
                                                    }
                                            }
                                            if (title !== '无标题') break;
                                            current = current.parentElement;
                                            depth++;
                                        }
                                    }
                                    
                                    // 从链接的属性获取
                                    if (title === '无标题') {
                                        title = link.getAttribute('aria-label') || 
                                               link.getAttribute('title') || 
                                               link.getAttribute('data-title') ||
                                               '无标题';
                                        if (title && (title.length < 2 || title.includes('http'))) {
                                            title = '无标题';
                                        }
                                    }
                                    
                                    videos.push({
                                        url: fullUrl,
                                        title: title || '无标题'
                                    });
                                }
                            });
                            return videos;
                        }
                    """)
                    
                    # 添加最终发现的视频（去重）
                    for video in final_videos:
                        url = video.get('url', '')
                        if url and url not in video_urls:
                            video_urls.add(url)
                            match = re.search(r'/video/(\d+)', url)
                            video_id = match.group(1) if match else ''
                            
                            title = video.get('title', '无标题').strip()
                            if not title or title == '无标题':
                                # 如果标题还是无标题，尝试从页面DOM中查找
                                try:
                                    # 这里可以添加更复杂的标题查找逻辑
                                    pass
                                except:
                                    pass
                            
                            all_videos.append({
                                "title": title or '无标题',
                                "share_url": url,
                                "create_time": "",
                                "aweme_id": video_id
                            })
                except Exception as e:
                    print(f"最终提取失败: {e}")
                
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
    
    print("=" * 60)
    print(f"✅ 提取完成！")
    print(f"📊 总共提取 {len(unique_videos)} 个视频")
    print(f"⏱️  结束时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
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
    # 使用更大的滚动次数，确保能加载所有视频
    return fetch_user_videos_browser(sec_user_id, cookies, headless=True, max_scroll=1000)

