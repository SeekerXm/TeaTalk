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
    const newPasswordInput = document.getElementById('new_password');
    const confirmPasswordInput = document.getElementById('confirm_password');
    
    if (newPasswordInput && confirmPasswordInput) {
        // 监听新密码输入
        newPasswordInput.addEventListener('input', function() {
            validatePasswords();
        });
        
        // 监听确认密码输入
        confirmPasswordInput.addEventListener('input', function() {
            validatePasswords();
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

    // 修改密码表单提交处理
    const changePasswordForm = document.getElementById('changePasswordForm');
    if (changePasswordForm) {
        changePasswordForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            try {
                // 获取表单数据
                const formData = new FormData(this);
                const oldPassword = formData.get('old_password');
                const newPassword = formData.get('new_password');
                const confirmPassword = formData.get('confirm_password');
                
                // 验证新密码
                if (!validatePassword(newPassword)) {
                    showAlertModal('新密码必须包含大小写字母、数字和特殊字符中的至少三种', 'warning');
                    return;
                }
                
                // 验证确认密码
                if (newPassword !== confirmPassword) {
                    showAlertModal('两次输入的密码不一致', 'warning');
                    return;
                }
                
                const response = await fetch('/users/change_password/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name="csrfmiddlewaretoken"]').value,
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: new URLSearchParams({
                        'old_password': oldPassword,
                        'new_password': newPassword,
                        'confirm_password': confirmPassword
                    })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                
                if (data.success) {
                    showAlertModal('密码修改成功', 'success');
                    // 关闭修改密码模态框
                    const modal = bootstrap.Modal.getInstance(document.getElementById('changePasswordModal'));
                    if (modal) {
                        modal.hide();
                    }
                    // 清空表单
                    this.reset();
                    
                    // 密码修改成功后延迟2秒跳转到登录页
                    setTimeout(() => {
                        window.location.href = '/logout/';
                    }, 2000);
                } else {
                    showAlertModal(data.message || '密码修改失败', 'danger');
                }
            } catch (error) {
                console.error('Error:', error);
                showAlertModal('服务器错误，请稍后重试', 'danger');
            }
        });
    }

    // 监听设置模态框的显示事件
    const settingsModal = document.getElementById('settingsModal');
    if (settingsModal) {
        settingsModal.addEventListener('show.bs.modal', function() {
            // 每次打开设置面板时检查用户状态
            checkUserStatus();
        });
    }

    // 监听修改密码模态框的显示事件
    const changePasswordModal = document.getElementById('changePasswordModal');
    if (changePasswordModal) {
        // 监听模态框显示事件，每次显示时重新初始化功能
        changePasswordModal.addEventListener('show.bs.modal', function() {
            // 初始化密码显示/隐藏功能
            initPasswordToggle();
            // 初始化密码验证
            initPasswordValidation();
        });
    }

    // 注销账号模态框相关功能初始化
    const deleteAccountModal = document.getElementById('deleteAccountModal');
    if (deleteAccountModal) {
        // 监听模态框显示事件，每次显示时重新初始化功能
        deleteAccountModal.addEventListener('show.bs.modal', function() {
            initDeleteAccountForm();
        });
    }

    // 初始化模型选择器
    initModelSelector();
});

// 初始化注销账号表单功能
function initDeleteAccountForm() {
    const deleteAccountForm = document.getElementById('deleteAccountForm');
    if (deleteAccountForm) {
        // 移除现有的事件监听器
        const oldForm = deleteAccountForm.cloneNode(true);
        deleteAccountForm.parentNode.replaceChild(oldForm, deleteAccountForm);
        
        // 重新添加表单提交事件监听
        oldForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // 检查确认框是否勾选
            const confirmCheckbox = document.getElementById('confirmDelete');
            if (!confirmCheckbox.checked) {
                showAlertModal('请确认您已了解注销账号的影响', 'warning');
                return;
            }
            
            try {
                const formData = new FormData(this);
                const password = formData.get('password');
                
                if (!password) {
                    showAlertModal('请输入密码确认', 'warning');
                    return;
                }
                
                const response = await fetch('/users/delete-account/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name="csrfmiddlewaretoken"]').value,
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: new URLSearchParams({
                        'password': password
                    })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                
                if (data.success) {
                    showAlertModal('账号已成功注销', 'success');
                    // 延迟2秒后跳转到首页
                    setTimeout(() => {
                        window.location.href = '/';
                    }, 2000);
                } else {
                    showAlertModal(data.message || '注销账号失败', 'danger');
                }
            } catch (error) {
                console.error('Error:', error);
                showAlertModal('服务器错误，请稍后重试', 'danger');
            }
        });
        
        // 初始化密码显示/隐藏功能
        const togglePasswordBtn = oldForm.querySelector('.toggle-password');
        if (togglePasswordBtn) {
            togglePasswordBtn.addEventListener('click', function(e) {
                e.preventDefault();
                const input = this.closest('.input-group').querySelector('input');
                const icon = this.querySelector('i');
                
                if (input.type === 'password') {
                    input.type = 'text';
                    icon.classList.remove('fa-eye');
                    icon.classList.add('fa-eye-slash');
                } else {
                    input.type = 'password';
                    icon.classList.remove('fa-eye-slash');
                    icon.classList.add('fa-eye');
                }
            });
        }
    }
}

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
    if (/[A-Z]/.test(password)) types++; // 大写母
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

