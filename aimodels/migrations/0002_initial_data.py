from django.db import migrations
from django.conf import settings

def create_initial_models(apps, schema_editor):
    AIModel = apps.get_model('aimodels', 'AIModel')
    
    models_data = [
        {
            'model_type': 'chat',
            'model_name': 'Spark Lite',
            'platform': 'spark',
            'weight': 1,
            'is_active': True,
            'original_model_name': 'lite',
            'config': {
                'SPARK_APPID': settings.SPARK_APPID,
                'SPARK_API_KEY': settings.SPARK_API_KEY,
                'SPARK_API_SECRET': settings.SPARK_API_SECRET
            }
        },
        {
            'model_type': 'chat',
            'model_name': 'GLM-4-Flash',
            'platform': 'bigmodel',
            'weight': 2,
            'is_active': True,
            'original_model_name': 'glm-4-flash',
            'config': {'ZHIPU_API_KEY': settings.ZHIPU_API_KEY}
        },
        {
            'model_type': 'chat',
            'model_name': 'Yi-34B',
            'platform': 'qianfan',
            'weight': 3,
            'is_active': True,
            'original_model_name': 'Yi-34B-Chat',
            'config': {
                'QIANFAN_ACCESS_KEY': settings.QIANFAN_ACCESS_KEY,
                'QIANFAN_SECRET_KEY': settings.QIANFAN_SECRET_KEY
            }
        },
        {
            'model_type': 'chat',
            'model_name': 'Qwen2.5-Coder',
            'platform': 'silicon',
            'weight': 4,
            'is_active': True,
            'original_model_name': 'Qwen2.5-Coder-7B-Instruct',
            'config': {'SILICON_API_KEY': settings.SILICON_API_KEY}
        },
        {
            'model_type': 'chat',
            'model_name': 'ChatGLM3-6B',
            'platform': 'silicon',
            'weight': 5,
            'is_active': True,
            'original_model_name': 'chatglm3-6b',
            'config': {'SILICON_API_KEY': settings.SILICON_API_KEY}
        },
        {
            'model_type': 'chat',
            'model_name': 'Qwen2.5-Chat',
            'platform': 'silicon',
            'weight': 6,
            'is_active': True,
            'original_model_name': 'Qwen2.5-7B-Instruct',
            'config': {'SILICON_API_KEY': settings.SILICON_API_KEY}
        },
        {
            'model_type': 'chat',
            'model_name': 'Gemma-2-9B',
            'platform': 'silicon',
            'weight': 7,
            'is_active': True,
            'original_model_name': 'gemma-2-9b-it',
            'config': {'SILICON_API_KEY': settings.SILICON_API_KEY}
        },
    ]
    
    for data in models_data:
        AIModel.objects.create(**data)

def delete_models(apps, schema_editor):
    AIModel = apps.get_model('aimodels', 'AIModel')
    AIModel.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('aimodels', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_models, delete_models),
    ] 