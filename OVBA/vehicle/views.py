from django.http import HttpRequest,HttpResponse,HttpResponseBadRequest
from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from django.http import JsonResponse
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import re
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Frame, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import black
from reportlab.pdfgen import canvas
from django.utils import timezone
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.conf import settings
import os
from django.http import HttpResponse, Http404
import razorpay
from collections import Counter
from twilio.rest import Client
import json
import requests
import math
from geopy.geocoders import Nominatim



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
        elif  worker.objects.filter(username=Uname , password=Pass):
                    request.session['wid'] = Uname
                    return redirect(profile)
           
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
        user = register.objects.get(username=data)
        return render(request, 'mindex.html',{'data':user})
    elif 'wid' in request.session:
        data = request.session['wid']
        user = worker.objects.get(username=data)
        return render(request,'workindex.html',{'data':user})
    elif 'aid' in request.session:
        data = request.session['aid']
        data3 = register.objects.filter(username=data)

        num_of_user = register.objects.filter(usertype='vehicleOwner').count()
        num_of_owner = register.objects.filter(usertype='mechanicOwner').count()
        num_of_worker = worker.objects.all().count()
        
        vehicle_owner_count = register.objects.filter(usertype='vehicleOwner').count()
        mechanical_owner_count = register.objects.filter(usertype='mechanicOwner').count()
        
        Shops = shopdetails.objects.all().count()
        
        shopreq = shopdetails.objects.all()
        
        comp = complaint.objects.all()

        return render(request, 'admin.html', {
            'nuser': num_of_user,
            'nowner': num_of_owner,
            'nwork': num_of_worker,
            'vehicle_owner_count': vehicle_owner_count,
            'mechanical_owner_count': mechanical_owner_count,
            'shop':shopreq,
            'complaints':comp,
            'shopcount':Shops
        })
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
        
        if not re.match(r'^[a-zA-Z0-9]{6,15}$', lnumb):
            return HttpResponse('<script>alert("Invalid License Number."); window.history.back();</script>')
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
        
# Haversine formula to calculate distance between two points (lat/lng)
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Radius of the Earth in kilometers
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c  # Distance in kilometers


def book_mechanic(request):
    if request.method == 'POST':
        if 'uid' in request.session:
            uname = request.session['uid']

            try:
                user = register.objects.get(username=uname)
            except register.DoesNotExist:
                return JsonResponse({'error': 'User does not exist'}, status=400)

            vehicle_type = request.POST.get('vehicle_type')
            issue = request.POST.get('issue')
            location = request.POST.get('location')  # Expecting format 'lat,lng'

            if vehicle_type and issue and location:
                try:
                    lati, longi = map(float, location.split(','))
                except ValueError:
                    return JsonResponse({'error': 'Invalid location format'}, status=400)

                # Find workers specializing in the user's issue
                workers = worker.objects.filter(special=issue)

                if not workers.exists():
                    return JsonResponse({'error': 'No workers found for this issue'}, status=404)

                # Calculate the distance to each worker
                workers_with_distance = []
                for worker_instance in workers:
                    worker_latitude = worker_instance.latitude
                    worker_longitude = worker_instance.longitude

                    if worker_latitude is not None and worker_longitude is not None:
                        # Calculate distance using Haversine formula
                        distance = haversine(lati, longi, worker_latitude, worker_longitude)
                        
                        # Get the shopname from the shopdetails model based on worker's username
                        try:
                            shop = shopdetails.objects.get(username=worker_instance.user)
                            shop_name = shop.shopname
                        except shopdetails.DoesNotExist:
                            shop_name = 'Unknown Shop'

                        workers_with_distance.append((worker_instance, distance, shop_name))

                # Sort workers by distance (closest first)
                workers_with_distance.sort(key=lambda x: x[1])

                # Prepare worker data for frontend
                worker_list = []

                for work, distance, shop_name in workers_with_distance:
                    worker_details = {
                        'id': work.id,
                        'name': work.name,
                        'special': work.special,
                        'distance': distance,
                        'phone': work.phone,
                        'mail': work.mail,
                        'rating': work.rating,
                        'dist': work.district,
                        'shopname': shop_name, 
                    }
                    worker_list.append(worker_details)

                context = {
                    'workers': worker_list,
                    'vehicle_type': vehicle_type,
                    'issue': issue,
                    'latitude': lati,
                    'longitude': longi,
                    'user_id': user.id,
                }

                return render(request, 'select_worker.html', context)
            else:
                return JsonResponse({'error': 'Missing required data'}, status=400)
        else:
            return JsonResponse({'error': 'User not logged in'}, status=403)

    return render(request, 'index.html')

