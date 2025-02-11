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
from django.conf import settings  
from django.conf.urls.static import static 

from app.views import Home_View
from app.views import Registration_View
from app.views import Admin_View
from app.views import User_View
from app.views import Login_View
from app.views import House_Name_Add_View
from app.views import House_Name_Update_View
from app.views import House_Name_Delete_View
from app.views import Update_UserProfile_View
from app.views import Member_Details_View,Delete
from app.views import All_Member_View
from app.views import Logout_View
from app.views import Certificate_View
from app.views import Death_Certificate_Add_View
from app.views import Death_Certificate_Update_View
from app.views import Death_Certificate_Delete_View
from app.views import Admin_Approval_View
from app.views import Death_Approval_View
from app.views import Death_Certificate_View
from app.views import Baptism_Certificate_Add_View
from app.views import Baptism_Certificate_Update_View
from app.views import Baptism_Certificate_Delete_View
from app.views import Baptism_Approval_View
from app.views import Baptism_Certificate_View


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
    path('hai/<int:pk>', Member_Details_View.as_view(),name='hai'),
    path('del/<int:pk>', Delete.as_view(),name='del'),
    path('all_members/', All_Member_View.as_view(),name='all_members'),
    path('logout/', Logout_View.as_view(),name='logout'),
    path('certificate/', Certificate_View.as_view(),name='certificate'),
    path('death_certificate_add/', Death_Certificate_Add_View.as_view(),name='death_certificate_add'),
    path('death_update/<int:pk>', Death_Certificate_Update_View.as_view(),name='death_update'),
    path('death_delete/<int:pk>', Death_Certificate_Delete_View.as_view(),name='death_delete'),
    path('admin_approval/', Admin_Approval_View.as_view(),name='admin_approval'),
    path('death_approval/<int:record_id>', Death_Approval_View.as_view(),name='death_approval'),
    path('death_certificate/<int:record_id>', Death_Certificate_View.as_view(),name='death_certificate'),
    path('baptism_certificate_add/', Baptism_Certificate_Add_View.as_view(),name='baptism_certificate_add'),
    path('baptism_update/<int:pk>', Baptism_Certificate_Update_View.as_view(),name='baptism_update'),
    path('baptism_delete/<int:pk>', Baptism_Certificate_Delete_View.as_view(),name='baptism_delete'),
    path('baptism_approval/<int:record_id>', Baptism_Approval_View.as_view(),name='baptism_approval'),
    path('baptism_certificate/<int:record_id>', Baptism_Certificate_View.as_view(),name='baptism_certificate'),



]+ static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)  
