#!/usr/bin/env python3
"""
命令行脚本：提取抖音用户视频 share_url
可以直接运行，无需启动 Web 服务
"""

import sys
import json
import argparse
from douyin_api import get_user_all_videos, extract_sec_user_id
from browser_scraper import get_user_videos_browser_fallback


def save_to_file(videos: list, filename: str = 'douyin_videos.txt'):
    """保存视频列表到文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        for i, video in enumerate(videos, 1):
            title = video.get('title', '无标题')
            share_url = video.get('share_url', '')
            create_time = video.get('create_time', '')
            
            if create_time:
                f.write(f"{i}. {title} [{create_time}]\n")
            else:
                f.write(f"{i}. {title}\n")
            f.write(f"{share_url}\n\n")
    
    print(f"✅ 已保存 {len(videos)} 个视频到 {filename}")


def main():
    parser = argparse.ArgumentParser(
        description='提取抖音用户发布的所有视频 share_url',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用 API 方式
  python fetch_videos.py MS4wLjABAAAA...
  
  # 使用浏览器方式
  python fetch_videos.py MS4wLjABAAAA... --use-browser
  
  # 提供 Cookie
  python fetch_videos.py MS4wLjABAAAA... --cookie "your_cookie_string"
  
  # 保存到文件
  python fetch_videos.py MS4wLjABAAAA... --output videos.txt
        """
    )
    
    parser.add_argument('sec_user_id', help='用户的 sec_user_id 或主页 URL')
    parser.add_argument('--access-token', help='Douyin 开放平台 access_token')
    parser.add_argument('--cookie', help='浏览器 Cookie 字符串')
    parser.add_argument('--use-browser', action='store_true', help='强制使用浏览器自动化方式')
    parser.add_argument('--no-fallback', action='store_true', help='API 失败时不回退到浏览器方式')
    parser.add_argument('--output', '-o', help='输出文件名（默认: douyin_videos.txt）')
    parser.add_argument('--json', action='store_true', help='以 JSON 格式输出')
    parser.add_argument('--list-only', action='store_true', help='仅输出 share_url 列表，每行一个')
    
    args = parser.parse_args()
    
    # 提取 sec_user_id
    if args.sec_user_id.startswith('http'):
        sec_user_id = extract_sec_user_id(args.sec_user_id)
        if not sec_user_id:
            print(f"❌ 无法从 URL 中提取 sec_user_id: {args.sec_user_id}")
            sys.exit(1)
    else:
        sec_user_id = args.sec_user_id
    
    print(f"📋 目标用户: {sec_user_id}")
    print("=" * 50)
    
    videos = []
    method_used = ""
    
    try:
        # 如果强制使用浏览器方式
        if args.use_browser:
            print("🌐 使用浏览器自动化方式...")
            videos = get_user_videos_browser_fallback(sec_user_id, args.cookie)
            method_used = "browser"
        else:
            # 优先使用 API 方式
            try:
                print("🔌 尝试使用 API 方式...")
                videos = get_user_all_videos(sec_user_id, args.access_token, args.cookie)
                method_used = "api"
                print("✅ API 方式成功")
            except Exception as e:
                print(f"❌ API 方式失败: {e}")
                
                # 如果允许回退到浏览器方式
                if not args.no_fallback:
                    try:
                        print("🌐 回退到浏览器自动化方式...")
                        videos = get_user_videos_browser_fallback(sec_user_id, args.cookie)
                        method_used = "browser_fallback"
                        print("✅ 浏览器方式成功")
                    except Exception as browser_error:
                        print(f"❌ 浏览器方式也失败: {browser_error}")
                        sys.exit(1)
                else:
                    sys.exit(1)
        
        print("=" * 50)
        print(f"✅ 成功获取 {len(videos)} 个视频")
        print(f"📊 使用方案: {method_used}")
        print("=" * 50)
        
        # 输出结果
        if args.json:
            # JSON 格式输出
            output = {
                "videos": videos,
                "count": len(videos),
                "method": method_used
            }
            print(json.dumps(output, ensure_ascii=False, indent=2))
        elif args.list_only:
            # 仅输出 share_url 列表
            for video in videos:
                print(video.get('share_url', ''))
        else:
            # 详细输出
            for i, video in enumerate(videos, 1):
                title = video.get('title', '无标题')
                share_url = video.get('share_url', '')
                create_time = video.get('create_time', '')
                
                print(f"\n{i}. {title}")
                if create_time:
                    print(f"   发布时间: {create_time}")
                print(f"   {share_url}")
            
            # 保存到文件
            output_file = args.output or 'douyin_videos.txt'
            save_to_file(videos, output_file)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

