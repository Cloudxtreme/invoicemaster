from django.test import TestCase
from django.test.client import Client
from django.db import IntegrityError
from django.contrib.auth.models import User

from invoicemaster.client.models import Client, Project
from invoicemaster.common.tests import Actor, CommonTestCase, AuthenticatedUserTestCase

class CreateTest(AuthenticatedUserTestCase):
    """ Tests the creation of the client object as a simple unit test
    """

    def test_create_client(self):
        # attempt to create a blank client object
        client = Client()
        self.failUnless(AssertionError)
        # create a client object with all required fields
        client = Client(first_name="Bob",last_name="Smith", email="bob@emlprime.com", phone_number="805-448-2304")
        self.failUnlessEqual(client.first_name, "Bob")
        self.failUnlessEqual(client.last_name, "Smith")
        self.failUnlessEqual(client.email, "bob@emlprime.com")
        self.failUnlessEqual(client.phone_number, "805-448-2304")
        # create a client object with all fields
        client = Client(first_name="Bob",last_name="Smith", email="bob@emlprime.com", phone_number="805-448-2304", notes="poor impulse control")
        self.failUnlessEqual(client.first_name, "Bob")
        self.failUnlessEqual(client.last_name, "Smith")
        self.failUnlessEqual(client.email, "bob@emlprime.com")
        self.failUnlessEqual(client.phone_number, "805-448-2304")
        self.failUnlessEqual(client.notes, "poor impulse control")

    def test_create_project(self):
        #create a project belonging to the above client with no data entered
        project=Project()
        self.failUnless(AssertionError)
        #create a project belonging to the above client with maximal data entered
        client = Client(first_name="Bob",last_name="Smith", email="bob@emlprime.com", phone_number="805-448-2304", notes="poor impulse control")
        client.save()
        project = Project(name="test", status="pending", client=client)
        self.failUnlessEqual(project.name, "test")
        self.failUnlessEqual(project.status, "pending")
        self.failUnlessEqual(project.client, client)

class UserTestCase(CommonTestCase):
    """Alice comes to the site for the first time.  She should...
    """

    def test_newUser(self):
        alice=self.alice

        # navigate to the home page
        templates_used = "base.html", "registration/login.html"
        doc = alice.clicks_a_link("/", templates_used=templates_used)
        # see the login form
        alice.sees_an_element(doc, id="login_form")
        # see the link to the registration form
        alice.sees_a_link(doc, href="/accounts/register/")
        # follow the link to the registration form
        templates_used = "base.html", "registration/registration_form.html"
        doc=alice.clicks_a_link("/accounts/register/", templates_used=templates_used)
        # sees the registration form
        form=alice.sees_a_form(doc, "register")        
        alice.sees_a_submit_button(form, name="submit")
        # submit the registration form
        alice.submits_a_form(doc, form_css_id="register", post_data={'username':'alice', 'email':'peter@emlprime.com', 'password1':'test', 'password2':'test'}, input_type="submit")

    def test_logIn(self):
        """ Alice has created her new user.  She should...
        """
        alice = self.alice
        self.user = User.objects.create_user(username="alice", email="peter@emlprime.com", password="test")
        self.alice.client.login(username=self.user.username, password="test")
        
        # navigate to the home page
        doc = alice.clicks_a_link("/")
        # submit the login form with her login information
        #alice.submits_a_form(doc, form_css_id="login", post_data={'username':'alice', 'password':'test'})
        pass
