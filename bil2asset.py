"""
Python script to convert between rasterio supported map formats and TEOCO ASSET
Enterprise Map Data format.
author: Lucas Marcolongo
email: lucas@marcolongo.dev
"""
import argparse
import shutil
import sys
from abc import ABC
from enum import Enum
from pathlib import Path

import numpy as np
import rasterio

# get list of supported rasterio extension formats
SUPPORTED_RASTERIO_FORMATS = rasterio.drivers.raster_driver_extensions().keys()


# enum for supported teoco asset map data formats
class SUPPORTED_ASSET(Enum):
    DLU = "dlu"
    DTM = "dtm"


class Converter(ABC):
    """
    The following methods are used to convert between rasterio supported formats and TEOCO ASSET formats.
    """

    def __init__(
        self,
        input_file: Path,
        output_file: Path,
        type: SUPPORTED_ASSET,
    ):
        self.input_file = input_file
        self.output_file = output_file
        self.type = type
        self.input_format: SUPPORTED_RASTERIO_FORMATS = input_file.suffix[-3:]

    def convert(self):
        """
        Convert the input file to the output file.
        """
        # nodata value is 0 for DLU and -9999 for DTM
        nodata_value = 0 if self.type == SUPPORTED_ASSET.DLU else -9999

        # read the input dataset, check if it has a valid crs, convert it to a numpy array and set the nodata value
        with rasterio.open(self.input_file) as src:
            if src.crs is None:
                raise ValueError(f"Input file {self.input_file} has no crs.")
            data = src.read(1)
            data[data == src.nodata] = nodata_value
            # convert to signed 16-bit integer (asset format)
            data = np.array(data).astype(">i2")
            # update dest metadata
            dest_meta = src.meta.copy()
            dest_meta.update(
                dtype=rasterio.int16,
                nodata=nodata_value,
            )
        # save to output file
        with rasterio.open(self.output_file, "w", **dest_meta):
            pass
        # use numpy .tofile to ensure right endianess
        data.tofile(self.output_file)
        # update "BYTEORDER=I" to "BYTEORDER=M" line in the header file
        with open(str(self.output_file) + ".hdr", "r") as f:
            lines = f.readlines()
        with open(str(self.output_file) + ".hdr", "w") as f:
            for line in lines:
                if line.startswith("BYTEORDER"):
                    f.write("BYTEORDER=M\n")
                else:
                    f.write(line)
        # generate index.txt file in the format: <filename> <easting_min> <easting_max> <northing_min> <northing_max> <resolution>
        with open(self.output_file.parent / "index.txt", "w") as f:
            f.write(
                f"{self.output_file.name} {src.bounds.left} {src.bounds.right} {src.bounds.bottom} {src.bounds.top} {src.res[0]}\n"
            )
        # if the format is DLU, check for existence of any *.mnu file and copy it to the output directory
        if self.type == SUPPORTED_ASSET.DLU:
            for mnu_file in self.input_file.parent.glob(".mnu"):
                shutil.copy(mnu_file, self.output_file.parent)
        print(f"Converted {self.input_file} to {self.output_file}.")

    def validate(self):
        """
        Validates the input and output files.
        """
        self.validate_input_file()
        self.validate_output_file()

    def validate_input_file(self):
        """
        Validates the input file.
        """
        if not Path(self.input_file).exists():
            raise FileNotFoundError(f"Input file {self.input_file} does not exist.")
        if not Path(self.input_file).is_file():
            raise IsADirectoryError(f"Input file {self.input_file} is not a file.")
        if self.input_format not in SUPPORTED_RASTERIO_FORMATS:
            raise ValueError(
                f"Input file {self.input_file} is not a supported rasterio format."
            )

    def validate_output_file(self):
        """
        Validates the output file.
        """
        output_file_dir = Path(self.output_file).parent
        if Path(self.output_file).exists():
            raise FileExistsError(f"Output file {self.output_file} already exists.")
        if Path(self.output_file).is_dir():
            raise IsADirectoryError(f"Output file {self.output_file} is a directory.")
        if not output_file_dir.exists():
            # create the output directory if it doesn't exist
            output_file_dir.mkdir(parents=True, exist_ok=True)

    def run(self):
        """
        Validates all inputs and run the converter.
        """
        self.validate()
        self.convert()


# main function (parse args, create converter and run it)
def main():
    parser = argparse.ArgumentParser(
        description=(
            "Convert between rasterio supported formats and TEOCO ASSET formats."
        )
    )
    parser.add_argument(
        "input_file",
        help="Input file to convert.",
        type=Path,
    )
    parser.add_argument(
        "output_file",
        help="Output file to convert to.",
        type=Path,
    )
    parser.add_argument(
        "--type",
        help="Type of the output file. Supported types: dlu, dtm.",
        type=str,
        choices=SUPPORTED_ASSET,
        default=SUPPORTED_ASSET.DLU,
    )
    args = parser.parse_args()
    converter = Converter(args.input_file, args.output_file)
    converter.run()


if __name__ == "__main__":
    main()
    sys.exit(0)
