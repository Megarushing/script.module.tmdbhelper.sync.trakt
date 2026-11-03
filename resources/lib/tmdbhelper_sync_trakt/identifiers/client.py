from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.sync.providers.identifiers import IdentifierResolver
from tmdbhelper_sync_trakt.identifiers.database import TraktIdentifiersDatabase
from tmdbhelper_sync_trakt.identifiers.mapping import GetTraktIDFactory


class TraktIdentifierClient:
    def __init__(self, api):
        self.api = api

    @cached_property
    def database(self):
        return self.get_database()

    def get_database(self):
        database = TraktIdentifiersDatabase()
        database.migrate_legacy_cache()
        return database

    def get_response(self, *path, **kwargs):
        response = self.api.get_response(*path, **kwargs)
        if not response:
            return
        try:
            return response.json()
        except ValueError:
            return
        finally:
            response.close()

    def get_item(self, id_value, id_type='tmdb', item_type='movie', season=None, episode=None):
        item = self.database.get_item(id_value, id_type, item_type, season, episode)
        if item is not None:
            return item
        query = f'search/{id_type}/{id_value}'
        if not self.database.is_queried(query):
            data = self.get_response(query, limit=4095)
            if data is None:
                return
            items = [mapped for mapped in (GetTraktIDFactory(row) for row in data) if mapped]
            self.database.save_items(query, items)
        return self.database.get_item(id_value, id_type, item_type, season, episode)

    def get_id(self, id_value, id_type='tmdb', item_type='movie', output_type='slug', season=None, episode=None):
        item = self.get_item(id_value, id_type, item_type, season, episode)
        return item.get(f'{output_type}_id') if item else None

    def get_episode(self, show, season, episode):
        item = self.database.get_item(show['tmdb_id'], 'tmdb', 'episode', season, episode)
        if item is not None and item['episode_slug_id']:
            return item
        query = f"shows/{show['slug_id']}/seasons/{season}/episodes/{episode}"
        if not self.database.is_queried(query):
            data = self.get_response(query)
            if data is None:
                return item
            show_ids = {key: show[f'{key}_id'] for key in ('tmdb', 'tvdb', 'imdb', 'slug', 'trakt')}
            mapped = GetTraktIDFactory({'type': 'episode', 'show': {'ids': show_ids}, 'episode': data})
            self.database.save_items(query, [mapped])
        return self.database.get_item(show['tmdb_id'], 'tmdb', 'episode', season, episode)

    @staticmethod
    def get_provider_ids(item, prefix='', episode=False):
        if item is None:
            return {}
        ids = {'trakt': item['trakt_id'], 'slug': item['episode_slug_id'] if episode else item['slug_id']}
        return {f'{prefix}{key}': value for key, value in ids.items() if value is not None and value != ''}

    def get_ids(self, tmdb_type, tmdb_id, season=None, episode=None):
        item_type = 'movie' if tmdb_type == 'movie' else 'show'
        item = self.get_item(tmdb_id, item_type=item_type)
        if tmdb_type == 'movie':
            return self.get_provider_ids(item)
        ids = self.get_provider_ids(item, prefix='tvshow.')
        if item is not None and season is not None and episode is not None:
            ids.update(self.get_provider_ids(self.get_episode(item, season, episode), episode=True))
        return ids


class TraktIdentifierResolver(IdentifierResolver):
    def get_id(self, id_value, id_type, item_type, output_type, season=None, episode=None):
        return self.provider.identifiers.get_id(id_value, id_type, item_type, output_type, season, episode)

    def get_ids(self, tmdb_type, tmdb_id, season=None, episode=None):
        return self.provider.identifiers.get_ids(tmdb_type, tmdb_id, season, episode)
