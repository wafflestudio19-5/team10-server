from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from datetime import date


class CustomUserManager(BaseUserManager):
    # CustomUserManager 가 위에 임포트해두고 쓰지 않는 UserManager 와 어떻게 다른지 파악하면서 보시면 좋을 것 같습니다.
    # 이메일 기반으로 인증 방식을 변경하기 위한 구현입니다.

    use_in_migrations = True

    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('이메일을 설정해주세요.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


def create_permalink():
    while True:
        permalink = User.objects.make_random_password(
            length=12, allowed_chars="abcdefghijklmnopqrstuvwxyz0123456789")
        if not User.objects.filter(permalink=permalink).exists():
            return permalink


class User(AbstractBaseUser):
    permalink = models.CharField(
        max_length=25, unique=True, default=create_permalink)
    display_name = models.CharField(max_length=25)
    email = models.EmailField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    birthday = models.DateField(default=date.today)
    gender = models.CharField(max_length=20, blank=True)
    first_name = models.CharField(max_length=35, blank=True)
    last_name = models.CharField(max_length=35, blank=True)
    city = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    # profile_image = models.ImageField(null=True, blank=True)
    # header_image = models.ImageField(null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'


class Follow(models.Model):
    follower = models.ForeignKey(get_user_model(), related_name="follows", on_delete=models.CASCADE)
    followee = models.ForeignKey(get_user_model(), related_name="followed_by", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True) 
