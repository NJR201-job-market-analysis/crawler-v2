import pandas as pd
from pathlib import Path

def save_to_csv(result, filename):
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)
    
    # save to csv
    df = pd.json_normalize(result)
    csv_filename = data_dir / f"{filename}.csv"
    df.to_csv(csv_filename, encoding="utf-8")