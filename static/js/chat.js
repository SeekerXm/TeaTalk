// 发送用户消息
function sendUserMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    input.value = '';
    sendMessage(message);
}

// 处理按键事件
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendUserMessage();
    }
}

// 显示消息
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
    
    // 如果是AI回复，使用打字效果
    if (role === 'assistant') {
        typeMessage(content, contentDiv);
    } else {
        contentDiv.textContent = content;
    }
    
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// 打字效果函数
function typeMessage(text, element, index = 0) {
    if (index < text.length) {
        element.textContent += text.charAt(index);
        const messagesDiv = document.getElementById('chatMessages');
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
        
        // 随机延迟，使打字效果更自然
        const delay = Math.random() * 30 + 20;  // 20-50ms之间的随机延迟
        setTimeout(() => typeMessage(text, element, index + 1), delay);
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