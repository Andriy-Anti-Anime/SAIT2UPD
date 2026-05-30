from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Avg
import random, string

from .models import (
    Category, Product, Review,
    Order, OrderItem, CartItem, PasswordResetCode
)
from .forms import (
    NewsletterForm, RegisterForm, LoginForm,
    OrderForm, PasswordResetRequestForm, PasswordResetConfirmForm
)

def home(request):
    categories = Category.objects.all()
    products   = Product.objects.filter(is_available=True).order_by('-created_at')[:8]
    return render(request, 'myapp/home.html', {
        'categories': categories,
        'products':   products,
    })

def catalog(request):
    categories = Category.objects.all()
    products   = Product.objects.filter(is_available=True).order_by('-created_at')
    return render(request, 'myapp/catalog.html', {
        'categories': categories,
        'products':   products,
    })

def category_detail(request, slug):
    categories = Category.objects.all()
    category   = get_object_or_404(Category, slug=slug)
    products   = Product.objects.filter(category=category, is_available=True)
    return render(request, 'myapp/category.html', {
        'categories': categories,
        'category':   category,
        'products':   products,
    })

def product_detail(request, slug):
    categories     = Category.objects.all()
    product        = get_object_or_404(Product, slug=slug)
    reviews        = product.reviews.all()
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    if average_rating:
        average_rating = round(average_rating, 1)

    success_msg = error_msg = None

    if request.method == 'POST':
        if not request.user.is_authenticated:
            error_msg = "Тільки авторизовані користувачі можуть залишати оцінки."
        elif Review.objects.filter(product=product, user=request.user).exists():
            error_msg = "Ви вже оцінювали цю деталь!"
        else:
            rating_value  = request.POST.get('rating')
            comment_value = request.POST.get('comment', '')
            if rating_value:
                Review.objects.create(
                    product=product, user=request.user,
                    rating=int(rating_value), comment=comment_value
                )
                success_msg    = "Дякуємо за вашу оцінку!"
                reviews        = product.reviews.all()
                average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
                if average_rating:
                    average_rating = round(average_rating, 1)
            else:
                error_msg = "Будь ласка, оберіть кількість зірочок."

    return render(request, 'myapp/product_detail.html', {
        'categories':     categories,
        'product':        product,
        'reviews':        reviews,
        'average_rating': average_rating,
        'success_msg':    success_msg,
        'error_msg':      error_msg,
    })

def cart_detail(request):
    categories = Category.objects.all()

    if request.user.is_authenticated:
        cart_items  = CartItem.objects.filter(user=request.user).select_related('product')
        total_price = sum(item.subtotal() for item in cart_items)
        return render(request, 'myapp/cart.html', {
            'categories':  categories,
            'cart_items':  cart_items,
            'total_price': total_price,
            'is_db_cart':  True,
        })

    cart        = request.session.get('cart', {})
    cart_items  = []
    total_price = 0
    for product_id, quantity in cart.items():
        try:
            product      = Product.objects.get(id=product_id)
            subtotal     = product.price * quantity
            total_price += subtotal
            cart_items.append({
                'product':  product,
                'quantity': quantity,
                'subtotal': subtotal,
            })
        except Product.DoesNotExist:
            pass

    return render(request, 'myapp/cart.html', {
        'categories':  categories,
        'cart_items':  cart_items,
        'total_price': total_price,
        'is_db_cart':  False,
    })


def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'quantity': 1}
        )
        if not created:
            if cart_item.quantity < product.stock:
                cart_item.quantity += 1
                cart_item.save()
    else:
        cart   = request.session.get('cart', {})
        p_id   = str(product_id)
        cart[p_id] = cart.get(p_id, 0) + 1
        request.session['cart'] = cart

    messages.success(request, f'«{product.name}» додано до кошика!')
    return redirect(request.META.get('HTTP_REFERER', 'catalog'))


def cart_remove(request, product_id):
    if request.user.is_authenticated:
        CartItem.objects.filter(user=request.user, product_id=product_id).delete()
    else:
        cart = request.session.get('cart', {})
        p_id = str(product_id)
        if p_id in cart:
            del cart[p_id]
            request.session['cart'] = cart

    return redirect('cart_detail')


def cart_update(request, product_id, action):
    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:
        try:
            cart_item = CartItem.objects.get(user=request.user, product=product)
            if action == 'increment':
                if cart_item.quantity < product.stock:
                    cart_item.quantity += 1
                    cart_item.save()
            elif action == 'decrement':
                cart_item.quantity -= 1
                if cart_item.quantity <= 0:
                    cart_item.delete()
                else:
                    cart_item.save()
        except CartItem.DoesNotExist:
            pass
    else:
        cart = request.session.get('cart', {})
        p_id = str(product_id)
        if p_id in cart:
            if action == 'increment' and cart[p_id] < product.stock:
                cart[p_id] += 1
            elif action == 'decrement':
                cart[p_id] -= 1
                if cart[p_id] <= 0:
                    del cart[p_id]
            request.session['cart'] = cart

    return redirect('cart_detail')

