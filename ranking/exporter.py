import pandas as pd


def export_rankings(rows, output_path):

    df = pd.DataFrame(rows)

    df.to_csv(
        output_path,
        index=False
    )