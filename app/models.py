from django.db import models

from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save


class House_Name(models.Model):

    name=models.CharField(max_length=100)
    
    def __str__(self):
         return self.name


class UserProfile_Model(models.Model):

    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Others', 'Others'),
    ]
    
    ROLE_CHOICES = [
        ('Member', 'Member'),
        ('Staff', 'Staff'),
        ('Youth', 'Youth'),
        ('Committee Member', 'Committee Member'),
        ('Choir', 'Choir'),
    ]

    name=models.CharField(max_length=100,null=True)

    house_name=models.ForeignKey(House_Name,on_delete=models.CASCADE,null=True,blank=True)

    address=models.TextField(null=True)

    age=models.PositiveIntegerField(null=True)

    email=models.EmailField(null=True)

    gender=models.CharField(max_length=100,choices=GENDER_CHOICES,null=True)
    
    profile_picture=models.FileField(upload_to='images',null=True,blank=True)

    phone_number=models.PositiveIntegerField(null=True)

    role=models.CharField(max_length=100,choices=ROLE_CHOICES,null=True)

    user=models.OneToOneField(User,on_delete=models.CASCADE)

    created_date=models.DateField(auto_now_add=True)  

    updated_date=models.DateField(auto_now=True)

    is_active=models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
@receiver(post_save,sender=User)
def create_profile(sender,instance,created,**kwargs):
        if created:      
            UserProfile_Model.objects.create(user=instance)