"""
Item is the key to the whole system which determine what is the result and where is the result. 

```
from toapi import XPath, Item

class MovieList(Item):
    __base_url__ = 'http://www.dy2018.com'

    url = XPath('//b//a[@class="ulink"]/@href')
    title = XPath('//b//a[@class="ulink"]/text()')

    class Meta:
        source = XPath('//table[@class="tbspan"]')
        route = {'/movies/?page=1': '/html/gndy/dyzz/',
                 '/movies/?page=:page': '/html/gndy/dyzz/index_:page.html',
                 '/movies/': '/html/gndy/dyzz/'}
```

When you visit http://127.0.0.1:/movies/?page=2, 
You could get the item from http://www.dy2018.com/html/gndy/dyzz/index_2.html

"""

from collections import OrderedDict

from htmlparsing import Selector, HTMLParsing


class ItemType(type):
    def __new__(cls, what, bases=None, attrdict=None):
        __fields__ = OrderedDict()

        for name, selector in attrdict.items():
            if isinstance(selector, Selector):
                __fields__[name] = selector

        for name in __fields__.keys():
            del attrdict[name]

        instance = type.__new__(cls, what, bases, attrdict)
        instance._list = None
        instance._site = None
        instance._selector = None
        instance.__fields__ = __fields__
        return instance


class Item(metaclass=ItemType):

    @classmethod
    def parse(cls, html: str):
        if cls._list:
            result = HTMLParsing(html).list(cls._selector, cls.__fields__)
            result = [cls._clean(item) for item in result]
        else:
            result = HTMLParsing(html).detail(cls.__fields__)
            result = cls._clean(result)
        return result

    @classmethod
    def _clean(cls, item):
        for name, selector in cls.__fields__.items():
            clean_method = getattr(cls, 'clean_%s' % name, None)
            if clean_method is not None:
                item[name] = clean_method(cls, item[name])
        return item
