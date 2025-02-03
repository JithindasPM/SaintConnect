from django import forms

from app.models import User
from app.models import UserProfile_Model
from app.models import House_Name


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
        fields=['name','house_name','address','age','email','gender','profile_picture','phone_number','role']
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
        } 


class Login_Form(forms.Form):

    username=forms.CharField(max_length=100,widget=forms.TextInput(attrs={'class':'form-control my-1',
                                                                            'placeholder':'Username . . .',
                                                                            'style':'background-color:rgba(255, 255, 255, 0.7)'}))
    password=forms.CharField(max_length=100,widget=forms.TextInput(attrs={'class':'form-control my-1',
                                                                           'placeholder':'Password . . .',
                                                                           'style':'background-color:rgba(255, 255, 255, 0.7)'}))