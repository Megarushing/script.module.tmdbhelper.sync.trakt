from jurialmunkey.ftools import cached_property


class TraktContainerAPIs:
    @cached_property
    def sync_provider(self):
        return self.get_sync_provider()

    def get_sync_provider(self):
        from tmdbhelper.lib.sync.providers.registry import SyncProviderRegistry
        return SyncProviderRegistry().get_provider('trakt')

    @cached_property
    def trakt_api(self):
        return self.get_trakt_api()

    def get_trakt_api(self):
        return self.sync_provider.api
