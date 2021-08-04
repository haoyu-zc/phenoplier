# PhenoPLIER (source code)

<!--
Unit tests are disabled for now
[![Code tests](https://github.com/greenelab/phenoplier/workflows/tests/badge.svg)](https://github.com/greenelab/phenoplier/actions/workflows/pytest.yaml)
-->
[![HTML Manuscript](https://img.shields.io/badge/manuscript-HTML-blue.svg)](https://greenelab.github.io/phenoplier_manuscript/)
[![PDF Manuscript](https://img.shields.io/badge/manuscript-PDF-blue.svg)](https://greenelab.github.io/phenoplier_manuscript/manuscript.pdf)

# Overview

![](images/phenoplier_overview.png)

Understanding how dysregulated transcriptional processes result in
tissue-specific pathology requires a mechanistic interpretation of expression
regulation across different cell types. It has been shown that this insight is
key for the development of new therapies. These mechanisms can be identified
with transcriptome-wide association studies (TWAS), which have represented a
significant step forward to test the mediating role of gene expression in GWAS
associations. However, it is hard to disentangle causal cell types using eQTL
data alone, and other methods generally do not use the large amounts of
publicly available RNA-seq data. Here we introduce PhenoPLIER, a polygenic
approach that maps both gene-trait associations and pharmacological
perturbation data into a common latent representation for a joint analysis.
This representation is based on modules of genes with similar expression
patterns across the same tissues. We observed that diseases were significantly
associated with gene modules expressed in relevant cell types, and our approach
was accurate in predicting known drug-disease pairs and inferring mechanisms of
action. Furthermore, using a CRISPR screen to analyze lipid regulation, we
found that functionally important players lacked TWAS associations but were
prioritized in phenotype-associated modules by PhenoPLIER. By incorporating
groups of co-expressed genes, PhenoPLIER can contextualize genetic associations
and reveal potential targets within associated processes that are missed by
single-gene strategies.


You can read the manuscript in
[bioRxiv](https://doi.org/10.1101/2021.07.05.450786) or the [Manubot
version](https://greenelab.github.io/phenoplier_manuscript/).


# Setup

To prepare the environment to run the PhenoPLIER code, follow the steps in
[environment](environment/). That will create a conda environment and download
the necessary data.

# Running code

## From command-line

First of all, export your settings to environmental variables, so non-Python scripts
can access them:
```bash
eval `python libs/conf.py`
```

The code to preprocess data and generate results is in the `nbs/` folder. All
notebooks are organized by directories, such as `01_preprocessing`, with file
names that indicate the order in which they should be run (if they share the prefix, then it
means they can be run in parallel). For example, to run
all notebooks for the preprocessing step, you can use this command (requires
[GNU Parallel](https://www.gnu.org/software/parallel/)):

```bash
cd nbs/
parallel -k --lb --halt 2 -j1 'bash run_nbs.sh {}' ::: 01_preprocessing/*.ipynb
```

Or if you want to run all the analyses at once, you can use:

```bash
shopt -s globstar
parallel -k --lb --halt 2 -j1 'bash run_nbs.sh {}' ::: nbs/{,**/}*.ipynb
```

## From your browser

Alternatively, you can start your JupyterLab server by running:

```bash
bash scripts/run_nbs_server.sh
```

Then, go to `http://localhost:8892`, browse the `nbs` folder, and run the
notebooks in the specified order.

## From a Docker image

Coming soon.

