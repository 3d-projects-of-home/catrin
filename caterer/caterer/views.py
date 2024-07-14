from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
#from geopy.geocoders import Nominatim
#from geopy.distance import geodesic
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .forms import CreateUserForm,CatererForm,MenuCategoryForm,FoodForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
import secrets
import string
from django.utils import timezone
from datetime import timedelta
from datetime import datetime

import requests

from django.core.mail import send_mail,EmailMultiAlternatives
from django.template.loader import render_to_string
import pytz

# views.py

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from catrinmodel.models import caterer,Food,CatarerFood,MenuCatagory,Address,Order

def check(request):
    return redirect("home.html")

from django.db.models import Count, F

@csrf_exempt  #  handle CSRF tokens properly.
def my_view(request):
    if request.method == 'POST':
        data_json = json.loads(request.body)
        key1_value = data_json.get('key1', 'default_value1')
        key2_value = data_json.get('key2', 'default_value2')
        
        #location = geolocator.reverse((key1_value, key2_value))
        response_data = {'message': 'Data received', 'received_data': data_json}
        
        request.session['userlatitude']=key1_value
        request.session['userlongitude']=key2_value
        #print(key1_value,key2_value)
        #request.session['location']=location.address if location else "Location not found"
        return JsonResponse(response_data)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=400)

#haversine method -----------------------------------------------------------------------------------------
def haversine(lat1, lon1, lat2, lon2):
    from math import radians, cos, sin, sqrt, atan2

    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = dlon = lon2 - lon1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    r = 6371  # Radius of Earth in kilometers. Use 3956 for miles.
    return r * c


# OpenStreetMap's Nominatim API---------------------------------------------------------------

def get_coordinates(address):
    url = 'https://nominatim.openstreetmap.org/search'
    params = {
        'q': address,
        'format': 'json',
        'limit': 1
    }
    headers = {
        'User-Agent': 'YourAppName/1.0'
    }
    response = requests.get(url, params=params, headers=headers)

    # Check the response status code
    if response.status_code == 200:
        try:
            response_json = response.json()
            if response_json:
                latitude = response_json[0]['lat']
                longitude = response_json[0]['lon']
                print(latitude, longitude)
                return latitude, longitude
            else:
                return None, None
        except ValueError:
            print("Error decoding JSON:", response.text)
            return None, None
    else:
        print(f"Error fetching data: {response.status_code} - {response.text}")
        return None, None
    

#geolocator=Nominatim(user_agent="finder")

@login_required(login_url='login')
def check(request):
    data={}
    try:
        request.session['username']=str(request.user)
        userlongitude=float(request.session['userlongitude'])
        userlatitude=float(request.session['userlatitude'])
        is_caterer=caterer.objects.filter(user_id=request.user).first()
        if is_caterer:
            isCaterer=True
        else:
            isCaterer=False
        nearby_caterers=[]
        #user_address=request.session.get('location')
        for caterers in caterer.objects.all():
            print(caterers.longitude)
            print(caterers.latitude)
            #get_coordinates(','.join([caterers.city,caterers.state,caterers.zip_code]))
            distance=haversine(userlongitude,userlatitude,caterers.longitude,caterers.latitude)
            #distance=get_distance(','.join([caterers.city,caterers.state,caterers.zip_code]),user_address)
            print(distance)
            if distance <= caterers.deliverable_area:
                nearby_caterers.append(caterers)
        print(is_caterer)
        data={
            'isCaterer':isCaterer,
            'address':"user_address",
            'all_caterers':nearby_caterers,
        }
        
    except Exception as e:
        print(e)
        #return redirect('home')
    
    return render(request,'check.html',data)

'''def get_distance(caterer_loc,user_loc):
    user_location=geolocator.geocode("576101")

    user_area=(user_location.latitude,user_location.longitude)
    
    try:
        caterer_location=geolocator.geocode(caterer_loc)
    except:
        caterer_location=geolocator.geocode(caterer_loc[-6:])
    print("user area",user_loc)
    caterer_area=(caterer_location.latitude,caterer_location.longitude)
    return geodesic(user_area,caterer_area).miles'''


