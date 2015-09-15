from django.db import models

class Package(models.Model):
    name = models.CharField(max_length=30, blank=False, null=False, unique=True)
    description = models.TextField(blank=False, null=False) 


class Audit(models.Model):
    name = models.CharField(max_length=30, blank=False, null=False, unique=True)
    description = models.TextField(blank=False, null=False)
    package = models.ForeignKey('Package')
    
    # Upgrade to FilePathFiled in the future
    execution_script = models.CharField(max_length=4096, blank=False, null=False)

    
    required_doctypes = models.ManyToManyField('Doctype')
    required_key_value_store = models.ManyToManyField('KeyValueStore')


class Doctype(models.Model):
    name = models.CharField(max_length=30, blank=False, null=False, unique=True)
    
    # Upgrade to FilePathFiled in the future
    parsing_instructions = models.CharField(max_length=4096, blank=True, null=False)

class KeyValueStore(models.Model):
    pass
