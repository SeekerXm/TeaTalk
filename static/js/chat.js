document.addEventListener('DOMContentLoaded', function() {
    // 登录表单验证
    const loginEmail = document.getElementById('loginEmail');
    const loginPassword = document.getElementById('loginPassword');
    
    if (loginEmail) {
        loginEmail.addEventListener('input', function() {
            const isValid = validateEmail(this.value);
            setInputValidation(this, isValid, '请输入有效的邮箱地址', true);  // 邮箱保持显示消息
        });
    }
    
    // 移除登录密码的即时验证
    if (loginPassword) {
        loginPassword.addEventListener('input', function() {
            // 移除所有验证相关的类和提示
            this.classList.remove('is-invalid', 'is-valid');
            const feedbackElement = this.parentElement.querySelector('.invalid-feedback');
            if (feedbackElement) {
                feedbackElement.style.display = 'none';
            }
        });
    }
    
    // 注册表单验证（不显示消息）
    const registerEmail = document.getElementById('registerEmail');
    const registerPassword = document.getElementById('registerPassword');
    const registerConfirmPassword = document.getElementById('registerConfirmPassword');
    
    if (registerEmail) {
        registerEmail.addEventListener('input', function() {
            const isValid = validateEmail(this.value);
            setInputValidation(this, isValid, '', false);  // 不显示消息
        });
    }
    
    if (registerPassword) {
        registerPassword.addEventListener('input', function() {
            const isValid = validatePassword(this.value);
            setInputValidation(this, isValid, '', false);  // 不显示消息，只显示红色边框
            
            // 同时验证确认密码
            if (registerConfirmPassword.value) {
                const confirmIsValid = this.value === registerConfirmPassword.value && isValid;
                setInputValidation(registerConfirmPassword, confirmIsValid, '', false);
            }
        });
    }
    
    if (registerConfirmPassword) {
        registerConfirmPassword.addEventListener('input', function() {
            const isValid = this.value === registerPassword.value && 
                          validatePassword(registerPassword.value);
            setInputValidation(this, isValid, '', false);  // 不显示消息，只显示红色边框
        });
    }
    
    // 找回密码表单验证（不显示消息）
    const resetEmail = document.getElementById('resetEmail');
    const resetPassword = document.getElementById('resetPassword');
    const resetConfirmPassword = document.getElementById('resetConfirmPassword');
    
    if (resetEmail) {
        resetEmail.addEventListener('input', function() {
            const isValid = validateEmail(this.value);
            setInputValidation(this, isValid, '', false);  // 不显示消息
        });
    }
    
    if (resetPassword) {
        resetPassword.addEventListener('input', function() {
            const isValid = validatePassword(this.value);
            setInputValidation(this, isValid, '', false);  // 不显示消息，只显示红色边框
            
            // 同时验证确认密码
            if (resetConfirmPassword.value) {
                const confirmIsValid = this.value === resetConfirmPassword.value && isValid;
                setInputValidation(resetConfirmPassword, confirmIsValid, '', false);
            }
        });
    }
    
    if (resetConfirmPassword) {
        resetConfirmPassword.addEventListener('input', function() {
            const isValid = this.value === resetPassword.value && 
                          validatePassword(resetPassword.value);
            setInputValidation(this, isValid, '', false);  // 不显示消息，只显示红色边框
        });
    }

    // 修改密码表单验证
    const newPassword = document.getElementById('newPassword');
    const confirmNewPassword = document.getElementById('confirmNewPassword');
    
    if (newPassword) {
        newPassword.addEventListener('input', function() {
            const isValid = validatePassword(this.value);
            setInputValidation(this, isValid, '', false);  // 不显示消息，只显示红色边框
            
            // 同时验证确认密码
            if (confirmNewPassword.value) {
                const confirmIsValid = this.value === confirmNewPassword.value && isValid;
                setInputValidation(confirmNewPassword, confirmIsValid, '', false);
            }
        });
    }
    
    if (confirmNewPassword) {
        confirmNewPassword.addEventListener('input', function() {
            const isValid = this.value === newPassword.value && 
                          validatePassword(newPassword.value);
            setInputValidation(this, isValid, '', false);  // 不显示消息，只显示红色边框
        });
    }

    // 添加输入框高度自动调整
    const messageInput = document.getElementById('messageInput');
    if (messageInput) {
        // 监听输入事件
        messageInput.addEventListener('input', function() {
            adjustTextareaHeight(this);
        });
        
        // 监听键盘事件
        messageInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();  // 阻止默认换行
                handleSendMessage();
            } else if (e.key === 'Enter' && e.shiftKey) {
                // Shift + Enter 换行时自动调整高度
                setTimeout(() => adjustTextareaHeight(this), 0);
            }
        });

        // 监听删除和退格键
        messageInput.addEventListener('keyup', function(e) {
            if (e.key === 'Backspace' || e.key === 'Delete') {
                adjustTextareaHeight(this);
            }
        });

        // 监听粘贴事件
        messageInput.addEventListener('paste', function() {
            setTimeout(() => adjustTextareaHeight(this), 0);
        });

        // 监听失去焦点事件
        messageInput.addEventListener('blur', function() {
            adjustTextareaHeight(this);
        });

        // 监听获得焦点事件
        messageInput.addEventListener('focus', function() {
            adjustTextareaHeight(this);
        });
    }
});

