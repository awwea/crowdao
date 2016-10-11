# encoding=utf-8
#
# copyright Gerbrandy SRL
# www.gerbrandy.com
# 2016-...
#

from django.contrib.auth.models import User

from .common import BaseTestCase
from ..utils import get_page
from ..models import Page


class PagesTestCase(BaseTestCase):
    """
    """

    def setUp(self):
        super(PagesTestCase, self).setUp()

        # adding these pages in setup, as re-creating the fixture test.json is too much hassle
        self.add_page('home')
        self.add_page('web')
        self.add_page('data')
        self.add_page('digitisation')

        home_page = get_page('home')
        home_page.title = 'Homepage Title'

    def add_page(self, slug, title=None, content=None):
        page = Page(slug=slug)
        if not title:
            title = slug
        page.title = title
        if content:
            page.content = content
        page.save()
        page.save()
        return page

    def create_superuser(self):
        """
        Create a superuser names 'admin'
        """
        self._username = "admin"
        self._password = "admin"
        args = (self._username, "example@example.com", self._password)
        try:
            self._user = User.objects.get(username='admin')
        except User.DoesNotExist:
            self._user = User.objects.create_superuser(*args)
        return self._user

    def test_description_and_content_on_page(self):
        # test the hoem page
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        # add a page, test if description and content arrive at the page, and also are updated when the page is
        slug = 'some-slug'
        self.add_page(slug)
        page = Page.objects.get(slug=slug)
        # page.description = 'description_en1'
        page.content = 'content_en1'
        page.save()
        response = self.app.get('/{}/'.format(slug))
        # self.assertEqual(response.context['page'].description, 'description_en1')
        # self.assertContains(response, 'description_en1')
        self.assertContains(response, 'content_en1')

        # page.description = 'description_en2'
        page.content = 'content_en2'
        page.save()
        response = self.app.get('/{}/'.format(slug))
        # self.assertEqual(response.context['page'].description, 'description_en2', msg='.. for slug {}'.format(slug))
        # self.assertContains(response, 'description_en2')
        self.assertContains(response, 'content_en2')
