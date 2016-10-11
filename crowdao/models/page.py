from django.db import models

from ..utils import sluggify


class Page(models.Model):
    """A page on the website
    """

    title = models.CharField(('Title'), max_length=255)
    subtitle = models.CharField(('Subtitle'), max_length=255, blank=True)
    content = models.TextField(('Content'), blank=True)
    image = models.FileField('Image or video', blank=True)
    slug = models.CharField(('Slug'), max_length=100, blank=True)  # defined the URL where this page can be found

    class Meta:
        verbose_name = ("Page")
        verbose_name_plural = ("Pages")
        ordering = ['title', 'slug']

    def __unicode__(self):
        return u'{self.title} [{self.slug}]'.format(self=self)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = sluggify(self.title)
        super(Page, self).save(*args, **kwargs)
