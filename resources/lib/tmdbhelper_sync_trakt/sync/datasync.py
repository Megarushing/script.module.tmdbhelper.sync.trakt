#!/usr/bin/python
# -*- coding: utf-8 -*-
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.sync.datasync import (
    SyncDataGetter,
    SyncDataGetterAllMoviesToWatch,
    SyncDataGetterAllShowsToWatch,
)


class TraktSyncDataGetterAllUnHiddenMoviesToWatch(SyncDataGetterAllMoviesToWatch):
    query_clauses = ('item_type=?', 'progress_watched_hidden_at IS NULL', )
    filter_keys = ('progress_watched_hidden_at', )


class TraktSyncDataGetterAllUnHiddenShowsToWatch(SyncDataGetterAllShowsToWatch):
    query_clauses = ('item_type=?', 'dropped_hidden_at IS NULL AND progress_watched_hidden_at IS NULL', )
    filter_keys = ('dropped_hidden_at', 'progress_watched_hidden_at', )


class TraktSyncDataGetterAllUnHiddenShowsInProgress(SyncDataGetter):
    calendar_startdate = -14
    calendar_days = 15

    @property
    def get_episode_watchedcount(self):
        return self.instance_syncdata.get_episode_watchedcount

    @property
    def get_episode_playcount(self):
        return self.instance_syncdata.get_episode_playcount

    @cached_property
    def calendar_data(self):
        return self.get_calendar_data()

    def get_calendar_data(self):
        return self.provider.calendar.get_episodes(self.calendar_startdate, self.calendar_days)

    @cached_property
    def calendar_episodes(self):
        return self.get_calendar_episodes()

    def get_calendar_episodes(self):
        from tmdbhelper.lib.addon.tmdate import date_in_range
        if not self.provider.settings.use_calendar:
            return

        if not self.calendar_data:
            return

        calendar = {}

        for i in self.calendar_data:
            try:
                # Check that date is still in range once utc_converted
                if not date_in_range(
                    i['first_aired'],
                    utc_convert=True,
                    start_date=self.calendar_startdate,
                    days=self.calendar_days):
                    continue

                # Ignore specials
                if i['episode']['season'] == 0:
                    continue

                show = calendar.setdefault(i['show']['ids']['tmdb'], {})
                show.setdefault(i['episode']['season'], []).append(i['episode']['number'])

            except KeyError:
                continue

        return calendar

    def is_calendar_watched(self, tmdb_id):
        if not self.calendar_episodes:
            return True
        if tmdb_id not in self.calendar_episodes:
            return True
        return all(
            self.is_calendar_season_watched(tmdb_id, season, episodes)
            for season, episodes in self.calendar_episodes[tmdb_id].items())

    def is_calendar_season_watched(self, tmdb_id, season, episodes):
        if not self.get_episode_watchedcount(tmdb_id, season):
            return False
        return all(self.get_episode_playcount(tmdb_id, season, episode) for episode in episodes)

    def is_inprogress_show(self, tmdb_id, aired_episodes, watched_episodes):
        if aired_episodes <= watched_episodes:
            if self.is_calendar_watched(tmdb_id):
                return False
        return True

    @cached_property
    def parent_getter(self):
        return self.get_parent_getter()

    def get_parent_getter(self):
        sd = self.instance_syncdata.get_all_unhidden_shows_started_getter()
        sd.additional_keys = self.parent_additional_keys
        return sd

    @cached_property
    def keys(self):
        return self.get_keys()

    def get_keys(self):
        return self.parent_getter.keys

    def get_sync_succeeded(self):
        if not self.parent_getter.sync_succeeded:
            return False
        return self.get_calendar_sync_succeeded()

    def get_calendar_sync_succeeded(self):
        if not self.provider.settings.use_calendar:
            return True
        if not any(item['aired_episodes'] <= item['watched_episodes'] for item in self.parent_getter.items):
            return True
        return self.calendar_data is not None

    @property
    def parent_additional_keys(self):
        return (
            'aired_episodes', 'watched_episodes', 'dropped_hidden_at', 'progress_watched_hidden_at',
            'last_watched_at', *(self.additional_keys or ()))

    def get_items(self):
        sd = self.parent_getter
        return [
            i for i in sd.items
            if self.is_inprogress_show(
                i['tmdb_id'],
                i['aired_episodes'],
                i['watched_episodes']
            )
        ]
