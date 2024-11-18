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

    // 注册密码确认验证
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
            }
        },
        'resetForm': {
            url: '/reset-password/',
            validate: function(form) {
                const email = form.querySelector('[name="email"]').value;
                const emailCode = form.querySelector('[name="email_code"]').value;
                const password1 = form.querySelector('[name="password1"]').value;
                const password2 = form.querySelector('[name="password2"]').value;

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
                
                if (!handler.validate(this)) {
                    return;
                }

                const formData = new FormData(this);
                const csrfToken = document.querySelector('[name="csrfmiddlewaretoken"]').value;
                
                fetch(handler.url, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: formData,
                    credentials: 'same-origin'
                })
                .then(response => {
                    console.log('响应状态:', response.status);
                    if (!response.ok) {
                        return response.text().then(text => {
                            console.error('错误响应内容:', text);
                            throw new Error(`HTTP error! status: ${response.status}`);
                        });
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('响应数据:', data);
                    if (data.success) {
                        if (formId === 'loginForm') {
                            showMessage('登录成功！', 'success');
                            setTimeout(() => {
                                location.reload();
                            }, 1000);
                        } else if (formId === 'resetForm' && data.email) {
                            // 重置密码成功后的处理
                            showMessage(data.message || '密码重置成功！', 'success');
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
                                
                                // 清空重置密码表单
                                form.reset();
                                form.classList.remove('was-validated');
                            }, 1500);
                        } else if (formId === 'registerForm' && data.email) {
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
                        }
                    } else {
                        // 显示错误消息
                        const errorMessage = data.message;
                        if (errorMessage.includes('封禁')) {
                            // 对于封禁消息使用特殊样式
                            showError(errorMessage, 'ban-error');
                        } else {
                            showError(errorMessage);
                        }
                        if (errorMessage && errorMessage.includes('验证码')) {
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
    function showError(message, className = '') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-danger alert-dismissible fade show position-relative ${className}`;
        alertDiv.style.marginBottom = '1rem';
        
        // 为封禁错误添加特殊样式
        const iconClass = className === 'ban-error' ? 'fa-ban' : 'fa-exclamation-circle';
        
        alertDiv.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas ${iconClass} me-2"></i>
                <div>${message}</div>
                <button type="button" class="btn-close ms-auto" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        // 找到当前激活的表单面板
        const activePane = document.querySelector('.tab-pane.active');
        if (activePane) {
            const form = activePane.querySelector('form');
            if (form) {
                form.insertAdjacentElement('beforebegin', alertDiv);
            }
        }
        
        // 封禁错误提示显示时间更长
        const timeout = className === 'ban-error' ? 5000 : 3000;
        setTimeout(() => {
            alertDiv.classList.remove('show');
            setTimeout(() => alertDiv.remove(), 150);
        }, timeout);
    }

    // 公告相关功能
    document.addEventListener('DOMContentLoaded', function() {
        // 处理公告点击事件
        document.querySelectorAll('.announcement-item').forEach(item => {
            item.addEventListener('click', function(e) {
                e.preventDefault();
                const announcementId = this.dataset.announcementId;
                
                // 获取公告详情
                fetch(`/announcement/${announcementId}/`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            // 填充公告详情模态框
                            document.getElementById('announcementTitle').textContent = data.title;
                            document.getElementById('announcementContent').innerHTML = data.content;
                            document.getElementById('announcementDate').textContent = 
                                `发布时间：${data.created_at}`;
                            
                            // 隐藏设置模态框，显示公告详情模态框
                            const settingsModal = bootstrap.Modal.getInstance(
                                document.getElementById('settingsModal')
                            );
                            settingsModal.hide();
                            
                            const announcementModal = new bootstrap.Modal(
                                document.getElementById('announcementDetailModal')
                            );
                            announcementModal.show();
                        } else {
                            showError('获取公告详情失败');
                        }
                    })
                    .catch(error => {
                        console.error('获取公告详情失败:', error);
                        showError('网络错误，请稍后重试');
                    });
            });
        });
    });

    // 设置模态框菜单切换
    const menuItems = document.querySelectorAll('.settings-menu .list-group-item');
    
    menuItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            
            // 移除所有菜单项的激活状态
            menuItems.forEach(i => i.classList.remove('active'));
            // 激活当前菜单项
            this.classList.add('active');
            
            // 获取目标面板
            const target = this.dataset.settingsTarget;
            
            // 隐藏所有面板
            document.querySelectorAll('.settings-panel').forEach(panel => {
                panel.classList.remove('active');
            });
            
            // 显示目标面板
            document.getElementById(`${target}Panel`).classList.add('active');
        });
    });
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