// 历史对话相关功能
let currentPage = 1;
const pageSize = 5;
let isLoading = false;
let isApiAvailable = true; // 添加API可用性标志

// 检查用户是否已登录
function isUserAuthenticated() {
    return document.body.classList.contains('user-authenticated');
}

// 创建新对话
async function createNewConversation() {
    if (!isUserAuthenticated()) {
        const authModal = new bootstrap.Modal(document.getElementById('authModal'));
        authModal.show();
        return;
    }

    // 如果API不可用，直接返回
    if (!isApiAvailable) {
        return;
    }

    try {
        const response = await fetch('/chat/create-conversation/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
            }
        });
        
        if (response.status === 404) {
            isApiAvailable = false;
            console.warn('对话API未就绪');
            return;
        }
        
        if (!response.ok) {
            throw new Error('创建对话失败');
        }
        
        const data = await response.json();
        if (data.success) {
            // 清空当前对话
            document.getElementById('chatMessages').innerHTML = '';
            // 重置对话状态
            currentConversationId = data.conversation_id;
            // 刷新对话列表
            loadConversationList();
        }
    } catch (error) {
        if (!error.message.includes('API未就绪')) {
            console.error('Error:', error);
            showError('创建新对话失败，请重试');
        }
    }
}

// 加载对话列表
async function loadConversationList(loadMore = false) {
    // 未登录或API不可用时不加载对话列表
    if (!isUserAuthenticated() || !isApiAvailable) {
        return;
    }
    
    if (isLoading) return;
    
    try {
        isLoading = true;
        const response = await fetch(`/chat/conversations/?page=${currentPage}&size=${pageSize}`);
        
        if (response.status === 404) {
            isApiAvailable = false;
            console.warn('对话列表API未就绪');
            return;
        }
        
        if (!response.ok) {
            throw new Error('获取对话列表失败');
        }
        
        const data = await response.json();
        if (data.success) {
            renderConversationList(data.conversations, loadMore);
            if (data.has_more) {
                showLoadMoreButton();
            } else {
                hideLoadMoreButton();
            }
        }
    } catch (error) {
        if (!error.message.includes('API未就绪')) {
            console.error('加载对话列表失败:', error);
            showError('加载对话列表失败');
        }
    } finally {
        isLoading = false;
    }
}

// 渲染对话列表
function renderConversationList(conversations, append = false) {
    const listContainer = document.querySelector('.conversation-list');
    if (!listContainer) return;
    
    if (!append) {
        listContainer.innerHTML = '';
    }
    
    conversations.forEach(conv => {
        const item = document.createElement('div');
        item.className = 'conversation-item';
        item.dataset.id = conv.id;
        
        const icon = conv.type === 'history' ? 
            '<i class="fas fa-question-circle text-primary" title="历史记录"></i>' :
            '<i class="fas fa-question-circle text-danger" title="临时记录"></i>';
            
        item.innerHTML = `
            <div class="conversation-title">${conv.title}</div>
            <div class="conversation-meta">
                ${icon}
                <button class="btn btn-sm btn-link delete-conversation">
                    <i class="fas fa-trash-alt"></i>
                </button>
            </div>
        `;
        
        listContainer.appendChild(item);
    });
}

// 显示加载更多按钮
function showLoadMoreButton() {
    let loadMoreBtn = document.querySelector('.load-more-btn');
    if (!loadMoreBtn) {
        loadMoreBtn = document.createElement('button');
        loadMoreBtn.className = 'load-more-btn btn btn-link w-100';
        loadMoreBtn.textContent = '加载更多';
        loadMoreBtn.onclick = () => {
            currentPage++;
            loadConversationList(true);
        };
        document.querySelector('.conversation-list').after(loadMoreBtn);
    }
    loadMoreBtn.style.display = 'block';
}

// 隐藏加载更多按钮
function hideLoadMoreButton() {
    const loadMoreBtn = document.querySelector('.load-more-btn');
    if (loadMoreBtn) {
        loadMoreBtn.style.display = 'none';
    }
}

// 修改初始化事件监听
document.addEventListener('DOMContentLoaded', function() {
    // 新建对话按钮
    const newChatBtn = document.getElementById('newChatBtn');
    if (newChatBtn) {
        newChatBtn.addEventListener('click', createNewConversation);
    }
    
    // 只在用户已登录且API可用时加载对话列表
    if (isUserAuthenticated()) {
        // 延迟加载对话列表，等待其他资源加载完成
        setTimeout(() => {
            loadConversationList();
        }, 500);
    }
    
    // 删除对话事件委托
    document.addEventListener('click', async function(e) {
        if (e.target.closest('.delete-conversation')) {
            if (!isUserAuthenticated() || !isApiAvailable) {
                if (!isUserAuthenticated()) {
                    const authModal = new bootstrap.Modal(document.getElementById('authModal'));
                    authModal.show();
                }
                return;
            }

            const item = e.target.closest('.conversation-item');
            if (!item) return;
            
            if (confirm('确定要删除这条对话吗？')) {
                try {
                    const response = await fetch(`/chat/delete-conversation/${item.dataset.id}/`, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': getCookie('csrftoken'),
                        }
                    });
                    
                    if (response.status === 404) {
                        isApiAvailable = false;
                        console.warn('删除对话API未就绪');
                        return;
                    }
                    
                    if (response.ok) {
                        item.remove();
                        showToast('删除成功');
                    }
                } catch (error) {
                    if (!error.message.includes('API未就绪')) {
                        console.error('Error:', error);
                        showError('删除失败，请重试');
                    }
                }
            }
        }
    });
}); 