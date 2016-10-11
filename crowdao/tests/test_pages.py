from django.core.urlresolvers import reverse
from .common import BaseTestCase


class PageTestCase(BaseTestCase):
    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        response = self.app.get('/questions/')
        self.assertEqual(response.status_code, 200)
        response = self.app.get('/updates/')
        self.assertEqual(response.status_code, 200)

    def test_admin(self):
        self.app.get('/', user='admin')
