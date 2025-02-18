from django import forms

from app.models import User
from app.models import UserProfile_Model
from app.models import House_Name
from app.models import Death_Record
from django.contrib.auth import get_user_model
from app.models import Baptism_Record
from app.models import Auditorium
from app.models import Marriage_Record
from app.models import Donation
from app.models import House_Donation
from app.models import Event


class House_Name_Form(forms.ModelForm):
    class Meta:
        model=House_Name
        fields=['name']

        widgets={
            'name':forms.TextInput(attrs={'class':'form-control',
                                              'placeholder': 'House Name . . .'})
        }

class Registration_Form(forms.ModelForm):
    class Meta:
        model=User
        fields=['username','password']

        widgets={
            'username':forms.TextInput(attrs={'class':'form-control',
                                              'placeholder': 'Username . . .'}),
            'password':forms.PasswordInput(attrs={'class':'form-control',
                                                  'placeholder': 'Password . . .'})
        }

class UserProfile_Form(forms.ModelForm):
    class Meta:
        model=UserProfile_Model
        fields=['name','house_name','address','age','email','gender','profile_picture','phone_number','role','date_of_birth']
        read_only_fields=['user','created_date','updated_date','is_active']

        widgets={

            'name':forms.TextInput(attrs={'class':'form-control my-1',
                                          'placeholder': 'Enter your name . . .',
                                          'style':'background-color:rgba(255, 255, 255, 0.75);border:2px solid rgba(0, 0, 0, 0.1)'}),
            'house_name':forms.Select(attrs={'class':'form-control my-1',
                                         'style':'background-color:rgba(255, 255, 255, 0.75);border:2px solid rgba(0, 0, 0, 0.1)'}),
            'address':forms.Textarea(attrs={'class':'form-control my-1',
                                          'placeholder': 'Enter your name . . .',
                                          'style':'background-color:rgba(255, 255, 255, 0.75);border:2px solid rgba(0, 0, 0, 0.1)'}),
            'age':forms.NumberInput(attrs={'class':'form-control my-1',
                                            'placeholder':'Enter Your age . . .',
                                            'style':'background-color:rgba(255, 255, 255, 0.75);border:2px solid rgba(0, 0, 0, 0.1)'}),
            'email':forms.EmailInput(attrs={'class':'form-control my-1',
                                               'placeholder':'Enter your weight in Kg . . .',
                                               'style':'background-color:rgba(255, 255, 255, 0.75);border:2px solid rgba(0, 0, 0, 0.1)'}),
            'gender':forms.Select(attrs={'class':'form-control my-1',
                                         'style':'background-color:rgba(255, 255, 255, 0.75);border:2px solid rgba(0, 0, 0, 0.1)'}),
            'profile_picture':forms.FileInput(attrs={'class':'form-control-file',
                                                      'id':'profile_image'}),
            'phone_number':forms.NumberInput(attrs={'class':'form-control my-1',
                                            'placeholder':'Enter Your phone number . . .',
                                            'style':'background-color:rgba(255, 255, 255, 0.75);border:2px solid rgba(0, 0, 0, 0.1)'}),
            'role':forms.Select(attrs={'class':'form-control my-1',
                                         'style':'background-color:rgba(255, 255, 255, 0.75);border:2px solid rgba(0, 0, 0, 0.1)'}),
            'date_of_birth':forms.DateInput(attrs={'class': 'form-control my-1',
                                                    'type': 'date',
                                                    'style': 'background-color:rgba(255, 255, 255, 0.75);border:2px solid rgba(0, 0, 0, 0.1)'})
        } 
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Get the logged-in user
        super(UserProfile_Form, self).__init__(*args, **kwargs)
    
        if user and user.is_superuser:
            self.fields['house_name'].queryset = House_Name.objects.filter(name='Admin')  # Superuser sees only 'Admin'
        else:
            self.fields['house_name'].queryset = House_Name.objects.exclude(name='Admin')  # Regular users see all except 'Admin'


class Login_Form(forms.Form):

    username=forms.CharField(max_length=100,widget=forms.TextInput(attrs={'class':'form-control my-1',
                                                                            'placeholder':'Username . . .',
                                                                            'style':'background-color:rgba(255, 255, 255, 0.7)'}))
    password=forms.CharField(max_length=100,widget=forms.TextInput(attrs={'class':'form-control my-1',
                                                                           'placeholder':'Password . . .',
                                                                           'style':'background-color:rgba(255, 255, 255, 0.7)'}))



