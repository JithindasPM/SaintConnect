from django.shortcuts import render,redirect,get_object_or_404
from django.views.generic import View
from django.contrib.auth import authenticate,login,logout
from datetime import date
from django.db.models import Sum

from app.models import User
from app.models import House_Name
from app.models import UserProfile_Model
from app.models import Death_Record
from app.models import Baptism_Record
from app.models import Auditorium
from app.models import Marriage_Record
from app.models import Donation
from app.models import House_Donation
from app.models import Event

from app.forms import Registration_Form
from app.forms import Login_Form
from app.forms import House_Name_Form
from app.forms import UserProfile_Form
from app.forms import Death_Record_Form
from app.forms import Baptism_Record_Form
from app.forms import Auditorium_Form
from app.forms import Marriage_Record_Form
from app.forms import Donation_Form
from app.forms import House_Donation_Form
from app.forms import Event_Form

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
        user_id=request.user.id
        user=UserProfile_Model.objects.get(user_id=user_id)
        # id=request.user.id
        # data=UserProfile_Model.objects.get(user_id=id)
        house_list = House_Name.objects.exclude(name='Admin')

        # Calculate total donation for each house
        house_donations = []
        for house in house_list:
            total_donation = House_Donation.objects.filter(house_name=house).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
            house_donations.append({'house': house, 'total_donation': total_donation})
        return render(request,'admin.html',{'datas':datas,'house_donations':house_donations,'user':user})
    
class User_View(View):
    def get(self,request):
        data=UserProfile_Model.objects.get(user_id=request.user)
        obj=UserProfile_Model.objects.filter(house_name_id=data.house_name_id).count()
         # Filter House_Donation only for the user's house
        if data.house_name:
            donation = House_Donation.objects.filter(house_name=data.house_name, status=False)  
        else:
            donation = House_Donation.objects.none()  # Returns an empty queryset if no house
        return render(request,'user.html',{'data':data,'obj':obj,'donation':donation})

class House_Name_Add_View(View):
    def get(self,request,*args,**kwargs):
        form=House_Name_Form()
        data=House_Name.objects.all()
        user_id=request.user.id
        user=UserProfile_Model.objects.get(user_id=user_id)
        return render(request,'house_name.html',{'form':form,'data':data,'user':user})
    def post(self,request,*args,**kwargs):
        user_id=request.user.id
        user=UserProfile_Model.objects.get(user_id=user_id)
        form=House_Name_Form(request.POST)
        if form.is_valid():
            form.save()
            form=House_Name_Form()
            data=House_Name.objects.all()
            return render(request,'house_name.html',{'form':form,'data':data,'user':user})

