from tmdbhelper_sync_trakt.api.contains import TraktContainerAPIs


class TraktAuthorisation(TraktContainerAPIs):
    authorisation_type = 'Trakt'

    def __init__(self, provider):
        self.sync_provider = provider

    @property
    def is_authorized(self):
        return self.trakt_api.authenticator.is_authorized
