from django.shortcuts import render,redirect
from django.views.generic import View
from django.contrib.auth import authenticate,login

from app.models import User
from app.models import House_Name
from app.models import UserProfile_Model

from app.forms import Registration_Form
from app.forms import Login_Form
from app.forms import House_Name_Form
from app.forms import UserProfile_Form


# Create your views here.

class Home_View(View):
    def get(self,request):
        return render(request,'index.html')
    
# class Registration_View(View):
#     def get(self,request):
#         return render(request,'registration.html')
    
class Registration_View(View):
    def get(self,request,*args,**kwargs):
        form=Registration_Form()
        return render(request,'reg.html',{'form':form})
    
    def post(self,request,*args,**kwargs):
        form=Registration_Form(request.POST)
        try:
            if form.is_valid():
               User.objects.create_user(**form.cleaned_data)
               form=Registration_Form()
               return redirect('login')
        except Exception as e:
            print(e,"===========")
        return render(request,'reg.html',{'form':form})
        
class Update_UserProfile_View(View):
    def get(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        data=UserProfile_Model.objects.get(id=id)
        form = UserProfile_Form(instance=data)
        return render(request, 'profile.html', {'form': form,'data':data})
    
    def post(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        data=UserProfile_Model.objects.get(id=id)
        form = UserProfile_Form(request.POST,request.FILES, instance=data)
        if form.is_valid():
            form.save()
            # UserProfile_Model.objects.create(**form.cleaned_data,user=request.user,total_calories=total_calorie)

            return redirect('user')
        else:
            form = UserProfile_Form(instance=data)
            return render(request, 'profile.html', {'form': form,'data':data})

class Login_View(View):
    def get(self,request):
        form=Login_Form()
        return render(request,'login.html',{'form':form})
    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user) 
            if user.is_superuser: 
                return redirect("admin") 
            else:
                return redirect("user") 
    
class Admin_View(View):
    def get(self,request):
        return render(request,'admin.html')
    
class User_View(View):
    def get(self,request):
        data=UserProfile_Model.objects.get(user_id=request.user)
        return render(request,'user.html',{'data':data})

from app.forms import House_Name_Form

class House_Name_Add_View(View):
    def get(self,request,*args,**kwargs):
        form=House_Name_Form()
        data=House_Name.objects.all()
        return render(request,'house_name.html',{'form':form,'data':data})
    def post(self,request,*args,**kwargs):
        form=House_Name_Form(request.POST)
        if form.is_valid():
            form.save()
            form=House_Name_Form()
            data=House_Name.objects.all()
            return render(request,'house_name.html',{'form':form,'data':data})

class House_Name_Update_View(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get('pk')
        obj=House_Name.objects.get(id=id)
        form=House_Name_Form(instance=obj)
        data=House_Name.objects.all()
        return render(request,'house_name.html',{'form':form,'data':data})
    def post(self,request,*args,**kwargs):
        id=kwargs.get('pk')
        obj=House_Name.objects.get(id=id)
        form=House_Name_Form(request.POST,instance=obj)
        if form.is_valid():
            form.save()
            form=House_Name_Form()
            data=House_Name.objects.all()
            return redirect('house_name')
        
class House_Name_Delete_View(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get('pk')
        House_Name.objects.get(id=id).delete()
        return redirect('house_name')

