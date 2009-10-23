from django.db import models

class Client(models.Model):
    """ Model for the client object
    """
    
    first_name = models.CharField(max_length = 100)
    last_name = models.CharField(max_length = 100)
    email = models.EmailField()
    phone_number = models.CharField(max_length = 20, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

class Project(models.Model):
    """Model for the project object
    """
    STATUS_CHOICES = (
        ("pending","Pending"),
        ("in_progress","In Progress"),
        ("billed","Billed"),
        ("closed","Closed"),
        )

    name = models.CharField(max_length = 255)
    status = models.CharField(max_length = 40, choices=STATUS_CHOICES)
    client = models.ForeignKey(Client)

