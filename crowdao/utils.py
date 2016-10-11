import copy
import urllib
import datetime

from django.http import Http404


def first_words(s, num_chars=100):
    """return a string of length not more than num_chars with the first words of the given string

    appends "..." if the original string is longer than num_chars
    """
    result = s[:100]
    result = ' '.join(result.split()[:-1])
    if len(s) > 100:
        result += '...'
    return result


def urlencode(d):
    """call urllib.urlencode, but first tries to avoid encoding errors"""
    try:
        return urllib.urlencode(d)
    except UnicodeEncodeError:
        d = copy.copy(d)
        for k in d:
            if type(d[k]) == type(u''):
                d[k] = d[k].encode('utf8')
        return urllib.urlencode(d)


def format_date_for_timeglider(d):
    return '%04d-%02d-%02d 01:00:00' % (d.year, d.month, d.day)


def prettyprint_date(y, m=None, d=None):
    if y and m and d:
        try:
            date = datetime.date(y, m, d)
            return date
        except ValueError:
            return '{d}-{m}-{y}'.format(d=d, m=m, y=y)
        except TypeError:
            return '{d}-{m}-{y}'.format(d=d, m=m, y=y)

    elif y and m:
        return '{m}-{y}'.format(m=m, y=y)
    elif y:
        return '{y}'.format(y=y)


def to_date(y, m=None, d=None):
    if not y:
        return None
    if not m:
        m = 1
    if not d:
        d = 1
    return datetime.date(y, m, d)


def sluggify(s):
    """Turn s into a friendlier URL fragment

    removes underscores, and strips forward slashes from beginning and end

    returns:
        a string
    """
    # XXX make this smarter
    s = s.lower()
    s = s.strip()
    s = s.replace(' ', '-')
    while '--' in s:
        s = s.replace('--', '-')

    if s.startswith('/'):
        s = s[1:]
    if s.endswith('/'):
        s = s[:-1]

    return s


def slugs2breadcrumbs(ls):
    """given a list of slugs, return a list of (title, url) tuples"""
    result = []
    for slug in ls:
        page = get_page(slug=slug)
        result.append(page)
    result = [(page.title, page.get_absolute_url()) for page in result]
    return result


def fix_date(s):
    if s.isdigit() and len(s) == 4:
        s = '%s-1-1' % s
    return s


def get_page(slug, default=None, raise_404=True):
    from crowdao import models
    try:
        page = models.Page.objects.get(slug=slug)
    except models.Page.DoesNotExist:
        if default is None and raise_404:
            msg = 'Could not find Page with slug "%s"' % slug
            raise Http404(msg)
        else:
            return default
    return page
