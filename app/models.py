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

    date_of_birth=models.DateField(null=True,blank=True)

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

class Death_Record(models.Model):
    member = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="death_records")
    applied_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="applied_death_records", null=True, blank=True,)  # User who submitted the record
    date_of_death = models.DateField()
    place_of_death = models.CharField(max_length=255)
    funeral_date = models.DateField(blank=True, null=True)
    funeral_location = models.CharField(max_length=255, blank=True, null=True)
    burial_place = models.CharField(max_length=255, blank=True, null=True)
    next_of_kin = models.CharField(max_length=255, blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.member} - Applied by {self.applied_by}"
    
class Baptism_Record(models.Model):
    member = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="baptism_records")
    applied_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="applied_baptism_records", null=True, blank=True,)  # User who submitted the record
    date_of_baptism=models.DateField(null=True, blank=True)
    father_name=models.CharField(max_length=255)
    mother_name=models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.member} - Applied by {self.applied_by}"
    
class Auditorium(models.Model):
    name=models.CharField(max_length=100)

    def __str__(self):
        return self.name
    

class Marriage_Record(models.Model):
    groom_name = models.CharField(max_length=100, blank=True)
    groom_family_name = models.CharField(max_length=100, blank=True)
    groom_address = models.CharField(max_length=255, blank=True)
    groom_phone_number = models.CharField(max_length=15, blank=True)
    groom_church_name = models.CharField(max_length=100, blank=True)
    groom_father_name = models.CharField(max_length=100, blank=True)
    groom_mother_name = models.CharField(max_length=100, blank=True)
    groom_date_of_birth = models.DateField(null=True, blank=True)

    bride_name = models.CharField(max_length=100, blank=True)
    bride_family_name = models.CharField(max_length=100, blank=True)
    bride_address = models.CharField(max_length=255, blank=True)
    bride_phone_number = models.CharField(max_length=15, blank=True)
    bride_church_name = models.CharField(max_length=100, blank=True)
    bride_father_name = models.CharField(max_length=100, blank=True)
    bride_mother_name = models.CharField(max_length=100, blank=True)
    bride_date_of_birth = models.DateField(null=True, blank=True)

    marriage_date = models.DateField(null=True, blank=True)
    held_at = models.ForeignKey(Auditorium, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True, blank=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.groom_name} & {self.bride_name} - {self.marriage_date}"


class Donation(models.Model):
    name = models.CharField(max_length=200)
    amount = models.PositiveIntegerField() 
    created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True, blank=True)

    def __str__(self):
        return self.name
    
class House_Donation(models.Model):
    donation = models.ForeignKey(Donation, on_delete=models.CASCADE)
    house_name = models.ForeignKey(House_Name, on_delete=models.CASCADE)
    total_amount = models.PositiveIntegerField()
    paid_amount = models.PositiveIntegerField(default=0)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    status=models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True, blank=True)

class Event(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    hall=models.ForeignKey(Auditorium,on_delete=models.CASCADE)
    event_name=models.CharField(max_length=100,null=True,blank=True)
    description=models.TextField(null=True,blank=True)
    date=models.DateField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True, blank=True)
    is_approved = models.BooleanField(default=False)

    


