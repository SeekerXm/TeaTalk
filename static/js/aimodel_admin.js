// 等待 DOM 加载完成
document.addEventListener('DOMContentLoaded', function() {
    // 使用立即执行函数确保 jQuery 可用
    (function checkJQuery() {
        // 优先使用 django.jQuery，如果不可用则使用 window.jQuery
        let $ = window.django?.jQuery || window.jQuery;
        
        if (!$) {
            console.log('Waiting for jQuery...');
            return setTimeout(checkJQuery, 100);
        }
        
        initializeForm($);
    })();
});

function initializeForm($) {
    // 确保在函数开始时再次检查必要的元素
    const platformSelect = $('#id_platform');
    const versionSelect = $('#id_version');
    const configField = $('#id_config');
    const configHelp = $('#config_help');
    
    // 检查是否是编辑页面
    const isEditPage = !window.location.pathname.endsWith('/add/');
    
    // 如果是编辑页面，不需要检查所有元素
    if (isEditPage) {
        if (!configField.length || !configHelp.length) {
            console.warn('Required form elements not found in edit mode, retrying...');
            return setTimeout(() => initializeForm($), 100);
        }
    } else {
        // 添加页面需要检查所有元素
        if (!platformSelect.length || !versionSelect.length || 
            !configField.length || !configHelp.length) {
            console.warn('Required form elements not found in add mode, retrying...');
            return setTimeout(() => initializeForm($), 100);
        }
    }

    // 平台版本选项
    const platformVersions = {
        'spark': [
            ['lite', 'Spark Lite (基础版)'],
            ['pro', 'Spark Pro (专业版)'],
            ['pro-128k', 'Spark Pro-128K (长文本版)'],
            ['max', 'Spark Max (高级版)'],
            ['max-32k', 'Spark Max-32K (长文本高级版)'],
            ['ultra', 'Spark 4.0 Ultra (旗舰版)']
        ],
        'bigmodel': [
            ['glm-4', 'GLM-4'],
            ['glm-4-vision', 'GLM-4-Vision'],
            ['glm-3-turbo', 'GLM-3-Turbo']
        ],
        'qianfan': [
            ['yi-34b-chat', 'Yi-34B-Chat'],
            ['llama2-70b-chat', 'Llama2-70B-Chat'],
            ['llama2-13b-chat', 'Llama2-13B-Chat']
        ],
        'silicon': [
            ['qwen-turbo', 'Qwen-Turbo'],
            ['qwen-plus', 'Qwen-Plus'],
            ['qwen-max', 'Qwen-Max']
        ]
    };
    
    // 平台配置说明
    const configDescriptions = {
        'spark': `
            <div class="mb-3">
                <strong>讯飞星火平台配置说明：</strong><br>
                - SPARK_APPID：应用ID<br>
                - SPARK_API_KEY：API密钥<br>
                - SPARK_API_SECRET：安全密钥<br><br>
                <strong>配置示例：</strong><br>
                <pre>{
    "SPARK_APPID": "xxxxxxxx",
    "SPARK_API_KEY": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "SPARK_API_SECRET": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}</pre>
            </div>
        `,
        'bigmodel': `
            <div class="mb-3">
                <strong>智谱AI平台配置说明：</strong><br>
                - ZHIPU_API_KEY：API密钥<br><br>
                <strong>配置示例：</strong><br>
                <pre>{
    "ZHIPU_API_KEY": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}</pre>
            </div>
        `,
        'qianfan': `
            <div class="mb-3">
                <strong>百度千帆平台配置说明：</strong><br>
                - QIANFAN_ACCESS_KEY：访问密钥<br>
                - QIANFAN_SECRET_KEY：安全密钥<br><br>
                <strong>配置示例：</strong><br>
                <pre>{
    "QIANFAN_ACCESS_KEY": "xxxxxxxxxxxxxxxxxxxxxxxx",
    "QIANFAN_SECRET_KEY": "xxxxxxxxxxxxxxxxxxxxxxxx"
}</pre>
            </div>
        `,
        'silicon': `
            <div class="mb-3">
                <strong>SiliconCloud平台配置说明：</strong><br>
                - SILICON_API_KEY：API密钥<br><br>
                <strong>配置示例：</strong><br>
                <pre>{
    "SILICON_API_KEY": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}</pre>
            </div>
        `
    };

    // 平台配置模板
    const configTemplates = {
        'spark': {
            "SPARK_APPID": "xxxxxxxx",
            "SPARK_API_KEY": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "SPARK_API_SECRET": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        },
        'bigmodel': {
            "ZHIPU_API_KEY": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        },
        'qianfan': {
            "QIANFAN_ACCESS_KEY": "xxxxxxxxxxxxxxxxxxxxxxxx",
            "QIANFAN_SECRET_KEY": "xxxxxxxxxxxxxxxxxxxxxxxx"
        },
        'silicon': {
            "SILICON_API_KEY": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        }
    };

    // 在编辑页面初始化时显示配置说明
    if (isEditPage) {
        // 尝试多种方式获取当前平台值
        let currentPlatform = configHelp.data('platform');
        
        // 如果没有找到，尝试从隐藏字段获取
        if (!currentPlatform) {
            currentPlatform = $('#id_platform').val();
        }
        
        console.log('Current platform in edit mode:', currentPlatform);
        
        // 确保配置说明显示
        if (currentPlatform && configDescriptions[currentPlatform]) {
            console.log('Setting config description for platform:', currentPlatform);
            configHelp.html(configDescriptions[currentPlatform]).show();
        } else {
            console.warn('Platform not found or no description available:', currentPlatform);
        }

        // 添加平台值变化的监听（以防万一）
        $('#id_platform').on('change', function() {
            const platform = $(this).val();
            if (platform && configDescriptions[platform]) {
                configHelp.html(configDescriptions[platform]).show();
            }
        });
    }

    // 只在添加页面时初始化这些功能
    if (!isEditPage) {
        // 处理状态切换
        const statusSwitch = $('#id_is_active');
        
        // 监听状态变化
        statusSwitch.on('change', function() {
            $(this).closest('.status-switch')
                .toggleClass('active', this.checked);
        });
        
        // 更新版本选项和配置说明
        function updateFormFields() {
            const platform = platformSelect.val();
            console.log('Updating form fields for platform:', platform);
            
            try {
                // 更新版本选项
                versionSelect.empty();
                if (platform && platformVersions[platform]) {
                    // 添加默认选项
                    versionSelect.append(new Option('请选择版本', ''));
                    
                    // 添加平台对应的版本选项
                    platformVersions[platform].forEach(([value, label]) => {
                        versionSelect.append(new Option(label, value));
                    });
                    versionSelect.prop('disabled', false);
                    versionSelect.prop('required', true);
                } else {
                    versionSelect.prop('disabled', true);
                    versionSelect.prop('required', false);
                }
                
                // 更新配置说明
                if (platform && configDescriptions[platform]) {
                    configHelp.html(configDescriptions[platform]).show();
                } else {
                    configHelp.empty().hide();
                }

                // 检查是否是添加新模型页面
                const isAddPage = window.location.pathname.endsWith('/add/');
                
                // 更新配置模板
                if (platform && configTemplates[platform]) {
                    // 只在添加页面或配置为空时更新配置模板
                    if (isAddPage || !configField.val().trim()) {
                        const formattedConfig = JSON.stringify(configTemplates[platform], null, 4);
                        configField.val(formattedConfig);
                    }
                } else if (isAddPage) {
                    // 在添加页面，如果没有选择平台则清空配置
                    configField.val('');
                }
                
            } catch (error) {
                console.error('Error updating form fields:', error);
            }
        }
        
        // 监听平台选择变化
        platformSelect.on('change', updateFormFields);
        
        // 监听版本选择变化
        versionSelect.on('change', function() {
            const selectedVersion = $(this).val();
            if (!selectedVersion) {
                $(this).addClass('is-invalid');
            } else {
                $(this).removeClass('is-invalid');
            }
        });
        
        // 初始化表单字段
        updateFormFields();
        
        // 如果已经选择了平台，触发一次更新
        if (platformSelect.val()) {
            platformSelect.trigger('change');
        }

        // 使用 Bootstrap 的方式初始化 tooltips
        try {
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.forEach(function(tooltipTriggerEl) {
                new bootstrap.Tooltip(tooltipTriggerEl);
            });
        } catch (error) {
            console.warn('Tooltip initialization failed:', error);
        }
    }
}