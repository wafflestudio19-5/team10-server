from django.db import models

# Create your models here.
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin


class CustomUserManager(BaseUserManager):
    # CustomUserManager 가 위에 임포트해두고 쓰지 않는 UserManager 와 어떻게 다른지 파악하면서 보시면 좋을 것 같습니다.
    # 이메일 기반으로 인증 방식을 변경하기 위한 구현입니다.

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('이메일을 설정해주세요.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):

        # setdefault -> 딕셔너리에 key가 없을 경우 default로 값 설정
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True or extra_fields.get('is_superuser') is not True:
            raise ValueError('권한 설정이 잘못되었습니다.')

        return self._create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    profile_id = models.CharField(max_length=25, unique=True)
    display_name = models.CharField(max_length=25)
    password = models.CharField(max_length=128)
    email = models.EmailField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    age = models.PositiveIntegerField(null=True)
    gender = models.CharField(max_length=20, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = email
    USERNAME_FIELD = 'email'
