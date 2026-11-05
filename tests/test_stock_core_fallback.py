"""With stock TMDb Helper (no stablerandom module) the provider must still load and pick at random."""
import ast
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / 'resources/lib/tmdbhelper_sync_trakt/directories/lists_random.py'


class StockCoreFallback(unittest.TestCase):
    def test_import_failure_falls_back(self):
        tree = ast.parse(SOURCE.read_text())
        node = next(n for n in tree.body if isinstance(n, ast.Try))
        ns = {}
        import builtins, random
        real = builtins.__import__

        def fake(name, *a, **k):
            if name == 'tmdbhelper.lib.addon.stablerandom':
                raise ImportError(name)
            return real(name, *a, **k)
        builtins.__import__ = fake
        try:
            exec(compile(ast.fix_missing_locations(ast.Module(body=[ast.Import(names=[ast.alias('random')]), node], type_ignores=[])),
                         str(SOURCE), 'exec'), ns)
        finally:
            builtins.__import__ = real
        self.assertIs(ns['stable_random']('info=x'), random)
        self.assertIn(ns['stable_list_choice']('info=x', [1, 2, 3]), (1, 2, 3))


if __name__ == '__main__':
    unittest.main()
