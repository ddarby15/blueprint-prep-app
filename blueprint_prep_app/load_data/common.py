from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def load_csv_data(
    filename: str,
    season_folder: int = 2026,
    subdir: str = "transformed_data",
) -> pd.DataFrame:
    """
    Load a CSV file from the project data directory.

    Parameters
    ----------
    filename : str
        Name of the CSV file to load.

    season_folder : int, default=2026
        Folder year under /data/ to load from.

    subdir : str, default="transformed_data"
        Subdirectory inside the season folder.

    Returns
    -------
    pd.DataFrame
        Loaded dataframe.
    """
    file_path = PROJECT_ROOT / "data" / str(season_folder) / subdir / filename
    return pd.read_csv(file_path)


