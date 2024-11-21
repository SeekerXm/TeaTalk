// 在文件开头初始化 markdown-it
const chatMd = window.markdownit({
    breaks: true,  // 转换换行符为 <br>
    linkify: true,  // 自动转换链接文本
    html: true,  // 允许 HTML
    highlight: function (str, lang) {  // 代码高亮
        if (lang && hljs.getLanguage(lang)) {
            try {
                // 先解码 HTML 实体
                const decodedStr = decodeHTMLEntities(str);
                // 然后进行代码高亮
                return hljs.highlight(decodedStr, { language: lang }).value;
            } catch (__) {
                // 如果高亮失败，返回原始字符串
                return str;
            }
        }
        // 对于没有指定语言或不支持的语言，进行自动检测
        return hljs.highlightAuto(str).value;
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
                // 如果有内容，根据内容调高度
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

// 添加暂停状态变量
let isPaused = false;
let currentTypingTask = null;

// 修改打字效果函数
function typeMessageWithMarkdown(text, element, index = 0) {
    // 保存当前任务的引用
    currentTypingTask = { text, element, index };
    
    // 首先解码 HTML 实体
    const decodedText = decodeHTMLEntities(text);
    
    if (index < decodedText.length) {
        // 如果暂停了，就不继续输出
        if (isPaused) {
            return;
        }

        const currentText = decodedText.substring(0, index + 1);
        try {
            // 渲染 markdown
            element.innerHTML = chatMd.render(currentText);
            
            // 在完成渲染后添加复制按钮
            if (index === decodedText.length - 1) {
                // 创建复制按钮
                const copyButton = document.createElement('button');
                copyButton.className = 'copy-button';
                copyButton.innerHTML = '<i class="fas fa-copy"></i> 复制';
                copyButton.onclick = () => copyMessageContent(element);
                
                // 添加复制按钮到消息内容
                element.appendChild(copyButton);
                
                // 应用代码高亮
                element.querySelectorAll('pre code').forEach((block) => {
                    const code = block.textContent;
                    block.textContent = code;
                    hljs.highlightElement(block);
                });
                
                // 输出完成，隐藏暂停按钮
                hidePauseButton();
            }
            
            // 滚动到底部
            const messagesDiv = document.getElementById('chatMessages');
            if (messagesDiv) {
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }
            
            // 使用 requestAnimationFrame 优化动画性能
            requestAnimationFrame(() => {
                const delay = Math.random() * 30 + 20;
                setTimeout(() => typeMessageWithMarkdown(text, element, index + 1), delay);
            });
        } catch (error) {
            console.error('Markdown rendering error:', error);
            element.textContent = text;
            hidePauseButton();
        }
    }
}

// 修改 appendMessage 函数
function appendMessage(role, content) {
    const messagesDiv = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    // 创建头像
    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'message-avatar';
    const avatarIcon = document.createElement('i');
    avatarIcon.className = `fas fa-${role === 'user' ? 'user' : 'robot'}`;
    avatarDiv.appendChild(avatarIcon);
    
    // 创建消息内容包装器
    const contentWrapper = document.createElement('div');
    contentWrapper.className = 'message-content-wrapper';
    
    // 创建消息内容
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // 如果是AI回复，显示暂停按钮并使用打字效果
    if (role === 'assistant') {
        // 重置暂停状态
        isPaused = false;
        // 显示暂停按钮
        showPauseButton();
        typeMessageWithMarkdown(content, contentDiv);
    } else {
        contentDiv.textContent = decodeHTMLEntities(content);
        // 为用户消息添加复制按钮
        const copyButton = document.createElement('button');
        copyButton.className = 'copy-button';
        copyButton.innerHTML = '<i class="fas fa-copy"></i> 复制';
        copyButton.onclick = () => copyMessageContent(contentDiv);
        contentDiv.appendChild(copyButton);
    }
    
    // 组装消息
    contentWrapper.appendChild(contentDiv);
    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentWrapper);
    messagesDiv.appendChild(messageDiv);
    
    // 滚动到底部
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// 修改暂停/继续功能
function toggleTyping() {
    isPaused = !isPaused;
    updatePauseButton();
    
    if (!isPaused && currentTypingTask) {
        // 继续输出
        typeMessageWithMarkdown(
            currentTypingTask.text,
            currentTypingTask.element,
            currentTypingTask.index
        );
    }
}

// 修改显示暂停按钮函数
function showPauseButton() {
    const chatInput = document.querySelector('.chat-input');
    let pauseButton = document.querySelector('.pause-button');
    
    if (!pauseButton) {
        pauseButton = document.createElement('button');
        pauseButton.className = 'pause-button';
        pauseButton.title = '暂停';
        pauseButton.innerHTML = '<i class="fas fa-pause"></i>';
        pauseButton.onclick = toggleTyping;
        chatInput.insertBefore(pauseButton, chatInput.firstChild);
    }
    
    updatePauseButton();
}

// 修改更新暂停按钮状态函数
function updatePauseButton() {
    const pauseButton = document.querySelector('.pause-button');
    if (pauseButton) {
        if (isPaused) {
            pauseButton.innerHTML = '<i class="fas fa-play"></i>';
            pauseButton.title = '继续';
        } else {
            pauseButton.innerHTML = '<i class="fas fa-pause"></i>';
            pauseButton.title = '暂停';
        }
    }
}

// 隐藏暂停按钮
function hidePauseButton() {
    const pauseButton = document.querySelector('.pause-button');
    if (pauseButton) {
        pauseButton.remove();
    }
    isPaused = false;
    currentTypingTask = null;
}

// 修改复制功能
function copyMessageContent(contentElement) {
    // 获取消息内容（不包括复制按钮的文本）
    let content = '';
    
    // 遍历所有子节点，排除复制按钮
    contentElement.childNodes.forEach(node => {
        if (!node.classList || !node.classList.contains('copy-button')) {
            content += node.textContent;
        }
    });
    
    // 复制到剪贴板
    navigator.clipboard.writeText(content.trim()).then(() => {
        showCopyTooltip('复制成功');
    }).catch(() => {
        showCopyTooltip('复制失败，请重试');
    });
}

// 显示复制提示
function showCopyTooltip(message) {
    // 移除现有提示
    const existingTooltip = document.querySelector('.copy-tooltip');
    if (existingTooltip) {
        existingTooltip.remove();
    }
    
    // 创建新提示
    const tooltip = document.createElement('div');
    tooltip.className = 'copy-tooltip';
    tooltip.textContent = message;
    document.body.appendChild(tooltip);
    
    // 自动移除提示
    setTimeout(() => {
        tooltip.remove();
    }, 1500);
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

// HTML 解码函数保持不变
function decodeHTMLEntities(text) {
    if (!text) return '';
    
    const textArea = document.createElement('textarea');
    textArea.innerHTML = text;
    let decodedText = textArea.value;
    
    // 额外的解码处理
    decodedText = decodedText
        .replace(/&amp;/g, '&')
        .replace(/&lt;/g, '<')
        .replace(/&gt;/g, '>')
        .replace(/&quot;/g, '"')
        .replace(/&#039;/g, "'")
        .replace(/&#x27;/g, "'")
        .replace(/&#x2F;/g, '/');
    
    return decodedText;
} 