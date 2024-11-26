from django.db import migrations

def create_initial_models(apps, schema_editor):
    AIModel = apps.get_model('aimodels', 'AIModel')
    
    # 添加所有默认模型
    default_models = [
        {
            'model_type': 'chat',
            'model_name': 'GLM-4-Flash',
            'platform': 'bigmodel',
            'is_active': True,
            'weight': 1,
            'config': {'ZHIPU_API_KEY': '8e1436a72f831bf54b6ae4ca43587788.sUsYvAEEXcNF84X0'}
        },
        {
            'model_type': 'chat',
            'model_name': 'Spark Lite',
            'platform': 'spark',
            'is_active': True,
            'weight': 2,
            'config': {
                'SPARK_APPID': '27ca9f10',
                'SPARK_API_KEY': '78de37f4f0cb76b95bb94de437d7fc5c',
                'SPARK_API_SECRET': 'YTYzZGE0ZmY2ZjFjOTIwNmZjNjdiZDAy'
            }
        },
        {
            'model_type': 'chat',
            'model_name': 'Yi-34B',
            'platform': 'qianfan',
            'is_active': True,
            'weight': 3,
            'config': {
                'QIANFAN_ACCESS_KEY': 'ALTAKp6vpru3TSWZ0ZDRmhhOza',
                'QIANFAN_SECRET_KEY': '2dac3d6e90ca44d7939932f26b68c2a2'
            }
        },
        {
            'model_type': 'chat',
            'model_name': 'Qwen2.5-Coder',
            'platform': 'silicon',
            'is_active': True,
            'weight': 4,
            'config': {'SILICON_API_KEY': 'sk-dbpqlfjeedqscsxcedtblzvtjtakcrmzhxpgihkmycdbyfkj'}
        },
        {
            'model_type': 'chat',
            'model_name': 'Qwen2.5-Chat',
            'platform': 'silicon',
            'is_active': True,
            'weight': 5,
            'config': {'SILICON_API_KEY': 'sk-dbpqlfjeedqscsxcedtblzvtjtakcrmzhxpgihkmycdbyfkj'}
        },
        {
            'model_type': 'chat',
            'model_name': 'ChatGLM3-6B',
            'platform': 'silicon',
            'is_active': True,
            'weight': 6,
            'config': {'SILICON_API_KEY': 'sk-dbpqlfjeedqscsxcedtblzvtjtakcrmzhxpgihkmycdbyfkj'}
        },
        {
            'model_type': 'chat',
            'model_name': 'Gemma-2-9B',
            'platform': 'silicon',
            'is_active': True,
            'weight': 7,
            'config': {'SILICON_API_KEY': 'sk-dbpqlfjeedqscsxcedtblzvtjtakcrmzhxpgihkmycdbyfkj'}
        }
    ]
    
    for model_data in default_models:
        AIModel.objects.create(**model_data)

def reverse_initial_models(apps, schema_editor):
    AIModel = apps.get_model('aimodels', 'AIModel')
    AIModel.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('aimodels', '0001_initial'),
    ]
    
    operations = [
        migrations.RunPython(create_initial_models, reverse_initial_models),
    ] 