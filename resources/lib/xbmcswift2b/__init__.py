'''
    resources.lib.xbmcswift2b
    ----------

    A micro framework to enable rapid development of XBMC plugins.

    :copyright: (c) 2012 by Jonathan Beluch
    :license: GPLv3, see LICENSE for more details.
'''
from types import ModuleType


class module(ModuleType):
    '''A wrapper class for a module used to override __getattr__. This class
    will behave normally for any existing module attributes. For any attributes
    which do not existi in in the wrapped module, a mock function will be
    returned. This function will also return itself enabling multiple mock
    function calls.
    '''

    def __init__(self, wrapped=None):
        self.wrapped = wrapped
        if wrapped:
            self.__dict__.update(wrapped.__dict__)

    def __getattr__(self, name):
        '''Returns any existing attr for the wrapped module or returns a mock
        function for anything else. Never raises an AttributeError.
        '''
        try:
            return getattr(self.wrapped, name)
        except AttributeError:
            def func(*args, **kwargs):
                '''A mock function which returns itself, enabling chainable
                function calls.
                '''
                log.warning('The %s method has not been implented on the CLI. '
                            'Your code might not work properly when calling '
                            'it.', name)
                return self
            return func


try:
    import xbmc
    import xbmcgui
    import xbmcplugin
    import xbmcaddon
    CLI_MODE = False
except ImportError:
    CLI_MODE = True

    import sys
    from logger import log

    # Mock the XBMC modules
    from mockxbmc import xbmc, xbmcgui, xbmcplugin, xbmcaddon, xbmcvfs
    xbmc = module(xbmc)
    xbmcgui = module(xbmcgui)
    xbmcplugin = module(xbmcplugin)
    xbmcaddon = module(xbmcaddon)
    xbmcvfs = module(xbmcvfs)


from resources.lib.xbmcswift2b.storage import TimedStorage
from resources.lib.xbmcswift2b.request import Request
from resources.lib.xbmcswift2b.common import (xbmc_url, enum, clean_dict, pickle_dict,
    unpickle_args, unpickle_dict, download_page, unhex)
from resources.lib.xbmcswift2b.constants import SortMethod, VIEW_MODES
from resources.lib.xbmcswift2b.listitem import ListItem
from resources.lib.xbmcswift2b.logger import setup_log
from resources.lib.xbmcswift2b.module import Module
from resources.lib.xbmcswift2b.urls import AmbiguousUrlException, NotFoundException, UrlRule
from resources.lib.xbmcswift2b.xbmcmixin import XBMCMixin
from resources.lib.xbmcswift2b.plugin import Plugin
