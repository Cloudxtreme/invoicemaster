import re

from django.http import HttpResponseRedirect
from django.test import TestCase
from django.test.client import Client
from django.template import TemplateDoesNotExist
from django.core.exceptions import ViewDoesNotExist
from django.contrib.auth.models import User

from BeautifulSoup import BeautifulSoup

class CommonTestCase(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.alice = Actor()

    def parse_doc(self, response):
        """ Parse an HTML content and return a BeautifulSoup doc
        """
        # check that this is a status OK response
        self.failUnlessEqual(response.status_code, 200)
        return BeautifulSoup(response.content)

class AuthenticatedUserTestCase(CommonTestCase):
    def setUp(self):
        super(AuthenticatedUserTestCase, self).setUp()
        self.user = User.objects.create_user(username="alice", email="peter@emlprime.com", password="test")
        self.alice.client.login(username=self.user.username, password="test")
        #self.bobs_user = User.objects.create_user("bob", "bob@emlprime.com", "test")
        #self.bob.client.login(username=self.bobs_user.username, password="test")

class Actor(TestCase):
    """ represent an Actor running automated actions

    alice = Actor(username="alice", password="test")
    """
    def __init__(self):
        self.client = Client()

    def clicks_a_link(self, url, verbose=True, templates_used=[]):
        """ Simulate a GET request using the test client
        """
        # request the page
        #submit the form
        import traceback, sys
        try:
            response = self.client.get(url)
        except TemplateDoesNotExist:
            exception_message = "".join(traceback.format_exception_only(sys.exc_type, sys.exc_value)).strip()
            
            self.fail("No url to handle (%s) or template does not exist: (%s)" % (url, exception_message))
        except ViewDoesNotExist:
            exception_message = "".join(traceback.format_exception_only(sys.exc_type, sys.exc_value)).strip()
            self.fail("No view to handle (%s): %s" % (url, exception_message))
        
        # check that this was a valid request
        self.failUnless(response.status_code in [200, 302])

        # if there are templates supplied for checking, make sure they are used to render the page
        for template in templates_used:
            self.assertTemplateUsed(response, template)

        # if we're not going to do anything with the response, don't bother using BeautifulSoup
        if not verbose:
            return True
        
        # return a BeautifulSoup document for navigating
        return BeautifulSoup(response.content)

    def sees_an_element(self, doc, element=None, css_class=None, id=None):
        """ Tests for the presence of a specified element on the current page...

        self.alice.sees_an_element(doc, id="element_id")
        self.alice.sees_an_element(doc, "element")
        self.alice.sees_an_element(doc, "div", "element_css_class")
        """
        selector = "any"
        if id:
            displayed_element=doc.find(id=id)
            selector = id
        else:
            if css_class:
                displayed_element=doc.find(element, css_class)
                selector = "%s.%s" % (element, css_class)
            else:
                displayed_element=doc.find(element)
                selector = element
        self.failUnless(displayed_element, "Could not find %s" % selector)
        return displayed_element

    def sees_a_link(self, doc, href, src=None):
        """Tests for the presence of a link, and optionally tests for the presence of the link's image 
        
        self.alice.sees_a_link(doc, "/page/")
        self.alice.sees_a_link(doc, "/page/", src="/media/images/link_image.png")
        """
        # look for a link in the doc with the expected href
        link = doc.find(href=href)
        self.failUnless(link, "Could not find link to %s in:\n%s" % (href, doc))

        # if there is an image being linked, look for the image in the link
        if src:
            image = link.find(src=src)
            self.failUnless(image, "Could not find the image %s" % src)
        return link
            
    def sees_a_string(self, doc, expected_string):
        """Tests for the presence of a particular string within the doc...
        
        self.alice.sees_a_string(doc, "my string")
        would succeed on the following html snippets:
        <p>my string</p>
        <p>this is my string.</p>        
        <p>here is <a href="/whatever/">my string</a></p>
        """
        found = False
        links = doc.findAll("a")
        for link in links:
            if expected_string in link.string:
                found=True
                break
        if not found:
            if doc.string and expected_string in doc.string:
                found = True
        self.failUnless(found, "Could not find %s in:\n%s" % (expected_string, doc))
        return found

    def submits_a_form(self, doc, form_css_id, post_data={}, errors={}, verbose=True, follow_redirects=True, input_type="submit"):
        """ Simulate submitting a form with a POST using the test client

        doc is a BeautifulSoup navigable string
        form_css_id is the identifier to find the form, we'll use it to confirm that the data
        could reasonably be submitted by this form
        """
        assert isinstance(doc, BeautifulSoup)
        assert isinstance(post_data, dict)
        
        form = self.sees_a_form(doc, form_css_id)
        # get all of the fields and put them in a dictionary
        fields = dict([(f['name'], f) for f in form.findAll("input") + form.findAll("textarea") + form.findAll("select") if f.has_key('name')])
        for field_name, value in post_data.items():
            # confirm that all of the fields provided exist in the HTML form
            self.failUnless(field_name in fields.keys(), "Field: %s not found in form keys" % field_name)
        self.sees_a_submit_button(form)
        #submit the form
        try:
            response = self.client.post(form['action'], post_data)
        except TemplateDoesNotExist:
            self.fail("No url to handle (%s)" % form['action'])
        except ViewDoesNotExist:
            self.fail("No view to handle (%s)" % form['action'])

        if errors:
            for field, message in errors.items():
                self.assertFormError(response, form["id"], field, message)
            
        if not verbose:
            return True

        if isinstance(response, HttpResponseRedirect):
            if follow_redirects:
                location_tuple = response._headers.get("location", None)
                if location_tuple:
                    location = location_tuple[1]
                    match = re.match("http://[^/]+(/.+)$", location)
                    if match:
                        url = match.groups()[0]
                        return self.clicks_a_link(url)
                
            else:
                return response

        return BeautifulSoup(response.content)

    def sees_a_submit_button(self, form, name="submit"):
        """ see a submit button as part of a form
        """
        submit_buttons = form.findAll(type="image") + form.findAll(type="submit")
        found = [submit_button for submit_button in submit_buttons if submit_button.get("name", None) == name]
        self.failUnless(found, "Submit Button does not exist in %s" % form)
        return found

    def sees_a_form(self, doc, form_css_id):
        """ parse a form from a form css id
        """
        # find the form
        actual_css_id = "%s_form" % form_css_id
        form = doc.find(id=actual_css_id)
        self.failUnless(form, "Form %s[_form] does not exist in %s" % (form_css_id, str(doc)))
        return form

    def sees_an_input(self, doc, name, value="DO_NOT_VALIDATE"):
        """ Find an input in the given navigable string
        """
        result = doc.find("input", {"name": name})
        self.failUnless(result, "Could not find an input named %s in %s" % (name, str(doc)))

        if value != "DO_NOT_VALIDATE":
            self.failUnlessEqual(result["value"], value)
        return result

    def sees_a_textarea(self, doc, name, value="DO_NOT_VALIDATE"):
        result = doc.find("textarea", {"name": name})
        self.failUnless(result, "Could not find a textarea named %s in %s" % (name, str(doc)))

        if value != "DO_NOT_VALIDATE":
            value = value if value else None
            self.failUnlessEqual(result.string, value)
        return result
        

    def sees_a_delete_button(self, doc, absolute_url):
        """ Find a delete button with a link around it.

        We will either use conventional delete confirm page or use javascript to prompt for confirm and then post delete.
        """
        delete_button = doc.find("a", {"class": "delete", "href": absolute_url + "delete/"})
        self.failUnlessEqual(
            delete_button.string,
            "Delete", "Could not find a Delete link for %s" % absolute_url
            )

    def sees_an_error_message(self, doc, message):
        """ Search a navigable string for an error message
        """
        error_message = doc.find(id="error_message")
        self.failUnless( message in error_message.string )
        return error_message

    def sees_a_confirm_message(self, doc, message):
        """ Search a navigable string for a confirm message
        """
        confirm_message = doc.find(id="confirm_message")
        self.failUnless(confirm_message, "There is no confirm message on this page: %s" % doc)
        self.failUnless( message in confirm_message.string, "Could not find (%s) in : %s" % (message, doc) )
        return confirm_message



        
        

        
        
        
