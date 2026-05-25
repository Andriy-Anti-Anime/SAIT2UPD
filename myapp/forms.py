from django import forms
from .models import Review, NewsletterSubscriber

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