# M2homeworkKP2

This repository includes an automated, deterministic workflow to rank 2024 MAcc courses by average student rating from the graduate exit survey Excel dataset.

## What the workflow does

1. Reads the `.xlsx` survey file from `data/`.
2. Uses the overall course rating columns (`Rate ACC ...`) as the numeric rating source.
3. Converts wide rating columns into a long table with:
   - `course_name`
   - `course_rating`
4. Cleans and validates ratings:
   - coerces ratings to numeric
   - drops blank or missing ratings
5. Computes by course:
   - mean rating
   - response count
6. Produces deterministic ranking:
   - sort by `mean_rating` descending
   - break ties alphabetically by `course_name`
7. Writes outputs to `outputs/`:
   - `macc_course_ranking_2024.csv`
   - `macc_course_ranking_2024.png`

## Run locally

```bash
pip install -r requirements.txt
python scripts/rank_macc_courses.py
```

## GitHub Actions

The workflow at `.github/workflows/macc-course-ranking.yml` runs automatically on each push and can also be started manually via **workflow_dispatch**.
