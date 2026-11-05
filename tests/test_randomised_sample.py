"""Randomised Trakt widgets keep the same sample all day, for single and mixed (both) lists."""
import ast
import random
import unittest
from functools import cached_property
from pathlib import Path

from _core import stablerandom

SOURCE = Path(__file__).resolve().parents[1] / 'resources/lib/tmdbhelper_sync_trakt/directories/lists_random.py'
NAMES = ('ListTraktRandomisedProperties', 'ListTraktMixedRandomisedProperties', 'ListTraktRandomised')


class StandardProperties:
    pmax = 1

    def __init__(self):
        self.filtered_items = [f'{self.__class__.__name__}-{i}' for i in range(200)]


class Standard:
    def configure_list_properties(self, list_properties):
        return list_properties


def classes():
    tree = ast.parse(SOURCE.read_text())
    nodes = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name in NAMES]
    ns = {'random': random, 'cached_property': cached_property, 'convert_type': lambda *a, **k: 'movies',
          'stable_random': stablerandom.stable_random,
          'ListTraktStandardProperties': StandardProperties, 'ListTraktStandard': Standard}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(SOURCE), 'exec'), ns)
    return ns


def sample(paramstring, mixed=False):
    ns = classes()
    lister = ns['ListTraktRandomised']()
    lister.paramstring = paramstring
    props_class = ns['ListTraktMixedRandomisedProperties' if mixed else 'ListTraktRandomisedProperties']
    props = lister.configure_list_properties(props_class())
    if mixed:
        props.page, props.length, props.trakt_filters = 1, None, {}
    return props.sorted_items


WIDGET = 'info=trakt_trending_random&tmdb_type=movie&reload=1'
REFRESHED = 'info=trakt_trending_random&tmdb_type=movie&reload=2&page=2'


class RandomisedSample(unittest.TestCase):
    def test_refresh_and_next_page_keep_the_sample(self):
        self.assertEqual(sample(WIDGET), sample(REFRESHED))

    def test_other_widget_gets_other_sample(self):
        self.assertNotEqual(sample(WIDGET), sample('info=trakt_popular_random&tmdb_type=movie'))

    def test_mixed_list_is_stable_too(self):
        a = sample('info=trakt_trending_random&tmdb_type=both&reload=1', mixed=True)
        b = sample('info=trakt_trending_random&tmdb_type=both&reload=9', mixed=True)
        self.assertEqual(a, b)
        self.assertTrue(a)


if __name__ == '__main__':
    unittest.main()
