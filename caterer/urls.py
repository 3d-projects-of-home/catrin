"""
URL configuration for caterer project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from caterer import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.check,name='home'),
    path('register/',views.registerPage,name='register'),
    path('login/',views.loginPage,name='login'),
    path('logout/',views.logoutUser,name='logout'),
    path('otp/',views.otpUser,name='otpUser'),
    path('forgot/',views.forgotUser,name='forgot'),
    path('timer/',views.timer,name='timer'),
    path('resend/',views.resend_link,name='resend_link'),
    path('my-view/', views.my_view, name='my_view'),
    path('menu/', views.menu, name='menu'),
    path('remove/', views.remove, name='remove'),
    path('order/', views.order, name='order'),
    path('delivery/', views.delivery, name='delivery'),
    path('success/', views.success, name='success'),
    path('catererform/', views.catererform, name='catererform'),
    path('catererAdmin/', views.catererAdmin, name='catererAdmin'),
    path('catererMenu/', views.catererMenu, name='catererMenu'),
    path('catererRemove/', views.catererRemove, name='catererRemove'),
    path('orderDetails/', views.orderDetails, name='orderDetails'),
    path('catererCatagory/', views.catererCatagory, name='catererCatagory'),
    path('foodForm/', views.foodForm, name='foodForm'),
    path('myOrder/', views.myOrder, name='myOrder'),
]

if settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
