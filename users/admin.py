from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import path
from django.template.response import TemplateResponse
from django.utils import timezone
from datetime import datetime, timedelta
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'status_tag', 'user_type_tag', 'date_joined', 'last_login')
    list_filter = ('status', 'user_type')
    search_fields = ('email', 'username')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('个人信息', {'fields': ('username',)}),
        ('权限', {
            'fields': (
                'user_type',
                'status',
                'ban_until',
                'is_active',
                'groups',
                'user_permissions',
            ),
        }),
        ('重要日期', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    
    change_list_template = "admin/user_changelist.html"
    change_form_template = "admin/user_change_form.html"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<id>/change-status/',
                self.admin_site.admin_view(self.change_status_view),
                name='user-change-status',
            ),
        ]
        return custom_urls + urls

    def change_status_view(self, request, id):
        user = self.get_object(request, id)
        
        # 检查是否是管理员
        if user.user_type == 'admin':
            self.message_user(request, "无法修改管理员状态！", level=messages.ERROR)
            return HttpResponseRedirect("../")
            
        if request.method == 'POST':
            ban_type = request.POST.get('ban_type')
            
            if ban_type == 'permanent':
                user.status = 'banned'
                user.ban_until = None  # 永久封禁
                self.message_user(request, "用户状态已更新为：永久封禁")
            elif ban_type == 'custom':
                try:
                    days = int(request.POST.get('custom_days', 0))
                    hours = int(request.POST.get('custom_hours', 0))
                    minutes = int(request.POST.get('custom_minutes', 0))
                    
                    if days == 0 and hours == 0 and minutes == 0:
                        raise ValueError("封禁时长必须大于0")
                    
                    total_minutes = days * 24 * 60 + hours * 60 + minutes
                    user.status = 'banned'
                    user.ban_until = timezone.now() + timedelta(minutes=total_minutes)
                    
                    # 构建时长显示
                    time_parts = []
                    if days > 0:
                        time_parts.append(f"{days}天")
                    if hours > 0:
                        time_parts.append(f"{hours}小时")
                    if minutes > 0:
                        time_parts.append(f"{minutes}分钟")
                    time_str = "".join(time_parts)
                    
                    self.message_user(request, f"用户状态已更新为：封禁({time_str})")
                except ValueError as e:
                    self.message_user(request, f"无效的封禁时长！{str(e)}", level=messages.ERROR)
                    return HttpResponseRedirect("../")
            else:
                try:
                    days = int(ban_type)
                    user.status = 'banned'
                    user.ban_until = timezone.now() + timedelta(days=days)
                    self.message_user(request, f"用户状态已更新为：封禁({days}天)")
                except ValueError:
                    self.message_user(request, "无效的封禁类型！", level=messages.ERROR)
                    return HttpResponseRedirect("../")
                
            user.save()
            return HttpResponseRedirect("../")
            
        return TemplateResponse(request, 'admin/user_ban_action.html', {
            'title': '修改用户状态',
            'queryset': [user],  # 包装成列表以兼容模板
            'opts': self.model._meta,
            'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
        })

    def response_change(self, request, obj):
        if "_change-status" in request.POST:
            return HttpResponseRedirect(
                f'change-status/'
            )
        return super().response_change(request, obj)
    
    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        if obj.user_type == 'admin':
            return self.fieldsets
        return self.fieldsets
    
    def status_tag(self, obj):
        """自定义状态显示"""
        status_colors = {
            'normal': 'success',
            'warning': 'warning',
            'banned': 'danger'
        }
        status_icons = {
            'normal': '●',
            'warning': '⚠',
            'banned': '⛔'
        }
        color = status_colors.get(obj.status, 'secondary')
        icon = status_icons.get(obj.status, '')
        
        if obj.status == 'banned' and obj.ban_until:
            return format_html(
                '<span class="badge bg-{}" data-ban-until="(至 {})">'
                '{} {}</span>',
                color,
                obj.ban_until.strftime('%Y-%m-%d %H:%M'),
                icon,
                obj.get_status_display()
            )
        return format_html(
            '<span class="badge bg-{}">{} {}</span>',
            color,
            icon,
            obj.get_status_display()
        )
    status_tag.short_description = '状态'
    status_tag.admin_order_field = 'status'

    def user_type_tag(self, obj):
        """自定义用户类型显示"""
        type_colors = {
            'admin': 'primary',
            'user': 'info'
        }
        type_icons = {
            'admin': '👑',
            'user': '👤'
        }
        color = type_colors.get(obj.user_type, 'secondary')
        icon = type_icons.get(obj.user_type, '')
        return format_html(
            '<span class="badge bg-{}">{} {}</span>',
            color,
            icon,
            obj.get_user_type_display()
        )
    user_type_tag.short_description = '用户类型'
    user_type_tag.admin_order_field = 'user_type'
    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            if obj.user_type == 'admin':
                return ['status', 'ban_until']
            return ['username', 'user_type']  # 普通用户不能修改用户名和用户类型
        return []
    
    def save_model(self, request, obj, form, change):
        if not change:  # 创建新用户时
            obj.set_password(form.cleaned_data["password1"])
            obj.username = None
            obj.user_type = 'user'
        super().save_model(request, obj, form, change)
    
    def display_username(self, obj):
        if obj.username and obj.email and obj.user_type == 'admin':
            return obj.username
        return '-'
    display_username.short_description = '用户名'
    
    def set_status_normal(self, modeladmin, request, queryset):
        admin_users = queryset.filter(user_type='admin')
        if admin_users.exists():
            self.message_user(request, "无法修改管理员状态！", level=messages.ERROR)
            return
        queryset.update(status='normal', ban_until=None)
        self.message_user(request, f"已将选中用户状态更新为：正常")
    set_status_normal.short_description = "设为正常状态"
    
    def set_status_warning(self, modeladmin, request, queryset):
        admin_users = queryset.filter(user_type='admin')
        if admin_users.exists():
            self.message_user(request, "无法修改管理员状态！", level=messages.ERROR)
            return
        queryset.update(status='warning', ban_until=None)
        self.message_user(request, f"已将选中用户状态更新为：警告")
    set_status_warning.short_description = "设为警告状态"
    
    def set_status_banned_custom(self, modeladmin, request, queryset):
        """自定义封禁时间"""
        if 'apply' in request.POST:
            ban_type = request.POST.get('ban_type')
            
            admin_users = queryset.filter(user_type='admin')
            if admin_users.exists():
                self.message_user(request, "无法修改管理员状态！", level=messages.ERROR)
                return
                
            if ban_type == 'permanent':
                queryset.update(status='banned', ban_until=None)
                self.message_user(request, "已将选中用户状态更新为：永久封禁")
            elif ban_type == 'custom':
                try:
                    days = int(request.POST.get('custom_days', 0))
                    hours = int(request.POST.get('custom_hours', 0))
                    minutes = int(request.POST.get('custom_minutes', 0))
                    
                    if days == 0 and hours == 0 and minutes == 0:
                        raise ValueError("封禁时长必须大于0")
                    
                    total_minutes = days * 24 * 60 + hours * 60 + minutes
                    ban_until = timezone.now() + timedelta(minutes=total_minutes)
                    queryset.update(status='banned', ban_until=ban_until)
                    
                    # 构建时长显示
                    time_parts = []
                    if days > 0:
                        time_parts.append(f"{days}天")
                    if hours > 0:
                        time_parts.append(f"{hours}小时")
                    if minutes > 0:
                        time_parts.append(f"{minutes}分钟")
                    time_str = "".join(time_parts)
                    
                    self.message_user(request, f"已将选中用户状态更新为：封禁({time_str})")
                except ValueError as e:
                    self.message_user(request, f"无效的封禁时长！{str(e)}", level=messages.ERROR)
            else:
                try:
                    days = int(ban_type)
                    ban_until = timezone.now() + timedelta(days=days)
                    queryset.update(status='banned', ban_until=ban_until)
                    self.message_user(request, f"已将选中用户状态更新为：封禁({days}天)")
                except ValueError:
                    self.message_user(request, "无效的封禁类型！", level=messages.ERROR)
            return None
            
        return TemplateResponse(request, 'admin/user_ban_action.html', {
            'title': '选择封禁时长',
            'queryset': queryset,
            'opts': self.model._meta,
            'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
        })
    set_status_banned_custom.short_description = "封禁选中用户"
    
    def get_actions(self, request):
        # 获取默认的操作
        actions = super().get_actions(request)
        
        if self.has_change_permission(request):
            # 自定义删除操作
            actions['delete_selected'] = (
                self.delete_selected_users,  # 新的删除方法
                'delete_selected',
                '删除所选的 %(verbose_name_plural)s'  # 保持原有的描述
            )
            
            # 添加状态修改操作
            actions['set_status_normal'] = (
                self.set_status_normal,
                'set_status_normal',
                "设为正常状态"
            )
            actions['set_status_warning'] = (
                self.set_status_warning,
                'set_status_warning',
                "设为警告状态"
            )
            actions['set_status_banned_custom'] = (
                self.set_status_banned_custom,
                'set_status_banned_custom',
                "封禁选中用户"
            )
        return actions
    
    def delete_selected_users(self, modeladmin, request, queryset):
        """自定义的删除操作，不需要二次确认"""
        queryset.delete()
        self.message_user(request, "选中的用户已被删除。")
    delete_selected_users.short_description = "删除所选的用户"

    class Media:
        css = {
            'all': ('css/custom_admin.css',)
        }