@login_required
def checkout(request):
    categories = Category.objects.all()
    cart_items = CartItem.objects.filter(user=request.user).select_related('product')

    if not cart_items.exists():
        messages.warning(request, 'Ваш кошик порожній.')
        return redirect('cart_detail')

    total_price = sum(item.subtotal() for item in cart_items)

    initial = {
        'first_name': request.user.first_name,
        'last_name':  request.user.last_name,
        'email':      request.user.email,
    }
    form = OrderForm(initial=initial)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order             = form.save(commit=False)
            order.user        = request.user
            order.total_price = total_price
            order.save()

            for item in cart_items:
                OrderItem.objects.create(
                    order    = order,
                    product  = item.product,
                    quantity = item.quantity,
                    price    = item.product.price,
                )

            cart_items.delete()

            _send_order_email(order)

            messages.success(request, f'Замовлення #{order.id} успішно оформлено! Перевірте email.')
            return redirect('profile')

    return render(request, 'myapp/checkout.html', {
        'categories':  categories,
        'form':        form,
        'cart_items':  cart_items,
        'total_price': total_price,
    })


def _send_order_email(order):
    items_text = '\n'.join(
        f'  - {item.product.name} × {item.quantity} = {item.subtotal()} ₴'
        for item in order.items.all()
    )
    message = f"""Вітаємо, {order.first_name}!

Ваше замовлення #{order.id} успішно оформлено.

Склад замовлення:
{items_text}

Загальна сума: {order.total_price} ₴

Адреса доставки: {order.address}
Телефон: {order.phone}

Статус замовлення ви можете відстежити в особистому кабінеті.

З повагою,
Команда PCShop
"""
    try:
        send_mail(
            subject=f'PCShop — Замовлення #{order.id} підтверджено',
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            fail_silently=False,
        )
    except Exception:
        pass

def newsletter_subscribe(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ви успішно підписались на розсилку!')
        else:
            messages.error(request, 'Цей email вже підписаний або введений невірно.')
    return redirect(request.META.get('HTTP_REFERER', 'home'))


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            _merge_session_cart(request, user)
            login(request, user)
            messages.success(request, f'Ласкаво просимо, {user.first_name or user.username}!')
            return redirect('home')
    return render(request, 'myapp/auth/register.html', {
        'form':       form,
        'categories': Category.objects.all(),
    })

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = LoginForm(request)
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # Переносимо кошик з сесії в БД
            _merge_session_cart(request, user)
            login(request, user)
            messages.success(request, f'Ласкаво просимо, {user.first_name or user.username}!')
            return redirect(request.GET.get('next', 'home'))
    return render(request, 'myapp/auth/login.html', {
        'form':       form,
        'categories': Category.objects.all(),
    })


def _merge_session_cart(request, user):
    session_cart = request.session.get('cart', {})
    for product_id, quantity in session_cart.items():
        try:
            product = Product.objects.get(id=product_id)
            cart_item, created = CartItem.objects.get_or_create(
                user=user,
                product=product,
                defaults={'quantity': quantity}
            )
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
        except Product.DoesNotExist:
            pass
    request.session['cart'] = {}

def logout_view(request):
    logout(request)
    messages.info(request, 'Ви вийшли з системи.')
    return redirect('home')


@login_required
def profile(request):
    categories = Category.objects.all()
    if request.user.is_staff:
        orders = Order.objects.all().select_related('user').prefetch_related('items__product')
    else:
        orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
    return render(request, 'myapp/auth/profile.html', {
        'categories': categories,
        'orders':     orders,
    })


def password_reset_request(request):
    form = PasswordResetRequestForm()
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                code = ''.join(random.choices(string.digits, k=6))
                PasswordResetCode.objects.create(user=user, code=code)

                send_mail(
                    subject='PCShop — Відновлення пароля',
                    message=f'''Вітаємо, {user.first_name or user.username}!

Ваш код для відновлення пароля: {code}

Код дійсний 15 хвилин.
Якщо ви не запитували відновлення пароля — проігноруйте цей лист.

З повагою,
Команда PCShop''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                messages.success(request, f'Код відправлено на {email}. Перевірте пошту.')
                request.session['reset_email'] = email
                return redirect('password_reset_confirm')
            except User.DoesNotExist:
                messages.error(request, 'Користувача з таким email не знайдено.')
            except Exception:
                messages.error(request, 'Помилка відправки email. Перевірте налаштування SMTP.')

    return render(request, 'myapp/auth/password_reset_request.html', {
        'form':       form,
        'categories': Category.objects.all(),
    })


def password_reset_confirm(request):
    email = request.session.get('reset_email')
    if not email:
        return redirect('password_reset_request')

    form = PasswordResetConfirmForm()
    if request.method == 'POST':
        form = PasswordResetConfirmForm(request.POST)
        if form.is_valid():
            code         = form.cleaned_data['code']
            new_password = form.cleaned_data['new_password']
            try:
                user       = User.objects.get(email=email)
                reset_code = PasswordResetCode.objects.filter(
                    user=user, code=code, is_used=False
                ).latest('created_at')
                reset_code.is_used = True
                reset_code.save()
                user.set_password(new_password)
                user.save()
                del request.session['reset_email']
                messages.success(request, 'Пароль успішно змінено! Увійдіть з новим паролем.')
                return redirect('login')
            except (User.DoesNotExist, PasswordResetCode.DoesNotExist):
                messages.error(request, 'Невірний або прострочений код.')

    return render(request, 'myapp/auth/password_reset_confirm.html', {
        'form':       form,
        'categories': Category.objects.all(),
    })