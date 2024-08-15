from django.http import HttpRequest,HttpResponse,HttpResponseBadRequest
from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from django.http import JsonResponse
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import re
from django.contrib.auth.hashers import make_password



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
        
        if data.exists():
            for i in data:
                if i.usertype == 'vehicleOwner':
                    return render(request, 'index.html')
                elif i.usertype == 'mechanicOwner':
                    return render(request, 'mindex.html')
                elif Uname == adminuser and Pass == adminpass:
                    return render(request, 'adminhome.html')
                
            messages.error(request, 'Incorrect username or password')
        else:
            messages.error(request, 'Incorrect username or password')
    
    return render(request, 'login.html')


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