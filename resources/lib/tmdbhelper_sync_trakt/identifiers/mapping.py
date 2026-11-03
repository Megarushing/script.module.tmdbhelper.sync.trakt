from jurialmunkey.ftools import cached_property


class GetTraktIDMovie:
    def __init__(self, meta):
        self.meta = meta

    item_type = 'movie'
    tmdb_type = 'movie'
    season = None
    episode = None
    tmdb_ep = None
    episode_slug_id = None

    @staticmethod
    def get_value(dictionary, key):
        try:
            return dictionary[key]
        except (KeyError, TypeError, AttributeError):
            return

    @cached_property
    def item_id(self):
        return f'{self.tmdb_type}.{self.tmdb_id}'

    @cached_property
    def item_meta(self):
        return self.get_value(self.meta, self.item_type)

    @cached_property
    def item_meta_ids(self):
        return self.get_value(self.item_meta, 'ids')

    @cached_property
    def tmdb_id(self):
        return self.get_value(self.item_meta_ids, 'tmdb')

    @cached_property
    def tvdb_id(self):
        return self.get_value(self.item_meta_ids, 'tvdb')

    @cached_property
    def imdb_id(self):
        return self.get_value(self.item_meta_ids, 'imdb')

    @cached_property
    def trakt_id(self):
        return self.get_value(self.item_meta_ids, 'trakt')

    @cached_property
    def slug_id(self):
        return self.get_value(self.item_meta_ids, 'slug')

    @cached_property
    def query(self):
        query = self.get_value(self.item_meta, 'title') or ''
        query = query.casefold()
        return query

    @cached_property
    def item(self):
        return {
            'id': self.item_id,
            'item_type': self.item_type,
            'query': self.query,
            'tmdb_id': self.tmdb_id,
            'tmdb_ep': self.tmdb_ep,
            'tvdb_id': self.tvdb_id,
            'imdb_id': self.imdb_id,
            'slug_id': self.slug_id,
            'episode_slug_id': self.episode_slug_id,
            'trakt_id': self.trakt_id,
            'season': self.season,
            'episode': self.episode,
        }


class GetTraktIDShow(GetTraktIDMovie):
    item_type = 'show'
    tmdb_type = 'tv'


class GetTraktIDEpisode(GetTraktIDShow):
    @cached_property
    def episode_slug_id(self):
        return self.get_value(self.item_meta_ids, 'slug')

    item_type = 'episode'
    tmdb_type = 'tv'

    @cached_property
    def item_id(self):
        return f'{self.tmdb_type}.{self.tmdb_id}.{self.season}.{self.episode}'

    @cached_property
    def show_meta(self):
        return self.get_value(self.meta, 'show')

    @cached_property
    def show_meta_ids(self):
        return self.get_value(self.show_meta, 'ids')

    @cached_property
    def tmdb_id(self):
        return self.get_value(self.show_meta_ids, 'tmdb')

    @cached_property
    def tmdb_ep(self):
        return self.get_value(self.item_meta_ids, 'tmdb')

    @cached_property
    def slug_id(self):
        return self.get_value(self.show_meta_ids, 'slug')

    @cached_property
    def season(self):
        return self.get_value(self.item_meta, 'season')

    @cached_property
    def episode(self):
        return self.get_value(self.item_meta, 'number')


def GetTraktIDFactory(item):
    routes = {
        'movie': GetTraktIDMovie,
        'show': GetTraktIDShow,
        'episode': GetTraktIDEpisode,
    }
    try:
        return routes[item['type']](item).item
    except KeyError:
        return
