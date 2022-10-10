from time import timezone
from django.db import models
from pytz import timezone


# Create your models here.
class fileMeta(models.Model):
    description=models.TextField(null=True,blank=True)
    file_name=models.CharField(max_length=50)
    file_size = models.IntegerField(null=True)
    created_at=models.DateTimeField(null=True)
    updated_at=models.DateTimeField(null=True)
    user_name = models.CharField(max_length=35, db_index=True)
    owner_first_name = models.CharField(max_length=35, db_index=True,null=True)
    owner_last_name = models.CharField(max_length=35, db_index=True,null=True)