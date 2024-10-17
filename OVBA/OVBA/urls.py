"""
URL configuration for OVBA project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from vehicle import views
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.first),
    path('trylog',views.second),
    path('reg',views.Register),
    path('log',views.Login),
    path('forgetpass',views.openforget),
    path('changepass',views.change_password),
    path('profile',views.profile),
    path('sreg',views.openshopreg),
    path('shopreg',views.shopreg),
    path('vreq',views.shoprequest),
    path('afreq',views.afterorder),
    path('book',views.book),
    path('book_mechanic/', views.book_mechanic, name='book_mechanic'),
    path('finalize_booking/', views.finalize_booking, name='finalize_booking'),
    path('back',views.afterbook),
    path('adreq',views.openrequest),
    path('accept_shop/', views.accept_shop, name='accept_shop'),
    path('reject_shop/', views.reject_shop, name='reject_shop'),
    path('aduser',views.view_user),
    path('adowner',views.view_mech),
    path('adwork',views.view_work),
    path('add',views.add_workeropen),
    path('addworker',views.addworker),
    path('vwork',views.viewworker),
    path('promech',views.mechpro),
    path('upro',views.upro),
    path('sout',views.logout),
    path('remove/<int:worker_id>/', views.remove_worker, name='remove_worker'),
    path('afdele',views.aftredele),
    path('remove_mech/<int:mech_id>/',views.remove_mech, name='remove_mech'),
    path('remove_user/<int:user_id>/',views.remove_user, name='remove_user'),
    path('cer',views.opencer),
    path('iscert', views.issue_certificate_view, name='issue_certificate'),
    path('serv',views.openserv),
    path('bookserv',views.book_service),
    path('req',views.service_list),
    path('owserv',views.ownerserv),
    path('service/<int:id>/', views.service_detail, name='service_detail'),
    path('update_service/<int:id>/', views.update_service, name='update_service'),
    path('home',views.mind),
    path('dcer',views.cerdown),
    path('wrprf',views.workpro),
    path('success',views.payment),
    path('sersu',views.sersuc),
    path('comp',views.complaintopen),
    path('complaint',views.submit_complaint),
    path('adcomp',views.openadvcomp),
    path('send-warning-sms/', views.send_warning_sms, name='send_warning_sms'),
    path('shops/delete/<int:shop_id>/', views.delete_shop, name='delete_shop'),
    path('wrreq',views.view_requests),
    path('breq',views.userbookreqopen),
    path('handle_request/', views.handle_request, name='handle_request'),
    path('rate_worker', views.rate_worker),
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
]

if settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)