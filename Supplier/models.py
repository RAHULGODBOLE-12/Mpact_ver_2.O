from django.db import models
from django.contrib.auth.models import User,Group
from django_pandas.managers import DataFrameManager
from Slate_CMT.templatetags.cmt_helper import *

# Create your models here.


class suppliers_detail_log(models.Model):
    modified_by=models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    modified_on=models.DateTimeField(auto_now_add=True,null=True)
    log=models.TextField(null=True)
    objects = DataFrameManager()
    class Meta:
        ordering = ['modified_on']
# def randomString(stringLength):
#     letters = string.ascii_letters
#     return ''.join(random.choice(letters) for i in range(stringLength))
class suppliers_detail(models.Model):
    Supplier_Name=models.CharField(max_length=255,null=True)
    Team=models.CharField(max_length=255,null=True)
    Distributor=models.CharField(max_length=255,null=True)
    Arista_Commodity_Manager=models.CharField(max_length=255,null=True)
    Commodity=models.CharField(max_length=255,null=True)
    Contact=models.CharField(max_length=255,null=True)
    Position=models.CharField(max_length=255,null=True)
    Direct =models.CharField(max_length=255,null=True)
    Mobile=models.CharField(max_length=255,null=True)
    Email=models.CharField(max_length=255,null=True)
    Comments=models.CharField(max_length=1000,null=True)
    password=models.CharField(max_length=255,null=True)
    user_model=models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    modified_on=models.DateTimeField(auto_now_add=True,null=True)
    modified_by=models.CharField(max_length=255,null=True)
    is_active=models.BooleanField(default=True)
    logger= models.ManyToManyField(suppliers_detail_log)
    User_created= models.ForeignKey(User,related_name='creator',on_delete=models.CASCADE,null=True)
    objects = DataFrameManager()

    def save(self,*args, **kwargs):
        print('saving...')
        ###Getting the  user with same email if or created one
        user,created=User.objects.get_or_create(username=self.Email,email=self.Email)
        password=None
        ####if the user is new set the essential details
        if created:
            user.first_name=self.Contact
            user.last_name=self.Position or ''
            password=randomString(8)
            password='iness123'
            user.set_password(password)
            user.groups.add(Group.objects.get(name='Suppliers/Distributors'))
            user.save()
        #else assign the user to user_model in supplier page
        self.user_model=user
        super(suppliers_detail, self).save(*args, **kwargs) 
        return created,password
    def __str__(self):
        return f'''{self.Supplier_Name}   |   {self.Distributor}   |   {self.Contact}   |   {self.Email} | {self.is_active}  '''

