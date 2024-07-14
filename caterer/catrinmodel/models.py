from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings
#User=get_user_model()

# Create your models here.

class caterer(models.Model):
    user_id=models.ForeignKey(User,on_delete=models.CASCADE,blank=False,null=False)
    caterer_name=models.CharField(max_length=100)
    description=models.TextField()
    image=models.FileField(upload_to="caterer/",max_length=250,null=True,default=None)
    starting_price=models.DecimalField(max_digits=10,decimal_places=2)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    country = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=11, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=6, null=True, blank=True)
    phone_number=PhoneNumberField(region='IN')
    deliverable_area = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    free_delivery_till_km = models.DecimalField(max_digits=5, decimal_places=2,default=0)
    gst_for_food = models.DecimalField(max_digits=5, decimal_places=2,default=0)
    max_order_night = models.IntegerField(default=0)
    max_order_day =  models.IntegerField(default=0)
    TYPE_CHOICES = [
        ('veg', 'Vegetarian'),
        ('non-veg', 'Non-Vegetarian'),
        ('both', 'Both'),
    ]
    type = models.CharField(max_length=7, choices=TYPE_CHOICES)
    gstin_number = models.CharField(max_length=15)
    advance_percentage=models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.caterer_name

# If you don't have an Address model, you can create it like this:
class Address(models.Model):
    user_id=models.ForeignKey(User,on_delete=models.CASCADE,blank=False,null=False)
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    phone_number=PhoneNumberField(region='IN')
    latitude = models.DecimalField(max_digits=11, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=6, null=True, blank=True)


    def __str__(self):
        return f"{self.street}, {self.city}, {self.state}, {self.country}"

class Food(models.Model):
    name=models.CharField(max_length=20,unique=True)
    TYPE_CHOICES = [
        ('veg', 'Vegetarian'),
        ('non-veg', 'Non-Vegetarian'),
        ('both','For Both Veg and NonVeg')
    ]
    type_food = models.CharField(max_length=7, choices=TYPE_CHOICES)
    TYPE_CHOICES_ANOTHER=[
        ('juice','Juice'),
        ('Starter','Veg Starter'),
        ('NStarter','Non-Veg Starter'),
        ('Vmain','Veg Main Course'),
        ('Nmain','Non-Veg Main Course'),
        ('BRD','Veg Bread,Rice,Noodles'),
        ('NBRD','Non-Veg Bread,Rice,Noodles'),
        ('dessert','Dessert'),
    ]
    menu_catagory = models.CharField(max_length=50, choices=TYPE_CHOICES_ANOTHER)
    food_image=models.FileField(upload_to="food/",max_length=250,null=True,default=None)

class CatarerFood(models.Model):
    user_id=models.ForeignKey(User,on_delete=models.CASCADE,blank=False,null=False)
    food_id=models.ForeignKey('Food',on_delete=models.CASCADE,blank=False,null=False)
    extra_cost=models.DecimalField(max_digits=5, decimal_places=2,default=0)

class Payment(models.Model):
    user_id=models.ForeignKey(User,on_delete=models.CASCADE,blank=False,null=False,related_name='payments_as_user')
    caterer_id=models.ForeignKey(User,on_delete=models.CASCADE,blank=False,null=False,related_name='payments_as_caterer')
    bank_name=models.CharField(max_length=50)
    accountno=models.CharField(max_length=50)
    ifsc_code=models.CharField(max_length=50)
    bank_type=models.CharField(max_length=50)
    branch=models.CharField(max_length=50)
    paid_time=models.DateTimeField()

class Order(models.Model):
    user_id=models.ForeignKey(User,on_delete=models.CASCADE,blank=False,null=False,related_name='orders_as_user')
    caterer_id=models.ForeignKey(User,on_delete=models.CASCADE,blank=False,null=False,related_name='orders_as_caterer')
    ordered_time=models.CharField(max_length=100)
    ordered_food_list=models.TextField()
    TYPE_CHOICES = [
        ('day', 'Day'),
        ('night','Night'),
    ]
    order_day = models.CharField(max_length=7, choices=TYPE_CHOICES)
    delivery_date=models.CharField(max_length=100)
    delivery_time=models.CharField(max_length=100)
    delivery_address=models.TextField()
    phone_number=models.CharField(max_length=20)
    function_name=models.CharField(max_length=100)
    food_amount=models.DecimalField(max_digits=10, decimal_places=2)
    gstin=models.DecimalField(max_digits=10, decimal_places=2,default=0)
    total_price=models.DecimalField(max_digits=10, decimal_places=2)
    delivery_charge=models.DecimalField(max_digits=10, decimal_places=2)
    total_member_veg=models.IntegerField()
    total_member_nonveg=models.IntegerField()
    total_paid=models.DecimalField(max_digits=10, decimal_places=2)
    note=models.TextField()

class MenuCatagory(models.Model):
    caterer_id=models.ForeignKey(User,on_delete=models.CASCADE,blank=False,null=False)
    juice=models.DecimalField(max_digits=10, decimal_places=2)
    veg_starters_cost=models.DecimalField(max_digits=10, decimal_places=2)
    nonveg_starters_cost=models.DecimalField(max_digits=10, decimal_places=2)
    veg_main_cost=models.DecimalField(max_digits=10, decimal_places=2)
    nonveg_main_cost=models.DecimalField(max_digits=10, decimal_places=2)
    veg_bread_rice_noodle_cost=models.DecimalField(max_digits=10, decimal_places=2)
    nonveg_bread_rice_noodle_cost=models.DecimalField(max_digits=10, decimal_places=2)
    dessert_cost=models.DecimalField(max_digits=10, decimal_places=2)
