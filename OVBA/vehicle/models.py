from django.db import models

class register(models.Model):
    name = models.CharField(max_length=100)
    mail = models.EmailField()
    phone = models.IntegerField()
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    usertype = models.CharField(max_length=20)
    
    def __str__(self):
        return self.name
    
    
    
class shopdetails(models.Model):
    username = models.ForeignKey(register, on_delete=models.CASCADE)
    shopname = models.CharField(max_length=100)
    lnumber = models.CharField(max_length=20)
    place = models.CharField(max_length=50)
    istate = models.CharField(max_length=50)
    idate = models.DateField()
    edate = models.DateField()
    status = models.CharField(max_length=20)
    
    def __str__(self):
        return self.shopname
    
    
    
class service(models.Model):
    user = models.ForeignKey(register, on_delete=models.CASCADE)
    email = models.EmailField()
    phone = models.IntegerField()
    shop = models.CharField(max_length=20)
    vehicle = models.CharField(max_length=20)
    serv_type = models.CharField(max_length=20)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20)
    cash = models.IntegerField()
    
    
    
class Booking(models.Model):
    user = models.ForeignKey(register, on_delete=models.CASCADE)
    vehicle_type = models.CharField(max_length=100)
    issue = models.CharField(max_length=20)
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Booking by {self.user.username} on {self.created_at.strftime("%Y-%m-%d %H:%M:%S")}'
    
    
    
class worker(models.Model): 
    user = models.ForeignKey(register,on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    phone = models.IntegerField()
    mail = models.EmailField()
    adhar = models.IntegerField()
    special = models.CharField(max_length=20)
    username  = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    pin = models.IntegerField()
    def __str__(self):
        return self.name    
    
    
    
    
class Certificate(models.Model):
    shop = models.OneToOneField(shopdetails, on_delete=models.CASCADE)
    issued_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='certificates/')
    
    def __str__(self):
        return f"Certificate for {self.shop.shopname}"
    
    
class complaint(models.Model):
    user = models.ForeignKey(register, on_delete=models.CASCADE)
    rating = models.CharField(max_length=10)
    mechanic = models.CharField(max_length=20)
    issue = models.CharField(max_length=20)
    
    
    
    def __str__(self):
        return self.user  