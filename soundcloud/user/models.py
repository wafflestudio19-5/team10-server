from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from datetime import date
from django.conf import settings


class CustomUserManager(BaseUserManager):
    # CustomUserManager 가 위에 임포트해두고 쓰지 않는 UserManager 와 어떻게 다른지 파악하면서 보시면 좋을 것 같습니다.
    # 이메일 기반으로 인증 방식을 변경하기 위한 구현입니다.

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('이메일을 설정해주세요.')
        path = extra_fields.get('path')
        email = self.normalize_email(email)
        permalink = self.create_permalink()
        user = self.model(email=email, permalink=permalink, **extra_fields)
        if (password == settings.SOCIAL_PASSWORD) and (path == "google"):
            user.set_unusable_password()
        else:
            user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_staff', False)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_superuser') is not True or extra_fields.get('is_staff') is not True:
            raise ValueError('권한 설정이 잘못되었습니다.')

        return self._create_user(email, password, **extra_fields)

    def create_permalink(self):
        while True:
            permalink = User.objects.make_random_password(
                length=12, allowed_chars="abcdefghijklmnopqrstuvwxyz0123456789")
            if not User.objects.filter(permalink=permalink).exists():
                return permalink


class User(AbstractBaseUser, PermissionsMixin):

    permalink = models.SlugField(max_length=25, unique=True)
    display_name = models.CharField(max_length=25)
    email = models.EmailField(max_length=100, unique=True)
    image_profile = models.URLField(null=True, unique=True)
    image_header = models.URLField(null=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    birthday = models.DateField(null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    gender = models.CharField(max_length=20, blank=True)
    first_name = models.CharField(max_length=35, blank=True)
    last_name = models.CharField(max_length=35, blank=True)
    city = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    path = models.TextField(blank=True) #add for sociallogin
    #is_staff field err

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'


class Follow(models.Model):

    follower = models.ForeignKey(get_user_model(), related_name="followings", on_delete=models.CASCADE)
    followee = models.ForeignKey(get_user_model(), related_name="followers", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