def finalize_booking(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        worker_id = request.POST.get('worker')
        vehicle_type = request.POST.get('vehicle_type')
        issue = request.POST.get('issue')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        if user_id and worker_id and vehicle_type and issue and latitude and longitude:
            try:
                latitude = float(latitude)
                longitude = float(longitude)
            except ValueError:
                return JsonResponse({'error': 'Invalid location values'}, status=400)

            user = get_object_or_404(register, id=user_id)
            worker_instance = get_object_or_404(worker, id=worker_id)  # Retrieve the Worker instance

            # Create and save the booking
            booking = Booking(
                user=user,
                worker=worker_instance,  # Use the actual Worker instance
                vehicle_type=vehicle_type,
                issue=issue,
                status='pending',
                latitude=latitude,
                longitude=longitude,
            )
            booking.save()

            # Twilio credentials (hardcoded or securely retrieved from environment variables)
            account_sid = 'ACf01e3a7d0721444522effabf8b8fa51a'  # Replace with your Twilio Account SID
            auth_token = '007bce032388b683a8f54842404b175f'  # Replace with your Twilio Auth Token
            twilio_phone_number = '+15738792764'  # Replace with your Twilio phone number
         
            # Initialize the Twilio client
            client = Client(account_sid, auth_token)

            # Send an SMS to the worker using Twilio
            worker_phone_number = '+91' + worker_instance.phone  # Assuming there's a phone_number field in the Worker model
            try:
                message = client.messages.create(
                    body=f"You have a new booking request for a {vehicle_type}. Issue: {issue}. Please review and accept/reject the request\n From RepairHub ✌️",
                    from_=twilio_phone_number,
                    to=worker_phone_number  # Send SMS to worker's registered phone number
                )
                sms_status = f'SMS sent successfully with SID {message.sid}'
            except Exception as e:
                sms_status = f'SMS sending failed: {str(e)}'

            return render(request,'booksucc.html')

    return JsonResponse({'error': 'Invalid request'}, status=400)

def afterbook(request):
    return render(request,'index.html')


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
        
      
        user = shop.username  
        owner_email = user.mail  
        
   
        send_mail(
            subject='Shop Request Accepted',
            message=f'The request for the shop "{shop.shopname}" has been accepted.\n\n'
                    f'User: {user.username}\n'
                    f'Phone: {user.phone}\n'
                    f'Address: {shop.place}, {shop.istate}\n'
                    f'Status: {shop.status}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[owner_email], 
            fail_silently=False,
        )
        
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
def reject_shop(request):
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        
        
        if not request_id:
            return JsonResponse({'status': 'error', 'message': 'No request_id provided'}, status=400)
   
        shop = get_object_or_404(shopdetails, id=request_id)
        
      
        user = shop.username  
        owner_email = user.mail  

    
        send_mail(
            subject='Shop Request Rejected',
            message=f'We regret to inform you that your request for the shop "{shop.shopname}" has been rejected.\n\n'
                    f'User: {user.username}\n'
                    f'Phone: {user.phone}\n'
                    f'Address: {shop.place}, {shop.istate}\n'
                    f'Status: {shop.status}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[owner_email], 
            fail_silently=False,
        )
        
      
        shop.delete()
        
    
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)



def view_user(request):
    data = register.objects.filter(usertype='vehicleOwner')
    return render(request,'viewuser.html',{'users':data})



def view_mech(request):
    data = register.objects.filter(usertype='mechanicOwner')
    return render(request,'viewmech.html',{'mech':data})

def view_work(request):
    data = worker.objects.all()
    return render(request,'viadminworker.html',{'worker':data})

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
    

