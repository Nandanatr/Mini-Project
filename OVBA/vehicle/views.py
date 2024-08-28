from django.http import HttpRequest,HttpResponse,HttpResponseBadRequest
from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from django.http import JsonResponse
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import re
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt



def first(request):
    return render(request , 'guesthome.html')

def second(request):
    return render(request, 'login.html')

def Register(request):
    if request.method == "POST":
        Name = request.POST.get('name')
        mail = request.POST.get('mail')
        num = request.POST.get('numb')
        Uname = request.POST.get('uname')
        Pass = request.POST.get('pass')
        utype = request.POST.get('userType')

        error_messages = []

        if register.objects.filter(username=Uname).exists():
            error_messages.append("Username already exists.")
        if register.objects.filter(mail=mail).exists():
            error_messages.append("Email already exists.")
        if register.objects.filter(phone=num).exists(): 
            error_messages.append("Phone number already exists.")

        try:
            validate_email(mail)
        except ValidationError:
            error_messages.append("Invalid email format.")

        if len(num) != 10 or not num.isdigit():
            error_messages.append("Phone number must be 10 digits long.")

        if len(Pass) < 8:
            error_messages.append("Password must be at least 8 characters long.")
        if not re.search(r'[A-Za-z]', Pass):
            error_messages.append("Password must contain at least one letter.")
        if not re.search(r'[0-9]', Pass):
            error_messages.append("Password must contain at least one number.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', Pass):
            error_messages.append("Password must contain at least one special character.")

        if error_messages:
            for message in error_messages:
                messages.error(request, message)
            return render(request, 'login.html') 

        user = register.objects.create(
            name=Name,
            mail=mail,
            phone=num,
            username=Uname,
            password=Pass,  
            usertype=utype
        )
        user.save()

        messages.success(request, "Registration successful!")
        return render(request, 'login.html')

    return render(request, 'login.html')

def Login(request):
    if request.method == 'POST':
        Uname = request.POST.get('uname')
        Pass = request.POST.get('pass')
        adminuser = "admin"
        adminpass = "admin123"
        
        data = register.objects.filter(username=Uname, password=Pass)
        
        
        if data.filter(usertype = 'vehicleOwner'):
                    # return render(request, 'index.html')
                     request.session['uid'] = Uname
                     return redirect(profile)
        elif data.filter(usertype =  'mechanicOwner'):
                     request.session['mid'] = Uname
                     return redirect(profile)
                    # return render(request, 'mindex.html')
        elif Uname == adminuser and Pass == adminpass:
                     request.session['aid'] = Uname
                     return redirect(profile)
                    # return render(request, 'adminhome.html')
        else:       
            messages.error(request, 'Incorrect username or password')
           
    
    return render(request, 'login.html')

def profile(request):
    if 'uid' in request.session:
        data = request.session['uid']
        data1 = register.objects.filter(username=data)
        return render(request, 'index.html')
    elif 'mid' in request.session:
        data = request.session['mid']
        data2 = register.objects.filter(username=data)
        return render(request, 'mindex.html')
    elif 'aid' in request.session:
        data = request.session['aid']
        data3 = register.objects.filter(username=data)
        num_of_user = register.objects.filter(usertype='vehicleOwner').count()
        num_of_owner = register.objects.filter(usertype='mechanicOwner').count()
        
        return render(request, 'admin.html',{'nuser':num_of_user,'nowner':num_of_owner})
    else:
            return HttpResponse('<script>alert("Invalid Account"); window.history.back();</script>')
def openforget(request):
    return render(request, 'forget.html', {'step': '1'})

def change_password(request):
    if request.method == 'POST':
        step = request.POST.get('step', '1')  # Default to 1 if no step is provided

        if step == '1':
            phone_number = request.POST['num']

            # Validate phone number 
            phone_pattern = re.compile(r'^\d{10}$')
            if not phone_pattern.match(phone_number):
                return render(request, 'forget.html', {
                    'error_message': 'Invalid phone number. Please enter a valid 10-digit phone number.',
                    'step': '1'
                })

            # Check if the phone number is associated with any account
            if not register.objects.filter(phone=phone_number).exists():
                return render(request, 'forget.html', {
                    'error_message': 'Phone number not found. Please check and try again.',
                    'step': '1'
                })

            # Proceed to the next step
            return render(request, 'forget.html', {
                'success_message': 'Phone number verified. Please enter your new password.',
                'step': '2',
                'num': phone_number
            })

        elif step == '2':
            phone_number = request.POST['num']
            new_password = request.POST['new_password']
            confirm_password = request.POST['confirm_password']

            if new_password != confirm_password:
                return render(request, 'forget.html', {
                    'error_message': 'Passwords do not match. Please try again.',
                    'step': '2',
                    'num': phone_number
                })
                
            if len(new_password) < 8 or not any(c.isnumeric() for c in new_password) or not any(c.isalpha() for c in new_password) or not any(not c.isalnum() for c in new_password):
                return render(request, 'forget.html', {
                'error_message': 'Password must have a minimum of 8 characters, including at least one number, one letter, and one symbol.', 'step': '2',
            })
            # Update the user's password
            user = register.objects.get(phone=phone_number)
            user.password = new_password
            user.save()

            return render(request, 'login.html', {
                'success_message': 'Password has been reset successfully.'
            })

    return render(request, 'forget.html', {'step': '1'})
def openshopreg(request):
    if 'mid' in request.session:
        uname = request.session['mid']
        
        try:
           
            user = register.objects.get(username=uname)
        except register.DoesNotExist:
            return HttpResponse('<script>alert("Invalid user."); window.history.back();</script>')
        
      
        existing_shop = shopdetails.objects.filter(username=user).exists()

        if existing_shop:
           
            return HttpResponse('<script>alert("You can only add one shop per user."); window.history.back();</script>')

        data = register.objects.filter(username=uname)
        return render(request, 'oshopreg.html', {'data': data})
    
    else:
        return HttpResponse('<script>alert("Invalid Account"); window.history.back();</script>')
def shopreg(request):
    if 'mid' in request.session:
        username = request.session['mid']
        print('Session username:', username)
        
       
        spname = request.POST.get('sname')
        lnumb = request.POST.get('lnum')
        plac = request.POST.get('place')
        isstate = request.POST.get('istate')
        ldat_str = request.POST.get('ida')
        edat_str = request.POST.get('eda')
        try:
            user = get_object_or_404(register, username=username)
            print('User:', user)
        except register.DoesNotExist:
            return render(request, 'shopreg.html', {'message': 'User not found.'})


        registration = shopdetails.objects.create(
            username=user,
            shopname=spname,
            lnumber=lnumb,
            place=plac,
            istate=isstate,
            idate=ldat_str,
            edate=edat_str,
            status='pending' 
        )
        print('New registration:', registration) 
        return render(request, 'succ.html', {'registration': registration})

    else:
       
        return render(request, 'oshopreg.html', {'message': 'Something Went Wrong Please Try Again Later.'})
    
def afterorder(request):
    return render(request,'mindex.html')
            

def shoprequest(request):
    if 'mid' in request.session:
        uname = request.session['mid']
        # print('Session username:', username)
        user = register.objects.get(username=uname)
        print('username',user)
        details = shopdetails.objects.filter(username=user)
        print('details',details)
        return render(request,'srequest.html',{'details':details})
    else:
        return render(request, 'login.html') 
    
def book(request):
    return render(request,'book.html')
        

# def book_mechanic(request):
#     if request.method == 'POST':
#         vehicle_type = request.POST.get('vehicleType')
#         issue = request.POST.get('issue')
#         latitude = float(request.POST.get('latitude'))
#         longitude = float(request.POST.get('longitude'))
        
#         # Save the booking
#         Booking.objects.create(
#             user=request.user,
#             vehicle_type=vehicle_type,
#             issue=issue,
#             latitude=latitude,
#             longitude=longitude
#         )
        
#         return JsonResponse({'status': 'success'})
    
#     return JsonResponse({'status': 'error'}, status=400)

def openrequest(request):
    
    data = shopdetails.objects.all()
    return render(request,'request.html',{'shops':data})

@csrf_exempt
def accept_shop(request):
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        shop = get_object_or_404(shopdetails, id=request_id)
        shop.status = 'confirmed'
        shop.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
def reject_shop(request):
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        shop = get_object_or_404(shopdetails, id=request_id)
        shop.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)



