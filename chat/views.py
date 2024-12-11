from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from aimodels.models import AIModel
from ModelPlatform.spark import SparkPlatform
from chat.models import ChatConversation, ChatDeletionLog, ChatMessage

def get_available_models(request):
    """获取可用的模型列表"""
    try:
        # 获取所有已启用的模型
        models = AIModel.objects.filter(is_active=True)
        
        # 准备基本的模型信息
        models_data = [{
            'id': model.id,
            'name': model.model_name,
            'platform': model.get_platform_display(),
            'version': model.get_version_display(),
            'type': model.model_type
        } for model in models]
        
        # 如果用户已登录，检查用户特定的权限
        if request.user.is_authenticated:
            user_model = request.user.user_models
            if not user_model.use_all_models:
                # 过滤出用户可用的模型
                allowed_model_ids = user_model.models.values_list('id', flat=True)
                models_data = [model for model in models_data if model['id'] in allowed_model_ids]
        
        return JsonResponse({
            'success': True,
            'models': models_data,
            'is_authenticated': request.user.is_authenticated
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'获取模型列表失败: {str(e)}'
        })

@login_required
def send_message(request):
    """处理发送消息的请求"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': '仅支持POST请求'})
        
    try:
        message = request.POST.get('message', '').strip()
        model_id = request.POST.get('model')
        conversation_id = request.POST.get('conversation_id')
        
        if not message:
            return JsonResponse({'success': False, 'message': '消息不能为空'})
            
        # 获取或创建对话
        if conversation_id:
            try:
                conversation = ChatConversation.objects.get(
                    id=conversation_id,
                    user=request.user,
                    status='active'
                )
            except ChatConversation.DoesNotExist:
                conversation = None
        else:
            conversation = None
        
        if not conversation:
            # 创建新对话，使用用户的第一条消息作为标题
            conversation = ChatConversation.objects.create(
                user=request.user,
                title=message[:100],  # 使用第一条消息作为标题，限制长度
                conversation_type='temporary',
                status='active'
            )
        
        # 保存用户消息
        ChatMessage.objects.create(
            conversation=conversation,
            role='user',
            content=message
        )
        
        # 获取模型配置并发送到AI
        try:
            model = AIModel.objects.get(id=model_id, is_active=True)
        except AIModel.DoesNotExist:
            return JsonResponse({'success': False, 'message': '选择的模型不可用'})
            
        # 创建讯飞星火平台实例
        platform = SparkPlatform()
        config = model.config or {}
        platform.appid = config.get('SPARK_APPID', '').strip()
        platform.api_key = config.get('SPARK_API_KEY', '').strip()
        platform.api_secret = config.get('SPARK_API_SECRET', '').strip()
        
        if not all([platform.appid, platform.api_key, platform.api_secret]):
            return JsonResponse({'success': False, 'message': '模型配置不完整'})
        
        platform.version = model.version
        
        try:
            # 调用AI接口
            response = platform.chat(message)
            
            # 保存AI回复
            ChatMessage.objects.create(
                conversation=conversation,
                role='assistant',
                content=response
            )
            
            return JsonResponse({
                'success': True,
                'response': response,
                'conversation_id': conversation.id
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'调用AI接口失败: {str(e)}'})
            
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'发送失败: {str(e)}'})

@login_required
def create_conversation(request):
    """创建新对话"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': '仅支持POST请求'})
        
    try:
        # 创建新对话
        conversation = ChatConversation.objects.create(
            user=request.user,
            title='',  # 不设置默认标题，等待第一条消息
            conversation_type='temporary',  # 默认为临时对话
            status='active'
        )
        
        return JsonResponse({
            'success': True,
            'conversation_id': conversation.id,
            'message': '新对话已创建'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'创建对话失败: {str(e)}'
        })

@login_required
def get_conversations(request):
    """获取对话列表"""
    try:
        page = int(request.GET.get('page', 1))
        size = int(request.GET.get('size', 5))
        
        # 获取用户的对话列表
        conversations = ChatConversation.objects.filter(
            user=request.user,
            status='active'
        ).order_by('-created_at')
        
        # 分页
        start = (page - 1) * size
        end = start + size
        page_conversations = conversations[start:end + 1]  # 多获取一条用于判断是否有更多
        
        has_more = len(page_conversations) > size
        if has_more:
            page_conversations = page_conversations[:size]
        
        # 准备返回数据
        conversations_data = [{
            'id': conv.id,
            'title': conv.title,
            'type': conv.conversation_type,
            'created_at': conv.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for conv in page_conversations]
        
        return JsonResponse({
            'success': True,
            'conversations': conversations_data,
            'has_more': has_more
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'获取对话列表失败: {str(e)}'
        })

@login_required
def delete_conversation(request, conversation_id):
    """删除对话"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': '仅支持POST请求'})
        
    try:
        conversation = ChatConversation.objects.get(
            id=conversation_id,
            user=request.user
        )
        
        # 软删除
        conversation.status = 'deleted'
        conversation.save()
        
        # 记录删除日志
        ChatDeletionLog.objects.create(
            conversation=conversation,
            user=request.user,
            deletion_type='user_initiated'
        )
        
        return JsonResponse({'success': True})
        
    except ChatConversation.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '对话不存在或无权限删除'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'删除失败: {str(e)}'
        })