def registerPage(request):
    form=CreateUserForm()
    if request.method == 'POST':
        form=CreateUserForm(request.POST)
        if form.is_valid():
            user_email=request.POST.get('email')
            username=request.POST.get('username')
            if User.objects.filter(email=user_email).count() == 0:
            
                form_partial = form.save(commit=False)
                form_partial.is_active = False  # Mark user as inactive until verification
                form_partial.save()
                
                token_gerated=generate_verification_token()
                request.session['username']=username
                request.session['token']=token_gerated
                send_verification_email(user_email, token_gerated,request)
                return redirect("timer")
                
            else:
                messages.error(request,"already exist")
    context={
        'form':form
        }
    return render(request,'register.html',context)

def loginPage(request):
    try:
        del request.session['minute']
        del request.session['second']
    except:
        pass
    if request.method == 'POST':
        user_email=request.POST.get('email')
        password=request.POST.get('password')
        try:
            username=User.objects.filter(email=user_email).first()
            user=authenticate(request,username=username.username,password=password)
        except:
            user=None

        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.info(request,"Username or Password is Incorrect")
            return render(request,'login.html')
    context={}
    return render(request,'login.html',context)


def logoutUser(request):
    logout(request)
    return redirect('login')

def otpUser(request): 
    token_from_email = request.GET.get('token')
    time=request.GET.get('time')
    time=str(time).replace("@"," ")
    current_time=str(timezone.now())[:-6]
    started_time = datetime.strptime(time,"%Y-%m-%d %H:%M:%S.%f")
    try:
        token_original=request.session.get('token')
        if token_original == token_from_email:
            del request.session['token']
            username=request.session.get('username')
            if datetime.strptime(current_time,"%Y-%m-%d %H:%M:%S.%f")<=(started_time+timedelta(minutes=1)):
                update_active=User.objects.get(username=username)
                update_active.is_active = True
                update_active.save()
                messages.success(request,"Account is Created  "+username) 
                return redirect('login')    
    except Exception as e:
        print("otpuser exception"+e)
        pass
    delete_session_and_details(request)
    return redirect('register')

#######
def generate_verification_token():
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(64))

def send_verification_email(user_email, verification_token,request):
    username=request.session.get('username')
    name=User.objects.get(username=username).first_name
    utc_time=timezone.now()
    ist_time=utc_time.astimezone(pytz.timezone('Asia/Kolkata'))
    request.session['minute']=ist_time.minute
    request.session['second']=ist_time.second
    
    current_time=str(timezone.now())[:-6].replace(" ","@")
    verification_link = f"http://127.0.0.1:8000/otp?token={verification_token}&time={current_time}"
    
    subject = "Verify Your Email Address"
    message = render_to_string('verification_email.html', {'verification_link': verification_link,'name':name})
    
    try:
        msg=EmailMultiAlternatives(subject, message, 'devadigaakash717@gmail.com', [user_email])
        msg.content_subtype="html"
        msg.send()
    except Exception as e:
        print("verification exception"+e)
        messages.info(request,"email is Incorrect")
        return redirect('register')


def forgotUser(request):
    if request.method == 'POST':
        user_email=request.POST.get('email')
        password=request.POST.get('password')
        if User.objects.filter(email=user_email).exists():
            try:
                validate_password(password)
                updatePassword= User.objects.filter(email__exact=user_email).first()
                username=updatePassword.username
                updatePassword.set_password(password)
                updatePassword.is_active = False  # Mark user as inactive until verification
                updatePassword.save()
                token_gerated=generate_verification_token()
                request.session['username']=username
                request.session['token']=token_gerated
                send_verification_email(user_email, token_gerated,request)
                return redirect("timer")
            except ValidationError as e:
                messages.error(request,e)

        print('not exist')    
    return render(request,"forgotPas.html")

