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
        return render(request, 'mindex.html')
    elif 'wid' in request.session:
        data = request.session['wid']
        return render(request,'workindex.html')
    elif 'aid' in request.session:
        data = request.session['aid']
        data3 = register.objects.filter(username=data)
        num_of_user = register.objects.filter(usertype='vehicleOwner').count()
        num_of_owner = register.objects.filter(usertype='mechanicOwner').count()
        num_of_worker = worker.objects.all().count()
        
        return render(request, 'admin.html',{'nuser':num_of_user,'nowner':num_of_owner,'nwork':num_of_worker})
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
        

def book_mechanic(request):
    if request.method == 'POST':
        if 'uid' in request.session:
            uname = request.session['uid']
            
            try:
                user = register.objects.get(username=uname)
            except register.DoesNotExist:
                return HttpResponse('User does not exist', status=400)
            
            vehicle_type = request.POST.get('vehicle_type')
            issue = request.POST.get('issue')
            location = request.POST.get('location')  # Location as 'lat,lng'
            
            if vehicle_type and issue and location:
                try:
                    lati, longi = map(float, location.split(','))
                except ValueError:
                    return HttpResponse('Invalid location format', status=400)
                
                # Create and save booking
                booking = Booking(
                    user=user,
                    vehicle_type=vehicle_type,
                    issue=issue,
                    latitude=lati,
                    longitude=longi
                )
                booking.save()
                return render(request,'bookin_success.html')
            else:
                return HttpResponse('Missing required data', status=400)
        else:
            return HttpResponse('User not logged in', status=403)
    
    # Render the form for GET requests
    return render(request, 'book_mechanic.html')



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
            pin = request.POST.get('pin')
            if len(adhar) != 12 or not re.match(r'^\d{12}$', adhar):
                 return HttpResponse(f'<script>alert("Enter valid adhar number"); window.history.back();</script>')
             
            if len(phone) != 10 or not re.match(r'^\d{10}$', phone):
                 return HttpResponse(f'<script>alert("Enter valid phone number"); window.history.back();</script>')

            try:
                
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
                    
                return HttpResponse("Certificate issued successfully.")
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
        users = register.objects.get(username=user_id)
        shopname = shopdetails.objects.get(username=users)
        data = service.objects.filter(shop=shopname)
        return render(request,'ownerservice.html',{'data':data})
    return render(request,'login.html')


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

        return render(request,'serupsucc.html')  # Redirect to the detail page or another page after update

    return render(request, 'update_service.html', {'service': service})
def mind(request):
    return render(request,'mindex.html')
def cerdown(request,):
    if 'mid' in request.session:
        user_id = request.session['mid']
        user = register.objects.get(username=user_id)
        shopname = shopdetails.objects.get(username=user)

        try:
            # Fetch the certificate for the given id and ensure it belongs to the user's shop
            certificate = Certificate.objects.get( shop=shopname)
        except Certificate.DoesNotExist:
            raise Http404("Certificate not found")

        # Serve the certificate file
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
        payment_id = request.GET.get('payment_id')  # Assuming you're using GET to capture payment_id
        username = request.session.get('sid')  # Retrieve username from session
        
        if username:
            # Find the corresponding service based on your logic
            # Assuming you pass the service ID when redirecting to the payment page
            service_id = request.GET.get('service_id')  # Capture the service ID
            services = service.objects.get(id=service_id)  # Fetch the service
            
            amount = service.cash * 100  # Convert to paisa, as Razorpay requires amount in the smallest unit
            
            # Initialize Razorpay client
            client = razorpay.Client(auth=("rzp_test_25QMSu2wWe3zbI", "oczP6DqWLp1biAN7GHWQjE4d"))
            try:
                # Create an order in Razorpay
                payment = client.order.create({
                    'amount': amount,
                    'currency': 'INR',
                    'payment_capture': '1'
                })
                order_id = payment['id']

                # Save payment details to your database
               

                # Redirect to success page or render payment confirmation
                return render(request, "index.html", {'payment_id': payment['id']})

            except Exception as e:
                return HttpResponse(f"Error occurred: {str(e)}")
                
        else:
            return HttpResponse('<script>alert("You need to login first"); window.location.href = "/";</script>')

    return HttpResponse('<script>alert("Invalid request method."); window.location.href = "/";</script>')