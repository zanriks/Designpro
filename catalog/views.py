from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import CustomUserCreationForm, CategoryForm ,OrderForm
from .models import Order, Category
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from .models import Order
from django.http import HttpResponseRedirect
from django.urls import reverse

def index(request):
    num_status = Order.objects.filter(status=Order.STATUS_IN_PROGRESS).count()
    last_orders = Order.objects.filter(status=Order.STATUS_COMPLETED).order_by('-timestamp')[:4]

    return render(request, 'index.html', {
        'num_status': num_status,
        'last_orders': last_orders,
    })

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

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('login')

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
def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.user != request.user:
        messages.error(request, "Вы не можете удалить чужую заявку.")
        return redirect('my_orders')

    if order.status != Order.STATUS_NEW:
        messages.error(request, "Нельзя удалить заявку, которая уже в работе или выполнена.")
        return redirect('my_orders')

    if request.method == 'POST':
        order.delete()
        messages.success(request, "Заявка успешно удалена!")
        return redirect('my_orders')

    return render(request, 'users/confirm_delete_order.html', {'order': order})

@login_required
def all_orders_view(request):
    orders = Order.objects.all()

    status = request.GET.get('status')
    if status in dict(Order.STATUS_CHOICES):
        orders = orders.filter(status=status)

    orders = orders.order_by('-timestamp')

    status_choices = Order.STATUS_CHOICES

    return render(request, 'users/all_orders.html', {
        'orders': orders,
        'selected_status': status,
        'status_choices': status_choices,
    })

@login_required
def change_status_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # Только администратор может менять статус
    if not request.user.is_staff:
        messages.error(request, "У вас нет прав на изменение этой заявки.")
        return redirect('my_orders')

    # Смена статуса возможна только из 'new'
    if order.status != Order.STATUS_NEW:
        messages.error(request, "Нельзя изменить статус заявки, которая уже в работе или выполнена.")
        return redirect('my_orders')

    if request.method == 'POST':
        new_status = request.POST.get('status')
        comment = request.POST.get('comment', '').strip()
        design_image = request.FILES.get('design_image')

        if new_status == Order.STATUS_IN_PROGRESS:
            if not comment:
                messages.error(request, "Требуется указать комментарий при смене статуса на «Принято в работу».")
                return redirect('change_status', order_id=order.id)

            order.status = Order.STATUS_IN_PROGRESS
            order.status_comment = comment
            order.save()
            messages.success(request, "Заявка переведена в статус «Принято в работу».")
            return redirect('my_orders')

        elif new_status == Order.STATUS_COMPLETED:
            if not design_image:
                messages.error(request, "Требуется прикрепить изображение дизайна при смене статуса на «Выполнено».")
                return redirect('change_status', order_id=order.id)

            order.status = Order.STATUS_COMPLETED
            order.design_image = design_image
            order.save()
            messages.success(request, "Заявка переведена в статус «Выполнено».")
            return redirect('my_orders')

        else:
            messages.error(request, "Недопустимый статус.")
            return redirect('change_status', order_id=order.id)

    return render(request, 'users/change_status.html', {'order': order})

@login_required
def order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.user != request.user and not request.user.is_staff:
        messages.error(request, "У вас нет прав для просмотра этой заявки.")
        return HttpResponseRedirect(reverse('my_orders'))

    return render(request, 'users/order_detail.html', {'order': order})

@login_required
def category_management_view(request):
    if not request.user.is_staff:
        messages.error(request, "Доступ разрешён только администраторам.")
        return redirect('index')

    categories = Category.objects.all()

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Категория успешно добавлена!")
            return redirect('category_management')
        else:
            messages.error(request, "Ошибка при добавлении категории.")
    else:
        form = CategoryForm()

    return render(request, 'users/category_management.html', {
        'form': form,
        'categories': categories,
    })

@login_required
def delete_category_view(request, category_id):
    category = get_object_or_404(Category, id=category_id)


    if request.method == 'POST':
        category.delete()

        messages.success(request, "Категория успешно удалена!")
        return redirect('category_management')