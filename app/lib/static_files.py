from pathlib import Path

from litestar.static_files.config import StaticFilesConfig

from .constants import STATIC_DIR, STATIC_PATH

here = Path(__file__).parent


config = StaticFilesConfig(directories=[here / STATIC_DIR], path=STATIC_PATH)
