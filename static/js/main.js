let countdown = 0;
const updateCountdown = (button) => {
    if (countdown > 0) {
        button.disabled = true;
        button.textContent = `${countdown}秒后重试`;
        countdown--;
        setTimeout(() => updateCountdown(button), 1000);
    } else {
        button.disabled = false;
        button.textContent = '获取验证码';
    }
};

// 添加消息提示函数
function showMessage(message, type = 'success') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-relative`;
    alertDiv.style.marginBottom = '1rem';
    alertDiv.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'} me-2"></i>
            <div>${message}</div>
            <button type="button" class="btn-close ms-auto" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // 找到当前激活的表单面板
    const activePane = document.querySelector('.tab-pane.active');
    if (activePane) {
        // 插入到表单之前
        const form = activePane.querySelector('form');
        if (form) {
            form.insertAdjacentElement('beforebegin', alertDiv);
        }
    }
    
    // 3秒后自动消失
    setTimeout(() => {
        alertDiv.classList.remove('show');
        setTimeout(() => alertDiv.remove(), 150);
    }, 3000);
}

// 错误提示函数
function showError(message) {
    showMessage(message, 'danger');
}

// 表单提交处理
const formHandlers = {
    'registerForm': {
        url: '/register/',
        validate: function(form) {
            const email = form.querySelector('[name="email"]').value;
            const password1 = form.querySelector('[name="password1"]').value;
            const password2 = form.querySelector('[name="password2"]').value;
            const emailCode = form.querySelector('[name="email_code"]').value;
            const captcha = form.querySelector('[name="captcha_value"]').value;

            // 邮箱验证
            if (!email) {
                showError('请输入邮箱地址');
                return false;
            }
            const emailRegex = /^[^\s@]+@(qq\.com|163\.com|sina\.com|126\.com)$/i;
            if (!emailRegex.test(email)) {
                showError('仅支持QQ邮箱、网易邮箱、新浪邮箱和126邮箱');
                return false;
            }

            // 密码验证
            if (!password1) {
                showError('请输入密码');
                return false;
            }
            if (password1.length < 8) {
                showError('密码长度至少为8个字符');
                return false;
            }
            let categories = 0;
            if (/[a-z]/.test(password1)) categories++;
            if (/[A-Z]/.test(password1)) categories++;
            if (/[0-9]/.test(password1)) categories++;
            if (/[!@#$%^&*()_+\-=\[\]{};:,.<>?]/.test(password1)) categories++;
            if (categories < 3) {
                showError('密码需要包含小写字母、大写字母、数字、特殊字符中的至少三类');
                return false;
            }

            // 确认密码验证
            if (password1 !== password2) {
                showError('两次输入的密码不一致');
                return false;
            }

            // 验证码验证
            if (!captcha) {
                showError('请输入图形验证码');
                return false;
            }

            // 邮箱验证码验证
            if (!emailCode) {
                showError('请输入邮箱验证码');
                return false;
            }
            if (!/^\d{6}$/.test(emailCode)) {
                showError('邮箱验证码必须是6位数字');
                return false;
            }

            return true;
        },
        onSuccess: function(data, form) {
            showMessage(data.message || '注册成功！', 'success');
            
            // 延迟1.5秒后切换到登录表单
            setTimeout(() => {
                // 切换到登录标签页
                const loginTab = document.querySelector('[data-bs-target="#loginTab"]');
                const tabInstance = new bootstrap.Tab(loginTab);
                tabInstance.show();
                
                // 自动填充邮箱
                const loginEmail = document.querySelector('#loginEmail');
                if (loginEmail && data.email) {
                    loginEmail.value = data.email;
                }
                
                // 聚焦到密码输入框
                const loginPassword = document.querySelector('#loginPassword');
                if (loginPassword) {
                    loginPassword.focus();
                }
                
                // 清空注册表单
                form.reset();
                form.classList.remove('was-validated');
            }, 1500);
        }
    },
    'loginForm': {
        url: '/login/',
        validate: function(form) {
            const email = form.querySelector('[name="email"]').value;
            const password = form.querySelector('[name="password"]').value;

            if (!email) {
                showError('请输入邮箱地址');
                return false;
            }
            if (!password) {
                showError('请输入密码');
                return false;
            }
            return true;
        },
        onSuccess: function(data) {
            showMessage(data.message || '登录成功！', 'success');
            // 延迟1秒后刷新页面
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        }
    },
    'resetForm': {
        url: '/reset-password/',
        validate: function(form) {
            const email = form.querySelector('[name="email"]').value;
            const emailCode = form.querySelector('[name="email_code"]').value;
            const password1 = form.querySelector('[name="password1"]').value;
            const password2 = form.querySelector('[name="password2"]').value;
            const captcha = form.querySelector('[name="captcha_value"]').value;

            // 邮箱验证
            if (!email) {
                showError('请输入邮箱地址');
                return false;
            }
            const emailRegex = /^[^\s@]+@(qq\.com|163\.com|sina\.com|126\.com)$/i;
            if (!emailRegex.test(email)) {
                showError('仅支持QQ邮箱、网易邮箱、新浪邮箱和126邮箱');
                return false;
            }

            // 验证码验证
            if (!captcha) {
                showError('请输入图形验证码');
                return false;
            }

            // 邮箱验证码验证
            if (!emailCode) {
                showError('请输入邮箱验证码');
                return false;
            }

            // 密码验证
            if (!password1) {
                showError('请输入新密码');
                return false;
            }
            if (password1.length < 8) {
                showError('新密码长度至少为8个字符');
                return false;
            }
            let categories = 0;
            if (/[a-z]/.test(password1)) categories++;
            if (/[A-Z]/.test(password1)) categories++;
            if (/[0-9]/.test(password1)) categories++;
            if (/[!@#$%^&*()_+\-=\[\]{};:,.<>?]/.test(password1)) categories++;
            if (categories < 3) {
                showError('新密码需要包含小写字母、大写字母、数字、特殊字符中的至少三类');
                return false;
            }

            // 确认密码验证
            if (password1 !== password2) {
                showError('两次输入的新密码不一致');
                return false;
            }

            return true;
        },
        onSuccess: function(data, form) {
            showMessage(data.message || '密码重置成功！', 'success');
            
            // 延迟1.5秒后切换到登录表单
            setTimeout(() => {
                // 切换到登录标签页
                const loginTab = document.querySelector('[data-bs-target="#loginTab"]');
                const tabInstance = new bootstrap.Tab(loginTab);
                tabInstance.show();
                
                // 自动填充邮箱
                const loginEmail = document.querySelector('#loginEmail');
                if (loginEmail && data.email) {
                    loginEmail.value = data.email;
                }
                
                // 聚焦到密码输入框
                const loginPassword = document.querySelector('#loginPassword');
                if (loginPassword) {
                    loginPassword.focus();
                }
                
                // 清空重置密码表单
                form.reset();
                form.classList.remove('was-validated');
            }, 1500);
        }
    }
};

// 为每个表单添加提交处理
Object.entries(formHandlers).forEach(([formId, handler]) => {
    const form = document.getElementById(formId);
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            if (!handler.validate(this)) {
                return;
            }

            try {
                const formData = new FormData(this);
                const csrfToken = getCsrfToken();
                
                const response = await fetch(handler.url, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: formData
                });

                if (!response.ok) {
                    throw new Error('请求失败');
                }

                const data = await response.json();
                
                if (data.success) {
                    if (handler.onSuccess) {
                        handler.onSuccess(data);
                    } else {
                        showMessage(data.message || '操作成功！', 'success');
                    }
                } else {
                    showError(data.message || '操作失败，请重试');
                    if (data.message && data.message.includes('验证码')) {
                        refreshCaptcha();
                    }
                }
            } catch (error) {
                console.error('请求失败:', error);
                showError('服务器错误，请稍后重试');
            }
        });
    }
});

// 验证码图片刷新功能
document.querySelectorAll('.captcha-image').forEach(img => {
    img.style.cursor = 'pointer';
    img.title = '点击刷新验证码';
    img.addEventListener('click', function(e) {
        e.preventDefault();
        refreshCaptcha();
    });
});

// 刷新验证码函数
function refreshCaptcha() {
    fetch('/captcha/refresh/', {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        // 更新所有验证码图片和对应的 hashkey
        document.querySelectorAll('.captcha-image').forEach(img => {
            img.src = data.image_url;
            // 找到对应的 hashkey 输入框并更新值
            const form = img.closest('form');
            if (form) {
                const hashkeyInput = form.querySelector('[name="captcha_key"]');
                if (hashkeyInput) {
                    hashkeyInput.value = data.key;
                }
            }
        });
    })
    .catch(error => console.error('刷新验证码失败:', error));
}

// 获取 CSRF Token 的函数
function getCsrfToken() {
    const csrfToken = document.querySelector('[name="csrfmiddlewaretoken"]').value;
    if (!csrfToken) {
        throw new Error('CSRF Token not found');
    }
    return csrfToken;
}

// 发送验证码按钮处理
document.querySelectorAll('.send-code-btn').forEach(button => {
    button.addEventListener('click', async function() {
        try {
            const form = this.closest('form');
            const email = form.querySelector('[name="email"]').value;
            const captcha = form.querySelector('[name="captcha_value"]').value;
            const captchaKey = form.querySelector('[name="captcha_key"]').value;
            const formType = form.id === 'registerForm' ? 'register' : 'reset';
            
            // 获取 CSRF Token
            const csrfToken = getCsrfToken();
            
            if (!email) {
                showError('请输入邮箱地址');
                return;
            }
            
            if (!captcha) {
                showError('请输入图形验证码');
                return;
            }

            // 禁用按钮，防止重复点击
            this.disabled = true;

            // 验证码验证
            const captchaResponse = await fetch('/verify-captcha/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: new URLSearchParams({
                    'captcha_key': captchaKey,
                    'captcha_value': captcha
                })
            });

            if (!captchaResponse.ok) {
                throw new Error('验证码验证失败');
            }

            const captchaData = await captchaResponse.json();
            
            if (!captchaData.valid) {
                throw new Error('验证码错误');
            }

            // 发送邮箱验证码
            const emailResponse = await fetch('/send-email-code/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: new URLSearchParams({
                    'email': email,
                    'type': formType
                })
            });

            if (!emailResponse.ok) {
                throw new Error('发送验证码请求失败');
            }

            const emailData = await emailResponse.json();
            
            if (emailData.success) {
                countdown = 60;
                updateCountdown(this);
                showMessage('验证码已发送到您的邮箱');
            } else {
                this.disabled = false;  // 重新启用按钮
                showError(emailData.message || '发送验证码失败');
                return;  // 直接返回，不进入 catch 块
            }
            
        } catch (error) {
            console.error('网络请求失败:', error);  // 只记录真正的网络错误
            this.disabled = false;
            showError('网络错误，请稍后重试');
            if (error.message === '验证码错误') {
                refreshCaptcha();
            }
        }
    });
});

// 密码显示/隐藏功能
document.querySelectorAll('.toggle-password').forEach(button => {
    button.addEventListener('click', function() {
        const input = this.previousElementSibling;  // 获取密码输入框
        const icon = this.querySelector('i');  // 获取图标元素
        
        // 切换密码显示状态
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
});

// 在文档加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 初始化公告列表功能
    initAnnouncementList();
    
    // 监听设置模态框显示事件
    const settingsModal = document.getElementById('settingsModal');
    if (settingsModal) {
        settingsModal.addEventListener('show.bs.modal', function() {
            // 确保在模态框显示时重新初始化公告列表
            setTimeout(initAnnouncementList, 0);
        });
    }
    
    // 监听设置面板切换事件
    document.querySelectorAll('.settings-menu .list-group-item').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            
            // 移除所有菜单项的激活状态
            document.querySelectorAll('.settings-menu .list-group-item').forEach(i => {
                i.classList.remove('active');
            });
            
            // 添加当前菜单项的激活状态
            this.classList.add('active');
            
            // 获取目标面板
            const target = this.getAttribute('data-settings-target');
            
            // 隐藏所有面板
            document.querySelectorAll('.settings-panel').forEach(panel => {
                panel.classList.remove('active');
            });
            
            // 显示目标面板
            const targetPanel = document.getElementById(target + 'Panel');
            if (targetPanel) {
                targetPanel.classList.add('active');
                // 如果是公告面板，重新初始化公告列表
                if (target === 'announcements') {
                    initAnnouncementList();
                }
            }
        });
    });
});

// 初始化公告列表功能
function initAnnouncementList() {
    // 初始化 markdown-it
    const md = window.markdownit({
        html: true,
        breaks: true,
        linkify: true
    });
    
    // 渲染所有公告内容
    document.querySelectorAll('.announcement-item').forEach(item => {
        const contentTextarea = item.querySelector('textarea[id^="announcement-content-list-"]');
        const renderedContent = item.querySelector('div[id^="rendered-content-list-"]');
        const toggle = item.querySelector('.announcement-toggle');
        const content = item.querySelector('.announcement-content');
        
        // 确保初始状态
        if (item.classList.contains('expanded')) {
            toggle.style.transform = 'rotate(90deg)';
            content.classList.add('show');
        } else {
            toggle.style.transform = '';
            content.classList.remove('show');
        }
        
        if (contentTextarea && renderedContent) {
            // 渲染 Markdown 内容
            renderedContent.innerHTML = md.render(contentTextarea.value);
            
            // 应用代码高亮
            renderedContent.querySelectorAll('pre code').forEach(block => {
                hljs.highlightElement(block);
            });
        }
    });
    
    // 移除现有的事件监听器（防止重复绑定）
    document.querySelectorAll('.announcement-header').forEach(header => {
        const newHeader = header.cloneNode(true);
        header.parentNode.replaceChild(newHeader, header);
    });
    
    // 重新添加点击事件处理
    document.querySelectorAll('.announcement-header').forEach(header => {
        header.addEventListener('click', function(e) {
            e.preventDefault();
            const item = this.closest('.announcement-item');
            const content = item.querySelector('.announcement-content');
            const toggle = item.querySelector('.announcement-toggle');
            const isExpanded = item.classList.contains('expanded');
            
            // 关闭所有其他展开的公告
            document.querySelectorAll('.announcement-item').forEach(otherItem => {
                if (otherItem !== item && otherItem.classList.contains('expanded')) {
                    otherItem.classList.remove('expanded');
                    otherItem.querySelector('.announcement-content').classList.remove('show');
                    otherItem.querySelector('.announcement-toggle').style.transform = '';
                }
            });
            
            // 切换当前公告的展开状态
            item.classList.toggle('expanded');
            content.classList.toggle('show');
            toggle.style.transform = isExpanded ? '' : 'rotate(90deg)';
            
            // 如果是展开状态，标记公告为已读
            if (!isExpanded) {
                const announcementId = item.dataset.announcementId;
                markAnnouncementAsRead(announcementId);
            }
        });
    });
}

// 标记公告为已读
async function markAnnouncementAsRead(announcementId) {
    try {
        const response = await fetch(`/mark-announcement-read/${announcementId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        if (!response.ok) {
            throw new Error('标记公告已读失败');
        }
        
        const data = await response.json();
        if (data.success) {
            // 在本地存储中标记为已读
            localStorage.setItem(`announcement_${announcementId}_read`, 'true');
        }
    } catch (error) {
        console.error('标记公告已读出错:', error);
    }
}