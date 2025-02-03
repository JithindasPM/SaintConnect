"""
URL configuration for SaintConnect project.

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

from app.views import Home_View
from app.views import Registration_View
from app.views import Admin_View
from app.views import User_View
from app.views import Login_View
from app.views import House_Name_Add_View
from app.views import House_Name_Update_View
from app.views import House_Name_Delete_View
from app.views import Update_UserProfile_View


urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', Home_View.as_view(),name='home'),
    path('registration/', Registration_View.as_view(),name='registration'),
    path('admin/', Admin_View.as_view(),name='admin'),
    path('user/', User_View.as_view(),name='user'),
    path('login/', Login_View.as_view(),name='login'),
    path('house_name/', House_Name_Add_View.as_view(),name='house_name'),
    path('house_name_update/<int:pk>', House_Name_Update_View.as_view(),name='house_name_update'),
    path('house_name_delete/<int:pk>', House_Name_Delete_View.as_view(),name='house_name_delete'),
    path('profile/<int:pk>', Update_UserProfile_View.as_view(),name='profile'),


]