def geocode_location(location_name):
    url = f'https://nominatim.openstreetmap.org/search?q={location_name}&format=json'
    response = requests.get(url)
    location_data = response.json()

    if location_data:
        latitude = location_data[0]['lat']
        longitude = location_data[0]['lon']
        return float(latitude), float(longitude)
    else:
        return None, None  # Handle case when location isn't found

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
            uname = request.POST.get('username')
            wpass = request.POST.get('pass')
            state = request.POST.get('state')
            district = request.POST.get('district')  # Capture district
            pin = request.POST.get('pin')

            if len(adhar) != 12 or not re.match(r'^\d{12}$', adhar):
                return HttpResponse('<script>alert("Enter valid Aadhar number."); window.history.back();</script>')
             
            if len(phone) != 10 or not re.match(r'^\d{10}$', phone):
                return HttpResponse('<script>alert("Enter valid phone number."); window.history.back();</script>')

            # Geocode the district to get latitude and longitude
            latitude, longitude = geocode_location(district)
            print(latitude,longitude)
            if latitude is None or longitude is None:
                return HttpResponse('<script>alert("Invalid location. Please try again."); window.history.back();</script>')

            try:
                # Save worker with latitude and longitude
                workers = worker.objects.create(
                    user=user,
                    name=name,
                    phone=phone,
                    mail=mail,
                    adhar=adhar,
                    special=special,
                    username=uname,
                    password=wpass,
                    state=state,
                    district=district,
                    rating = 0,
                    pin=pin,
                    latitude=latitude,  # Store latitude
                    longitude=longitude  # Store longitude
                )
                workers.save()

                return render(request, 'worksucc.html', {'data': workers})
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

def mechpro(request):
    if 'mid' in request.session:
        uname = request.session['mid']
      
        user = register.objects.filter(username=uname)
        return render(request,'mprofile.html',{'data':user})
       
    return render(request,'login.html')

def upro(request):
     if 'uid' in request.session:
        uname = request.session['uid']
      
        user = register.objects.filter(username=uname)
        return render(request,'uprofile.html',{'data':user})
       
     return render(request,'login.html')
    

def logout(request):
    if 'uid' in request.session:
        request.session.flush()
        return render(request,'login.html')
    elif 'mid' in request.session:
        request.session.flush()
        return render(request,'login.html')
    elif 'wid' in request.session:
        request.session.flush()
        return render(request,'login.html')
    elif 'aid' in request.session:
        request.session.flush()
        return render(request,'login.html')
        
def remove_worker(request, worker_id):
    workers = get_object_or_404(worker, id=worker_id)
    workers.delete()
    return render(request,'sudele.html')

def aftredele(reqest):
    return redirect(profile)

def remove_mech(request, mech_id):
    mech = get_object_or_404(register, id=mech_id)
    mech.delete()
    return render(request,'sudele.html')

def remove_user(request,user_id):
    user = get_object_or_404(register, id=user_id)
    user.delete()
    return render(request,'sudele.html')

def opencer(request):
    data = shopdetails.objects.all()
    return render(request,'certificate.html',{'data':data})

def issue_certificate_view(request):
    if request.method == 'POST':
        shop_id = request.POST.get('shop_id')
        if shop_id:
            try:
                shop = shopdetails.objects.get(id=shop_id)
                
                if not Certificate.objects.filter(shop=shop).exists():
                    buffer = BytesIO()

                    # Define the PDF document
                    doc = SimpleDocTemplate(buffer, pagesize=letter)
                    
                    # Define styles
                    styles = getSampleStyleSheet()
                    title_style = ParagraphStyle('Title', parent=styles['Title'], fontName='Helvetica-Bold', fontSize=24, alignment=1, spaceAfter=12)
                    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontName='Helvetica', fontSize=14, alignment=1, spaceAfter=12)
                    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=12, alignment=1)

                    # Content list
                    elements = []

                    # Add border
                    border_frame = Frame(0.75 * inch, 0.75 * inch, 6.0 * inch, 9.5 * inch, showBoundary=0)
                    
                    def add_border(canvas, doc):
                        canvas.saveState()
                        canvas.setStrokeColor(black)
                        canvas.setLineWidth(2)
                        canvas.rect(0.5 * inch, 0.5 * inch, 7.5 * inch, 10.0 * inch)
                        canvas.restoreState()
                    
                    # Add the border to the PDF
                    doc.build(elements, onFirstPage=add_border, onLaterPages=add_border)

                    # Add certificate content
                    elements.append(Paragraph("Certificate of Registration", title_style))
                    elements.append(Paragraph("This is to certify that", body_style))
                    elements.append(Paragraph(f"<b>{shop.shopname}</b><br/><br/>Located at {shop.place}, {shop.istate}<br/><br/>has been registered and is recognized as a valid entity.<br/><br/>Issued on: {timezone.now().strftime('%Y-%m-%d')}", body_style))
                    

                    # Build the PDF
                    doc.build(elements)

                    # Save PDF to buffer
                    buffer.seek(0)
                    file_content = ContentFile(buffer.read(), 'certificate.pdf')
                    Certificate.objects.create(shop=shop, file=file_content)
                return HttpResponse('<script>alert("Certificate issued successfully."); window.history.back();</script>')
            except shopdetails.DoesNotExist:
                return HttpResponse("Shop not found.")
    
    shops = shopdetails.objects.all()
    return render(request, 'certificate.html', {'data': shops})

