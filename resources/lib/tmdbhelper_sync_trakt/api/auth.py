from tmdbhelper.lib.api.contains import CommonContainerAPIs
from jurialmunkey.ftools import cached_property


class TraktAuthorisation(CommonContainerAPIs):
    authorisation_type = 'Trakt'

    @cached_property
    def trakt_api(self):
        return self.get_trakt_api()

    def get_trakt_api(self):
        from tmdbhelper_sync_trakt.api.api import TraktAPI
        return TraktAPI()

    @property
    def is_authorized(self):
        return self.trakt_api.authenticator.is_authorized
