import random
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import convert_type
try:  # Our TMDb Helper fork owns the daily-stable picks; stock TMDb Helper lacks the module
    from tmdbhelper.lib.addon.stablerandom import stable_random, stable_list_choice
except ImportError:  # Fall back to upstream behaviour (a new random pick per load) instead of failing to load
    def stable_random(paramstring, day=None):
        return random

    def stable_list_choice(paramstring, items, day=None):
        return random.choice(items)
from tmdbhelper_sync_trakt.directories.lists_filtered import (
    ListTraktTrending,
    ListTraktPopular,
    ListTraktMostPlayed,
    ListTraktMostWatched,
    ListTraktAnticipated,
)
from tmdbhelper_sync_trakt.directories.lists_trakt import (
    ListTraktStandard,
    ListTraktStandardProperties,
)
from tmdbhelper_sync_trakt.directories.lists_custom import ListTraktCustom
from tmdbhelper_sync_trakt.directories.lists_static import (
    ListTraktStaticTrending,
    ListTraktStaticPopular,
    ListTraktStaticLiked,
    ListTraktStaticOwned,
)


class ListTraktRandomisedProperties(ListTraktStandardProperties):

    @cached_property
    def limit(self):
        return self.pmax * 40  # Use double normal limit to get a decent sample size

    @cached_property
    def sample_limit(self):
        return min((self.pmax * 20), len(self.filtered_items))  # Make sure we dont try to sample more items than we have

    rng = random  # ListTraktRandomised swaps in a generator that keeps the same picks all day

    @cached_property
    def sorted_items(self):
        return self.get_sorted_items()

    def get_sorted_items(self):
        return self.rng.sample(self.filtered_items, self.sample_limit)


class ListTraktMixedRandomisedProperties(ListTraktRandomisedProperties):
    @cached_property
    def configured_media_properties(self):
        return self.get_configured_media_properties()

    def get_configured_media_properties(self):
        return tuple(self.configure_media_properties(properties) for properties in self.media_properties)

    def configure_media_properties(self, properties):
        properties.page = self.page
        properties.length = self.length
        properties.trakt_filters = self.trakt_filters
        return properties

    @cached_property
    def items(self):
        return self.get_items()

    def get_items(self):
        return [
            item for properties in self.configured_media_properties
            for item in properties.sorted_items]

    @cached_property
    def sample_limit(self):
        # Preserve the mixed list's existing cap, taken from its TV sample.
        return self.configured_media_properties[-1].sample_limit

    def get_sorted_items(self):
        return self.rng.sample(self.items, self.sample_limit)

    @cached_property
    def container_content(self):
        return convert_type(self.tmdb_type, 'container', items=self.sorted_items)


class ListTraktRandomised(ListTraktStandard):

    list_properties_class = ListTraktRandomisedProperties
    pagination = False

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.rng = stable_random(self.paramstring)
        if isinstance(list_properties, ListTraktMixedRandomisedProperties):
            list_properties.media_properties = tuple(
                self.get_media_properties(tmdb_type) for tmdb_type in ('movie', 'tv'))
        return list_properties

    def get_media_properties(self, tmdb_type):
        properties = self.configure_list_properties(self.list_properties_class())
        properties.tmdb_type = tmdb_type
        return properties

    def get_items(self, *args, tmdb_type=None, **kwargs):
        if tmdb_type == 'both':
            self.list_properties = self.configure_list_properties(ListTraktMixedRandomisedProperties())
        return super().get_items(*args, tmdb_type=tmdb_type, **kwargs)


class ListTraktTrendingRandomised(ListTraktRandomised, ListTraktTrending):
    pass


class ListTraktPopularRandomised(ListTraktRandomised, ListTraktPopular):
    pass


class ListTraktMostPlayedRandomised(ListTraktRandomised, ListTraktMostPlayed):
    pass


class ListTraktMostWatchedRandomised(ListTraktRandomised, ListTraktMostWatched):
    pass


class ListTraktAnticipatedRandomised(ListTraktRandomised, ListTraktAnticipated):
    pass


class ListTraktStaticTrendingRandomised(ListTraktCustom):
    sample_class = ListTraktStaticTrending

    def get_items(self, *args, tmdb_type=None, **kwargs):
        items = [i for i in self.sample_class(-1, 'nextpage=false').get_items(tmdb_type='both') or () if i and i.get('params')]
        if not items:
            return []
        # Keep the requested page/options when delegating to the selected list.
        kwargs.update(stable_list_choice(self.paramstring, items)['params'])
        return super().get_items(**kwargs)


class ListTraktStaticPopularRandomised(ListTraktStaticTrendingRandomised):
    sample_class = ListTraktStaticPopular


class ListTraktStaticLikedRandomised(ListTraktStaticTrendingRandomised):
    sample_class = ListTraktStaticLiked


class ListTraktStaticOwnedRandomised(ListTraktStaticTrendingRandomised):
    sample_class = ListTraktStaticOwned