// 添加邮箱验证函数
function validateEmail(email) {
    if (!email) return false;
    
    // 支持的邮箱后缀
    const allowedDomains = ['qq.com', '126.com', '163.com', 'sina.com'];
    // 邮箱格式则表达式
    const emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
    
    if (!emailRegex.test(email)) return false;
    
    // 检查邮箱后缀是否在允许列表中
    const domain = email.split('@')[1];
    return allowedDomains.includes(domain);
}

// 添加密码验证函数
function validatePassword(password) {
    if (!password) return false;
    
    // 至少包含三类字符
    let types = 0;
    if (/[A-Z]/.test(password)) types++; // 大写字母
    if (/[a-z]/.test(password)) types++; // 小写字母
    if (/[0-9]/.test(password)) types++; // 数字
    if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) types++; // 特殊字符
    
    return types >= 3;
}

// 添加 setInputValidation 函数
function setInputValidation(input, isValid, message = '', showMessage = true) {
    if (isValid) {
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
        // 移除错误提示
        const feedbackElement = input.parentElement.querySelector('.invalid-feedback');
        if (feedbackElement) {
            feedbackElement.style.display = 'none';
        }
    } else {
        input.classList.remove('is-valid');
        input.classList.add('is-invalid');
        // 只在需要显示消息时处理反馈元素
        if (showMessage && message) {
            let feedbackElement = input.parentElement.querySelector('.invalid-feedback');
            if (!feedbackElement) {
                feedbackElement = document.createElement('div');
                feedbackElement.className = 'invalid-feedback';
                // 对于带有 input-group 的输入框，将反馈元素添加到 input-group 之后
                const inputGroup = input.closest('.input-group');
                if (inputGroup) {
                    inputGroup.parentElement.appendChild(feedbackElement);
                } else {
                    input.parentElement.appendChild(feedbackElement);
                }
            }
            feedbackElement.textContent = message;
            feedbackElement.style.display = 'block';
        }
    }
}

// 添加按键处理函数
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        handleSendMessage();
    }
}

