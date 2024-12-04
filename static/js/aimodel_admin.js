(function($) {
    $(document).ready(function() {
        const platformSelect = $('#id_platform');
        const versionSelect = $('#id_version');
        const configHelp = $('.field-config .help');
        
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
            // ... 其他平台的版本选项
        };
        
        // 平台配置说明
        const platformConfigHelp = {
            'spark': `星火平台配置示例：
{
    "SPARK_APPID": "xxxxxxxx",
    "SPARK_API_KEY": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "SPARK_API_SECRET": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}`,
            // ... 其他平台的配置说明
        };
        
        // 更新版本选项和配置说明
        function updateFormFields() {
            const platform = platformSelect.val();
            
            // 更新版本选项
            versionSelect.empty();
            if (platform in platformVersions) {
                platformVersions[platform].forEach(([value, label]) => {
                    versionSelect.append(new Option(label, value));
                });
            }
            
            // 更新配置说明
            if (platform in platformConfigHelp) {
                configHelp.text(platformConfigHelp[platform]);
            }
        }
        
        // 监听平台选择变化
        platformSelect.on('change', updateFormFields);
        
        // 页面加载时初始化
        updateFormFields();
    });
})(django.jQuery); 