from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import get_language
from tmdbhelper.lib.addon.tmdate import get_datetime_today, get_timedelta
from tmdbhelper.lib.files.bcache import BasicCache


class TraktCalendarClient:
    cache_days = 0.25

    def __init__(self, api):
        self.api = api

    @cached_property
    def cache(self):
        return self.get_cache()

    def get_cache(self):
        return BasicCache(filename='ItemContainer.db')

    def get_episodes(self, startdate, days):
        if not self.api.is_authorized:
            return
        # Fetch an extra day at each end for the later UTC-to-local range check.
        start_date = get_datetime_today() + get_timedelta(days=startdate - 1)
        url = f'calendars/my/shows/{start_date:%Y-%m-%d}/{days + 2}'
        return self.cache.use_cache(
            lambda: self.get_response(url),
            cache_days=self.cache_days,
            cache_name=f'TraktData_{url}_{get_language()}',
            cache_combine_name=True)

    def get_response(self, url):
        response = self.api.get_response(url)
        return response.json() if response else None
