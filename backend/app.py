"""
Flask 后端服务
提供抖音视频提取 API
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from douyin_api import get_user_all_videos
import traceback

app = Flask(__name__)
# 允许跨域请求
CORS(app)


@app.route('/api/fetch_user_videos', methods=['POST'])
def fetch_user_videos():
    """
    获取用户的所有视频
    
    接收 JSON: {"sec_user_id": "..."}
    返回 JSON 列表: [{"title": "...", "url": "..."}, ...]
    """
    try:
        # 获取请求数据
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "请求数据为空"}), 400
        
        sec_user_id = data.get('sec_user_id')
        
        if not sec_user_id:
            return jsonify({"error": "缺少 sec_user_id 参数"}), 400
        
        # 调用抖音 API 获取视频列表
        videos = get_user_all_videos(sec_user_id)
        
        # 返回视频列表
        return jsonify(videos), 200
        
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

