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
    lnumber = models.IntegerField()
    place = models.CharField(max_length=50)
    istate = models.CharField(max_length=50)
    idate = models.DateField()
    edate = models.DateField()
    status = models.CharField(max_length=20)
    
    def __str__(self):
        return self.shopname
    
class Booking(models.Model):
    user = models.ForeignKey(register, on_delete=models.CASCADE)
    vehicle_type = models.CharField(max_length=100)
    issue = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.user
    
class worker(models.Model):
    user = models.ForeignKey(register,on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    phone = models.IntegerField()
    mail = models.EmailField()
    adhar = models.IntegerField()
    special = models.CharField(max_length=20)
    area  = models.CharField(max_length=20)
    city = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    pin = models.IntegerField()
    def __str__(self):
        return self.name    
    