def timer(request):
    try:
        minute=int(request.session.get('minute'))
        second=int(request.session.get('second'))
        data={
            'minute':minute,
            'second':second,
        }
        return render(request,"timer.html",data)
    except Exception as e:
        delete_session_and_details(request)
    return render(request,"timer.html")

def delete_session_and_details(request):
    try:
        del request.session['minute']
        del request.session['second']
        del request.session['token']
    except:
        pass

def resend_link(request):
    try:
        token_gerated=generate_verification_token()
        username=request.session.get('username')
        token_gerated=generate_verification_token()
        request.session['token']=token_gerated
        user_email=User.objects.filter(username=username).first()
        send_verification_email(user_email.email, token_gerated,request)
        return redirect("timer")
    except Exception as e:
        print(e)
    return redirect("register")

@login_required(login_url='login')
def menu(request):
    
    catererUserId=request.session.get('catererId')
    user = get_object_or_404(User, username=catererUserId) #reffer to caterer

    excluded_ids=request.session.get('food_item', [])
    type_choices = Food.TYPE_CHOICES_ANOTHER
    if request.method == 'POST' and request.POST.get('add_to_order') == "submit":
        return redirect("delivery")
    if request.method == 'POST' and request.POST.get('add_item') == "add":
        food_list = request.POST.getlist('items')
        request.session['food_item'] += food_list
    food_list=set(request.session.get('food_item', []))
    request.session['food_item']=list(food_list)
    print(food_list)
    selected_items=Food.objects.filter(id__in=food_list)
    print(request.session.get('food_item', []))
    records = CatarerFood.objects.filter(user_id=user).exclude(food_id__in=excluded_ids)
    context = {'selected_items': selected_items,
               'record':records,
               'type':type_choices,
               }
    return render(request, 'food_menu.html', context)


def remove(request):
    food_list=[]
    if(request.method == 'GET'):
        item_to_remove=request.GET.get("delete")
        food_list = request.session.get('food_item', [])
        food_list.remove(item_to_remove)
        request.session['food_item'] = food_list
        print(item_to_remove)
        return redirect("menu")
    
@login_required(login_url='login')
def order(request):
    if(request.method == 'GET'):
        catererId=request.GET.get("caterer_id")
        caterer=request.GET.get("caterer")
        request.session['caterer'] = caterer
        request.session['catererId'] = catererId
    if(request.method == 'POST'):
        request.session['orderDate']=request.POST.get("orderDate")
        request.session['orderTime']=request.POST.get("orderTime")
        request.session['functionName']=request.POST.get("functionName")
        request.session['functionNonMember']=request.POST.get("functionNonMember")
        request.session['functionVegMember']=request.POST.get("functionVegMember")
        request.session['userZipCode']=request.POST.get("zip")
        return redirect("menu")
    context={}
    return render(request, 'order.html', context)