class House_Name_Update_View(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get('pk')
        obj=House_Name.objects.get(id=id)
        form=House_Name_Form(instance=obj)
        data=House_Name.objects.all()
        user_id=request.user.id
        user=UserProfile_Model.objects.get(user_id=user_id)
        return render(request,'house_name.html',{'form':form,'data':data,'user':user})
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
        user_id=request.user.id
        user=UserProfile_Model.objects.get(user_id=user_id)
        death=Death_Record.objects.all().order_by('-id')
        baptism=Baptism_Record.objects.all().order_by('-id')
        marriage=Marriage_Record.objects.all().order_by('-id')
        return render(request,'admin_approval.html',{'death':death,'baptism':baptism,'marriage':marriage,'user':user})

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
        user_id=request.user.id
        user=UserProfile_Model.objects.get(user_id=user_id)
        return render(request,'auditorium.html',{'form':form,'data':data,'user':user})
    def post(self,request,*args,**kwargs):
        user_id=request.user.id
        user=UserProfile_Model.objects.get(user_id=user_id)
        form=Auditorium_Form(request.POST)
        if form.is_valid():
            form.save()
            form=Auditorium_Form()
            data=Auditorium.objects.all()
            return render(request,'auditorium.html',{'form':form,'data':data,'user':user})

class Auditorium_Update_View(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get('pk')
        obj=Auditorium.objects.get(id=id)
        form=Auditorium_Form(instance=obj)
        data=Auditorium.objects.all()
        user_id=request.user.id
        user=UserProfile_Model.objects.get(user_id=user_id)
        return render(request,'auditorium.html',{'form':form,'data':data,'user':user})
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
    
    
class Donation_Add_View(View):
    def get(self, request, *args, **kwargs):
        form = Donation_Form()
        data=Donation.objects.all().order_by('-id')
        user_id=request.user.id
        user=UserProfile_Model.objects.get(user_id=user_id)
        return render(request, 'donation_form.html', {'form': form,"data":data,'user':user})

    def post(self, request, *args, **kwargs):
        user_id=request.user.id
        user=UserProfile_Model.objects.get(user_id=user_id)
        form = Donation_Form(request.POST)
        if form.is_valid():
            donation = form.save()  
            
            # Exclude "admin" family from house list
            houses = House_Name.objects.exclude(name__iexact="Admin")  

            for house in houses:
                House_Donation.objects.get_or_create(
                    donation=donation,
                    house_name=house,
                    defaults={'total_amount': donation.amount, 'paid_amount': 0, 'user': request.user} 
                )
            form = Donation_Form()
            data=Donation.objects.all().order_by('-id')
        return render(request, 'donation_form.html', {'form': form,"data":data,'user':user})

class Donation_Update_View(View):
    def get(self, request, *args, **kwargs):
        id=kwargs.get('pk')
        data=Donation.objects.get(id=id)
        form = Donation_Form(instance=data)
        data=Donation.objects.all().order_by('-id')
        user_id=request.user.id
        user=UserProfile_Model.objects.get(user_id=user_id)
        return render(request, 'donation_form.html', {'form': form,"data":data,'user':user})
    def post(self, request, *args, **kwargs):
        id=kwargs.get('pk')
        data=Donation.objects.get(id=id)
        form = Donation_Form(request.POST,instance=data)
        if form.is_valid():
            form.save()
            data=Donation.objects.all().order_by('-id')
            form = Donation_Form()
        return redirect('donation_add')

class Donation_Delete_View(View):
    def get(self, request, *args, **kwargs):
        id=kwargs.get('pk')
        Donation.objects.get(id=id).delete()
        return redirect('donation_add')


class Donation_Paid_View(View):
    def get(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        data = get_object_or_404(House_Donation, id=id)
        form = House_Donation_Form()  # Create a fresh form for entering new payment
        return render(request, 'donation_paid.html', {
            'form': form,
            'success': False,
            'total_amount': data.total_amount,
            'paid_amount': data.paid_amount
        })

    def post(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        data = get_object_or_404(House_Donation, id=id)
        form = House_Donation_Form(request.POST)

        if form.is_valid():
            new_paid_amount = form.cleaned_data.get('paid_amount')

            # Ensure valid payment
            if new_paid_amount is None or new_paid_amount <= 0:
                return render(request, 'donation_paid.html', {
                    'form': form,
                    'success': False,
                    'error': "Invalid payment amount!",
                    'total_amount': data.total_amount,
                    'paid_amount': data.paid_amount
                })

            total_paid = data.paid_amount + new_paid_amount  # Corrected logic

            # Prevent overpayment
            if total_paid > data.total_amount:
                return render(request, 'donation_paid.html', {
                    'form': form,
                    'success': False,
                    'error': "You cannot pay more than the total amount!",
                    'total_amount': data.total_amount,
                    'paid_amount': data.paid_amount
                })

            # Update model instance correctly
            data.paid_amount = total_paid
            
            # Update status if fully paid
            if total_paid == data.total_amount:
                data.status = True

            data.save()

            return render(request, 'donation_paid.html', {
                'form': House_Donation_Form(),  # Reset form
                'success': True,
                'total_amount': data.total_amount,
                'paid_amount': total_paid
            })

        return render(request, 'donation_paid.html', {
            'form': form,
            'success': False,
            'error': "Please correct the errors in the form.",
            'total_amount': data.total_amount,
            'paid_amount': data.paid_amount
        })
    
class Event_Add_View(View):
    def get(self,request,*args,**kwargs):
        form=Event_Form()
        return render(request,'event_form.html',{'form':form})


# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.contrib.auth.mixins import LoginRequiredMixin
# from django.views import View
# from .models import Event
# from .forms import EventForm

# class BookAuditoriumView(LoginRequiredMixin, View):
#     template_name = "book_auditorium.html"  

#     def get(self, request):
#         """Display the booking form"""
#         form = EventForm()
#         return render(request, self.template_name, {"form": form})

#     def post(self, request):
#         """Handle form submission"""
#         form = EventForm(request.POST)
#         if form.is_valid():
#             user = request.user
#             hall = form.cleaned_data['hall']
#             event_name = form.cleaned_data['event_name']
#             description = form.cleaned_data['description']
#             date = form.cleaned_data['date']

#             # Check if this auditorium is already booked on the same date
#             if Event.objects.filter(hall=hall, date=date).exists():
#                 messages.error(request, f"The auditorium '{hall}' is already booked for {date}.")
#                 return render(request, self.template_name, {"form": form})

#             # Check if the total number of events on this date is already 3
#             if Event.objects.filter(date=date).count() >= 3:
#                 messages.error(request, f"Only three events are allowed per day. No more bookings available for {date}.")
#                 return render(request, self.template_name, {"form": form})

#             # Save the event if validation passes
#             event = Event(user=user, hall=hall, event_name=event_name, description=description, date=date)
#             event.save()

#             messages.success(request, f"Your event '{event_name}' has been booked successfully for {date}.")
#             return redirect("event_list")  

#         return render(request, self.template_name, {"form": form})  


