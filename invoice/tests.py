from django.test import TestCase
from django.test.client import Client
from django.db import IntegrityError
from django.contrib.auth.models import User

from invoicemaster.client.models import Client, Project
from invoicemaster.invoice.models import Invoice, Lineitem
from invoicemaster.common.tests import AuthenticatedUserTestCase

class CreateTest(AuthenticatedUserTestCase):
    """ Tests the creation of the invoice and line item objects as simple unit tests
    """

    def test_create_invoice(self):
        # attempt to create a blank invoice object
        invoice = Invoice()
        self.failUnless(AssertionError)
        # create a invoice object with all required fields
        client = Client(first_name="Bob",last_name="Smith", email="bob@emlprime.com", phone_number="805-448-2304")
        client.save()
        project = Project(name="test", status="pending", client=Client.objects.get())
        project.save()
        invoice = Invoice(client=client, project=project, date_issued="", date_due="", amount=0.00)
        self.failUnlessEqual(invoice.client, client)
        self.failUnlessEqual(invoice.project, project)
        self.failUnlessEqual(invoice.date_issued, "")
        self.failUnlessEqual(invoice.date_due, "")
        self.failUnlessEqual(invoice.amount, 0.00)

    def test_create_lineitem(self):
        #create a lineitem belonging to the above invoice with no data entered
        lineitem=Lineitem()
        self.failUnless(AssertionError)
        #create a lineitem belonging to the above invoice with maximal data entered
        lineitem = Lineitem(name="test", amount=1.00)
        self.failUnlessEqual(lineitem.name, "test")
        self.failUnlessEqual(lineitem.amount, 1.00)

