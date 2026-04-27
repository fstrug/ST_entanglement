# coding: utf-8

"""
Basic import checks for core analysis dependencies.
"""

import importlib
import unittest


class DependencyImportTest(unittest.TestCase):

    modules = (
        "law",
        "luigi",
        "order",
        "cmsdb",
        "columnflow",
        # "awkward",
        "numpy",
        "st_entanglement",
        "st_entanglement.selection.lepton",
    )

    def test_imports(self):
        for module_name in self.modules:
            with self.subTest(module=module_name):
                importlib.import_module(module_name)


if __name__ == "__main__":
    unittest.main()
