"""Load TMDbHelper core helpers from the sibling fork checkout (override with TMDBHELPER_CORE)."""
import importlib.util
import os
from pathlib import Path

CORE = Path(os.environ.get('TMDBHELPER_CORE', Path(__file__).resolve().parents[2] / 'plugin.video.themoviedb.helper'))


def load(relpath, name):
    spec = importlib.util.spec_from_file_location(name, CORE / relpath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


stablerandom = load('resources/tmdbhelper/lib/addon/stablerandom.py', 'stablerandom')
