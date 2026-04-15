from django.shortcuts import render

def home(request):
    context = {
        'title': 'Головна сторінка'
    }
    return render(request, 'myapp/home.html', context)


def page1(request):
    context = {
        'title': 'Сторінка 1'
    }
    return render(request, 'myapp/page1.html', context)


def page2(request):
    context = {
        'title': 'Сторінка 2'
    }
    return render(request, 'myapp/page2.html', context)
