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
});

// 添加邮箱验证函数
function validateEmail(email) {
    if (!email) return false;
    
    // 支持的邮箱后缀
    const allowedDomains = ['qq.com', '126.com', '163.com', 'sina.com'];
    // 邮箱格式正则表达式
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