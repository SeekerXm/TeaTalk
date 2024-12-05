from django.http import JsonResponse
from .models import AIModel
from django.db import transaction
from django.contrib.admin.views.decorators import staff_member_required

def get_available_models(request):
    """获取可用的模型列表"""
    try:
        models = AIModel.objects.filter(
            is_active=True,
            platform='spark'  # 目前只返回星火平台的模型
        ).order_by('weight')
        
        model_list = [{
            'id': model.id,
            'name': model.model_name,
            'platform': model.get_platform_display()
        } for model in models]
        
        return JsonResponse({
            'success': True,
            'models': model_list
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

@staff_member_required
def change_model_weight(request, model_id, direction):
    """调整模型权重"""
    try:
        with transaction.atomic():
            # 获取当前模型
            current_model = AIModel.objects.get(id=model_id)
            current_weight = current_model.weight
            
            # 使用一个足够大的临时权重值
            temp_weight = 99999
            
            if direction == 'up' and current_weight > 1:
                # 获取上一个模型
                prev_model = AIModel.objects.get(weight=current_weight - 1)
                
                # 使用临时权重进行交换
                current_model.weight = temp_weight
                current_model.save()
                
                prev_model.weight = current_weight
                prev_model.save()
                
                current_model.weight = current_weight - 1
                current_model.save()
                
            elif direction == 'down':
                try:
                    # 获取下一个模型
                    next_model = AIModel.objects.get(weight=current_weight + 1)
                    
                    # 使用临时权重进行交换
                    current_model.weight = temp_weight
                    current_model.save()
                    
                    next_model.weight = current_weight
                    next_model.save()
                    
                    current_model.weight = current_weight + 1
                    current_model.save()
                    
                except AIModel.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'error': '已经是最后一个模型'
                    })
            
            return JsonResponse({'success': True})
            
    except AIModel.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': '模型不存在'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })