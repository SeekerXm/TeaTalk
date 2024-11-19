// 在文件开头初始化 markdown-it
const md = window.markdownit({
    breaks: true,  // 转换换行符为 <br>
    linkify: true,  // 自动转换链接文本
    highlight: function (str, lang) {  // 代码高亮
        if (lang && hljs.getLanguage(lang)) {
            try {
                return hljs.highlight(str, { language: lang }).value;
            } catch (__) {}
        }
        return '';  // 使用默认的转义
    }
});

// 自动调整高度的函数
function autoResizeTextarea(textarea) {
    // 先将高度设为最小值，以便正确计算新的高度
    textarea.style.height = '24px';
    
    // 根据内容计算新的高度
    const newHeight = Math.min(textarea.scrollHeight, 150);  // 最大高度为150px
    textarea.style.height = newHeight + 'px';
}

// 重置输入框高度的函数
function resetTextareaHeight(textarea) {
    textarea.style.height = '24px';  // 设置为初始高度
    textarea.value = '';  // 清空内容
}

// 发送用户消息
function sendUserMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // 重置输入框
    resetTextareaHeight(input);
    
    // 发送消息
    sendMessage(message);
}

// 在 DOMContentLoaded 事件中添加监听器
document.addEventListener('DOMContentLoaded', function() {
    const messageInput = document.getElementById('messageInput');
    if (messageInput) {
        // 设置初始高度
        messageInput.style.height = '24px';
        
        // 监听输事件，包括输入和删除
        messageInput.addEventListener('input', function() {
            autoResizeTextarea(this);
        });
        
        // 监听失焦事件
        messageInput.addEventListener('blur', function() {
            if (!this.value.trim()) {
                // 如果内容为空，恢复初始高度
                this.style.height = '24px';
            } else {
                // 如果有内容，根据内容调整高度
                autoResizeTextarea(this);
            }
        });
        
        // 监听聚焦事件
        messageInput.addEventListener('focus', function() {
            // 聚焦时根据内容调整高度
            autoResizeTextarea(this);
        });
        
        // 监听键盘事件，处理退格键和删除键
        messageInput.addEventListener('keydown', function(e) {
            if (e.key === 'Backspace' || e.key === 'Delete') {
                // 使用 setTimeout 确保在内容更新后调整高度
                setTimeout(() => autoResizeTextarea(this), 0);
            }
        });
        
        // 允许鼠标滚轮滚动
        messageInput.addEventListener('wheel', function(e) {
            const maxScroll = this.scrollHeight - this.clientHeight;
            const currentScroll = this.scrollTop;
            
            if ((currentScroll === 0 && e.deltaY < 0) || 
                (currentScroll >= maxScroll && e.deltaY > 0)) {
                return true;
            } else {
                e.stopPropagation();
            }
        });
    }
});

// 处理发送消息
function handleSendMessage() {
    // 检查用户是否已登录
    const isAuthenticated = document.body.classList.contains('user-authenticated');
    
    if (!isAuthenticated) {
        // 如果未登录，显示登录模态框
        const authModal = new bootstrap.Modal(document.getElementById('authModal'));
        authModal.show();
        return;
    }
    
    // 如果已登录，正常发送消息
    sendUserMessage();
}

// 处理按键事件
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        handleSendMessage();  // 使用新的处理函数
    }
}

// 修改显示消息的函数
function appendMessage(role, content) {
    console.log('Appending message:', role, content);
    
    const messagesDiv = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    // 创建头像
    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'message-avatar';
    const avatarIcon = document.createElement('i');
    
    if (role === 'user') {
        avatarIcon.className = 'fas fa-user';
    } else {
        avatarIcon.className = 'fas fa-robot';
    }
    avatarDiv.appendChild(avatarIcon);
    
    // 创建消息内容包装器
    const contentWrapper = document.createElement('div');
    contentWrapper.className = 'message-content-wrapper';
    
    // 创建消息内容
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // 组装消息
    contentWrapper.appendChild(contentDiv);
    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentWrapper);
    messagesDiv.appendChild(messageDiv);
    
    // 如果是AI回复，使用打字效果并渲染markdown
    if (role === 'assistant') {
        typeMessageWithMarkdown(content, contentDiv);
    } else {
        contentDiv.textContent = content;
    }
    
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// 修改打字效果函数以支持markdown
function typeMessageWithMarkdown(text, element, index = 0) {
    if (index < text.length) {
        const currentText = text.substring(0, index + 1);
        // 渲染markdown
        element.innerHTML = md.render(currentText);
        // 高亮代码块
        element.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightElement(block);
        });
        
        const messagesDiv = document.getElementById('chatMessages');
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
        
        // 随机延迟，使打字效果更自然
        const delay = Math.random() * 30 + 20;  // 20-50ms之间的随机延迟
        setTimeout(() => typeMessageWithMarkdown(text, element, index + 1), delay);
    }
}

// 发送消息到服务器
function sendMessage(message) {
    const formData = new FormData();
    formData.append('message', message);
    
    // 显示用户消息
    appendMessage('user', message);
    
    // 显示加载动画
    showLoading();
    
    fetch('/chat/send/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            // 显示AI响应
            appendMessage('assistant', data.response);
        } else {
            showError(data.message);
        }
    })
    .catch(error => {
        hideLoading();
        showError('发送消息失败，请稍后重试');
        console.error('Error:', error);
    });
}

// 加载动画控制
function showLoading() {
    const loadingSpinner = document.getElementById('loadingSpinner');
    const messagesDiv = document.getElementById('chatMessages');
    
    if (loadingSpinner && messagesDiv) {
        // 克隆加载动画元素
        const loadingClone = loadingSpinner.cloneNode(true);
        loadingClone.style.display = 'flex';
        loadingClone.style.position = 'relative';  // 改为相对定位
        
        // 添加到消息列表
        messagesDiv.appendChild(loadingClone);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
}

function hideLoading() {
    const messagesDiv = document.getElementById('chatMessages');
    if (messagesDiv) {
        // 移除所有加载动画
        const loadingElements = messagesDiv.getElementsByClassName('typing-indicator');
        while (loadingElements.length > 0) {
            loadingElements[0].closest('.message').remove();
        }
    }
}

// 错误提示
function showError(message) {
    alert(message);
}

// 获取CSRF Token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
} 