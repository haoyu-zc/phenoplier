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
# # Description

# %% [markdown] tags=[]
# TODO

# %% [markdown] tags=[]
# # Modules loading

# %% tags=[]
# %load_ext autoreload
# %autoreload 2

# %% tags=[]
from pathlib import Path

import pandas as pd
from IPython.display import HTML

from entity import Trait, Gene
from data.cache import read_data
import conf

# %% [markdown] tags=[]
# # Settings

# %% tags=[]
EXPERIMENT_NAME = "single_gene"

LIPIDS_GENE_SET = "gene_set_increase"
LIPIDS_GENE_SET_QUERY = "(rank == 3) | (rank == 2)"

# %% tags=[]
OUTPUT_DIR = Path(
    conf.RESULTS["CRISPR_ANALYSES"]["BASE_DIR"], f"{EXPERIMENT_NAME}-{LIPIDS_GENE_SET}"
)
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)
display(OUTPUT_DIR)

# %% [markdown] tags=[]
# # Data loading

# %% [markdown] tags=[]
# ## S-MultiXcan results

# %% [markdown] tags=[]
# ### Load

# %% tags=[]
smultixcan_results_filename = conf.PHENOMEXCAN[
    "SMULTIXCAN_EFO_PARTIAL_MASHR_ZSCORES_FILE"
]

display(smultixcan_results_filename)

# %% tags=[]
smultixcan_results = pd.read_pickle(smultixcan_results_filename)

# %% [markdown] tags=[]
# ### Rename genes and remove repeated ones

# %% tags=[]
smultixcan_results = smultixcan_results.rename(index=Gene.GENE_ID_TO_NAME_MAP)

# %% tags=[]
smultixcan_results.index[smultixcan_results.index.duplicated(keep="first")]

# %% tags=[]
smultixcan_results = smultixcan_results.loc[
    ~smultixcan_results.index.duplicated(keep="first")
]

# %% tags=[]
smultixcan_results.shape

# %% tags=[]
smultixcan_results.head()

# %% [markdown] tags=[]
# ### Standardize by trait

# %% tags=[]
_tmp = smultixcan_results.apply(lambda x: x / x.sum())

# %% tags=[]
_tmp.shape

# %% tags=[]
assert _tmp.shape == smultixcan_results.shape

# %% tags=[]
# some testing
_trait = "body height"
_gene = "SCYL3"
assert (
    _tmp.loc[_gene, _trait]
    == smultixcan_results.loc[_gene, _trait] / smultixcan_results[_trait].sum()
)

_trait = "100001_raw-Food_weight"
_gene = "DPM1"
assert (
    _tmp.loc[_gene, _trait]
    == smultixcan_results.loc[_gene, _trait] / smultixcan_results[_trait].sum()
)

_trait = "estrogen-receptor negative breast cancer"
_gene = "CFH"
assert (
    _tmp.loc[_gene, _trait]
    == smultixcan_results.loc[_gene, _trait] / smultixcan_results[_trait].sum()
)

_trait = "asthma"
_gene = "C1orf112"
assert (
    _tmp.loc[_gene, _trait]
    == smultixcan_results.loc[_gene, _trait] / smultixcan_results[_trait].sum()
)

# %% tags=[]
smultixcan_results = _tmp

# %% [markdown] tags=[]
# ## Differentially expressed genes

# %% [markdown] tags=[]
# ### Load

# %% tags=[]
input_filepath = Path(conf.CRISPR["BASE_DIR"], "lipid_DEG.csv")
display(input_filepath)

# %% tags=[]
deg_genes = pd.read_csv(input_filepath)

# %% tags=[]
deg_genes.shape

# %% tags=[]
deg_genes.head()

# %% [markdown] tags=[]
# ### Select gene set

# %% tags=[]
df = deg_genes.query(LIPIDS_GENE_SET_QUERY)

# %% tags=[]
df.shape

# %% tags=[]
df_genes = df["gene_name"].unique().tolist()

display(len(df_genes))
display(df_genes[:10])

assert len(df_genes) == 175

# %% tags=[]
# keep genes present in S-MultiXcan results
df_genes_present = smultixcan_results.index.intersection(df_genes).tolist()

display(len(df_genes_present))
display(df_genes_present[:10])

assert len(df_genes_present) == 164

# %% [markdown] tags=[]
# # Get top traits

# %% tags=[]
traits = []

for g in df_genes_present:
    _tmp = smultixcan_results.loc[g]
    _tmp = _tmp[_tmp > 0.0].sort_values(ascending=False)

    #     _tmp = _tmp.head(50)
    traits.append(_tmp)

# %% tags=[]
traits_df = (
    pd.concat(traits)
    .reset_index()
    .groupby("index")
    .sum()
    .sort_values(0, ascending=False)
    .reset_index()
).rename(columns={"index": "trait", 0: "value"})

# %% tags=[]
# add trait category
trait_code_to_trait_obj = [
    Trait.get_trait(full_code=t)
    if not Trait.is_efo_label(t)
    else Trait.get_traits_from_efo(t)
    for t in traits_df["trait"]
]

# %% tags=[]
traits_df = traits_df.assign(
    category=[
        t.category if not isinstance(t, list) else t[0].category
        for t in trait_code_to_trait_obj
    ]
)

# %% tags=[]
traits_df.shape

# %% tags=[]
traits_df.head()

# %% tags=[]
output_file = Path(OUTPUT_DIR, "traits.pkl").resolve()
display(output_file)

# %% tags=[]
traits_df.to_pickle(output_file)

# %% [markdown] tags=[]
# # Summary

# %% tags=[]
top_traits = traits_df.head(100)

# %% tags=[]
with pd.option_context(
    "display.max_rows", None, "display.max_columns", None, "max_colwidth", None
):
    display(top_traits)

# %% [markdown] tags=[]
# # Summary using trait categories

# %% tags=[]
top_traits_categories = (
    top_traits.groupby("category")
    .mean()
    .sort_values("value", ascending=False)
    .reset_index()
)

# %% tags=[]
top_traits_categories.head()

# %% tags=[]
with pd.option_context(
    "display.max_rows", None, "display.max_columns", None, "max_colwidth", None
):
    display(top_traits_categories)

# %% tags=[]
for row_idx, row in top_traits_categories.iterrows():
    category = row["category"]
    display(HTML(f"<h2>{category}</h2>"))

    _df = (
        top_traits[top_traits["category"] == category]
        .groupby("trait")["value"]
        .mean()
        .sort_values()
    )
    display(_df)

# %% tags=[]