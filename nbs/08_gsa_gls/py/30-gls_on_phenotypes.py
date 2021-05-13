# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: all,-execution,-papermill,-trusted
#     formats: ipynb,py//py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.7.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown] tags=[]
# # Environment variables

# %%
# %load_ext autoreload
# %autoreload 2

# %%
import conf

# %% tags=[]
N_JOBS = 1  # conf.GENERAL["N_JOBS"]
display(N_JOBS)

# %% tags=[]
# %env MKL_NUM_THREADS=$N_JOBS
# %env OPEN_BLAS_NUM_THREADS=$N_JOBS
# %env NUMEXPR_NUM_THREADS=$N_JOBS
# %env OMP_NUM_THREADS=$N_JOBS

# %% [markdown]
# # Modules

# %%
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

import statsmodels.api as sm
import numpy as np
import pandas as pd
from sklearn.preprocessing import scale
from tqdm import tqdm

from gls import GLSPhenoplier

# %% [markdown]
# # Settings

# %%
OUTPUT_DIR = conf.RESULTS["GLS"]
display(OUTPUT_DIR)

OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

# %% [markdown]
# # Load data

# %% [markdown]
# ## PhenomeXcan (S-MultiXcan)

# %%
INPUT_SUBSET = "z_score_std"

# %%
INPUT_STEM = "projection-smultixcan-efo_partial-mashr-zscores"

# %%
input_filepath = Path(
    conf.RESULTS["DATA_TRANSFORMATIONS_DIR"],
    INPUT_SUBSET,
    f"{INPUT_SUBSET}-{INPUT_STEM}.pkl",
).resolve()

# %%
data = pd.read_pickle(input_filepath)

# %%
data.shape

# %%
data.head()

# %% [markdown]
# ## Clustering results

# %%
CONSENSUS_CLUSTERING_DIR = Path(
    conf.RESULTS["CLUSTERING_DIR"], "consensus_clustering"
).resolve()

display(CONSENSUS_CLUSTERING_DIR)

# %%
input_file = Path(CONSENSUS_CLUSTERING_DIR, "best_partitions_by_k.pkl").resolve()
display(input_file)

# %%
best_partitions = pd.read_pickle(input_file)

# %%
best_partitions.shape

# %%
best_partitions.head()

# %% [markdown]
# ## MultiPLIER summary

# %%
multiplier_model_summary = pd.read_pickle(conf.MULTIPLIER["MODEL_SUMMARY_FILE"])

# %%
multiplier_model_summary.shape

# %%
multiplier_model_summary.head()

# %%
well_aligned_lvs = multiplier_model_summary[
    (multiplier_model_summary["FDR"] < 0.05) | (multiplier_model_summary["AUC"] >= 0.75)
]

display(well_aligned_lvs.shape)
display(well_aligned_lvs.head())

# %%
well_aligned_lv_codes = set([f"LV{lvi}" for lvi in well_aligned_lvs["LV index"]])

# %%
len(well_aligned_lv_codes)

# %%
list(well_aligned_lv_codes)[:5]

# %% [markdown]
# # Select partition / cluster pairs

# %%
# key: a tuple (partition_k, cluster_id)
# value: a list of tuples
# this specifies
PHENOTYPES_LVS_CONFIG = {
    # cardiovascular
    (29, 14): [(16, 15)],
    (29, 16): [(26, 13), (16, 15)],
    (29, 11): [(26, 13), (16, 15)],
    (29, 21): [(26, 25), (22, 0), (16, 15)],
    (29, 17): [],
    # autoimmune
    (29, 8): [(25, 18), (22, 8)],
    (29, 26): [(25, 12), (25, 18), (22, 8)],
    (29, 13): [(25, 12), (22, 8)],
    # keratometry
    (29, 10): [],
    # heel bone mineral density
    (29, 15): [],
    # hapiness
    (29, 27): [],
    # asthma
    (29, 12): [],
}

# %%
CLUSTER_LV_DIR = conf.RESULTS["CLUSTERING_INTERPRETATION"]["BASE_DIR"] / "cluster_lvs"
assert CLUSTER_LV_DIR.exists()

