from __future__ import unicode_literals

from waff.models import Flag, Switch
from waff.tests.base import TestCase


class DecoratorTests(TestCase):
    def test_flag_must_be_active(self):
        resp = self.client.get('/flag-on')
        self.assertEqual(404, resp.status_code)
        Flag.objects.create(name='foo', everyone=True)
        resp = self.client.get('/flag-on')
        self.assertEqual(200, resp.status_code)

    def test_flag_must_be_inactive(self):
        resp = self.client.get('/flag-off')
        self.assertEqual(200, resp.status_code)
        Flag.objects.create(name='foo', everyone=True)
        resp = self.client.get('/flag-off')
        self.assertEqual(404, resp.status_code)

    def test_switch_must_be_active(self):
        resp = self.client.get('/switch-on')
        self.assertEqual(404, resp.status_code)
        Switch.objects.create(name='foo', active=True)
        resp = self.client.get('/switch-on')
        self.assertEqual(200, resp.status_code)

    def test_switch_must_be_inactive(self):
        resp = self.client.get('/switch-off')
        self.assertEqual(200, resp.status_code)
        Switch.objects.create(name='foo', active=True)
        resp = self.client.get('/switch-off')
        self.assertEqual(404, resp.status_code)

    def test_switch_must_be_inactive_and_redirect_to_view(self):
        resp = self.client.get('/switched_view_with_valid_redirect')
        self.assertEqual(302, resp.status_code)
        Switch.objects.create(name='foo', active=True)
        resp = self.client.get('/switched_view_with_valid_redirect')
        self.assertEqual(200, resp.status_code)

    def test_switch_must_be_inactive_and_redirect_to_named_view(self):
        resp = self.client.get('/switched_view_with_valid_url_name')
        self.assertEqual(302, resp.status_code)
        Switch.objects.create(name='foo', active=True)
        resp = self.client.get('/switched_view_with_valid_url_name')
        self.assertEqual(200, resp.status_code)

    def test_switch_must_be_inactive_and_not_redirect(self):
        resp = self.client.get('/switched_view_with_invalid_redirect')
        self.assertEqual(404, resp.status_code)
        Switch.objects.create(name='foo', active=True)
        resp = self.client.get('/switched_view_with_invalid_redirect')
        self.assertEqual(200, resp.status_code)

    def test_flag_must_be_inactive_and_redirect_to_view(self):
        resp = self.client.get('/flagged_view_with_valid_redirect')
        self.assertEqual(302, resp.status_code)
        Flag.objects.create(name='foo', everyone=True)
        resp = self.client.get('/flagged_view_with_valid_redirect')
        self.assertEqual(200, resp.status_code)

    def test_flag_must_be_inactive_and_redirect_to_named_view(self):
        resp = self.client.get('/flagged_view_with_valid_url_name')
        self.assertEqual(302, resp.status_code)
        Flag.objects.create(name='foo', everyone=True)
        resp = self.client.get('/flagged_view_with_valid_url_name')
        self.assertEqual(200, resp.status_code)

    def test_flag_must_be_inactive_and_not_redirect(self):
        resp = self.client.get('/flagged_view_with_invalid_redirect')
        self.assertEqual(404, resp.status_code)
        Flag.objects.create(name='foo', everyone=True)
        resp = self.client.get('/flagged_view_with_invalid_redirect')
        self.assertEqual(200, resp.status_code)
