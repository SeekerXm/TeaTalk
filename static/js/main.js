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
            // ... 重置密码的验证代码 ...
            return true;
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