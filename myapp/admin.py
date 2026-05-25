from django.contrib import admin
from .models import Category, Product, Review, NewsletterSubscriber


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at', 'updated_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'brand', 'price', 'stock', 'is_available', 'created_at', 'updated_at']
    list_filter = ['category', 'is_available', 'brand']
    search_fields = ['name', 'brand']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['price', 'stock', 'is_available']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'rating', 'created_at', 'updated_at']
    list_filter = ['rating']
    search_fields = ['user__username', 'product__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at')
    ordering = ('-subscribed_at',)
    search_fields = ('email',)