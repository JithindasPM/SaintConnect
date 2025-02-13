from django.shortcuts import render,redirect
from django.views.generic import View
from django.contrib.auth import authenticate,login,logout
from datetime import date

from app.models import User
from app.models import House_Name
from app.models import UserProfile_Model
from app.models import Death_Record
from app.models import Baptism_Record
from app.models import Auditorium
from app.models import Marriage_Record

from app.forms import Registration_Form
from app.forms import Login_Form
from app.forms import House_Name_Form
from app.forms import UserProfile_Form
from app.forms import Death_Record_Form
from app.forms import Baptism_Record_Form
from app.forms import Auditorium_Form
from app.forms import Marriage_Record_Form


# Create your views here.

class Home_View(View):
    def get(self,request):
        return render(request,'index.html')
    
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
        form = UserProfile_Form(instance=data,user=request.user)
        return render(request, 'profile.html', {'form': form,'data':data})
    
    def post(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        data=UserProfile_Model.objects.get(id=id)
        form = UserProfile_Form(request.POST,request.FILES, instance=data,user=request.user)
        if form.is_valid():
            form.save()
            if request.user.is_superuser:
                return redirect('admin')  # Redirect to 'admin' if superuser
            else:
                return redirect('user')  # Redirect to 'user' otherwise

        return render(request, 'profile.html', {'form': form, 'data': data})

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
        form=Login_Form()
        return render(request, "login.html", {"error": "Invalid credentials",'form':form})
    
class Logout_View(View):
    def get(self,request,*args,**kwargs):
        logout(request)
        return redirect('home')
    
class Admin_View(View):
    def get(self,request):
        datas = User.objects.filter(is_superuser=False).count()
        id=request.user.id
        data=UserProfile_Model.objects.get(user_id=id)
        house=House_Name.objects.all()
        return render(request,'admin.html',{'datas':datas,'house':house,"data":data})
    
class User_View(View):
    def get(self,request):
        data=UserProfile_Model.objects.get(user_id=request.user)
        obj=UserProfile_Model.objects.filter(house_name_id=data.house_name_id).count()
        return render(request,'user.html',{'data':data,'obj':obj})

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
    
class Member_Details_View(View):
    def get(self, request,*args,**kwargs):
        house_id=kwargs.get('pk')
        data=UserProfile_Model.objects.filter(house_name_id=house_id)
        house_name = House_Name.objects.get(id=house_id).name if House_Name.objects.filter(id=house_id).exists() else None
        print(house_name)
        return render(request,'member_details.html',{'data':data,'house_name':house_name})
    

# k================================================

class Delete(View):
    def get(self, request,*args,**kwargs):
        id=kwargs.get('pk')
        User.objects.get(id=id).delete()


# k================================================


class All_Member_View(View):
    def get(self, request,*args,**kwargs):
        data=User.objects.filter(is_superuser=False)
        return render(request,'all_members.html',{'data':data})
    
class Certificate_View(View):
    def get(self, request,*args,**kwargs):
        data=UserProfile_Model.objects.get(user_id=request.user)
        id=request.user.id
        death=Death_Record.objects.filter(applied_by_id=id)
        baptism=Baptism_Record.objects.filter(applied_by_id=id)
        marriage=Marriage_Record.objects.filter(user_id=id)
        return render(request,'certificates.html',{'data':data,'death':death,'baptism':baptism,'marriage':marriage})

class Death_Certificate_Add_View(View):
    def get(self, request,*args,**kwargs):
        form=Death_Record_Form(user=request.user)
        return render(request,'death_form.html',{'form':form})
    def post(self, request, *args, **kwargs):
        form = Death_Record_Form(request.POST, user=request.user)  # Pass request.user
        if form.is_valid():
            death_record = form.save(commit=False)
            death_record.applied_by = request.user  # Save the applicant
            death_record.save()
            return redirect('certificate')  # Redirect to success page
        return render(request,'death_form.html',{'form':form})
    
class Death_Certificate_Update_View(View):
    def get(self, request,*args,**kwargs):
        id=kwargs.get('pk')
        data=Death_Record.objects.get(id=id)
        form=Death_Record_Form(instance=data,user=request.user)
        return render(request,'death_form.html',{'form':form})
    def post(self, request,*args,**kwargs):
        id=kwargs.get('pk')
        data=Death_Record.objects.get(id=id)
        form=Death_Record_Form(request.POST,instance=data,user=request.user)
        if form.is_valid():
            form.save()
            return redirect('certificate')
        else:
            return render(request,'death_form.html',{'form':form})
        
class Death_Certificate_Delete_View(View):
    def get(self, request,*args,**kwargs):
        id=kwargs.get('pk')
        Death_Record.objects.get(id=id).delete()
        return redirect('certificate')
    
class Admin_Approval_View(View):
    def get(self, request,*args,**kwargs):
        death=Death_Record.objects.all().order_by('-id')
        baptism=Baptism_Record.objects.all().order_by('-id')
        marriage=Marriage_Record.objects.all().order_by('-id')
        return render(request,'admin_approval.html',{'death':death,'baptism':baptism,'marriage':marriage})

class Death_Approval_View(View):
    def post(self, request, record_id, *args, **kwargs):
        death= Death_Record.objects.get(id=record_id)
        death.is_approved = not death.is_approved  # Toggle between True/False
        death.save()
        return redirect('admin_approval')

class Death_Certificate_View(View):
    def get(self, request, record_id, *args, **kwargs):
        death= Death_Record.objects.get(id=record_id)
        data=death.member
        person=UserProfile_Model.objects.get(user=data)
        age=person.age
        today = date.today()
        formatted_date = today.strftime("%d-%m-%Y")
        return render(request,'death_certificate.html',{'death':death,'formatted_date':formatted_date,'age':age})
    
class Baptism_Certificate_Add_View(View):
    def get(self, request,*args,**kwargs):
        form=Baptism_Record_Form(user=request.user)
        return render(request,'baptism_form.html',{'form':form})
    def post(self, request, *args, **kwargs):
        form = Baptism_Record_Form(request.POST, user=request.user)
        if form.is_valid():
            baptism_record = form.save(commit=False)
            baptism_record.applied_by = request.user
            baptism_record.save()
            return redirect('certificate')
        return render(request,'baptism_form.html',{'form':form})

class Baptism_Certificate_Update_View(View):
    def get(self, request,*args,**kwargs):
        id=kwargs.get('pk')
        data=Baptism_Record.objects.get(id=id)
        form=Baptism_Record_Form(instance=data,user=request.user)
        return render(request,'baptism_form.html',{'form':form})
    def post(self, request,*args,**kwargs):
        id=kwargs.get('pk')
        data=Baptism_Record.objects.get(id=id)
        form=Baptism_Record_Form(request.POST,instance=data,user=request.user)
        if form.is_valid():
            form.save()
            return redirect('certificate')
        else:
            return render(request,'baptism_form.html',{'form':form})
        
class Baptism_Certificate_Delete_View(View):
    def get(self, request,*args,**kwargs):
        id=kwargs.get('pk')
        Baptism_Record.objects.get(id=id).delete()
        return redirect('certificate')
    
class Baptism_Approval_View(View):
    def post(self, request, record_id, *args, **kwargs):
        baptism= Baptism_Record.objects.get(id=record_id)
        baptism.is_approved = not baptism.is_approved  # Toggle between True/False
        baptism.save()
        return redirect('admin_approval')
    
class Baptism_Certificate_View(View):
    def get(self, request, record_id, *args, **kwargs):
        baptism= Baptism_Record.objects.get(id=record_id)
        data=baptism.member
        person=UserProfile_Model.objects.get(user=data)
        dob=person.date_of_birth
        today = date.today()
        formatted_date = today.strftime("%d-%m-%Y")
        return render(request,'baptism_certificate.html',{'baptism':baptism,'formatted_date':formatted_date,'dob':dob})

class Auditorium_Add_View(View):
    def get(self,request,*args,**kwargs):
        form=Auditorium_Form()
        data=Auditorium.objects.all()
        return render(request,'auditorium.html',{'form':form,'data':data})
    def post(self,request,*args,**kwargs):
        form=Auditorium_Form(request.POST)
        if form.is_valid():
            form.save()
            form=Auditorium_Form()
            data=Auditorium.objects.all()
            return render(request,'auditorium.html',{'form':form,'data':data})

class Auditorium_Update_View(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get('pk')
        obj=Auditorium.objects.get(id=id)
        form=Auditorium_Form(instance=obj)
        data=Auditorium.objects.all()
        return render(request,'auditorium.html',{'form':form,'data':data})
    def post(self,request,*args,**kwargs):
        id=kwargs.get('pk')
        obj=Auditorium.objects.get(id=id)
        form=Auditorium_Form(request.POST,instance=obj)
        if form.is_valid():
            form.save()
            form=Auditorium_Form()
            data=Auditorium.objects.all()
            return redirect('auditorium_add')
        
class Auditorium_Delete_View(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get('pk')
        Auditorium.objects.get(id=id).delete()
        return redirect('auditorium_add')
        
class Marriage_Certificate_Add_View(View):
    def get(self, request, *args, **kwargs):
        form = Marriage_Record_Form() 
        return render(request, 'marriage_form.html', {'form': form})
    def post(self, request, *args, **kwargs):
        form = Marriage_Record_Form(request.POST) 
        if form.is_valid():
            marriage_record = form.save(commit=False)
            marriage_record.user = request.user
            marriage_record.save() 
            form = Marriage_Record_Form() 
        return redirect('certificate')
    
class Marriage_Certificate_Update_View(View):
    def get(self, request,*args,**kwargs):
        id=kwargs.get('pk')
        data=Marriage_Record.objects.get(id=id)
        form=Marriage_Record_Form(instance=data)
        return render(request,'marriage_form.html',{'form':form})
    def post(self, request,*args,**kwargs):
        id=kwargs.get('pk')
        data=Marriage_Record.objects.get(id=id)
        form=Marriage_Record_Form(request.POST,instance=data)
        if form.is_valid():
            form.save()
            return redirect('certificate')
        else:
            return render(request,'marriage_form.html',{'form':form})
        
class Marriage_Certificate_Delete_View(View):
    def get(self, request,*args,**kwargs):
        id=kwargs.get('pk')
        Marriage_Record.objects.get(id=id).delete()
        return redirect('certificate')
    
class Marriage_Approval_View(View):
    def post(self, request, record_id, *args, **kwargs):
        marriage= Marriage_Record.objects.get(id=record_id)
        marriage.is_approved = not marriage.is_approved  # Toggle between True/False
        marriage.save()
        return redirect('admin_approval')
    
class Marriage_Certificate_View(View):
    def get(self, request, record_id, *args, **kwargs):
        marriage= Marriage_Record.objects.get(id=record_id)
        today = date.today()
        formatted_date = today.strftime("%d-%m-%Y")
        return render(request,'marriage_certificate.html',{'marriage':marriage,'formatted_date':formatted_date})
    
class User_Filter_View(View):
    def get(self,request, role,*args, **kwargs):
        users = UserProfile_Model.objects.filter(role=role).exclude(user__is_superuser=True)
        return render(request, 'user_filter.html', {'users': users, 'role': role})