class Death_Record_Form(forms.ModelForm):
    class Meta:
        model = Death_Record
        fields = ['member', 'date_of_death', 'place_of_death', 'funeral_date', 
                  'funeral_location', 'burial_place', 'next_of_kin', 'contact_number']
        read_only_fields = ['created_at', 'updated_at', 'is_approved']

        widgets = {
            'member': forms.Select(attrs={'class': 'form-control my-1'}),
            'date_of_death': forms.DateInput(attrs={'class': 'form-control my-1', 'type': 'date'}),
            'funeral_date': forms.DateInput(attrs={'class': 'form-control my-1', 'type': 'date'}),
            'place_of_death': forms.TextInput(attrs={'class': 'form-control my-1', 'placeholder': 'Enter place of death . . .'}),
            'funeral_location': forms.TextInput(attrs={'class': 'form-control my-1', 'placeholder': 'Enter funeral location . . .'}),
            'burial_place': forms.TextInput(attrs={'class': 'form-control my-1', 'placeholder': 'Enter burial place . . .'}),
            'next_of_kin': forms.TextInput(attrs={'class': 'form-control my-1', 'placeholder': 'Enter next of kin . . .'}),
            'contact_number': forms.NumberInput(attrs={'class': 'form-control my-1', 'placeholder': 'Enter contact number . . .'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Extract user from kwargs
        super().__init__(*args, **kwargs)

        if user:
            try:
                user_profile = UserProfile_Model.objects.get(user=user)
                house_name = user_profile.house_name  # Get the house name
                # Filter out members who belong to the same house name
                self.fields['member'].queryset = get_user_model().objects.filter(
                    userprofile_model__house_name=house_name,  # Access UserProfile_Model via reverse relation
                    is_superuser=False
                ).exclude(id=user.id)  # Exclude the logged-in user
            except UserProfile_Model.DoesNotExist:
                self.fields['member'].queryset = get_user_model().objects.none()  # If no profile, show empty queryset


class Baptism_Record_Form(forms.ModelForm):
    class Meta:
        model = Baptism_Record
        fields = ['member', 'date_of_baptism', 'father_name', 'mother_name']

        widgets = {
            'member': forms.Select(attrs={'class': 'form-control my-1'}),
            'date_of_baptism': forms.DateInput(attrs={'class': 'form-control my-1', 'type': 'date'}),
            'father_name': forms.TextInput(attrs={'class': 'form-control my-1', 'placeholder': 'Enter father name . . .'}),
            'mother_name': forms.TextInput(attrs={'class': 'form-control my-1', 'placeholder': 'Enter mother name . . .'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
        if user:
            self.fields['member'].queryset = get_user_model().objects.none()
            try:
                user_profile = UserProfile_Model.objects.get(user=user)
                house_name = user_profile.house_name
                
                #  Use the correct related name (userprofile_model)
                self.fields['member'].queryset = get_user_model().objects.filter(
                    userprofile_model__house_name=house_name, is_superuser=False
                ).exclude(id=user.id)
            except UserProfile_Model.DoesNotExist:
                pass

class Auditorium_Form(forms.ModelForm):
    class Meta:
        model=Auditorium
        fields=['name']

        widgets={
            'name':forms.TextInput(attrs={'class':'form-control',
                                              'placeholder': 'Auditorium Name . . .'})
        }

class Marriage_Record_Form(forms.ModelForm):
    class Meta:
        model = Marriage_Record
        exclude = ['user', 'created_at', 'updated_at', 'is_approved']
        widgets = {
            'groom_name': forms.TextInput(attrs={'class': 'form-control'}),
            'groom_family_name': forms.TextInput(attrs={'class': 'form-control'}),
            'groom_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'groom_phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'groom_church_name': forms.TextInput(attrs={'class': 'form-control'}),
            'groom_father_name': forms.TextInput(attrs={'class': 'form-control'}),
            'groom_mother_name': forms.TextInput(attrs={'class': 'form-control'}),
            'groom_date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),

            'bride_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bride_family_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bride_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'bride_phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'bride_church_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bride_father_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bride_mother_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bride_date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),

            'marriage_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'held_at': forms.Select(attrs={'class': 'form-control'}),
        }


class Donation_Form(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ['name', 'amount']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter donation name'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter amount'}),
        }


class House_Donation_Form(forms.ModelForm):
    class Meta:
        model = House_Donation
        # fields = ['donation', 'paid_amount']
        fields = ['paid_amount']
        widgets = {
            # 'donation': forms.Select(attrs={'class': 'form-control'}),
            'paid_amount': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class Event_Form(forms.ModelForm):
    class Meta:
        model=Event
        fields=['hall','event_name','description','date']
        widgets = {
            'hall': forms.Select(attrs={'class': 'form-control'}),
            'event_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
        }


class EventFilterForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=True
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=True
    )