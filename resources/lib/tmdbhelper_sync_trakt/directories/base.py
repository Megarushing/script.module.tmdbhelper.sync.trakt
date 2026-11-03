from tmdbhelper_sync_trakt.api.contains import TraktContainerAPIs


class TraktList(TraktContainerAPIs):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.sync_provider = self.sync_provider
        list_properties.trakt_api = self.trakt_api
        return list_properties
