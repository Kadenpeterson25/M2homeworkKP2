from __future__ import annotations

import re
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

DATA_DIR = Path('data')
OUTPUT_DIR = Path('outputs')
OUTPUT_CSV = OUTPUT_DIR / 'macc_course_ranking_2024.csv'
OUTPUT_PNG = OUTPUT_DIR / 'macc_course_ranking_2024.png'


def find_excel_file(data_dir: Path) -> Path:
    excel_files = sorted(data_dir.glob('*.xlsx'))
    if not excel_files:
        raise FileNotFoundError(f'No .xlsx file found in {data_dir.resolve()}')
    if len(excel_files) > 1:
        raise ValueError(f'Expected exactly one .xlsx file in {data_dir.resolve()}, found {len(excel_files)}')
    return excel_files[0]


def extract_course_name(column_name: str) -> str:
    course_match = re.search(r'ACC\s*\d+[A-Z]*\s+[^\-\n]+', column_name)
    if course_match:
        return ' '.join(course_match.group(0).split())
    trailing = column_name.split(' - ')[-1].strip()
    return ' '.join(trailing.split())


def main() -> None:
    input_file = find_excel_file(DATA_DIR)

    # Header row 2 contains human-readable survey question text.
    df = pd.read_excel(input_file, header=1)

    # Drop Qualtrics metadata row if present.
    response_id_col = 'Response ID'
    if response_id_col in df.columns:
        df = df[~df[response_id_col].astype(str).str.startswith('{"ImportId"', na=False)]

    rating_columns = [
        col
        for col in df.columns
        if isinstance(col, str) and col.startswith('Rate ACC')
    ]

    if not rating_columns:
        raise ValueError('No overall course rating columns found. Expected columns starting with "Rate ACC".')

    course_name_column = 'course_name'
    rating_value_column = 'course_rating'

    long_df = (
        df[rating_columns]
        .melt(var_name=course_name_column, value_name=rating_value_column)
        .assign(
            course_name=lambda x: x[course_name_column].map(extract_course_name),
            course_rating=lambda x: pd.to_numeric(x[rating_value_column], errors='coerce'),
        )
        .dropna(subset=['course_rating'])
    )

    ranked = (
        long_df.groupby('course_name', as_index=False)
        .agg(
            mean_rating=('course_rating', 'mean'),
            response_count=('course_rating', 'size'),
        )
        .sort_values(by=['mean_rating', 'course_name'], ascending=[False, True], kind='mergesort')
        .reset_index(drop=True)
    )
    ranked.insert(0, 'rank', ranked.index + 1)
    ranked['mean_rating'] = ranked['mean_rating'].round(4)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ranked.to_csv(OUTPUT_CSV, index=False)

    chart_df = ranked.sort_values('mean_rating', ascending=True)
    fig, ax = plt.subplots(figsize=(12, max(4, 0.55 * len(chart_df))))
    ax.barh(chart_df['course_name'], chart_df['mean_rating'], color='#4C78A8')
    ax.set_xlabel('Average Course Rating (1-5)')
    ax.set_ylabel('Course')
    ax.set_title('2024 MAcc Course Ratings Ranked by Average Score')
    ax.set_xlim(0, 5)

    for idx, value in enumerate(chart_df['mean_rating']):
        ax.text(value + 0.03, idx, f'{value:.2f}', va='center', fontsize=9)

    fig.tight_layout()
    fig.savefig(OUTPUT_PNG, dpi=200)


if __name__ == '__main__':
    main()
