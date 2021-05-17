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

# %% tags=[]
# %load_ext autoreload
# %autoreload 2

# %% tags=[]
import conf

# %% tags=[]
N_JOBS = conf.GENERAL["N_JOBS"]
display(N_JOBS)

# %% tags=[]
# %env MKL_NUM_THREADS=$N_JOBS
# %env OPEN_BLAS_NUM_THREADS=$N_JOBS
# %env NUMEXPR_NUM_THREADS=$N_JOBS
# %env OMP_NUM_THREADS=$N_JOBS

# %% [markdown] tags=[]
# # Modules

# %% tags=[]
from pathlib import Path

import statsmodels.api as sm
import numpy as np
import pandas as pd
from sklearn.preprocessing import scale
from tqdm import tqdm

from gls import GLSPhenoplier

# %% [markdown] tags=[]
# # Settings

# %% tags=[]
OUTPUT_DIR = conf.RESULTS["GLS"]
display(OUTPUT_DIR)

OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

# %% [markdown] tags=[]
# # Load data

# %% [markdown] tags=[]
# ## eMERGE to PhenomeXcan maps

# %% tags=[]
# FIXME: hardcoded
input_filepath = Path(
    "/home/miltondp/projects/labs/greenelab/phenoplier/base/data/emerge",
    "eMERGE_III_PMBB_GSA_v2_2020_phecode_AFR_EUR_cc50_counts_w_dictionary.txt",
).resolve()
display(input_filepath)

# %% tags=[]
emerge_traits_df = pd.read_csv(
    input_filepath,
    sep="\t",
    dtype={"phecode": str},
    usecols=["phecode", "phenotype", "category"],
)

# %% tags=[]
emerge_traits_df = emerge_traits_df.rename(
    columns={
        "phenotype": "phecode_phenotype",
        "category": "phecode_category",
    }
)

# %% tags=[]
emerge_traits_df.shape

# %% tags=[]
emerge_traits_df.head()

# %% [markdown] tags=[]
# ## eMERGE to PhenomeXcan maps

# %% tags=[]
# FIXME: hardcoded
emerge_phenomexcan_maps_filepath = Path(
    "/home/miltondp/projects/labs/greenelab/phenoplier/base/data/emerge",
    "phecodes_phenomexcan_maps.tsv",
).resolve()
display(emerge_phenomexcan_maps_filepath)

# %% tags=[]
emerge_phenomexcan_maps = pd.read_csv(
    emerge_phenomexcan_maps_filepath, sep="\t", dtype={"phecode": str}
)

# %% tags=[]
emerge_phenomexcan_maps = emerge_phenomexcan_maps.dropna(
    subset=["phecode", "phenomexcan"], how="any"
)

# %% tags=[]
emerge_phenomexcan_maps.shape

# %% tags=[]
emerge_phenomexcan_maps.head()

# %% [markdown] tags=[]
# ## eMERGE (S-MultiXcan) projection

# %% tags=[]
# FIXME hardcoded
input_filepath = Path(
    "/home/miltondp/projects/labs/greenelab/phenoplier/base/results/projections",
    "projection-emerge-smultixcan-mashr-zscores.pkl",
).resolve()
display(input_filepath)

# %% tags=[]
emerge_projection = pd.read_pickle(input_filepath)

# %% tags=[]
emerge_projection.shape

# %% tags=[]
emerge_projection.head()

# %% [markdown] tags=[]
# ## eMERGE (S-MultiXcan) projection

# %% tags=[]
# FIXME: path hardcoded
emerge_smultixcan_projection_filepath = Path(
    "/home/miltondp/projects/labs/greenelab/phenoplier/base/data/emerge/gene_assoc/emerge-smultixcan-mashr-zscores.pkl"
).resolve()

display(emerge_smultixcan_projection_filepath)

# %% tags=[]
_tmp = pd.read_pickle(emerge_smultixcan_projection_filepath)

# %% tags=[]
_tmp.shape

# %% tags=[]
_tmp.head()

# %% [markdown] tags=[]
# ## GLS results on PhenomeXcan

# %% tags=[]
input_filepath = conf.RESULTS["GLS"] / "gls_phenotypes.pkl"
display(input_filepath)

# %% tags=[]
gls_phenomexcan = pd.read_pickle(input_filepath)

# %% tags=[]
gls_phenomexcan.shape

# %% tags=[]
gls_phenomexcan.head()

# %% [markdown] tags=[]
# ## MultiPLIER summary

# %% tags=[]
multiplier_model_summary = pd.read_pickle(conf.MULTIPLIER["MODEL_SUMMARY_FILE"])