// 修改用户状态检查函数
function checkUserStatus() {
    const userInfo = document.querySelector('.user-info');
    if (userInfo) {
        const statusBadge = userInfo.querySelector('.badge.bg-danger');
        // 检查是否存在封禁状态的徽章
        if (statusBadge && statusBadge.textContent.includes('封禁')) {
            // 找到修改密码按钮并禁用
            const changePasswordBtn = document.querySelector('[data-bs-target="#changePasswordModal"]');
            if (changePasswordBtn) {
                changePasswordBtn.disabled = true;
                changePasswordBtn.classList.add('disabled');
                changePasswordBtn.style.opacity = '0.5';
                changePasswordBtn.style.cursor = 'not-allowed';
                // 移除模态框触发器
                changePasswordBtn.removeAttribute('data-bs-target');
                changePasswordBtn.removeAttribute('data-bs-toggle');
            }
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

// 修改显示提示模态框函数
function showAlertModal(message, type = 'danger') {
    // 移除可能存在的旧弹窗
    const existingModal = document.getElementById('alertModal');
    if (existingModal) {
        const bsModal = bootstrap.Modal.getInstance(existingModal);
        if (bsModal) {
            bsModal.hide();
        }
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

    // 显弹窗
    alertModal.show();

    // 3秒后自动关闭
    setTimeout(() => {
        const modalElement = document.getElementById('alertModal');
        if (modalElement) {  // 添加检查
            const bsModal = bootstrap.Modal.getInstance(modalElement);
            if (bsModal) {
                bsModal.hide();
                // 监听隐藏完成事件
                modalElement.addEventListener('hidden.bs.modal', function() {
                    if (modalElement && modalElement.parentNode) {  // 再次检查
                        modalElement.remove();
                    }
                });
            } else {
                // 如果没有 Modal 实例，直接移除元
                if (modalElement.parentNode) {
                    modalElement.remove();
                }
            }
        }
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
        showPauseButton();  // 显示暂停按钮
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

// 修改 typeMessageWithMarkdown 函数
function typeMessageWithMarkdown(text, element, index = 0) {
    // 保存当前任务的引用
    currentTypingTask = { text, element, index };
    
    // 在开始打字时禁用发送按钮(仅在非暂停状态下)
    const sendButton = document.querySelector('.btn-send');
    if (sendButton && !isPaused) {
        disableSendButton(sendButton);
    }
    
    if (index < text.length) {
        // 如果暂停了，就不继续输出
        if (isPaused) {
            return;
        }

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
                
                // 加复制按钮到消息内容
                element.appendChild(copyButton);
                
                // 应用代码高亮
                element.querySelectorAll('pre code').forEach((block) => {
                    const code = block.textContent;
                    block.textContent = code;
                    hljs.highlightElement(block);
                });
                
                // 输出完成，隐藏暂停按钮
                hidePauseButton();
                
                // 输出完成，启用发送按钮
                if (sendButton) {
                    enableSendButton(sendButton);
                }
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
            hidePauseButton();
            // 确保在出错时也启用发送按钮
            if (sendButton) {
                enableSendButton(sendButton);
            }
        }
    } else {
        // 输出完成，隐藏暂停按钮
        hidePauseButton();
        // 确保在完成时启用发送按钮
        if (sendButton) {
            enableSendButton(sendButton);
        }
    }
}

// 添加禁用发送按钮的函数
function disableSendButton(button) {
    button.disabled = true;
    button.style.opacity = '0.5';
    button.style.cursor = 'not-allowed';
}

// 添加启用发送按钮的函数
function enableSendButton(button) {
    button.disabled = false;
    button.style.opacity = '1';
    button.style.cursor = 'pointer';
}

// 添加显示 Toast 提示函数
function showToast(message) {
    // 移除可能存在的旧提示
    const existingToast = document.querySelector('.toast-tip');
    if (existingToast) {
        existingToast.remove();
    }
    
    // 创建新提示
    const toast = document.createElement('div');
    toast.className = 'toast-tip';
    toast.textContent = message;
    document.body.appendChild(toast);
    
    // 触发重绘以启动动画
    toast.offsetHeight;
    toast.classList.add('show');
    
    // 2秒后移除提示
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 2000);
}

// 修改复制消息内容函数
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
        showToast('已复制');  // 使用新的 Toast 提示
    }).catch(() => {
        showToast('复制失败');  // 使用新的 Toast 提示
    });
}

// 修改输入框自动调整高度函数
function adjustTextareaHeight(textarea) {
    // 先将高度设为 0，以便正确计算 scrollHeight
    textarea.style.height = '0px';
    
    // 获取当前内容的行数
    const lines = textarea.value.split('\n');
    const lineCount = lines.length;
    
    // 如果内容为空，直接设为初始高度
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

// 添加暂停状态变量
let isPaused = false;
let currentTypingTask = null;

// 修改 toggleTyping 函数
function toggleTyping() {
    isPaused = !isPaused;
    updatePauseButton();
    
    const sendButton = document.querySelector('.btn-send');
    
    if (!isPaused && currentTypingTask) {
        // 继续输出时禁用发送钮
        if (sendButton) {
            disableSendButton(sendButton);
        }
        
        // 继续打字效果
        typeMessageWithMarkdown(
            currentTypingTask.text,
            currentTypingTask.element,
            currentTypingTask.index
        );
    } else if (isPaused) {
        // 暂停时启用发送按钮
        if (sendButton) {
            enableSendButton(sendButton);
        }
    }
}

// 显示暂停按钮
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

// 隐藏暂停按钮
function hidePauseButton() {
    const pauseButton = document.querySelector('.pause-button');
    if (pauseButton) {
        pauseButton.remove();
    }
    isPaused = false;
    currentTypingTask = null;
    
    // 确保在隐藏暂停按钮时启用发送按钮
    const sendButton = document.querySelector('.btn-send');
    if (sendButton) {
        enableSendButton(sendButton);
    }
}

// 更新暂停按钮状态
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

// 添加新建对话函数
function startNewChat() {
    // 清空聊天记录
    const chatMessages = document.getElementById('chatMessages');
    if (chatMessages) {
        chatMessages.innerHTML = '';
    }
    
    // 清空输入框
    const messageInput = document.getElementById('messageInput');
    if (messageInput) {
        messageInput.value = '';
        messageInput.style.height = '24px';  // 重置输入框高度
    }
}

// 密码验证函数
function validatePasswords() {
    const newPassword = document.getElementById('new_password');
    const confirmPassword = document.getElementById('confirm_password');
    
    if (!newPassword || !confirmPassword) return;
    
    const newPasswordValue = newPassword.value;
    const confirmPasswordValue = confirmPassword.value;
    
    if (confirmPasswordValue) {
        if (newPasswordValue === confirmPasswordValue && validatePassword(newPasswordValue)) {
            confirmPassword.classList.remove('is-invalid');
            confirmPassword.classList.add('is-valid');
            newPassword.classList.remove('is-invalid');
            newPassword.classList.add('is-valid');
        } else {
            confirmPassword.classList.remove('is-valid');
            confirmPassword.classList.add('is-invalid');
            if (!validatePassword(newPasswordValue)) {
                newPassword.classList.remove('is-valid');
                newPassword.classList.add('is-invalid');
            }
        }
    } else {
        confirmPassword.classList.remove('is-invalid', 'is-valid');
        if (validatePassword(newPasswordValue)) {
            newPassword.classList.remove('is-invalid');
            newPassword.classList.add('is-valid');
        } else {
            newPassword.classList.remove('is-valid');
            newPassword.classList.add('is-invalid');
        }
    }
}

// 初始化密码显示/隐藏功能
function initPasswordToggle() {
    document.querySelectorAll('#changePasswordModal .toggle-password').forEach(button => {
        // 移除现有的事件监听器
        button.replaceWith(button.cloneNode(true));
        
        // 重新获取按钮（因为上面的操作创建了新的元素）
        const newButton = document.querySelector(`#${button.id}`);
        if (newButton) {
            newButton.addEventListener('click', function(e) {
                e.preventDefault();
                const input = this.closest('.input-group').querySelector('input[type="password"], input[type="text"]');
                const icon = this.querySelector('i');
                
                if (input.type === 'password') {
                    input.type = 'text';
                    icon.classList.remove('fa-eye');
                    icon.classList.add('fa-eye-slash');
                } else {
                    input.type = 'password';
                    icon.classList.remove('fa-eye-slash');
                    icon.classList.add('fa-eye');
                }
            });
        }
    });
}

// 初始化密码验证
function initPasswordValidation() {
    const newPassword = document.getElementById('new_password');
    const confirmPassword = document.getElementById('confirm_password');
    
    if (newPassword && confirmPassword) {
        // 移除现有的事件监听器
        newPassword.replaceWith(newPassword.cloneNode(true));
        confirmPassword.replaceWith(confirmPassword.cloneNode(true));
        
        // 重新获取输入框
        const newPasswordInput = document.getElementById('new_password');
        const confirmPasswordInput = document.getElementById('confirm_password');
        
        // 添加新的事件监听器
        newPasswordInput.addEventListener('input', validatePasswords);
        confirmPasswordInput.addEventListener('input', validatePasswords);
    }
}

// 添加模型选择器初始化函数
async function initModelSelector() {
    try {
        const response = await fetch('/api/available-models/', {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            if (data.models && data.models.length > 0) {
                updateModelList(data.models);
            } else {
                console.warn('没有可用的模型');
                // 显示一个默认状态
                const modelText = document.querySelector('.model-text');
                const modelName = document.querySelector('.model-name');
                if (modelText) modelText.textContent = '暂无可用模型';
                if (modelName) modelName.textContent = '暂无可用模型';
            }
        } else {
            console.error('获取模型列表失败:', data.message);
            throw new Error(data.message);
        }
    } catch (error) {
        console.error('初始化模型选择器失败:', error);
        // 显示错误状态
        const modelText = document.querySelector('.model-text');
        const modelName = document.querySelector('.model-name');
        if (modelText) modelText.textContent = '加载失败';
        if (modelName) modelName.textContent = '加载失败';
    }
}

// 更新模型列表函数
function updateModelList(models) {
    const modelSelect = document.getElementById('modelSelect');
    const modelMenu = document.querySelector('.model-menu');
    const modelText = document.querySelector('.model-text');
    const modelName = document.querySelector('.model-name');
    const modelInfo = document.querySelector('.model-info');
    
    if (!modelSelect || !modelMenu || !modelText || !modelName || !modelInfo) return;
    
    // 清空现有选项
    modelSelect.innerHTML = '';
    modelMenu.innerHTML = '';
    
    // 添加新的选项
    models.forEach((model, index) => {
        // 添加到隐藏的 select 元素
        const option = document.createElement('option');
        option.value = model.id;
        option.textContent = model.name;
        modelSelect.appendChild(option);
        
        // 添加到下拉菜单
        const item = document.createElement('li');
        item.innerHTML = `
            <a class="dropdown-item model-item ${index === 0 ? 'active' : ''}" 
               href="#" 
               data-model-id="${model.id}"
               data-model-name="${model.name}"
               data-model-type="${model.type}"
               data-model-platform="${model.platform}"
               data-original-name="${model.original_name}">
                <i class="fas fa-${model.type === 'chat' ? 'comment' : 'code'} me-2"></i>
                ${model.name}
            </a>
        `;
        modelMenu.appendChild(item);
        
        // 设置第一个模型为当前选中的模型
        if (index === 0) {
            modelText.textContent = model.name;
            modelName.textContent = model.name;
            modelInfo.setAttribute('data-bs-title', `
                <p>模型类型：${model.type === 'chat' ? '对话' : '图像'}</p>
                <p>模型平台：${model.platform}</p>
                <p>原始模型：${model.original_name}</p>
            `);
            // 重新初始化 tooltip
            new bootstrap.Tooltip(modelInfo, {
                html: true,
                template: '<div class="tooltip model-tooltip" role="tooltip"><div class="tooltip-arrow"></div><div class="tooltip-inner"></div></div>'
            });
        }
    });
    
    // 添加模型切换事件监听
    document.querySelectorAll('.model-item').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            
            // 更新选中状态
            document.querySelectorAll('.model-item').forEach(i => i.classList.remove('active'));
            this.classList.add('active');
            
            // 更新显示的模型名称和信息
            const modelId = this.dataset.modelId;
            const modelName = this.dataset.modelName;
            const modelType = this.dataset.modelType;
            const modelPlatform = this.dataset.modelPlatform;
            const originalName = this.dataset.originalName;
            
            modelSelect.value = modelId;
            modelText.textContent = modelName;
            document.querySelector('.model-name').textContent = modelName;
            
            // 更新模型信息提示
            const modelInfo = document.querySelector('.model-info');
            modelInfo.setAttribute('data-bs-title', `
                <p>模型类型：${modelType === 'chat' ? '对话' : '图像'}</p>
                <p>模型平台：${modelPlatform}</p>
                <p>原始模型：${originalName}</p>
            `);
            
            // 销毁旧的 tooltip 并重新初始化
            const oldTooltip = bootstrap.Tooltip.getInstance(modelInfo);
            if (oldTooltip) {
                oldTooltip.dispose();
            }
            new bootstrap.Tooltip(modelInfo, {
                html: true,
                template: '<div class="tooltip model-tooltip" role="tooltip"><div class="tooltip-arrow"></div><div class="tooltip-inner"></div></div>'
            });
        });
    });
}

// 其他现有代码保持不变... 