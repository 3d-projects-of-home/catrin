from django.contrib import admin
from catrinmodel.models import Order
from catrinmodel.models import caterer
from catrinmodel.models import Address
from catrinmodel.models import Payment
from catrinmodel.models import Food
from catrinmodel.models import CatarerFood,MenuCatagory

class CatrerAdmin(admin.ModelAdmin):
    list_display=('id','user_id','caterer_name','description','image','starting_price','street','city','state','zip_code','country','latitude','longitude','phone_number','deliverable_area','delivery_charge','free_delivery_till_km','gst_for_food','max_order_night','max_order_day','type','gstin_number','advance_percentage')
# Register your models here.

admin.site.register(caterer,CatrerAdmin)

class AddressAdmin(admin.ModelAdmin):
    list_display=('user_id','street','city','state')
# Register your models here.

admin.site.register(Address,AddressAdmin)

class FoodAdmin(admin.ModelAdmin):
    list_display=('id','name','type_food','menu_catagory','food_image')
# Register your models here.

admin.site.register(Food,FoodAdmin)

class CatarerFoodAdmin(admin.ModelAdmin):
    list_display=()
# Register your models here.

admin.site.register(CatarerFood,CatarerFoodAdmin)

class OrderAdmin(admin.ModelAdmin):
    list_display=()
# Register your models here.

admin.site.register(Order,OrderAdmin)

class PaymentAdmin(admin.ModelAdmin):
    list_display=()
# Register your models here.

admin.site.register(Payment,PaymentAdmin)

class MenuCatagoryAdmin(admin.ModelAdmin):
    list_display=()
# Register your models here.

admin.site.register(MenuCatagory,MenuCatagoryAdmin)

