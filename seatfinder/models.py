from django.db import models
from django_mysql.models import ListTextField

from django.db.models.signals import pre_save

from lxml import etree
import os.path
import re


class FloorPlan(models.Model):
    
    floor_name = models.CharField(max_length=255, unique=True)
    floor_data = models.TextField()
    file_with_data = models.FilePathField()  # Note you have to "export as XML" when saving the file for the data to be correct

    # https://django-mysql.readthedocs.io/en/latest/model_fields/list_fields.html for more information
    indexed_names = ListTextField(
        base_field=models.CharField(max_length=255),
        size=10000,
    )

    @property
    def file_basename(self):
        return os.path.basename(self.file_with_data)
