from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Avg
from .models import Category, Product, Review
from .forms import NewsletterForm


def home(request):

    categories = Category.objects.all()
    products = Product.objects.filter(is_available=True).order_by('-created_at')[:8]

    return render(request, 'myapp/home.html', {
        'categories': categories,
        'products': products,
    })

def catalog(request):
    categories = Category.objects.all()
    products = Product.objects.filter(is_available=True).order_by('-created_at')

    return render(request, 'myapp/catalog.html', {
        'categories': categories,
        'products': products,
    })

def category_detail(request, slug):
    categories = Category.objects.all()
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, is_available=True)

    return render(request, 'myapp/category.html', {
        'categories': categories,
        'category': category,
        'products': products,
    })


def product_detail(request, slug):
    categories = Category.objects.all()
    product = get_object_or_404(Product, slug=slug)
    reviews = product.reviews.all()

    average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    if average_rating:
        average_rating = round(average_rating, 1)

    success_msg = None
    error_msg = None

    if request.method == 'POST':
        if not request.user.is_authenticated:
            error_msg = "Тільки авторизовані користувачі можуть залишати оцінки."
        else:

            if Review.objects.filter(product=product, user=request.user).exists():
                error_msg = "Ви вже оцінювали цю деталь!"
            else:
                rating_value = request.POST.get('rating')
                comment_value = request.POST.get('comment')

                if rating_value:
                    Review.objects.create(
                        product=product,
                        user=request.user,
                        rating=int(rating_value),
                        comment=comment_value
                    )
                    success_msg = "Дякуємо за вашу оцінку комплектуючого!"
                    reviews = product.reviews.all()
                    average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
                    if average_rating:
                        average_rating = round(average_rating, 1)
                else:
                    error_msg = "Будь ласка, оберіть кількість зірочок для оцінки."

    return render(request, 'myapp/product_detail.html', {
        'categories': categories,
        'product': product,
        'reviews': reviews,
        'average_rating': average_rating,
        'success_msg': success_msg,
        'error_msg': error_msg,
    })


def cart_detail(request):
    categories = Category.objects.all()
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0

    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)

            if quantity > product.stock:
                quantity = product.stock
                cart[product_id] = quantity
                request.session['cart'] = cart

            subtotal = product.price * quantity
            total_price += subtotal
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })
        except Product.DoesNotExist:
            pass

    return render(request, 'myapp/cart.html', {
        'categories': categories,
        'cart_items': cart_items,
        'total_price': total_price
    })


def cart_update(request, product_id, action):
    cart = request.session.get('cart', {})
    p_id = str(product_id)

    if p_id in cart:
        product = get_object_or_404(Product, id=product_id)
        if action == 'increment':
            if cart[p_id] < product.stock:
                cart[p_id] += 1
        elif action == 'decrement':
            cart[p_id] -= 1
            if cart[p_id] <= 0:
                del cart[p_id]

        request.session['cart'] = cart
    return redirect('cart_detail')
def cart_add(request, product_id):
    cart = request.session.get('cart', {})
    p_id = str(product_id)

    if p_id in cart:
        cart[p_id] += 1
    else:
        cart[p_id] = 1

    request.session['cart'] = cart
    return redirect('cart_detail')


def cart_remove(request, product_id):
    cart = request.session.get('cart', {})
    p_id = str(product_id)
    if p_id in cart:
        del cart[p_id]
        request.session['cart'] = cart
    return redirect('cart_detail')


def newsletter_subscribe(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
    return redirect(request.META.get('HTTP_REFERER', 'home'))