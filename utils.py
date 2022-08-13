import datetime
from typing import List

import pandas as pd


def get_snp500_symbols() -> List[str]:
    df = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
    return df['Symbol'].values.tolist()


def generate_relevant_years(number_of_years: int) -> List[int]:
    current_year = datetime.datetime.utcnow().year
    return list(range(current_year, current_year - number_of_years, -1))