// 修改发送消息处理函数
async function handleSendMessage() {
    // 检查用户是否已登录
    const isAuthenticated = document.body.classList.contains('user-authenticated');
    
    if (!isAuthenticated) {
        const authModal = new bootstrap.Modal(document.getElementById('authModal'));
        authModal.show();
        return;
    }
    
    // 检查用户状态
    if (!checkUserStatus()) {
        showAlertModal('您的账号已被封禁，无法发送消息', 'danger');
        return;
    }
    
    // 获取消息输入框和消息内容
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();
    
    // 检查消息是否为空
    if (!message) {
        showAlertModal('消息不能为空', 'warning');
        return;
    }
    
    try {
        // 添加用户消息到聊天区域
        appendMessage('user', message);
        
        // 清空输入框并重置高度
        messageInput.value = '';
        messageInput.style.height = '24px';
        
        // 显示加载动画（确保在用户消息之后）
        showLoading();
        
        // 获取必要的数据
        const currentModel = document.getElementById('modelSelect')?.value || 'default';
        const sessionId = messageInput.dataset.sessionId || '';
        const csrfToken = document.querySelector('[name="csrfmiddlewaretoken"]').value;
        
        // 构建 FormData
        const formData = new FormData();
        formData.append('message', message);
        formData.append('model', currentModel);
        formData.append('session_id', sessionId);
        
        // 发送消息到服务器
        const response = await fetch('/chat/send/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: formData
        });
        
        const data = await response.json();
        hideLoading();
        
        if (data.success) {
            appendMessage('assistant', data.response);
        } else {
            showError(data.message || '发送失败，请重试');
        }
    } catch (error) {
        console.error('Error:', error);
        hideLoading();
        showError('发送消息失败，请重试');
    }
}

// 添加用户状态检查函数
function checkUserStatus() {
    const userInfo = document.querySelector('.user-info');
    if (userInfo) {
        const statusBadge = userInfo.querySelector('.badge.bg-danger');
        // 检查是否存在封禁状态的徽章
        if (statusBadge && statusBadge.textContent.includes('封禁')) {
            return false;
        }
    }
    return true;
}