def view_user(request):
    data = register.objects.filter(usertype='vehicleOwner')
    return render(request,'viewuser.html',{'users':data})



def view_mech(request):
    data = register.objects.filter(usertype='mechanicOwner')
    return render(request,'viewmech.html',{'mech':data})


def add_workeropen(request):
    if 'mid' in request.session:
        uname = request.session['mid']
        
        try:
            
            user = register.objects.get(username=uname)
        except register.DoesNotExist:
            return HttpResponse('<script>alert("Invalid user."); window.history.back();</script>')

        try:
           
            user_shop = shopdetails.objects.get(username=user)
        except shopdetails.DoesNotExist:
            return HttpResponse('<script>alert("Shop details not found."); window.history.back();</script>')

       
        if user_shop.status != 'confirmed':
            return HttpResponse('<script>alert("Your shop is not confirmed. You cannot access this page."); window.history.back();</script>')

       
        return render(request, 'addworker.html')
    
    else:
        return HttpResponse('<script>alert("Invalid Account"); window.history.back();</script>')
    

def addworker(request):
    if request.method == 'POST':
        if 'mid' in request.session:
            uname = request.session['mid']
            
            try:
                user = register.objects.get(username=uname)
            except register.DoesNotExist:
                return HttpResponse('<script>alert("Invalid user."); window.history.back();</script>')

 
            name = request.POST.get('name')
            phone = request.POST.get('phone')
            mail = request.POST.get('email')
            adhar = request.POST.get('adhar')
            special = request.POST.get('special')
            area = request.POST.get('area')
            city = request.POST.get('city')
            state = request.POST.get('state')
            pin = request.POST.get('pin')

            try:
                
                workers = worker.objects.create(
                    user=user,
                    name=name,
                    phone=phone,
                    mail=mail,
                    adhar=adhar,
                    special=special,
                    area=area,
                    city=city,
                    state=state,
                    pin=pin
                )
                workers.save()
                
               
                return render(request,'worksucc.html' ,{'data':workers}) 
            except Exception as e:
                return HttpResponse(f'<script>alert("An error occurred: {e}"); window.history.back();</script>')

    return render(request, 'mindex.html')

def viewworker(request):
    if 'mid' in request.session:
        uname = request.session['mid']
        try:
           
            user = register.objects.get(username=uname)
            
          
            workers = worker.objects.filter(user=user)
            
         
            return render(request, 'viewworker.html', {'workers': workers})
        
        except register.DoesNotExist:
            return HttpResponse('<script>alert("User does not exist."); window.history.back();</script>')
    
    # Handle cases where 'mid' is not in the session
    return render(request,'login.html')