@login_required(login_url='login')
def delivery(request):
    catererUserId=request.session.get('catererId')
    catererId=request.session.get('caterer')
    username=request.session.get('username')
    caterer_user_id= get_object_or_404(User, username=catererUserId)
    user_id= get_object_or_404(User, username=username)
    caterer_zip_code=caterer.objects.filter(id=catererId).first()
    user_zip_code=request.session.get("userZipCode")
    food_list=request.session.get('food_item', [])
    selected_items=Food.objects.filter(id__in=food_list)
    ##extra cost
    #extra_cost_food=getExtraCost(selected_items)
    

    ####total amount for food
    
    totalAmountFood=int(getTotalAmount(request,selected_items,food_list,catererUserId)) #543
    

   
    ###########################
    print(caterer_zip_code.latitude,caterer_zip_code.longitude,float(request.session['userlongitude']),float(request.session['userlatitude']))
    total_distance=int(haversine(caterer_zip_code.longitude,caterer_zip_code.latitude,float(request.session['userlongitude']),float(request.session['userlatitude'])))  #146
    total_distance-=caterer_zip_code.free_delivery_till_km
    
    ### delivery cost
    delivery_cost=int(total_distance*caterer_zip_code.delivery_charge)
    if(delivery_cost<0):
        delivery_cost=0
    
     ###advance amount
    totalAmount=totalAmountFood+delivery_cost
    
    advanceAmount=int(totalAmount*(float(caterer_zip_code.advance_percentage)/100))
    
    
    #about delivery page address
    userAddress=Address.objects.filter(user_id=user_id.id).first()
    
    addressVal={}
    if userAddress:
        addressVal={
            "street":userAddress.street,
            "city":userAddress.city,
            "state":userAddress.state,
            "zip_code":userAddress.zip_code,
            "phone":userAddress.phone_number,
            "country":userAddress.country,

        }
    else:
        print(user_id.id)
########################################################################
    utc_time=timezone.now()
    ist_time=utc_time.astimezone(pytz.timezone('Asia/Kolkata'))
    if(request.method == 'POST'):
        
        address_val=request.POST.getlist("addr")
        phone=request.POST.get("phone")
        address=request.POST.getlist("address")
        paid=float(request.POST.get("amount"))
        note=request.POST.get("note")
        zipcode=request.POST.get("zip")
        address_val+=address
        if(request.session['userZipCode']==zipcode and int(paid) >= advanceAmount):
            delivery=Order(
            user_id=user_id,
            caterer_id=caterer_user_id,
            function_name=request.session['functionName'],
            food_amount=totalAmountFood,
            total_price=totalAmount,
            delivery_charge=delivery_cost,
            total_member_veg=int(request.session['functionVegMember']),
            total_member_nonveg=int(request.session['functionNonMember']),
            ordered_food_list=','.join(str(item) for item in food_list),
            delivery_date=request.session['orderDate'],
            delivery_time=request.session['orderTime'],
            delivery_address=','.join(str(item) for item in address_val),
            phone_number=phone,
            total_paid=paid,
            note=note,
            ordered_time=str(ist_time)
            )
            delivery.save()
            delete_order_details(request) #562
            return redirect("success")
        else:
            messages.error(request,"enter the same zipcode as entered before or advance amount should be equal or greater")

###############################################
    context={
        'address':addressVal,
        'selected_items':selected_items,
        'delivery_cost':delivery_cost,
        'totalAmountFood':totalAmountFood,
        'totalAmount':totalAmount,
        'advanceAmount':advanceAmount,
    }
    return render(request, 'delivery.html', context)


def get_category_counts(selected_items):
    category_counts = selected_items.values('menu_catagory').annotate(count=Count('menu_catagory'))
    return {item['menu_catagory']: item['count'] for item in category_counts}

def totalAmountForFood(request,selected_items,category_counts,catererId):
    catererId_id = User.objects.filter(username=catererId).first()
    menu_category = MenuCatagory.objects.filter(caterer_id=catererId_id.id).first()

    ##########################
    selected_food_ids = selected_items.values_list('id', flat=True)
    
    # Fetch all corresponding CatarerFood entries in one query
    caterer_foods = CatarerFood.objects.filter(food_id__in=selected_food_ids)
    # Create a dictionary for quick lookup
    caterer_food_dict = {cf.food_id_id: cf.extra_cost for cf in caterer_foods}

    veg_total = 0
    non_veg_total = 0
    both_total = 0

    for item in selected_items:
        print(item.name)
        extra_cost = caterer_food_dict.get(item.id, 0)
        print(extra_cost)
        if item.type_food == "veg":
            veg_total += extra_cost
        elif item.type_food == "non-veg":
            non_veg_total += extra_cost
        elif item.type_food == "both":
            both_total += extra_cost

    return (veg_total, non_veg_total, both_total)

    

    #############################
    

