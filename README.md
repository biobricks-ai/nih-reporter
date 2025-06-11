# NIH RePORTER — U.S. Federally Funded Biomedical Research Grants

> **Brick ID:** `biobricks-ai/nih-reporter`
>
> **Release pinned:** **RePORTER Export (snapshot 2024‑12‑01)**
> **Primary assets:** partitioned **Parquet** tables derived from the official CSV dump at [https://reporter.nih.gov/exporter](https://reporter.nih.gov/exporter)
> **Licence:** Public Domain (U.S. Government Works)

---

## What is NIH RePORTER?

NIH RePORTER is the public database of all NIH‑funded research projects since 1985, including abstracts, budgets, PIs, institutions, peer‑review details, and outcomes (publications, patents, clinical trials).  The NIH provides yearly *EXPORTER* dumps as zipped CSV files.  This brick converts those raw CSVs into columnar Parquet so you can query them in seconds with Arrow, DuckDB, Spark, or Pandas.

---

## File layout

The brick mirrors the NIH EXPORTER directory structure verbatim.  The following **five** Parquet datasets are what you’ll see when you run `biobricks.assets("nih-reporter")` (row counts from the current 2024‑12‑01 snapshot):

| Asset attribute (`nih.<attr>`)                     |          Rows | Notes                                                                       |
| -------------------------------------------------- | ------------: | --------------------------------------------------------------------------- |
| `ExPORTER_projects_RePORTER_PRJ_C_parquet`         | **2 875 061** | Core grant‑year table (`PRJ_C.csv`)                                         |
| `ExPORTER_projects_RePORTER_PRJFUNDING_C_parquet`  |   **840 226** | Funding‑only slice (`PRJFUNDING_C.csv`)                                     |
| `ExPORTER_abstracts_RePORTER_PRJABS_C_parquet`     | **2 523 979** | Project abstracts (`PRJABS_C.csv`)                                          |
| `ExPORTER_clinicalstudies_ClinicalStudies_parquet` |    **36 346** | Grant ↔ ClinicalTrials.gov linkage                                          |
| `nih_reporter_parquet`                             |   *composite* | Concatenation of the four project‑centric tables above (handy scratch file) |

**Tip :** call

```python
import biobricks, pyarrow.parquet as pq
nih = biobricks.assets("nih-reporter")
for k, p in nih.__dict__.items():
    print(k, pq.read_metadata(p).num_rows)
```

if you want to verify these counts on your own snapshot.

---

## Quick start

The fastest way to look around is to list all Parquet files shipped in the brick:

```python
import biobricks, pathlib
nih = biobricks.assets("nih-reporter")  # SimpleNamespace with attributes

for name, path in nih.__dict__.items():
    print(f"{name} → {path}")
```

Need the first five oncology grants from 2024?

```python
import pandas as pd, biobricks, pyarrow.dataset as ds
proj_path = biobricks.assets("nih-reporter").projects_parquet
projects = ds.dataset(proj_path)  # Arrow dataset

oncology_2024 = projects.to_table(
    filter = (
        (ds.field("fy") == 2024) &
        (ds.field("abstract_text").utf8_lower().str_contains("cancer"))
    ),
    columns=["project_num", "project_title", "total_cost", "org_city", "abstract_text"]
).to_pandas().head()
print(oncology_2024)
```

---

## Provenance & build pipeline

| Stage             | Script                     | Action                                                                                            |
| ----------------- | -------------------------- | ------------------------------------------------------------------------------------------------- |
| **Download**      | `stages/1_fetch.sh`        | Pulls the latest `2024*CSV.zip` bundle from reporter.nih.gov/exporter and verifies MD5 checksums. |
| **Unzip**         | `stages/2_unzip.sh`        | Extracts eight CSVs (projects, orgs, PIs …).                                                      |
| **Convert**       | `stages/3_csv2parquet.py`  | Streams each CSV into Arrow, writes to `*.parquet` (Snappy), preserving all columns and dtypes.   |
| **Relationships** | `stages/4_bridge_tables.R` | Explodes multi‑PI and multi‑org columns into tidy bridge tables.                                  |
| **Manifest**      | `stages/5_manifest.R`      | Captures row counts + SHA‑256 hashes for reproducibility.                                         |

The pipeline is orchestrated with **DVC**; each monthly NIH release receives a Git commit hash so you can pin via `brick_pull nih-reporter@<hash>`.

---

## Update cadence

NIH posts a fresh EXPORTER bundle **monthly**.  A GitHub Action checks on the 5th of each month and rebuilds the brick if a newer zip appears.  Expect ≈ 12 snapshots per year (one per NIH release).

---

## Tips & gotchas

* **Inflation adjusted dollars** – only nominal costs are provided; adjust externally if you need constant dollars.
* **Multiyear grants** – one `projects` row per fiscal‑year slice.  Aggregate by `core_project_num` for the full award history.
* **Organisation IDs** – `org_duns` is occasionally missing; join via `org_name` + `org_city` for older records.
* **UTF‑8 quirks** – abstracts occasionally carry Windows‑1252 artifacts; Arrow keeps them as UTF‑8 but you may need `.str.encode("latin-1", errors="ignore")` cleanup.

---

## Road‑map

* Add **clinical\_trials.parquet** once NIH begins exporting the new CT x Grant linkage table (expected 2026).
* Build **Delta Lake mirror** with ACID merges for incremental NIH updates.

---

## Citation

```
NIH Research Portfolio Online Reporting Tools (RePORTER). EXPORTER files, snapshot 2024‑12‑01.  
BioBricks.ai – nih‑reporter brick, commit <hash>.
```

---

## Licence

U.S. Government Works are in the **public domain**.  You are free to use, redistribute, and remix the NIH RePORTER data without restriction; attribution to NIH is appreciated.
