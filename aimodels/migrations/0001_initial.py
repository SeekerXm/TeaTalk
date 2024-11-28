from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AIModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model_type', models.CharField(choices=[('chat', '对话'), ('image', '图像')], max_length=10, verbose_name='模型类型')),
                ('model_name', models.CharField(max_length=50, verbose_name='模型名称')),
                ('platform', models.CharField(choices=[('spark', '讯飞星火'), ('bigmodel', 'BigModel'), ('qianfan', '百度千帆'), ('silicon', 'SiliconCloud')], max_length=20, verbose_name='模型平台')),
                ('is_active', models.BooleanField(choices=[(True, '启用'), (False, '停用')], default=True, verbose_name='模型状态')),
                ('weight', models.IntegerField(unique=True, verbose_name='模型权重')),
                ('config', models.JSONField(default=dict, verbose_name='模型配置')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('original_model_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='原始模型名称')),
            ],
            options={
                'verbose_name': '模型管理',
                'verbose_name_plural': '模型管理',
                'ordering': ['weight'],
            },
        ),
        migrations.CreateModel(
            name='UserModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('use_all_models', models.BooleanField(default=True, verbose_name='使用所有模型')),
                ('updated_at', models.DateTimeField(blank=True, null=True, verbose_name='编辑时间')),
                ('models', models.ManyToManyField(blank=True, to='aimodels.aimodel', verbose_name='可用模型')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='users.user', verbose_name='用户')),
            ],
            options={
                'verbose_name': '用户模型',
                'verbose_name_plural': '用户模型',
                'ordering': ['-updated_at'],
            },
        ),
    ]
