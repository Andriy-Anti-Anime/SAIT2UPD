from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Review, NewsletterSubscriber, Order


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, f'{i} ★') for i in range(5, 0, -1)], attrs={'class': 'form-input'}),
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Ваш відгук про деталь...', 'class': 'form-input'}),
        }

class NewsletterForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Введіть ваш Email...', 'required': True}),
        }
class RegisterForm(UserCreationForm):
    email      = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': "Ім'я"}))
    last_name  = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Прізвище'}))

    class Meta:
        model  = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Логін'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.PasswordInput(attrs={'placeholder': 'Пароль'})
        self.fields['password2'].widget = forms.PasswordInput(attrs={'placeholder': 'Повторіть пароль'})


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget = forms.TextInput(attrs={'placeholder': 'Логін'})
        self.fields['password'].widget = forms.PasswordInput(attrs={'placeholder': 'Пароль'})


class OrderForm(forms.ModelForm):
    class Meta:
        model  = Order
        fields = ['first_name', 'last_name', 'email', 'phone', 'address']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': "Ім'я"}),
            'last_name':  forms.TextInput(attrs={'placeholder': 'Прізвище'}),
            'email':      forms.EmailInput(attrs={'placeholder': 'Email'}),
            'phone':      forms.TextInput(attrs={'placeholder': '+380XXXXXXXXX'}),
            'address':    forms.Textarea(attrs={'rows': 3, 'placeholder': 'Місто, вулиця, будинок'}),
        }
        labels = {
            'first_name': "Ім'я",
            'last_name':  'Прізвище',
            'email':      'Email',
            'phone':      'Телефон',
            'address':    'Адреса доставки',
        }


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'placeholder': 'Ваш email'})
    )


class PasswordResetConfirmForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        label='Код підтвердження',
        widget=forms.TextInput(attrs={'placeholder': '6-значний код', 'maxlength': '6'})
    )
    new_password  = forms.CharField(
        label='Новий пароль',
        widget=forms.PasswordInput(attrs={'placeholder': 'Новий пароль'})
    )
    new_password2 = forms.CharField(
        label='Повторіть пароль',
        widget=forms.PasswordInput(attrs={'placeholder': 'Повторіть пароль'})
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('new_password')
        p2 = cleaned_data.get('new_password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Паролі не співпадають.')
        return cleaned_data