display(CLUSTER_LV_DIR)


# %%
def _get_lvs_data(part_k, cluster_idx):
    cluster_lvs = pd.read_pickle(
        CLUSTER_LV_DIR
        / f"part{part_k}"
        / f"cluster_interpreter-part{part_k}_k{cluster_idx}.pkl"
    )

    #     # keep well-aligned lvs only
    #     cluster_lvs = cluster_lvs[
    #         cluster_lvs.index.astype(str).isin(well_aligned_lvs["LV index"])
    #     ]

    cluster_lvs["cluster"] = cluster_idx

    return list(cluster_lvs["name"])


# %%
_get_lvs_data(29, 11)[:5]

# %% [markdown]
# # GLSPhenoplier

# %% [markdown]
# ## Get list of phenotypes/lvs pairs

# %%
phenotypes_lvs_pairs = []

for (part_k, cluster_id), extra_for_lvs in PHENOTYPES_LVS_CONFIG.items():
    part = best_partitions.loc[part_k, "partition"]

    # get traits
    cluster_traits = data.index[part == cluster_id]

    # get extra lvs
    lv_list = _get_lvs_data(part_k, cluster_id)

    for extra_part_k, extra_cluster_id in extra_for_lvs:
        extra_lv_list = _get_lvs_data(part_k, cluster_id)
        lv_list.extend(extra_lv_list)

    for phenotype_code in cluster_traits:
        for lv_code in lv_list:
            phenotypes_lvs_pairs.append(
                {
                    "phenotype_part_k": part_k,
                    "phenotype_cluster_id": cluster_id,
                    "phenotype": phenotype_code,
                    "lv": lv_code,
                }
            )

phenotypes_lvs_pairs = pd.DataFrame(phenotypes_lvs_pairs).drop_duplicates()

# %%
phenotypes_lvs_pairs = phenotypes_lvs_pairs.sort_values("phenotype")

# %%
phenotypes_lvs_pairs.shape

# %%
phenotypes_lvs_pairs.head()

# %% [markdown]
# ## Run

# %%
from utils import chunker

# %%
output_file = OUTPUT_DIR / "gls_phenotypes.pkl"
display(output_file)

# %%
phenotype_lvs_chunks = chunker(phenotypes_lvs_pairs, 25)
phenotype_lvs_chunks = list(phenotype_lvs_chunks)

# %%
len(phenotype_lvs_chunks)


# %%
def _process_phenotypes(chunk):
    results = []

    for idx, row in chunk.iterrows():
        phenotype_code = row["phenotype"]
        lv_code = row["lv"]

        gls_model = GLSPhenoplier()
        gls_model.fit_named(lv_code, phenotype_code)
        res = gls_model.results

        results.append(
            {
                "part_k": row["phenotype_part_k"],
                "cluster_id": row["phenotype_cluster_id"],
                "phenotype": phenotype_code,
                "lv": lv_code,
                "lv_with_pathway": lv_code in well_aligned_lv_codes,
                "coef": res.params.loc["lv"],
                "pvalue": res.pvalues.loc["lv"],
                "summary": gls_model.results_summary,
            }
        )

    return results


# %%
all_results = []

pbar = tqdm(total=phenotypes_lvs_pairs.shape[0])

with ProcessPoolExecutor(max_workers=conf.GENERAL["N_JOBS"]) as executor:
    tasks = [
        executor.submit(_process_phenotypes, chunk) for chunk in phenotype_lvs_chunks
    ]

    for idx, future in enumerate(as_completed(tasks)):
        res = future.result()
        all_results.extend(res)

        if (idx % 10) == 0:
            pd.DataFrame(results).to_pickle(output_file)

        pbar.update(len(res))

pbar.close()

# %%
results = pd.DataFrame(results)

# %%
results.shape

# %%
results.head()

# %%
results.sort_values("pvalue").head(10)

# %% [markdown]
# ## Save

# %%
results.to_pickle(output_file)

# %%