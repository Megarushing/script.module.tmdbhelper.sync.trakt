from xbmc import executebuiltin


def run(action=None):
    if action is None:
        executebuiltin(
            'RunScript(plugin.video.themoviedb.helper,configure_sync_provider,'
            'addon_id=script.module.tmdbhelper.sync.trakt)')
        return
    from tmdbhelper.lib.sync.providers.registry import SyncProviderRegistry
    from tmdbhelper_sync_trakt.account import TraktAccountActions
    provider = SyncProviderRegistry().find_provider('trakt')
    if provider is None:
        return
    actions = TraktAccountActions(provider)
    return {'authenticate': actions.authenticate, 'revoke': actions.revoke}[action]()


if __name__ == '__main__':
    import sys
    run(**dict(arg.split('=', 1) for arg in sys.argv[1:]))
