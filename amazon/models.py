from django.db import models
from django import forms
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.db.models import F, Sum, Avg
# Create your models here.

class Product(models.Model):
    class Meta:
        verbose_name = '商品'
        verbose_name_plural = "商品"

    thumbnail = models.ImageField(
        verbose_name = 'サムネイル',
        upload_to = "thumbnails/"
    )

    name = models.CharField(
        verbose_name = '名前',
        max_length=150,
        null = False,
        blank=False
    )
    price = models.IntegerField(
        verbose_name = '価格'
    )
    description = models.TextField(
        verbose_name = '説明'
    )

    @property
    def avg_rating(self):
        return self.reviews.all().aggregate(avg_rating = Avg('rating'))['avg_rating'] or 0

class MyUserManager(BaseUserManager):
    """ユーザーマネージャー."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """メールアドレスでの登録を必須にする"""
        if not email:
            raise ValueError('The given email must be set')

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """is_staff(管理サイトにログインできるか)と、is_superuer(全ての権限)をFalseに"""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """スーパーユーザーは、is_staffとis_superuserをTrueに"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)
class User(AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name = 'ユーザ'
        verbose_name_plural = 'ユーザ'

    """カスタムユーザーモデル."""
    email = models.EmailField('メールアドレス', max_length=150, null = False, blank=False, unique = True)
    name = models.CharField('名前', max_length=150, null = False, blank=False)
    
    is_staff = models.BooleanField(
        '管理者',
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        '有効',
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = MyUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name',]

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    @property
    def username(self):
        """username属性のゲッター

        他アプリケーションが、username属性にアクセスした場合に備えて定義
        メールアドレスを返す
        """
        return self.email

class ShoppingCart(models.Model):
    user = models.OneToOneField(
        User, 
        verbose_name = 'ユーザー',
        related_name = 'cart',
        on_delete = models.CASCADE
    )
    
    @property
    def item_count(self):
        return  self.cart_items.all().aggregate(amount = Sum('amount'))['amount']
    
    @property
    def item_price(self):
        return  self.cart_items.all().aggregate(total = Sum(F('product__price') * F('amount')))['total']

class ShoppingCartItem(models.Model):
    cart = models.ForeignKey(
        ShoppingCart,
        related_name = 'cart_items',
        verbose_name = 'ショッピングカート',
        on_delete = models.CASCADE
    )

    product = models.ForeignKey(
        Product,
        verbose_name = '商品',
        on_delete = models.CASCADE,
    )

    amount = models.IntegerField(
        verbose_name = '数量'
    )

class Review(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name = 'ユーザ',
        on_delete = models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        related_name = 'reviews',
        verbose_name = '商品',
        on_delete = models.CASCADE
    )
    rating = models.IntegerField(
        verbose_name = '評価',
        default = 0
    )
    title = models.CharField(
        verbose_name = 'タイトル',
        null = False,
        blank = False,
        max_length = 255
    )
    comment = models.TextField(
        verbose_name = 'コメント',
        blank = True,
        null = True
    )

