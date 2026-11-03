IDENTIFIER_COLUMNS = {
    'id': {
        'data': 'TEXT PRIMARY KEY',
    },
    'item_type': {
        'data': 'TEXT',
        'indexed': True,
    },
    'query': {
        'data': 'TEXT',
        'indexed': True,
    },
    'tmdb_id': {
        'data': 'INTEGER',
        'indexed': True,
    },
    'tmdb_ep': {
        'data': 'INTEGER',
        'indexed': True,
    },
    'tvdb_id': {
        'data': 'INTEGER',
        'indexed': True,
    },
    'imdb_id': {
        'data': 'TEXT',
        'indexed': True,
    },
    'slug_id': {
        'data': 'TEXT',
        'indexed': True,
    },
    'trakt_id': {
        'data': 'INTEGER',
        'indexed': True,
    },
    'season': {
        'data': 'INTEGER',
        'indexed': True,
    },
    'episode': {
        'data': 'INTEGER',
        'indexed': True,
    },
    'episode_slug_id': {'data': 'TEXT'},
    'expiry': {'data': 'INTEGER'},
}
