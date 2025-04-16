import pandas as pd, zipfile, os, logging
from tqdm import tqdm

def safe_csv_to_pdf(zipf, csv, encoding=None):
    if encoding is None:
        encoding = 'UTF-8'
    try:
        with zipf.open(csv) as f:
            return pd.read_csv(f, encoding=encoding, dtype=str, on_bad_lines='skip')
    except pd.errors.ParserError as e:
        logging.warning(f"Error parsing {csv}: {e}")
        return None

def extract_df_from_zip(zip, encoding=None):
    with zipfile.ZipFile(zip, 'r') as zipf:
        csvs = [f for f in zipf.namelist() if f.endswith('.csv')]
        dfs = [safe_csv_to_pdf(zipf, csv, encoding=encoding) for csv in csvs]
        dfs = [df for df in dfs if df is not None]
        return pd.concat(dfs, ignore_index=True) if len(dfs) > 0 else None

# EXTRACT PROJECTS ============================================================
def extract_projects():
    dir = 'download/projects'
    zips = [os.path.join(dir, f) for f in os.listdir(dir) if f.endswith('.zip')]
    dfs = [extract_df_from_zip(zip, encoding='UTF-8') for zip in tqdm(zips)]
    return pd.concat(dfs, ignore_index=True)

# EXTRACT ABSTRACTS ============================================================
def extract_abstracts():
    dir = 'download/abstracts'
    zips = [os.path.join(dir, f) for f in os.listdir(dir) if f.endswith('.zip')]
    dfs = [extract_df_from_zip(zip, encoding='ISO-8859-1') for zip in tqdm(zips)]
    return pd.concat(dfs, ignore_index=True)

# PUT IT ALL TOGETHER ============================================================
projects = extract_projects()
abstracts = extract_abstracts()

nih_reporter = projects.merge(abstracts, on='APPLICATION_ID', how='left')

# Example of how to convert data types
num_cols = ['APPLICATION_ID', 'FY', 'ORG_DISTRICT', 'SUBPROJECT_ID', 'SUPPORT_YEAR', 'DIRECT_COST_AMT', 'INDIRECT_COST_AMT', 'TOTAL_COST', 'TOTAL_COST_SUB_PROJECT']
date_columns = ['AWARD_NOTICE_DATE', 'BUDGET_START', 'BUDGET_END', 'PROJECT_START', 'PROJECT_END']

for column in num_cols:
    nih_reporter[column] = pd.to_numeric(nih_reporter[column], errors='coerce')

for column in date_columns:
    nih_reporter[column] = pd.to_datetime(nih_reporter[column], errors='coerce')

# transform 'FY' column to int32
nih_reporter['FY'] = nih_reporter['FY'].astype('Int32')

# group by fiscal year and write to a parquet dataset (one file per fiscal year)
for fy, df in tqdm(nih_reporter.groupby('FY')):
    os.makedirs(f'brick/nih_reporter.parquet/FY={fy}', exist_ok=True)
    df.to_parquet(f'brick/nih_reporter.parquet/FY={fy}/part-0.parquet', index=False)
