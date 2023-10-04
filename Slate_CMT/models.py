from django.db import models
from django.contrib.auth.models import User,Group
from django_pandas.managers import DataFrameManager


class parts_detail(models.Model):
    cpn=models.CharField(max_length=255,null=True)
    commodity=models.CharField(default='Miscellaneous',max_length=255,null=True)
    arista_pic=models.CharField(max_length=255,null=True)
    Ownership=models.CharField(max_length=255,null=True)
    Team=models.CharField(max_length=255,null=True)
    cm=models.CharField(max_length=255,null=True)
    modified_by=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    modified_on=models.DateTimeField(auto_now=True)
    objects=DataFrameManager()

class Master_notification(models.Model):
    message=models.CharField(max_length=255,null=True)
    text=models.TextField(null=True)
    user=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    notification_read=models.BooleanField(default=False,null=True)
    created_on=models.DateTimeField(auto_now_add=True)
    url=models.URLField(default='/')
    objects=DataFrameManager()