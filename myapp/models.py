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
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending',    'Очікує'),
        ('processing', 'Обробляється'),
        ('shipped',    'Відправлено'),
        ('delivered',  'Доставлено'),
        ('cancelled',  'Скасовано'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Користувач'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус'
    )
    total_price = models.DecimalField(
        max_digits=12, decimal_places=2,
        default=0, verbose_name='Загальна сума (грн)'
    )
    first_name  = models.CharField(max_length=100, verbose_name="Ім'я")
    last_name   = models.CharField(max_length=100, verbose_name='Прізвище')
    email       = models.EmailField(verbose_name='Email')
    phone       = models.CharField(max_length=20, verbose_name='Телефон')
    address     = models.TextField(verbose_name='Адреса доставки')
    created_at  = models.DateTimeField(auto_now_add=True, verbose_name='Створено о')
    updated_at  = models.DateTimeField(auto_now=True,     verbose_name='Оновлено о')

    class Meta:
        verbose_name = 'Замовлення'
        verbose_name_plural = 'Замовлення'
        ordering = ['-created_at']

    def __str__(self):
        return f'Замовлення #{self.id} — {self.user.username}'


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Замовлення'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='order_items',
        verbose_name='Товар'
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name='Кількість')
    price    = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Ціна за одиницю')

    class Meta:
        verbose_name = 'Позиція замовлення'
        verbose_name_plural = 'Позиції замовлення'

    def __str__(self):
        return f'{self.product.name} x{self.quantity}'

    def subtotal(self):
        return self.price * self.quantity


class PasswordResetCode(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reset_codes')
    code       = models.CharField(max_length=6, verbose_name='Код')
    is_used    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Код відновлення пароля'
        verbose_name_plural = 'Коди відновлення пароля'

    def __str__(self):
        return f'{self.user.username} — {self.code}'
class CartItem(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart_items',
        verbose_name='Користувач'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_items',
        verbose_name='Товар'
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name='Кількість')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Додано о')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Оновлено о')

    class Meta:
        verbose_name = 'Кошик'
        verbose_name_plural = 'Кошик'
        unique_together = ('user', 'product')

    def __str__(self):
        return f'{self.user.username}: {self.product.name} x{self.quantity}'

    def subtotal(self):
        return self.product.price * self.quantity