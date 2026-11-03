from tmdbhelper.lib.api.api_keys.tokenhandler import TokenHandler
from tmdbhelper_sync_trakt.settings import TraktSettings


class TraktTokenHandler(TokenHandler):
    def __init__(self):
        self.settings = TraktSettings()
        self.settings.migrate_credentials()
        super().__init__('token', store_as='setting')

    def _get_setting(self, name, *args):
        return self.settings.addon.getSetting(name)

    def _set_setting(self, name, value, *args):
        self.settings.migrate_setting(name, value)
