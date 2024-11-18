from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from .models import User

class EmailOrUsernameModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # 使用 Q 对象来实现 OR 查询
            user = User.objects.get(
                Q(username=username) | Q(email=username)
            )
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None 