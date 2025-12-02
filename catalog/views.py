from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm, OrderForm
from django.contrib.auth import login, logout, authenticate
from .models import Order

def index(request):
    return render(request, 'index.html')

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        agreement = request.POST.get('agreement') == 'on'
        if not agreement:
            messages.error(request, 'Необходимо согласие на обработку персональных данных.')
        elif form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Регистрация прошла успешно!")
            return redirect('index')
        else:
            # Вывод конкретных ошибок в консоль для отладки
            print("Ошибки формы:", form.errors)
            # Показ конкретных ошибок пользователю
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Добро пожаловать, {username}!")
                return redirect('profile')
            else:
                messages.error(request, "Неверный логин или пароль.")
        else:
            messages.error(request, "Неверный логин или пароль.")
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

@login_required
def profile_view(request):
    return render(request, 'users/profile.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('login')

@login_required
def my_orders_view(request):
    orders = Order.objects.filter(user=request.user)

    status = request.GET.get('status')
    if status in dict(Order.STATUS_CHOICES):
        orders = orders.filter(status=status)

    orders = orders.order_by('-timestamp')

    status_choices = Order.STATUS_CHOICES

    return render(request, 'users/my_orders.html', {
        'orders': orders,
        'selected_status': status,
        'status_choices': status_choices,
    })

@login_required
def create_order_view(request):
    if request.method == 'POST':
        form = OrderForm(request.POST, request.FILES)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            messages.success(request, "Заказ успешно создан!")
            return redirect('my_orders')
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = OrderForm()
    return render(request, 'users/create_order.html', {'form': form})

@login_required
def delete_order_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.user != request.user:
        messages.error(request, "Вы не можете удалить чужую заявку.")
        return redirect('my_orders')

    if order.status != Order.STATUS_NEW:
        messages.error(request, "Нельзя удалить заявку, которая уже в работе или выполнена.")
        return redirect('my_orders')

    if request.method == 'POST':
        order.delete()
        messages.success(request, "Заказ успешно удалён!")
        return redirect('my_orders')

    return render(request, 'users/confirm_delete_order.html', {'order': order})