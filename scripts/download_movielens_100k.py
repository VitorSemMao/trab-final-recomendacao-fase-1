from __future__ import annotations

from io import BytesIO
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile


DOWNLOAD_URL = "https://files.grouplens.org/datasets/movielens/ml-100k.zip"
OUTPUT_DIR = Path("data/movielens-100k")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with urlopen(DOWNLOAD_URL) as response:
        archive_bytes = response.read()

    with ZipFile(BytesIO(archive_bytes)) as archive:
        archive.extractall(OUTPUT_DIR)

    print(f"Dataset extracted to: {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()
