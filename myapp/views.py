from django.shortcuts import render, get_object_or_404
from .models import Category, Product


def home(request):
    categories = Category.objects.all()
    products = Product.objects.filter(is_available=True).order_by('-created_at')[:4]
    return render(request, 'myapp/home.html', {
        'categories': categories,
        'products': products,
    })


def category_detail(request, slug):
    categories = Category.objects.all()
    category = Category.objects.get(slug=slug)
    products = Product.objects.filter(category=category, is_available=True)
    return render(request, 'myapp/category.html', {
        'categories': categories,
        'category': category,
        'products': products,
    })


def catalog(request):
    categories = Category.objects.all()
    products = Product.objects.filter(is_available=True)

    return render(request, 'myapp/catalog.html', {
        'categories': categories,
        'products': products,
    })


def product_detail(request, slug):
    categories = Category.objects.all()
    product = get_object_or_404(Product, slug=slug)

    return render(request, 'myapp/product_detail.html', {
        'categories': categories,
        'product': product
    })
