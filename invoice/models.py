from django.db import models

from invoicemaster.client.models import Client, Project


class Lineitem(models.Model):
    """Model for the lineitem object
    """

    name = models.CharField(max_length = 255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(null=True, blank=True)

class Invoice(models.Model):
    """ Model for the invoice object
    """
    client = models.ForeignKey(Client)
    project = models.ForeignKey(Project)
    date_issued = models.DateField()
    date_due = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(null=True, blank=True)
    lineitems = models.ManyToManyField(Lineitem)
