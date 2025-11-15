"""
Flask 后端服务
提供抖音视频提取 API
支持 API 方式和浏览器自动化两种方案
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from douyin_api import get_user_all_videos
from browser_scraper import get_user_videos_browser_fallback
import traceback

app = Flask(__name__)
# 允许跨域请求
CORS(app)


@app.route('/api/fetch_user_videos', methods=['POST'])
def fetch_user_videos():
    """
    获取用户的所有视频
    
    接收 JSON: {
        "sec_user_id": "...",           # 必需：用户 sec_user_id 或主页 URL
        "access_token": "...",          # 可选：Douyin 开放平台 access_token
        "cookie": "...",                # 可选：浏览器 Cookie
        "use_browser": false,           # 可选：是否强制使用浏览器方式
        "fallback_to_browser": true     # 可选：API 失败时是否回退到浏览器方式
    }
    
    返回 JSON 列表: [{"title": "...", "share_url": "...", "create_time": "...", "aweme_id": "..."}, ...]
    """
    try:
        # 获取请求数据
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "请求数据为空"}), 400
        
        sec_user_id = data.get('sec_user_id')
        access_token = data.get('access_token')
        cookie = data.get('cookie')
        use_browser = data.get('use_browser', False)
        fallback_to_browser = data.get('fallback_to_browser', True)
        
        if not sec_user_id:
            return jsonify({"error": "缺少 sec_user_id 参数"}), 400
        
        videos = []
        method_used = ""
        
        # 如果强制使用浏览器方式
        if use_browser:
            try:
                print("使用浏览器自动化方式...")
                videos = get_user_videos_browser_fallback(sec_user_id, cookie)
                method_used = "browser"
            except Exception as e:
                error_msg = str(e)
                print(f"浏览器方式失败: {error_msg}")
                return jsonify({"error": f"浏览器自动化失败: {error_msg}"}), 500
        else:
            # 优先使用 API 方式
            try:
                print("尝试使用 API 方式...")
                videos = get_user_all_videos(sec_user_id, access_token, cookie)
                method_used = "api"
            except Exception as e:
                error_msg = str(e)
                print(f"API 方式失败: {error_msg}")
                
                # 如果允许回退到浏览器方式
                if fallback_to_browser:
                    try:
                        print("API 失败，回退到浏览器自动化方式...")
                        videos = get_user_videos_browser_fallback(sec_user_id, cookie)
                        method_used = "browser_fallback"
                    except Exception as browser_error:
                        return jsonify({
                            "error": f"API 方式失败: {error_msg}。浏览器方式也失败: {str(browser_error)}"
                        }), 500
                else:
                    return jsonify({"error": f"API 方式失败: {error_msg}"}), 500
        
        # 返回视频列表，包含使用的方案信息
        return jsonify({
            "videos": videos,
            "count": len(videos),
            "method": method_used
        }), 200
        
    except Exception as e:
        # 捕获所有异常并返回错误信息
        error_msg = str(e)
        print(f"错误: {error_msg}")
        print(traceback.format_exc())
        return jsonify({"error": error_msg}), 500


@app.route('/health', methods=['GET'])
def health():
    """健康检查接口"""
    return jsonify({"status": "ok"}), 200


if __name__ == '__main__':
    print("启动 Flask 服务器...")
    print("API 地址: http://localhost:5001/api/fetch_user_videos")
    app.run(host='0.0.0.0', port=5001, debug=True)

