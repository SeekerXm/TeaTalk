// 初始化 Markdown 编辑器
if (document.getElementById('id_content-wmd-wrapper')) {
    var editor = editormd("id_content-wmd-wrapper", {
        width: "100%",
        height: 500,
        path: "/static/mdeditor/lib/",
        toolbarIcons: function() {
            return [
                "undo", "redo", "|",
                "bold", "del", "italic", "quote", "ucwords", "uppercase", "lowercase", "|",
                "h1", "h2", "h3", "h5", "h6", "|",
                "list-ul", "list-ol", "hr", "|",
                "link", "reference-link", "image", "code", "preformatted-text", "code-block", "table",
                "datetime", "emoji", "html-entities", "pagebreak", "goto-line", "|",
                "help", "info", "||",
                "preview", "watch", "fullscreen"
            ]
        },
        flowChart: false,
        sequenceDiagram: false,
        tex: true,
        saveHTMLToTextarea: true,
        emoji: true,
        taskList: true,
        tocm: true,
        imageUpload: true,
        imageFormats: ["jpg", "jpeg", "gif", "png", "bmp", "webp"],
        imageUploadURL: "/upload/",
        lang: {
            toolbar: {
                undo: "撤销",
                redo: "重做",
                bold: "粗体",
                del: "删除线",
                italic: "斜体",
                quote: "引用",
                ucwords: "将每个单词首字母转成大写",
                uppercase: "将所选转换成大写",
                lowercase: "将所选转换成小写",
                h1: "标题1",
                h2: "标题2",
                h3: "标题3",
                h5: "标题5",
                h6: "标题6",
                "list-ul": "无序列表",
                "list-ol": "有序列表",
                hr: "横线",
                link: "链接",
                "reference-link": "引用链接",
                image: "添加图片",
                code: "行内代码",
                "preformatted-text": "预格式文本 / 代码块",
                "code-block": "代码块",
                table: "表格",
                datetime: "日期时间",
                emoji: "Emoji表情",
                "html-entities": "HTML实体字符",
                pagebreak: "分页符",
                "goto-line": "跳转到行",
                help: "使用帮助",
                info: "关于编辑器",
                preview: "预览",
                watch: "关注",
                fullscreen: "全屏"
            },
            buttons: {
                enter: "确定",
                cancel: "取消"
            },
            dialog: {
                link: {
                    title: "添加链接",
                    url: "链接地址",
                    urlTitle: "链接标题",
                    urlEmpty: "错误：请填写链接地址。"
                },
                image: {
                    title: "添加图片",
                    url: "图片地址",
                    link: "图片链接",
                    alt: "图片描述",
                    uploadButton: "本地上传",
                    imageURLEmpty: "错误：图片地址不能为空。",
                    uploadFileEmpty: "错误：上传的图片不能为空。"
                }
            }
        },
        onload: function() {
            console.log('Editor loaded successfully');
        }
    });
} 