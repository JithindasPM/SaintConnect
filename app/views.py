from django.shortcuts import render,redirect,get_object_or_404
from django.views.generic import View
from django.contrib.auth import authenticate,login,logout
from datetime import date
from django.db.models import Sum
from django.core.paginator import Paginator
from datetime import datetime
from django.utils import timezone
from django.contrib import messages
from django.utils.timezone import now
from datetime import timedelta
import os
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
from django.http import Http404
from django.utils.decorators import method_decorator
from django.db.models import Exists, OuterRef


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



def Login_required(fn):
    def wrapper(request,*args,**kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        else:
            return fn(request,*args,**kwargs)
    return wrapper  

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
        error_message = 'Invalid username or password.'
        return render(request, "login.html", {"error_message": error_message,'form':form})
    
class Logout_View(View):
    def get(self,request,*args,**kwargs):
        logout(request)
        return redirect('home')
    
@method_decorator(Login_required,name='dispatch')
class Admin_View(View):
    def get(self,request):
        datas = User.objects.filter(is_superuser=False).count()
        user_id=request.user.id
        user=UserProfile_Model.objects.get(user_id=user_id)
        now = timezone.now()

        # Count approved records for each model in the current month
        approved_death_records = Death_Record.objects.filter(is_approved=True,created_at__month=now.month,created_at__year=now.year).count()
        approved_baptism_records = Baptism_Record.objects.filter(is_approved=True,created_at__month=now.month,created_at__year=now.year).count()
        approved_marriage_records = Marriage_Record.objects.filter(is_approved=True,created_at__month=now.month,created_at__year=now.year).count()

        # Calculate total approved records
        total_approved_records = approved_death_records + approved_baptism_records + approved_marriage_records

        # Calculate total number of approved events for the current month
        total_approved_events = Event.objects.filter(is_approved=True,created_at__month=now.month,created_at__year=now.year).count()

        # Calculate total paid_amount for the current month
        total_paid_for_month = House_Donation.objects.filter(created_at__month=now.month,created_at__year=now.year).aggregate(Sum('paid_amount'))
        # Access the sum from the result
        total_paid = total_paid_for_month['paid_amount__sum'] or 0  # Default to 0 if no results

        # Calculate total donation for each house
        house_list = House_Name.objects.exclude(name='Admin')
        house_donations = []
        for house in house_list:
            total_donation = House_Donation.objects.filter(house_name=house).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
            house_donations.append({'house': house, 'total_donation': total_donation})
        return render(request,'admin.html',{'datas':datas,'house_donations':house_donations,'user':user,
                                            'total_paid':total_paid,'total_approved_events':total_approved_events,
                                            'total_approved_records':total_approved_records})
    


@method_decorator(Login_required,name='dispatch')
class User_View(View):
    def get(self, request):
        data = UserProfile_Model.objects.get(user_id=request.user)
        if data.house_name:
            obj = UserProfile_Model.objects.filter(house_name=data.house_name).count()
        else:
            obj = 0

        events=Event.objects.filter(user=request.user).count()

        # Count Death, Baptism, and Marriage certificates applied by the user
        death_count = Death_Record.objects.filter(applied_by=request.user).count()
        baptism_count = Baptism_Record.objects.filter(applied_by=request.user).count()
        marriage_count = Marriage_Record.objects.filter(user=request.user).count()

        # Total certificates
        total_certificates = death_count + baptism_count + marriage_count

        current_month = datetime.now().month
        current_year = datetime.now().year

        # Fetch donations for the user's house for the current month
        if data.house_name:
            # Filter House_Donation for the current month
            donation = House_Donation.objects.filter(house_name=data.house_name,status=False,
                                                     created_at__month=current_month,created_at__year=current_year)
            
            # Calculate the total paid amount for donations in the current month
            total_paid_amount = House_Donation.objects.filter(
                house_name=data.house_name, 
                created_at__month=current_month,
                created_at__year=current_year
            ).aggregate(total_paid=Sum('paid_amount'))['total_paid'] or 0
        else:
            donation = House_Donation.objects.none()  # Returns an empty queryset if no house
            total_paid_amount = 0

        return render(request, 'user.html', {
            'data': data,
            'obj': obj,
            'donation': donation,
            'total_paid_amount': total_paid_amount,
            'events':events,
            'total_certificates':total_certificates
        })

@method_decorator(Login_required,name='dispatch')
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

@method_decorator(Login_required,name='dispatch')
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

@method_decorator(Login_required,name='dispatch')      
class House_Name_Delete_View(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get('pk')
        House_Name.objects.get(id=id).delete()
        return redirect('house_name')
    

@method_decorator(Login_required,name='dispatch')  
class Member_Details_View(View):
    def get(self, request, *args, **kwargs):
        house_id = kwargs.get('pk')
        death_records = Death_Record.objects.filter(member=OuterRef('user'), is_approved=True)
        data = UserProfile_Model.objects.filter(house_name_id=house_id).annotate(
            is_dead=Exists(death_records)
        )
        house_name = House_Name.objects.get(id=house_id).name if House_Name.objects.filter(id=house_id).exists() else None
        return render(request, 'member_details.html', {'data': data, 'house_name': house_name})

# k================================================

class Delete(View):
    def get(self, request,*args,**kwargs):
        id=kwargs.get('pk')
        User.objects.get(id=id).delete()


# k================================================

@method_decorator(Login_required,name='dispatch')
class All_Member_View(View):
    def get(self, request,*args,**kwargs):
        data=User.objects.filter(is_superuser=False)
        user = get_object_or_404(UserProfile_Model, user=request.user)
        return render(request,'all_members.html',{'data':data,'user':user})

@method_decorator(Login_required,name='dispatch')  
class Certificate_View(View):
    def get(self, request,*args,**kwargs):
        data=UserProfile_Model.objects.get(user_id=request.user)
        id=request.user.id
        death=Death_Record.objects.filter(applied_by_id=id)
        baptism=Baptism_Record.objects.filter(applied_by_id=id)
        marriage=Marriage_Record.objects.filter(user_id=id)
        return render(request,'certificates.html',{'data':data,'death':death,'baptism':baptism,'marriage':marriage})

@method_decorator(Login_required,name='dispatch')
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

@method_decorator(Login_required,name='dispatch')  
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

@method_decorator(Login_required,name='dispatch')
class Death_Certificate_Delete_View(View):
    def get(self, request,*args,**kwargs):
        id=kwargs.get('pk')
        Death_Record.objects.get(id=id).delete()
        return redirect('certificate')

@method_decorator(Login_required,name='dispatch') 
class Admin_Approval_View(View):
    def get(self, request,*args,**kwargs):
        user_id=request.user.id
        user=UserProfile_Model.objects.get(user_id=user_id)
        death=Death_Record.objects.all().order_by('-id')
        baptism=Baptism_Record.objects.all().order_by('-id')
        marriage=Marriage_Record.objects.all().order_by('-id')
        return render(request,'admin_approval.html',{'death':death,'baptism':baptism,'marriage':marriage,'user':user})

@method_decorator(Login_required,name='dispatch')
class Death_Approval_View(View):
    def post(self, request, record_id, *args, **kwargs):
        death= Death_Record.objects.get(id=record_id)
        death.is_approved = not death.is_approved  # Toggle between True/False
        death.save()
        return redirect('admin_approval')


@method_decorator(Login_required,name='dispatch')
class Death_Certificate_View(View):
    def get(self, request, record_id, *args, **kwargs):
        try:
            # Fetch death record details
            death = Death_Record.objects.get(id=record_id)
            data = death.member
            person = UserProfile_Model.objects.get(user=data)
            age = person.age
        except Death_Record.DoesNotExist:
            raise Http404("Death record not found")
        except UserProfile_Model.DoesNotExist:
            raise Http404("User profile not found")

        today = date.today()
        formatted_date = today.strftime("%d-%m-%Y")

        # Render the HTML template with context
        html_content = render_to_string('death_certificate.html', {
            'death': death,
            'formatted_date': formatted_date,
            'age': age
        })

        if "download" in request.GET:
            # Generate PDF and return response
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="Death_Certificate.pdf"'

            # Ensure temporary directory is not inside OneDrive
            temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp')
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)

            # Create temporary file outside OneDrive
            with tempfile.NamedTemporaryFile(delete=False, dir=temp_dir) as temp_file:
                HTML(string=html_content).write_pdf(temp_file.name)
                with open(temp_file.name, 'rb') as pdf:
                    response.write(pdf.read())

            return response

        # Render normal HTML page if not downloading
        return render(request, 'death_certificate.html', {
            'death': death,
            'formatted_date': formatted_date,
            'age': age
        })

@method_decorator(Login_required,name='dispatch')  
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

@method_decorator(Login_required,name='dispatch')
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

@method_decorator(Login_required,name='dispatch')       
class Baptism_Certificate_Delete_View(View):
    def get(self, request,*args,**kwargs):
        id=kwargs.get('pk')
        Baptism_Record.objects.get(id=id).delete()
        return redirect('certificate')

@method_decorator(Login_required,name='dispatch')  
class Baptism_Approval_View(View):
    def post(self, request, record_id, *args, **kwargs):
        baptism= Baptism_Record.objects.get(id=record_id)
        baptism.is_approved = not baptism.is_approved  # Toggle between True/False
        baptism.save()
        return redirect('admin_approval')
    

@method_decorator(Login_required,name='dispatch')
class Baptism_Certificate_View(View):
    def get(self, request, record_id, *args, **kwargs):
        # Set a custom temporary directory path
        os.environ["TMPDIR"] = "C:/path/to/your/desired/temp/folder"  # Ensure this folder has write permissions
        
        baptism = Baptism_Record.objects.get(id=record_id)
        data = baptism.member
        person = UserProfile_Model.objects.get(user=data)
        dob = person.date_of_birth
        today = date.today()
        formatted_date = today.strftime("%d-%m-%Y")

        html_content = render_to_string('baptism_certificate.html', {
            'baptism': baptism,
            'formatted_date': formatted_date,
            'dob': dob,
        })

        if request.GET.get('download') == 'true':
            # Generate the PDF and return it as a response
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="baptism_certificate_{record_id}.pdf"'

            HTML(string=html_content).write_pdf(response)
            return response
        
        return render(request, 'baptism_certificate.html', {'baptism': baptism, 'formatted_date': formatted_date, 'dob': dob})


@method_decorator(Login_required,name='dispatch')
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

@method_decorator(Login_required,name='dispatch')
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

@method_decorator(Login_required,name='dispatch')       
class Auditorium_Delete_View(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get('pk')
        Auditorium.objects.get(id=id).delete()
        return redirect('auditorium_add')

@method_decorator(Login_required,name='dispatch')     
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

@method_decorator(Login_required,name='dispatch') 
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

@method_decorator(Login_required,name='dispatch')     
class Marriage_Certificate_Delete_View(View):
    def get(self, request,*args,**kwargs):
        id=kwargs.get('pk')
        Marriage_Record.objects.get(id=id).delete()
        return redirect('certificate')
    
@method_decorator(Login_required,name='dispatch')
class Marriage_Approval_View(View):
    def post(self, request, record_id, *args, **kwargs):
        marriage= Marriage_Record.objects.get(id=record_id)
        marriage.is_approved = not marriage.is_approved  # Toggle between True/False
        marriage.save()
        return redirect('admin_approval')


@method_decorator(Login_required,name='dispatch')
class Marriage_Certificate_View(View):
    def get(self, request, record_id, *args, **kwargs):
        # Fetch the marriage record
        marriage = Marriage_Record.objects.get(id=record_id)
        today = date.today()
        formatted_date = today.strftime("%d-%m-%Y")
        
        # Check if the 'download' parameter is present in the URL
        if request.GET.get('download'):
            # Generate the PDF file using WeasyPrint
            html_content = render(request, 'marriage_certificate.html', {'marriage': marriage, 'formatted_date': formatted_date})
            pdf_file = HTML(string=html_content.content.decode('utf-8')).write_pdf()

            # Create the HTTP response to prompt the file download
            response = HttpResponse(pdf_file, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="marriage_certificate_{record_id}.pdf"'
            return response
        
        # If no download parameter, render the certificate normally
        return render(request, 'marriage_certificate.html', {'marriage': marriage, 'formatted_date': formatted_date})

@method_decorator(Login_required,name='dispatch')   
class User_Filter_View(View):
    def get(self,request, role,*args, **kwargs):
        user = get_object_or_404(UserProfile_Model, user=request.user)
        users = UserProfile_Model.objects.filter(role=role).exclude(user__is_superuser=True)
        return render(request, 'user_filter.html', {'users': users, 'role': role,'user':user})
    
@method_decorator(Login_required,name='dispatch')  
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

@method_decorator(Login_required,name='dispatch')
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

@method_decorator(Login_required,name='dispatch')
class Donation_Delete_View(View):
    def get(self, request, *args, **kwargs):
        id=kwargs.get('pk')
        Donation.objects.get(id=id).delete()
        return redirect('donation_add')

@method_decorator(Login_required,name='dispatch')
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

@method_decorator(Login_required,name='dispatch')
class Event_Add_View(View):
    def get(self,request,*args,**kwargs):
        form=Event_Form()
        user = get_object_or_404(UserProfile_Model, user=request.user)
        one_month_ago = now().date() - timedelta(days=30)
        datas = Event.objects.filter(user=request.user, date__gte=one_month_ago).order_by('-id')
        return render(request,'event_form.html',{'form':form,'datas':datas,'user':user})
        
    def post(self,request,*args,**kwargs):
        one_month_ago = now().date() - timedelta(days=30)
        datas = Event.objects.filter(user=request.user, date__gte=one_month_ago).order_by('-id')
        user = get_object_or_404(UserProfile_Model, user=request.user)
        form = Event_Form(request.POST)
        if form.is_valid():
            user = request.user
            hall = form.cleaned_data['hall']
            event_name = form.cleaned_data['event_name']
            description = form.cleaned_data['description']
            date = form.cleaned_data['date']

            if Event.objects.filter(hall=hall, date=date).exists():
                messages.error(request, f"The auditorium '{hall}' is already booked for {date}.")
                form = Event_Form()
                user = get_object_or_404(UserProfile_Model, user=request.user)
                return render(request, 'event_form.html', {"form": form,'datas':datas,'user':user})

            if Event.objects.filter(date=date).count() >= 3:
                messages.error(request, f"Only three events are allowed per day. No more bookings available for {date}.")
                form = Event_Form()
                user = get_object_or_404(UserProfile_Model, user=request.user)
                return render(request, 'event_form.html', {"form": form,'datas':datas,'user':user})

            event = Event(user=user, hall=hall, event_name=event_name, description=description, date=date)
            event.save()

            messages.success(request, f"Your event '{event_name}' has been submitted for {date} and is awaiting approval.")

            form=Event_Form()
            user = get_object_or_404(UserProfile_Model, user=request.user)
            return render(request, 'event_form.html', {"form": form,'datas':datas,'user':user})
        form=Event_Form()
        user = get_object_or_404(UserProfile_Model, user=request.user)
        return render(request, 'event_form.html', {"form": form,'datas':datas,'user':user})

@method_decorator(Login_required,name='dispatch')
class Event_Update_View(View):
    def get(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        event_instance = get_object_or_404(Event, id=id)
        form = Event_Form(instance=event_instance)
        one_month_ago = now().date() - timedelta(days=30)
        datas = Event.objects.filter(user=request.user, date__gte=one_month_ago).order_by('-id')
        user = get_object_or_404(UserProfile_Model, user=request.user)
        return render(request, 'event_form.html', {'form': form, "datas": datas, 'user': user})

    def post(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        event_instance = get_object_or_404(Event, id=id)
        user = get_object_or_404(UserProfile_Model, user=request.user)
        one_month_ago = now().date() - timedelta(days=30)
        datas = Event.objects.filter(user=request.user, date__gte=one_month_ago).order_by('-id')
        form = Event_Form(request.POST, instance=event_instance)
        if form.is_valid():
            form.save()
            form = Event_Form()
            messages.success(request, "Your event has been updated successfully.")
        return redirect('event_add')


@method_decorator(Login_required,name='dispatch')
class Event_Delete_View(View):
    def get(self, request, *args, **kwargs):
        id=kwargs.get('pk')
        Event.objects.get(id=id).delete()
        return redirect('event_add')

@method_decorator(Login_required,name='dispatch')
class Event_List_View(View):
    def get(self, request, *args, **kwargs):
        # Get start and end date from request
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        # Convert dates to proper format if provided
        if start_date and end_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                datas = Event.objects.filter(date__range=[start_date, end_date]).order_by('date')
            except ValueError:
                datas = Event.objects.all().order_by('date')  # If date parsing fails, return all events
        else:
            datas = Event.objects.all().order_by('date')  # Default: return all events

        # Paginate the events (10 per page)
        paginator = Paginator(datas, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Get user profile
        user = get_object_or_404(UserProfile_Model, user=request.user)

        # Render template
        return render(request, 'event_approval.html', {'page_obj': page_obj, 'user': user, 'start_date': start_date, 'end_date': end_date})


@method_decorator(Login_required,name='dispatch')
class Event_Approval_View(View):
    def post(self, request, record_id, *args, **kwargs):
        datas=Event.objects.all()
        user = get_object_or_404(UserProfile_Model, user=request.user)
        event= Event.objects.get(id=record_id)
        event.is_approved = not event.is_approved  # Toggle between True/False
        event.save()
        return redirect('event_list')

@method_decorator(Login_required,name='dispatch')
class Approved_Event_View(View):
    def get(self, request, *args, **kwargs):
        start_date = request.GET.get('start_date', '')
        end_date = request.GET.get('end_date', '')

        # Get events that are approved
        datas = Event.objects.filter(is_approved=True)

        # Filter based on date range if both dates are provided
        if start_date and end_date:
            try:
                start_date = datetime.strptime(start_date, "%Y-%m-%d")
                end_date = datetime.strptime(end_date, "%Y-%m-%d")
                datas = datas.filter(date__range=[start_date, end_date])
            except ValueError:
                pass  # Handle invalid date formats

        # Pagination (10 records per page)
        paginator = Paginator(datas, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Get user profile
        data = get_object_or_404(UserProfile_Model, user=request.user)

        return render(request, 'approved_events.html', {
            'datas': page_obj,
            'user': data,
            'data': data,
            'start_date': start_date.strftime("%Y-%m-%d") if start_date else '',
            'end_date': end_date.strftime("%Y-%m-%d") if end_date else '',
        })

@method_decorator(Login_required,name='dispatch')  
class Death_Members_View(View):
    def get(self, request, *args, **kwargs):
        user = get_object_or_404(UserProfile_Model, user=request.user)
        death=Death_Record.objects.filter(is_approved=True)
        return render(request, 'death_members.html', {'death': death, 'user': user})
    

class Family_Members_View(View):
    template_name = 'family_members.html'

    def get(self, request, *args, **kwargs):
        # Get the current user's profile
        user_profile = UserProfile_Model.objects.filter(user=request.user).first()
        data=UserProfile_Model.objects.get(user_id=request.user)
        
        
        # Fetch family members with the same house_name (excluding the current user)
        family_members = []
        if user_profile and user_profile.house_name:
            family_members = UserProfile_Model.objects.filter(
                house_name=user_profile.house_name
            ).exclude(user=request.user)

        context = {
            'family_members': family_members,
            'data':data
        }
        return render(request, self.template_name, context)
