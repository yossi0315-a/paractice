from django.urls import path
from . import views
from django.contrib import admin
from django.contrib.auth import views as django_auth_views

app_name = 'amazon'

urlpatterns = [
    path('lp/', views.Lp.as_view(), name = 'lp'),
    path('items/', views.ItemList.as_view(), name = 'item_list'),
    path('item/<int:pk>', views.ItemDetail.as_view(), name = 'item_detail'),
    path('', views.Login.as_view(), name = "login"),
    path('logout', django_auth_views.LogoutView.as_view(), name = "logout"),
    path('sign_up/', views.SignUp.as_view(), name='sign_up'),
    path('sign_up/done/<token>', views.SignUpDone.as_view(), name='sign_up_done'),
    path('cart/<int:pk>', views.ShoppingCartDetail.as_view(), name = 'cart'),
    path('ajax_amount/', views.update_cart_item_amount, name = 'update_cart_item_amount'),
    path('ajax_delete/', views.delete_cart_item, name = 'delete_cart_item'),]