def openserv(request):
    if 'uid' in request.session:
        uname = request.session['uid']
        user = register.objects.filter(username=uname)
        data = shopdetails.objects.all()
        return render(request, 'service.html',{'data':user,'shop':data})
    return render(request,'login.html')
        
@csrf_exempt
def book_service(request):
    if request.method == 'POST':
        # Extract data from the form
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        sh = request.POST.get('shop')
        vehicle = request.POST.get('vehicle')
        vehinum = request.POST.get('vnum')
        service_types = request.POST.getlist('service[]')
        other_service = request.POST.get('other_service', '').strip()
        Date = request.POST.get('date')
        Time = request.POST.get('time')
        
        if 'other' in service_types and other_service:
                service_types.append(other_service)
   
        print(name , email , phone , vehicle , service_types , Date , Time)

        # Validate the data
        if not (name and email and phone and vehicle and service_types and Date and Time):
            return HttpResponse('All fields are required.', status=400)

        # Validate phone number
        if not phone.isdigit() or len(phone) < 10:
            return HttpResponse('Invalid phone number.', status=400)

        try:
            # Fetch user from Register model
            user = register.objects.get(name=name)  # or use another identifier like username

            # Create and save the Service instance
            ser = service.objects.create(
                user=user,
                email=email,
                phone=phone,
                shop=sh,
                vehicle=vehicle,
                vehiclenum = vehinum,
                serv_type=', '.join(service_types),  # Store service types as a comma-separated string
                date=Date,
                time=Time,
                status='Pending',  # Default status
                cash=0
            )
            ser.save()

            # Send confirmation email
            send_mail(
                subject='Service Booking Confirmation',
                message=f'Thank you for booking our service.\n\nDetails:\nName: {name}\nEmail: {email}\nPhone: {phone}\nVehicle: {vehicle}\nServices: {", ".join(service_types)}\nDate: {Date}\nTime: {Time}\nStatus: Pending\nWe will inform further updates.',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],  # Send confirmation to the user
                fail_silently=False,
            )

            return render(request, 'index.html') 
        except register.DoesNotExist:
            return HttpResponse('User not found.', status=404)

        except Exception as e:
            return HttpResponse(f'Error processing request: {e}', status=500)

    return HttpResponse('Invalid request method.', status=405)

def service_list(request):
    if 'uid' in request.session:
        user_id = request.session['uid']
        users = register.objects.get(username=user_id)
        services = service.objects.filter(user=users)
        return render(request, 'serreq.html', {'services': services})
    return render(request,'login.html')

def ownerserv(request):
    if 'mid' in request.session:
        user_id = request.session['mid']
        try:
            users = register.objects.get(username=user_id)
        except register.DoesNotExist:
            return HttpResponse('<script>alert("User does not exist."); window.history.back();</script>')

        try:
            # Check if the shop exists for the user
            shopname = shopdetails.objects.get(username=users)
            data = service.objects.filter(shop=shopname)
            return render(request, 'ownerservice.html', {'data': data})
        except shopdetails.DoesNotExist:
            # Alert if the shop is removed
            return HttpResponse('<script>alert("Your shop has been removed."); window.history.back();</script>')

    return render(request, 'login.html')


def service_detail(request, id):
    service_instance = get_object_or_404(service, id=id)
    return render(request, 'update_service.html', {'service': service_instance})

def update_service(request, id):
    services = get_object_or_404(service, id=id)

    if request.method == 'POST':
        status = request.POST.get('status')
        cash = request.POST.get('cash')

        # Update service fields
        services.status = status
        services.cash = cash
        services.save()

        return render(request,'serupsucc.html') 

    return render(request, 'update_service.html', {'service': service})
def mind(request):
    return render(request,'mindex.html')