# %% tags=[]
multiplier_model_summary.shape

# %% tags=[]
multiplier_model_summary.head()

# %% tags=[]
well_aligned_lvs = multiplier_model_summary[
    (multiplier_model_summary["FDR"] < 0.05) | (multiplier_model_summary["AUC"] >= 0.75)
]

display(well_aligned_lvs.shape)
display(well_aligned_lvs.head())

# %% tags=[]
well_aligned_lv_codes = set([f"LV{lvi}" for lvi in well_aligned_lvs["LV index"]])

# %% tags=[]
len(well_aligned_lv_codes)

# %% tags=[]
list(well_aligned_lv_codes)[:5]

# %% [markdown] tags=[]
# # Select LV from previous GLS run on PhenomeXcan

# %% tags=[]
gls_phenomexcan_lvs = gls_phenomexcan["lv"].unique()

# %% tags=[]
gls_phenomexcan_lvs.shape

# %% tags=[]
gls_phenomexcan_lvs

# %% [markdown] tags=[]
# # Select eMERGE traits

# %% tags=[]
gls_phenomexcan_traits = gls_phenomexcan["phenotype"].unique()

# %% tags=[]
gls_phenomexcan_traits.shape

# %% tags=[]
gls_phenomexcan_in_emerge = emerge_phenomexcan_maps[
    (emerge_phenomexcan_maps["efo"].isin(gls_phenomexcan_traits))
    | (emerge_phenomexcan_maps["phenomexcan"].isin(gls_phenomexcan_traits))
]

# %% tags=[]
gls_phenomexcan_in_emerge

# %% tags=[]
gls_emerge_phecodes = gls_phenomexcan_in_emerge["phecode"].unique().tolist()

# %% tags=[]
# these are the mapped traits from PhenomeXcan to phecodes
gls_emerge_phecodes

# %% tags=[]
# phecode_to_desc_map = emerge_traits_df[["phecode", "phecode_phenotype"]].set_index("phecode").squeeze().to_dict()

# %% [markdown] tags=[]
# # GLSPhenoplier

# %% [markdown] tags=[]
# ## Get list of phenotypes/lvs pairs

# %% tags=[]
phenotypes_lvs_pairs = []

# for lvs run for PhenomeXcan, I take the top traits in eMERGE + global mapped phenotypes
for lv in gls_phenomexcan_lvs:
    lv_traits = emerge_projection.loc[lv]
    lv_traits = lv_traits[lv_traits > 0.0]
    lv_traits = lv_traits.sort_values(ascending=False).head(20)

    for phenotype_code in set(lv_traits.index.tolist() + gls_emerge_phecodes):
        phenotypes_lvs_pairs.append(
            {
                "phenotype": phenotype_code,
                "lv": lv,
            }
        )

phenotypes_lvs_pairs = pd.DataFrame(phenotypes_lvs_pairs).drop_duplicates()

# %% tags=[]
phenotypes_lvs_pairs = phenotypes_lvs_pairs.sort_values("phenotype").reset_index(
    drop=True
)

# %% tags=[]
phenotypes_lvs_pairs.shape

# %% tags=[]
phenotypes_lvs_pairs.head()

# %% [markdown] tags=[]
# ## Run

# %% tags=[]
output_file = OUTPUT_DIR / "gls_phenotypes-emerge.pkl"
display(output_file)

# %% tags=[]
results = []

pbar = tqdm(total=phenotypes_lvs_pairs.shape[0])

for idx, row in phenotypes_lvs_pairs.iterrows():
    phenotype_code = row["phenotype"]
    lv_code = row["lv"]

    pbar.set_description(f"{phenotype_code} - {lv_code}")

    gls_model = GLSPhenoplier(
        smultixcan_result_set_filepath=emerge_smultixcan_projection_filepath
    )
    gls_model.fit_named(lv_code, phenotype_code)
    res = gls_model.results

    results.append(
        {
            "phenotype": phenotype_code,
            "lv": lv_code,
            "lv_with_pathway": lv_code in well_aligned_lv_codes,
            "coef": res.params.loc["lv"],
            "pvalue": res.pvalues.loc["lv"],
            "summary": gls_model.results_summary,
        }
    )

    if (idx % 10) == 0:
        pd.DataFrame(results).to_pickle(output_file)

    pbar.update(1)

pbar.close()

# %% tags=[]
results = pd.DataFrame(results)

# %% tags=[]
results.shape

# %% tags=[]
results.head()

# %% tags=[]
results.sort_values("pvalue").head(10)

# %% [markdown] tags=[]
# ## Save

# %% tags=[]
results.to_pickle(output_file)

# %% tags=[]