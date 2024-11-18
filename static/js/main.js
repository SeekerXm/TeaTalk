document.addEventListener('DOMContentLoaded', function() {
    // 表单验证
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // 密码显示切换
    const toggleButtons = document.querySelectorAll('.toggle-password');
    toggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const input = this.previousElementSibling;
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
    });

    // 注册单密码确认验证
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        const password = registerForm.querySelector('#registerPassword');
        const confirmPassword = registerForm.querySelector('#registerConfirmPassword');
        
        function validatePassword() {
            if (password.value !== confirmPassword.value) {
                confirmPassword.setCustomValidity('两次输入的密码不一致');
            } else {
                confirmPassword.setCustomValidity('');
            }
        }

        password.addEventListener('change', validatePassword);
        confirmPassword.addEventListener('keyup', validatePassword);
    }

    // 刷新验证码
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

    // 为所有验证码图片添加点击事件
    const captchaImages = document.querySelectorAll('.captcha-image');
    console.log('找到验证码图片:', captchaImages.length); // 调试日志
    
    captchaImages.forEach(img => {
        img.style.cursor = 'pointer';
        img.title = '点击刷新验证码';
        img.addEventListener('click', function(e) {
            console.log('验证码图片被点击'); // 调试日志
            e.preventDefault();
            refreshCaptcha();
        });
    });

    // 发送邮箱验证码
    let countdown = 0;
    const updateCountdown = (button) => {
        if (countdown > 0) {
            button.disabled = true;
            button.textContent = `${countdown}秒后重试`;
            countdown--;
            setTimeout(() => updateCountdown(button), 1000);
        } else {
            button.disabled = false;
            button.textContent = '获验证码';
        }
    };
    
    document.querySelectorAll('.send-code-btn').forEach(button => {
        button.addEventListener('click', function() {
            const form = this.closest('form');
            const email = form.querySelector('[name="email"]').value;
            const captcha = form.querySelector('[name="captcha_value"]').value;
            const captchaKey = form.querySelector('[name="captcha_key"]').value;
            const csrfToken = document.querySelector('[name="csrfmiddlewaretoken"]').value;

            console.log('发送验证码 - 表单数据:', {
                email,
                captcha,
                captchaKey,
                csrfToken
            });

            // 验证码验证
            fetch('/verify-captcha/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken
                },
                body: new URLSearchParams({
                    'captcha_key': captchaKey,
                    'captcha_value': captcha
                })
            })
            .then(response => response.json())
            .then(data => {
                console.log('验证码验证结果:', data);
                if (data.valid) {
                    // 发送邮箱验证码
                    return fetch('/send-email-code/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'X-CSRFToken': csrfToken
                        },
                        body: new URLSearchParams({
                            'email': email
                        })
                    });
                } else {
                    throw new Error('验证码错误');
                }
            })
            .then(response => response.json())
            .then(data => {
                console.log('邮箱验证码发送结果:', data);
                if (data.success) {
                    countdown = 60;
                    updateCountdown(this);
                    showMessage('验证码已发送到您的邮箱', 'success');
                } else {
                    showError(data.message || '发送验证码失败');
                    refreshCaptcha();
                }
            })
            .catch(error => {
                console.error('请求失败:', error);
                showError(error.message || '网络错误，请稍后重试');
                if (error.message === '验证码错误') {
                    refreshCaptcha();
                }
            });
        });
    });
    
    // 表单提交处理
    const formHandlers = {
        'registerForm': {
            url: '/register/',
            validate: function(form) {
                const email = form.querySelector('[name="email"]').value;
                const password1 = form.querySelector('#registerPassword').value;
                const password2 = form.querySelector('#registerConfirmPassword').value;
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
                    showError('请输入人机验证码');
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
            }
        },
        'loginForm': {
            url: '/login/',
            validate: function(form) {
                const email = form.querySelector('#loginEmail').value;
                const password = form.querySelector('#loginPassword').value;

                if (!email) {
                    showError('请输入邮箱地址');
                    return false;
                }
                if (!password) {
                    showError('请输入密码');
                    return false;
                }
                return true;
            }
        },
        'resetForm': {
            url: '/reset-password/',
            validate: function(form) {
                const email = form.querySelector('#resetEmail').value;
                const emailCode = form.querySelector('[name="email_code"]').value;
                const password1 = form.querySelector('#resetPassword').value;
                const password2 = form.querySelector('#resetConfirmPassword').value;

                // 邮箱验证
                if (!email) {
                    showError('请输入邮箱地址');
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
            }
        }
    };

    // 为每个表单添加提交处理
    Object.entries(formHandlers).forEach(([formId, handler]) => {
        const form = document.getElementById(formId);
        if (form) {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                
                // 先进行客户端验证
                if (!handler.validate(this)) {
                    return;
                }

                const formData = new FormData(this);
                
                fetch(handler.url, {
                    method: 'POST',
                    body: formData
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        showMessage(data.message || '操作成功', 'success');
                        
                        // 如果是注册成功
                        if (formId === 'registerForm' && data.email) {
                            // 延迟1.5秒后切换到登录表单
                            setTimeout(() => {
                                // 切换到登录标签页
                                const loginTab = document.querySelector('[data-bs-target="#loginTab"]');
                                const tabInstance = new bootstrap.Tab(loginTab);
                                tabInstance.show();
                                
                                // 自动填充邮箱
                                const loginEmail = document.querySelector('#loginEmail');
                                if (loginEmail) {
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
                        } else if (formId === 'loginForm') {
                            location.reload();
                        }
                    } else {
                        showError(data.message || '操作失败');
                        // 如果是验证码错误，刷新验证码
                        if (data.message && data.message.includes('验证码')) {
                            refreshCaptcha();
                        }
                    }
                })
                .catch(error => {
                    console.error('请求失败:', error);
                    showError('服务器错误，请稍后重试');
                });
            });
        }
    });

    // 消息提示函数
    function showMessage(message, type = 'error') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type === 'success' ? 'success' : 'danger'} alert-dismissible fade show position-relative`;
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

    // 错误提示函数（使用 showMessage）
    function showError(message) {
        showMessage(message, 'error');
    }
});

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
    .catch(error => {
        console.error('刷新验证码失败:', error);
    });
} 