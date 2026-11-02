from tmdbhelper_sync_trakt.actions.service import ItemAction
from tmdbhelper.lib.script.sync.provider import ItemSync as ProviderItemSync


class ItemSync(ProviderItemSync, ItemAction):
    pass