// 修改显示加载动画函数
function showLoading() {
    const messagesDiv = document.getElementById('chatMessages');
    const loadingSpinner = document.getElementById('loadingSpinner');
    if (loadingSpinner) {
        // 先移除加载动画的现有样式
        loadingSpinner.removeAttribute('style');
        loadingSpinner.className = 'message assistant';
        
        // 创建消息内容包装器
        const contentWrapper = document.createElement('div');
        contentWrapper.className = 'message-content-wrapper';
        
        // 创建头像
        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        const avatarIcon = document.createElement('i');
        avatarIcon.className = 'fas fa-robot';
        avatarDiv.appendChild(avatarIcon);
        
        // 创建加载动画内容
        const loadingContent = document.createElement('div');
        loadingContent.className = 'message-content typing-indicator';
        loadingContent.innerHTML = '<span></span><span></span><span></span>';
        
        // 组装加载动画
        contentWrapper.appendChild(loadingContent);
        loadingSpinner.innerHTML = '';  // 清空现有内容
        loadingSpinner.appendChild(avatarDiv);
        loadingSpinner.appendChild(contentWrapper);
        
        // 修改这里：确保加载动画在最后一条消息之后
        const messages = messagesDiv.querySelectorAll('.message');
        if (messages.length > 0) {
            const lastMessage = messages[messages.length - 1];
            lastMessage.after(loadingSpinner);
        } else {
            messagesDiv.appendChild(loadingSpinner);
        }
        
        // 显示加载动画
        loadingSpinner.style.display = 'flex';
        
        // 滚动到底部
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
}

// 修改隐藏加载动画函数
function hideLoading() {
    const loadingSpinner = document.getElementById('loadingSpinner');
    if (loadingSpinner) {
        // 重置加载动画的样式和内容
        loadingSpinner.style.display = 'none';
        loadingSpinner.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content-wrapper">
                <div class="message-content typing-indicator">
                    <span></span><span></span><span></span>
                </div>
            </div>
        `;
        // 将加载动画移回原位
        document.querySelector('.chat-container').appendChild(loadingSpinner);
    }
}

// 添加错误提示函数
function showError(message) {
    showAlertModal(message, 'danger');
}

// 添加 getCookie 函数
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

// 添加显示提示模态框函数
function showAlertModal(message, type = 'danger') {
    // 移除可能存在的旧弹窗
    const existingModal = document.getElementById('alertModal');
    if (existingModal) {
        existingModal.remove();
    }

    // 创建新的弹窗HTML
    const modalHTML = `
        <div class="modal fade" id="alertModal" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content border-0">
                    <div class="modal-body p-4">
                        <div class="d-flex align-items-center">
                            <div class="alert-icon me-3">
                                <i class="fas fa-${type === 'danger' ? 'exclamation-circle' : 'check-circle'} text-${type} fs-4"></i>
                            </div>
                            <div class="alert-content flex-grow-1">
                                <h5 class="mb-1">提示</h5>
                                <p class="mb-0 text-secondary">${message}</p>
                            </div>
                            <button type="button" class="btn-close ms-3" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    // 添加弹窗到页面
    document.body.insertAdjacentHTML('beforeend', modalHTML);

    // 获取弹窗实例
    const alertModal = new bootstrap.Modal(document.getElementById('alertModal'), {
        backdrop: 'static',
        keyboard: false
    });

    // 显示弹窗
    alertModal.show();

    // 3秒后自动关闭
    setTimeout(() => {
        alertModal.hide();
        // 弹窗关闭后移除DOM
        setTimeout(() => {
            document.getElementById('alertModal').remove();
        }, 500);
    }, 3000);
}

// 添加 markdown-it 初始化
const chatMd = window.markdownit({
    breaks: true,
    linkify: true,
    html: true
});

// 添加消息显示函数
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
    
    // 如果是AI回复，使用打字效果并渲染markdown
    if (role === 'assistant') {
        typeMessageWithMarkdown(content, contentDiv);
    } else {
        contentDiv.textContent = content;
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

// 添加打字效果函数
function typeMessageWithMarkdown(text, element, index = 0) {
    if (index < text.length) {
        const currentText = text.substring(0, index + 1);
        try {
            // 渲染 markdown
            element.innerHTML = chatMd.render(currentText);
            
            // 在完成渲染后添加复制按钮
            if (index === text.length - 1) {
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
            }
            
            // 滚动到底部
            const messagesDiv = document.getElementById('chatMessages');
            if (messagesDiv) {
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }
            
            requestAnimationFrame(() => {
                const delay = Math.random() * 30 + 20;
                setTimeout(() => typeMessageWithMarkdown(text, element, index + 1), delay);
            });
        } catch (error) {
            console.error('Markdown rendering error:', error);
            element.textContent = text;
        }
    }
}

// 添加复制消息内容函数
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
        showAlertModal('复制成功', 'success');
    }).catch(() => {
        showAlertModal('复制失败，请重试', 'danger');
    });
}

// 修改输入框自动调整高度函数
function adjustTextareaHeight(textarea) {
    // 先将高度设为 0，以便正确计算 scrollHeight
    textarea.style.height = '0px';
    
    // 获取当前内容的行数
    const lines = textarea.value.split('\n');
    const lineCount = lines.length;
    
    // 如果内容为空，直接设置为初始高度
    if (!textarea.value.trim()) {
        textarea.style.height = '24px';
        return;
    }
    
    // 计算每行的高度（包括行间距）
    const lineHeight = 24;  // 基础行高
    
    // 根据内容行数计算理想高度
    const idealHeight = Math.min(lineHeight * lineCount, 150);  // 最大高度限制为 150px
    
    // 设置实际高度（不小于初始高度）
    const newHeight = Math.max(24, Math.min(idealHeight, textarea.scrollHeight));
    textarea.style.height = newHeight + 'px';
    
    // 如果内容高度超过最大限制，显示滚动条
    if (textarea.scrollHeight > 150) {
        textarea.style.overflowY = 'auto';
    } else {
        textarea.style.overflowY = 'hidden';
    }
}

// 其他现有代码保持不变... 