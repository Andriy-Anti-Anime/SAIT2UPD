from django.contrib.auth.models import User
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Назва категорії')
    slug = models.SlugField(unique=True, verbose_name='URL-ідентифікатор')
    description = models.TextField(blank=True, verbose_name='Опис')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Створено о')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Оновлено о')

    class Meta:
        verbose_name = 'Категорія'
        verbose_name_plural = 'Категорії'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Категорія'
    )
    name = models.CharField(max_length=200, verbose_name='Назва товару')
    slug = models.SlugField(unique=True, verbose_name='URL-ідентифікатор')
    description = models.TextField(verbose_name='Опис')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Ціна (грн)')
    stock = models.PositiveIntegerField(default=0, verbose_name='Кількість на складі')
    brand = models.CharField(max_length=100, blank=True, verbose_name='Бренд')
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name='Зображення')
    is_available = models.BooleanField(default=True, verbose_name='Доступний')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Створено о')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Оновлено о')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товари'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True, verbose_name='Електронна пошта')
    subscribed_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата підписки')

    class Meta:
        verbose_name = 'Підписник'
        verbose_name_plural = 'Підписники'

    def __str__(self):
        return self.email
class Review(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Товар'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Користувач'
    )
    rating = models.PositiveSmallIntegerField(verbose_name='Оцінка (1-5)')
    comment = models.TextField(blank=True, verbose_name='Коментар')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Створено о')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Оновлено о')

    class Meta:
        verbose_name = 'Відгук'
        verbose_name_plural = 'Відгуки'
        unique_together = ('product', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} → {self.product.name} ({self.rating}★)'