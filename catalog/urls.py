from django.contrib import admin
from . import views
from django.urls import path

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('create_order/', views.create_order_view, name='create_order'),
    path('my_orders/', views.my_orders_view, name='my_orders'),
    path('order/<int:order_id>/delete/', views.delete_order_view, name='delete_order')
]