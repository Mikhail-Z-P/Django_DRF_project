from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.core.exceptions import ValidationError
from django.db import models

from materials.models import Course, Lesson


class UserManager(BaseUserManager):
    """Менеджер для создания пользователя с email вместо username."""

    def create_user(self, email, password=None, **extra_fields):
        """Создаёт обычного пользователя с указанным email."""
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Создаёт суперпользователя с правами администратора."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Кастомная модель пользователя с авторизацией по email."""

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    city = models.CharField(max_length=100, blank=True, verbose_name="Город")
    avatar = models.ImageField(
        upload_to="users/avatars/", blank=True, null=True, verbose_name="Аватарка"
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email


class Payment(models.Model):
    """Модель платежа пользователя за курс или урок с интеграцией Stripe."""

    PAYMENT_METHOD_CHOICES = [
        ("cash", "Наличные"),
        ("transfer", "Перевод на счет"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="payments"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Сумма оплаты"
    )
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата оплаты")
    payment_method = models.CharField(
        max_length=10, choices=PAYMENT_METHOD_CHOICES, verbose_name="Способ оплаты"
    )
    stripe_product_id = models.CharField(
        max_length=255, blank=True, default="", verbose_name="ID продукта в Stripe"
    )
    stripe_price_id = models.CharField(
        max_length=255, blank=True, default="", verbose_name="ID цены в Stripe"
    )
    stripe_session_id = models.CharField(
        max_length=255, blank=True, default="", verbose_name="ID сессии в Stripe"
    )
    payment_link = models.URLField(
        max_length=500, blank=True, default="", verbose_name="Ссылка на оплату"
    )

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
        ordering = ["-payment_date"]

    def __str__(self):
        return f"Платеж {self.amount} от {self.user.email}"

    def clean(self):
        """Валидация: должен быть выбран либо курс, либо урок, но не оба."""
        if not self.course and not self.lesson:
            raise ValidationError("Необходимо указать оплаченный курс или урок.")
        if self.course and self.lesson:
            raise ValidationError("Нельзя одновременно указать и курс, и урок.")
