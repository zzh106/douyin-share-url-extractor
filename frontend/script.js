/**
 * 抖音视频链接导出工具 - 前端脚本
 */

const API_BASE_URL = 'http://localhost:5000';

// DOM 元素
const userInput = document.getElementById('userInput');
const fetchBtn = document.getElementById('fetchBtn');
const loading = document.getElementById('loading');
const error = document.getElementById('error');
const resultSection = document.getElementById('resultSection');
const videoList = document.getElementById('videoList');
const videoCount = document.getElementById('videoCount');
const exportBtn = document.getElementById('exportBtn');

// 存储视频列表
let videos = [];

/**
 * 从输入中提取 sec_user_id
 * 支持：
 * 1. 直接输入 sec_user_id
 * 2. 用户主页 URL: https://www.douyin.com/user/xxx
 * 3. 用户主页 URL: https://www.douyin.com/user/xxx?sec_user_id=xxx
 */
function extractSecUserId(input) {
    if (!input || !input.trim()) {
        return null;
    }

    const trimmed = input.trim();

    // 如果是 URL
    if (trimmed.startsWith('http')) {
        try {
            const url = new URL(trimmed);
            
            // 从查询参数中获取 sec_user_id
            const secUserId = url.searchParams.get('sec_user_id');
            if (secUserId) {
                return secUserId;
            }
            
            // 从路径中提取（如果 URL 格式是 /user/xxx）
            const pathParts = url.pathname.split('/');
            const userIndex = pathParts.indexOf('user');
            if (userIndex !== -1 && pathParts[userIndex + 1]) {
                return pathParts[userIndex + 1];
            }
            
            // 尝试从整个路径中提取（可能是其他格式）
            const lastPart = pathParts[pathParts.length - 1];
            if (lastPart && lastPart.length > 10) {
                return lastPart;
            }
        } catch (e) {
            console.error('URL 解析失败:', e);
        }
    }
    
    // 如果不是 URL，直接当作 sec_user_id 返回
    return trimmed;
}

/**
 * 显示错误信息
 */
function showError(message) {
    error.textContent = `❌ ${message}`;
    error.classList.remove('hidden');
    loading.classList.add('hidden');
}

/**
 * 隐藏错误信息
 */
function hideError() {
    error.classList.add('hidden');
}

/**
 * 渲染视频列表
 */
function renderVideoList(videoListData) {
    videos = videoListData;
    videoCount.textContent = videos.length;
    
    if (videos.length === 0) {
        videoList.innerHTML = '<p class="empty">未找到视频</p>';
        return;
    }
    
    videoList.innerHTML = videos.map((video, index) => `
        <div class="video-item">
            <div class="video-number">${index + 1}</div>
            <div class="video-content">
                <div class="video-title">${escapeHtml(video.title || '无标题')}</div>
                <div class="video-url">
                    <a href="${video.url}" target="_blank" rel="noopener noreferrer">
                        ${video.url}
                    </a>
                </div>
            </div>
        </div>
    `).join('');
    
    resultSection.classList.remove('hidden');
}

/**
 * HTML 转义
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * 导出为 TXT 文件
 */
function exportToTxt() {
    if (videos.length === 0) {
        alert('没有可导出的视频');
        return;
    }
    
    // 生成 TXT 内容
    const lines = videos.map((video, index) => {
        return `${index + 1}. ${video.title}\n${video.url}\n`;
    });
    
    const content = lines.join('\n');
    
    // 创建 Blob 并下载
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'douyin_links.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

/**
 * 获取用户视频
 */
async function fetchUserVideos() {
    const input = userInput.value;
    const secUserId = extractSecUserId(input);
    
    if (!secUserId) {
        showError('请输入有效的用户主页 URL 或 sec_user_id');
        return;
    }
    
    // 显示加载状态
    hideError();
    loading.classList.remove('hidden');
    resultSection.classList.add('hidden');
    fetchBtn.disabled = true;
    
    try {
        // 调用后端 API
        const response = await fetch(`${API_BASE_URL}/api/fetch_user_videos`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ sec_user_id: secUserId }),
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || '请求失败');
        }
        
        // 渲染结果
        renderVideoList(data);
        
    } catch (err) {
        console.error('获取视频失败:', err);
        showError(err.message || '获取视频列表失败，请检查网络连接或 sec_user_id 是否正确');
    } finally {
        loading.classList.add('hidden');
        fetchBtn.disabled = false;
    }
}

// 事件监听
fetchBtn.addEventListener('click', fetchUserVideos);
exportBtn.addEventListener('click', exportToTxt);

// 支持回车键提交
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        fetchUserVideos();
    }
});

