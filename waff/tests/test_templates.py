from __future__ import unicode_literals

from django.contrib.auth.models import AnonymousUser
from django.template import Template
from django.template.base import VariableNode
from django.test import RequestFactory

from test_app import views
from waff.middleware import WaffleMiddleware
from waff.tests.base import TestCase


def get():
    request = RequestFactory().get('/foo')
    request.user = AnonymousUser()
    return request


def process_request(request, view):
    response = view(request)
    return WaffleMiddleware().process_response(request, response)


class WaffleTemplateTests(TestCase):

    def test_django_tags(self):
        request = get()
        response = process_request(request, views.flag_in_django)
        self.assertContains(response, 'flag off')
        self.assertContains(response, 'switch off')
        self.assertContains(response, 'sample')
        self.assertContains(response, 'flag_var off')
        self.assertContains(response, 'switch_var off')
        self.assertContains(response, 'sample_var')
        self.assertContains(response, 'window.waffle =')

    def test_get_nodes_by_type(self):
        """WaffleNode.get_nodes_by_type() should correctly find all child nodes"""
        test_template = Template('{% load waffle_tags %}{% switch "x" %}{{ a }}{% else %}{{ b }}{% endswitch %}')
        children = test_template.nodelist.get_nodes_by_type(VariableNode)
        self.assertEqual(len(children), 2)

    def test_no_request_context(self):
        """Switches and Samples shouldn't require a request context."""
        request = get()
        content = process_request(request, views.no_request_context)
        assert 'switch off' in content
        assert 'sample' in content

    def test_jinja_tags(self):
        request = get()
        response = process_request(request, views.flag_in_jingo)
        self.assertContains(response, 'flag off')
        self.assertContains(response, 'switch off')
        self.assertContains(response, 'sample')
        self.assertContains(response, 'window.waffle =')