"""def getExtraCost(selected_items):
    total_extra=0
    for key in selected_items:
        cfood=CatarerFood.objects.filter(food_id=key).first()
        total_extra+=cfood.extra_cost
    return total_extra"""

def calc(request,vegfixedcost,nonvegfixedcost,bothfixedcost):
    totalVegMember=int(request.session.get('functionVegMember'))
    totalNonVegMember=int(request.session.get('functionNonMember'))
    print(totalVegMember,totalNonVegMember)
    totalMember=totalVegMember+totalNonVegMember
    totalVegAmount=totalVegMember*float(vegfixedcost)
    totalNonVegAmount=totalNonVegMember*float(nonvegfixedcost)
    totalBothAmount=totalMember*float(bothfixedcost)
    
    return totalVegAmount+totalNonVegAmount+totalBothAmount


def getTotalAmount(request,selected_items,food_list,catererUserId):
    items_to_divide=[]
    for item in selected_items:
        #if item.type_food == "both":
        items_to_divide.append(str(item.id))

    #items_to_divide = [item for item in food_list if item not in both_items_to_divide]
    
    #total_cost_food=Food.objects.filter(id__in=items_to_divide)
    total_cost_food=Food.objects.filter(id__in=items_to_divide)

    ####
    #category_counts_both= get_category_counts(total_cost_food_both)
    #print(total_cost_food_both)
    #vegfixedcostboth,nonvegfixedcostboth,bothvegfixedcostboth=totalAmountForFood(request,selected_items,category_counts_both,catererUserId)
    category_counts = get_category_counts(total_cost_food) #486
    vegfixedcost,nonvegfixedcost,bothvegfixedcost=totalAmountForFood(request,selected_items,category_counts,catererUserId)
    return calc(request,vegfixedcost,nonvegfixedcost,bothvegfixedcost) #490

def delete_order_details(request):
    del request.session['orderDate']
    del request.session['orderTime']
    del request.session['functionName']
    del request.session['functionNonMember']
    del request.session['functionVegMember']
    del request.session['userZipCode']
    del request.session['food_item']

@login_required(login_url='login')
def catererform(request):
    if request.method == 'POST':
        form = CatererForm(request.POST, request.FILES)
        
        if form.is_valid():
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zip_code = form.cleaned_data['zip_code']
            latitude,longitude=get_coordinates(','.join([city,state,zip_code]))
            caterer = form.save(commit=False)
            caterer.user_id = request.user  # Assign the current user
            caterer.latitude=float(latitude)
            caterer.longitude=float(longitude)
            caterer.save()
            return redirect('catererCatagory')  # Redirect to a success page
        else:
            print(form.errors)  # Print form errors for debugging
    else:
        form = CatererForm()

    return render(request, 'catererForm.html', {'form': form, 'user': request.user})

def success(request):
    return render(request, 'success.html')

@login_required(login_url='login')
def catererAdmin(request):
    return render(request, 'catererAdmin.html')

