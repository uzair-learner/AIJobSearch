from io import BytesIO

import pandas as pd

from app.importers.perm_importer import PermImporter


def test_importer_can_be_constructed() -> None:
    importer = PermImporter()
    assert importer is not None
