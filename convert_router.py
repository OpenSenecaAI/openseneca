import pandas as pd
import fire

class Converter(object):
    def csv_to_pickle(self, csv_path: str, pickle_path: str):
        # Load the CSV file
        df = pd.read_csv(csv_path)

        # Save as a pickle file
        df.to_pickle(pickle_path)

        print(f'Successfully converted {csv_path} to {pickle_path}')

def main():
    fire.Fire(Converter)


if __name__ == "__main__":
    """
    python convert_router.py csv_to_pickle \
        --csv_path table_weights.csv \
        --pickle_path openseneca/weights.pk
    """
    main()