@login_required(login_url='login')
def catererMenu(request):
    
    excluded_ids=[]
    
    user = get_object_or_404(User, username=request.user) #reffer to caterer
    
    extract_food=CatarerFood.objects.filter(user_id_id=user.id)
    extract_food_ids = [str(item.food_id_id) for item in extract_food]
    excluded_session_ids=request.session.get('caterer_food_item', [])
    print("i38urhf")
    print(request.session.get('caterer_food_item', []))
    excluded_ids=extract_food_ids
    print(excluded_ids)
    type_choices = Food.TYPE_CHOICES_ANOTHER
    fixedCostDic=[]
    fixedCost = get_object_or_404(MenuCatagory, caterer_id=user.id)
    field = fixedCost._meta.get_fields()
    i=-2
    # Access the field by index
    for fields in field:
        print(i)
        field_name = fields.name
        if(i<0):
            i=i+1
            continue
    # Get the value of the field from the model instance
        field_value = getattr(fixedCost, field_name)

    # Print the value
        fixedCostDic.append((type_choices[i][0],type_choices[i][1],field_value))
        i=i+1
    #print(type_choices[0][1])
    print(fixedCostDic)

    if request.method == 'POST' and request.POST.get('add_to_order') == "submit":
        rate=request.POST.getlist('extrcost')
        food=request.POST.getlist('orderedFood')
        food_tt=Food.objects.filter(id__in=food)
        for i in range(len(rate)):
            catererFood=CatarerFood(
                user_id=user,
                food_id= food_tt[i],
                extra_cost=rate[i],
            )
            catererFood.save()
        del request.session['caterer_food_item']
        return redirect("success")
    if request.method == 'POST' and request.POST.get('add_item') == "add":
        food_list = request.POST.getlist('items')
        
        request.session['caterer_food_item'] += food_list



    food_list=set(request.session.get('caterer_food_item', []))
    
    request.session['caterer_food_item']=list(food_list)
    
    selected_items=Food.objects.filter(id__in=food_list)
    

    records = Food.objects.all().exclude(id__in=(excluded_ids+excluded_session_ids))
    context = {'selected_items': selected_items,
               'record':records,
               'type':fixedCostDic,
               }
    return render(request, 'catererMenu.html', context)

@login_required(login_url='login')
def catererRemove(request):
    food_list=[]
    if(request.method == 'GET'):
        item_to_remove=request.GET.get("delete")
        food_list = request.session.get('caterer_food_item', [])
        food_list.remove(item_to_remove)
        request.session['caterer_food_item'] = food_list
        
        return redirect("catererMenu")
    
@login_required(login_url='login')   
def orderDetails(request):
    caterer_user_id= get_object_or_404(User, username=request.user)
    orders = Order.objects.filter(caterer_id=caterer_user_id.id)
    if request.method == "GET":
        food_to_show=request.GET.get('show')
        if food_to_show:
            food= get_object_or_404(Order, id=food_to_show)
            food_string=food.ordered_food_list
            food_list=food_string.split(',')
            selected_items=Food.objects.filter(id__in=food_list)
            type_choices = Food.TYPE_CHOICES_ANOTHER
            
            return render(request, 'orderDetails.html',{'orders': orders,'selected_items':selected_items,'type':type_choices,})
    
    return render(request, 'orderDetails.html',{'orders': orders})

@login_required(login_url='login')
def catererCatagory(request):
    caterer_user_id= get_object_or_404(User, username=request.user)
    if request.method == 'POST':
        form = MenuCategoryForm(request.POST)
        if form.is_valid():
            menu_category = form.save(commit=False)
            menu_category.caterer_id =request.user 
            menu_category.save()
            return redirect('success')  # Redirect to a success page or desired URL
    else:
        form = MenuCategoryForm()
    return render(request, 'catererCatagory.html', {'form': form})

@login_required(login_url='login')
def foodForm(request):
    if request.method == 'POST':
        form = FoodForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('catererMenu')  # Redirect to a success page after saving
    else:
        form = FoodForm()
    return render(request, 'foodForm.html', {'form': form})


@login_required(login_url='login')   
def myOrder(request):
    user_id= get_object_or_404(User, username=request.user)
    orders = Order.objects.filter(user_id=user_id.id)
    if request.method == "GET":
        food_to_show=request.GET.get('show')
        if food_to_show:
            food= get_object_or_404(Order, id=food_to_show)
            food_string=food.ordered_food_list
            food_list=food_string.split(',')
            selected_items=Food.objects.filter(id__in=food_list)
            type_choices = Food.TYPE_CHOICES_ANOTHER
            
            return render(request, 'myOrder.html',{'orders': orders,'selected_items':selected_items,'type':type_choices,})
    
    return render(request, 'myOrder.html',{'orders': orders})