def cerdown(request,):
    if 'mid' in request.session:
        user_id = request.session['mid']
        user = register.objects.get(username=user_id)
        shopname = shopdetails.objects.get(username=user)

        try:
          
            certificate = Certificate.objects.get( shop=shopname)
        except Certificate.DoesNotExist:
            raise Http404("Certificate not found")

      
        if certificate.file:
            file_path = certificate.file.path
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    response = HttpResponse(f.read(), content_type='application/pdf')
                    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                    return response
            else:
                raise Http404("File not found")
        else:
            return HttpResponse("No file associated with this certificate.", status=404)
    else:
        return HttpResponse("Unauthorized", status=401)
    
def workpro(request):
    if 'wid' in request.session:
        name = request.session['wid']
        data = worker.objects.filter(username=name)
        return render(request,'woprofile.html',{'data':data})
    return render(request,'login.html')


def payment(request):
    if request.method in ['POST', 'GET']:
        payment_id = request.GET.get('payment_id')
        username = request.session.get('uid') 
        
        if username:
            # Capture the service ID
            service_id = request.GET.get('service_id')
            try:
              
                services = service.objects.get(id=service_id) 
                

                amount = services.cash * 100  
  
                client = razorpay.Client(auth=("rzp_test_25QMSu2wWe3zbI", "oczP6DqWLp1biAN7GHWQjE4d"))
                
                payment_order = client.order.create({
                    'amount': amount,  
                    'currency': 'INR',
                    'payment_capture': '1'
                })
                services.delete()
                order_id = payment_order['id']
                
                return render(request, "sersucc.html", {'payment_id': order_id})

            except service.DoesNotExist:
                return HttpResponse('<script>alert("Service not found."); window.location.href = "/";</script>')
            except Exception as e:
                return HttpResponse(f"Error occurred: {str(e)}")
                
        else:
            return HttpResponse('<script>alert("You need to login first."); window.location.href = "/";</script>')

    return HttpResponse('<script>alert("Invalid request method."); window.location.href = "/";</script>')


def sersuc(request):
    return render(request,'index.html')

def complaintopen(request):
    shop = shopdetails.objects.all()
    return render(request,'complaint.html',{'shop':shop})

