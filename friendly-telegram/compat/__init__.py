#    Friendly Telegram Userbot
#    by GeekTG Team

import logging
import sys
from importlib.abc import Loader, MetaPathFinder
from importlib.machinery import ModuleSpec

from .raphielgang import RaphielgangConfig, RaphielgangEvents, RaphielgangDatabase
from .uniborg import UniborgUtil, Uniborg

# When a name is matched, the import is overriden, and our custom object is returned
MODULES = {"userbot": RaphielgangConfig, "userbot.events": RaphielgangEvents,
           "userbot.modules": RaphielgangConfig, "userbot.modules.dbhelper": RaphielgangDatabase, "uniborg": Uniborg,
           "uniborg.util": UniborgUtil}


class BotCompat(MetaPathFinder, Loader):  # pylint: disable=W0223 # It's wrong - https://kutt.it/hkjRb9
    """importlib Loader that loads the classes in MODULES under their pseudonyms"""

    def __init__(self, clients):
        self.clients = clients
        self.created = []

    def find_spec(self, fullname, path, target=None):
        """https://docs.python.org/3.7/library/importlib.html#importlib.abc.MetaPathFinder.find_spec"""
        if fullname in MODULES:
            return ModuleSpec(fullname, self)

    def create_module(self, spec):
        """https://docs.python.org/3.7/library/importlib.html#importlib.abc.Loader.create_module"""
        ret = MODULES[spec.name](self.clients)
        self.created += [ret]
        return ret

    def exec_module(self, module):
        """https://docs.python.org/3.7/library/importlib.html#importlib.abc.Loader.exec_module"""
        module.__path__ = []

    async def client_ready(self, client):
        """Signal all mods that client_ready()"""
        self.clients += [client]
        for mod in self.created:
            try:
                await mod.client_ready(client)
            except BaseException:
                logging.exception("Failed to send client_ready to compat layer " + repr(mod))


def activate(clients):
    """Activate the compat layer"""
    compatlayer = BotCompat(clients)
    sys.meta_path.insert(0, compatlayer)
    return compatlayer
