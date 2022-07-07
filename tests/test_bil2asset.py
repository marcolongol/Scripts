from pathlib import Path

from bil2asset import Converter, SUPPORTED_ASSET

BASE_DIR = Path(__file__).parent
DATA_FOLDER = BASE_DIR / "data"


class TestConverters:
    """
    Class for testing the Converter class.
    """

    def test_dtm_converter(self):
        converter = Converter(
            DATA_FOLDER / "mapdata" / "dtm" / "dtm.bil",
            DATA_FOLDER / "output" / "dtm" / "dtm",
            SUPPORTED_ASSET.DTM,
        )
        converter.run()

    def test_dlu_converter(self):
        converter = Converter(
            DATA_FOLDER / "mapdata" / "dlu" / "dlu.bil",
            DATA_FOLDER / "output" / "dlu" / "dlu",
            SUPPORTED_ASSET.DLU,
        )
        converter.run()