def submit_complaint(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            user_id = request.POST.get('user')
            rating = int(request.POST.get('rating'))
            complaint_desc = request.POST.get('complaint')
            compname = get_object_or_404(shopdetails, id=user_id)
            print('name',name,'userid',user_id,'rateing',rating,'copna',complaint_desc,'conam',compname)

            if 'uid' not in request.session:
                return JsonResponse({'error': 'User not logged in'}, status=401)

            user = request.session['uid']
            rating_category = 'good' if rating >= 7 else 'average' if rating >= 5 else 'bad'

            complaint_obj = complaint.objects.create(
                user=user,
                rating=rating_category,
                mechanic=compname,
                issue=complaint_desc
            )

            return JsonResponse({'message': 'Complaint submitted successfully!'})
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

def openadvcomp(request):
    shops_with_bad_reviews = []

    shops = shopdetails.objects.all()
    
    for shop in shops:
      
        bad_review_count = complaint.objects.filter(mechanic=shop.shopname, rating='bad').count()
        
 
        phone_number = shop.username.phone
       
        
      
        shops_with_bad_reviews.append({
            'shop': shop,
            'bad_review_count': bad_review_count,
            'phone_number': phone_number,
        })
    
    return render(request, 'adviewcomplaint.html', {'shops_with_bad_reviews': shops_with_bad_reviews})



def send_warning_sms(request):
    if request.method == 'POST':
        data = json.loads(request.body) 
        shop_id = data.get('shop_id')
        phone_number = data.get('phone_number')
        phone_number = '+91' + phone_number
        print(phone_number)

        try:
          
            shop = shopdetails.objects.get(id=shop_id)
        except shopdetails.DoesNotExist:
            return JsonResponse({'error': 'Shop not found'}, status=404)

  
        message_body = f"Warning: The shop {shop.shopname} has received a bad review! If this continue we will terminate your account\n From RepairHub 🥰"
        TWILIO_ACCOUNT_SID = 'ACf01e3a7d0721444522effabf8b8fa51a'
        TWILIO_AUTH_TOKEN = '007bce032388b683a8f54842404b175f'
        TWILIO_PHONE_NUMBER = '+15738792764'

        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    
        try:
            message = client.messages.create(
                body=message_body,
                from_=TWILIO_PHONE_NUMBER,
                to=phone_number
            )
            return JsonResponse({'message': 'SMS sent successfully!'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request'}, status=400)


def delete_shop(request, shop_id):
    try:
        shop = shopdetails.objects.get(id=shop_id)
        shop.delete()
        return JsonResponse({'message': 'Shop deleted successfully.'}, status=200)
    except shopdetails.DoesNotExist:
        return JsonResponse({'error': 'Shop not found.'}, status=404)



def view_requests(request):
    # Assume you already have the mechanic's requests stored
    if 'wid' in request.session:
        uname = request.session['wid']
        data = worker.objects.get(username=uname)
        
        # print(data)
        
        
    
        bookings = Booking.objects.filter(worker=data.name)
        
        # print('boo',bookings)
                                        

        # Use geopy to get the location name from lat, long
        geolocator = Nominatim(user_agent="vehicle_breakdown_service")
        
        # Prepare the booking data with actual addresses
        booking_details = []
        for booking in bookings:
            location = geolocator.reverse(f"{booking.latitude}, {booking.longitude}")
            address = location.address if location else "Location not found"
            # print(address)
            booking_details.append({
                'user':booking.user,
                'vehicle_type': booking.vehicle_type,
                'issue': booking.issue,
                'location': address,
                'status':booking.status,
                'id':booking.id
            })
        
        return render(request, 'view_requests.html', {'bookings': booking_details})
    
    
def userbookreqopen(request):
    if 'uid' in request.session:
        uname = request.session['uid']
        user_data = register.objects.get(username=uname)  
        bookings = Booking.objects.filter(user=user_data)  
        
       
        geolocator = Nominatim(user_agent="vehicle_app")

        
        booking_data = []
        for booking in bookings:
            location = geolocator.reverse((booking.latitude, booking.longitude), exactly_one=True)
            address = location.address if location else "Unknown location"
            booking_data.append({
                'worker': booking.worker,
                'vehicle_type': booking.vehicle_type,
                'issue': booking.issue,
                'address': address,  # Human-readable address
                'status': booking.status,
                'created_at': booking.created_at,
            })

        if booking_data:
            return render(request, 'userbookreqopen.html', {'bookings': booking_data})
        else:
            return render(request, 'userbookreqopen.html', {'message': 'No bookings found.'})
    return render(request, 'login.html')


def handle_request(request):
    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        action = request.POST.get('action')
   
        if booking_id:
            # Fetch booking or return 404 if not found
            booking = get_object_or_404(Booking, id=booking_id)
            
            # Get the user who made the booking (assuming the user field is linked to the register model)
            user_email = booking.user.mail
            user_name = booking.user.name
            
            # Update the booking status based on action
            if action == 'accept':
                booking.status = 'Accepted'
                subject = "Your Booking has been Accepted"
                message = f"Dear {user_name}, your booking with ID {booking.id} has been accepted."
            elif action == 'reject':
                booking.delete()
                subject = "Your Booking has been Rejected"
                message = f"Dear {user_name}, your booking with ID {booking_id} has been rejected."
                send_mail(subject, message, 'your_email@example.com', [user_email], fail_silently=False)
                return HttpResponse("Booking has been removed and an email has been sent to the user.")
            
            booking.save()
            
            # Send an email to the user
            send_mail(subject, message, 'your_email@example.com', [user_email], fail_silently=False)

            return HttpResponse(f"Booking {booking.id} has been {booking.status}, and an email has been sent to the user.")
    
    # In case the method is not POST, return an appropriate message
    return HttpResponse("Invalid request.")
@csrf_exempt
def rate_worker(request):
    if 'uid' in request.session:
        uname = request.session['uid']  # Fix typo here
        if request.method == 'POST':
            worker_name = request.POST.get('worker_name')
            iss = request.POST.get('issue')
            rating = request.POST.get('rating')
            
            try:
                # Create complaintwoker entry
                data = complaintwoker.objects.create(
                    user=uname,
                    rating=rating,
                    mechanic=worker_name,
                    issue=iss
                )
                data.save()

                # Update the worker's rating
                try:
                    workers = worker.objects.get(name=worker_name)  # Adjust the query if needed
                    if rating == 'good':
                        workers.rating += 1  # Increment rating
                    elif rating == 'bad':
                        workers.rating -= 1  # Decrement rating, if your logic requires this
                    workers.save()
                    
                    return JsonResponse({"message": f"Worker {worker_name} has been rated as {rating}."})
                
                except worker.DoesNotExist:
                    return JsonResponse({"error": f"No worker matches the name '{worker_name}'."}, status=404)

            except Exception as e:
                return JsonResponse({"error": str(e)}, status=500)

    else:
        return JsonResponse({"error": "Unauthorized: You must be logged in."}, status=403)

    return JsonResponse({"error": "Invalid request."}, status=400)

def wokercomplaint(request):
    if 'mid' in request.session:  # Check if the mechanic owner is logged in
        uname = request.session['mid']  # Retrieve the session data (username for mechanic owner)
        
        try:
            # Fetch the mechanic owner's user data from the register model
            user = register.objects.get(username=uname)
            
            # Get all workers that belong to the logged-in user
            workers = worker.objects.filter(user=user)
            
            # Get all complaints related to the workers of the logged-in user
            complaints = complaintwoker.objects.all()
            l = []
            for i in complaints:
                for j in workers:
                    if i.mechanic == j.name:
                        l.append(i)
                        

           
           
            return render(request, 'viewworkercomp.html', {'workers': workers, 'complaints': l})
        
        except register.DoesNotExist:
            return HttpResponse('<script>alert("User does not exist."); window.history.back();</script>')

    # If the mechanic owner is not logged in, redirect them to the login page
    return render(request, 'login.html')


@csrf_exempt
def send_warning_email(request):
    if request.method == 'POST':
        complaint_id = request.POST.get('worker_id')  # Assuming this is the complaint ID now
        print(f'Complaint ID received: {complaint_id}')

        try:
            # Fetch the complaint instance
            complaint_instance = complaintwoker.objects.get(id=int(complaint_id))
            print(f'Complaint instance found: {complaint_instance}')

            # Now get the associated worker using the mechanic name
            worker_instance = worker.objects.get(name=complaint_instance.mechanic)  # Match by name
            print(f'Worker instance found: {worker_instance.name}')  # Debugging line

            # Compose email details
            subject = 'Warning Notification'
            message = (
                f'Dear {worker_instance.name},\n\n'
                'This is a warning regarding your recent performance.\n\n'
                'Please review your conduct and ensure adherence to company policies.\n\n'
                'If you have any questions or require clarification, feel free to reach out.\n\n'
                'Best Regards,\n'
                'RepairHub Team'
            )
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [worker_instance.mail]  # Sending to the worker's email
            
            # Send the email
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=recipient_list,
                fail_silently=False,
            )

            return HttpResponse('<script>alert("Warning mail sent successfully."); window.history.back();</script>')
        
        except complaintwoker.DoesNotExist:
            print(f'Complaint with ID {complaint_id} does not exist.')  # Debugging line
            return JsonResponse({"error": "Complaint not found."}, status=404)
        except worker.DoesNotExist:
            print(f'Worker with name {complaint_instance.mechanic} does not exist.')  # Debugging line
            return JsonResponse({"error": "Worker not found."}, status=404)

    return JsonResponse({"error": "Invalid request."}, status=400)


def delete_worker(request):
    if request.method == 'POST':
        worker_id = request.POST['worker_id']
        workers = get_object_or_404(worker, id=worker_id)
        workers.delete()
        return HttpResponse('<script>alert("Worker removed successfully."); window.history.back();</script>')
    
    
def remove_shop(request):
    if 'mid' in request.session:
        uname = request.session['mid']
        
        if request.method == 'POST':
            shop_id = request.POST.get('shop_id')
            
            try:
                # Get the shop and delete it
                shop = shopdetails.objects.get(id=shop_id)
                shop.delete()

                # Get the user from the register model
                user = register.objects.get(username=uname)  # Assuming `uname` refers to the username field

                # Delete all workers associated with the user
                workers = worker.objects.filter(user=user)
                workers.delete()

                return HttpResponse('<script>alert("Shop and associated workers removed successfully."); window.history.back();</script>')
            
            except shopdetails.DoesNotExist:
                return HttpResponse('<script>alert("Shop not found."); window.history.back();</script>')
            
            except register.DoesNotExist:
                return HttpResponse('<script>alert("User not found."); window.history.back();</script>')

    return HttpResponse('<script>alert("Invalid session or request method."); window.history.back();</script>')