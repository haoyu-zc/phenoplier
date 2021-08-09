# PhenoPLIER (source code)

<!--
Unit tests are disabled for now
[![Code tests](https://github.com/greenelab/phenoplier/workflows/tests/badge.svg)](https://github.com/greenelab/phenoplier/actions/workflows/pytest.yaml)
-->
[![HTML Manuscript](https://img.shields.io/badge/manuscript-HTML-blue.svg)](https://greenelab.github.io/phenoplier_manuscript/)
[![PDF Manuscript](https://img.shields.io/badge/manuscript-PDF-blue.svg)](https://greenelab.github.io/phenoplier_manuscript/manuscript.pdf)

## Overview

![](images/phenoplier_overview.png)

PhenoPLIER is new computational strategy that integrates statistical associations from GWAS/TWAS with groups of genes (gene modules) that have similar expression patterns across the same cell types.
This allows us to go beyond gene-trait statistical associations and infer the cell types where gene expression regulation is likely to be disrupted, resulting in cell type-specific pathology.

For more details, check out our manuscript in [bioRxiv](https://doi.org/10.1101/2021.07.05.450786) or our [Manubot web version](https://greenelab.github.io/phenoplier_manuscript/).

## Data

You can access all the data generated by this project by going to the [`data/`](data/)
folder. Please carefully follow instructions for citations, since this project
uses data generated by others.

## Setup

To prepare the environment to run the PhenoPLIER code, follow the steps in
[environment](environment/). This will create a conda environment and download
the necessary data. Alternatively, you can use our Docker image (see below).

## Running code

### From command-line

First, export your settings to environmental variables, so non-Python scripts
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

<!--
Or if you want to run all the analyses at once, you can use:

```bash
shopt -s globstar
parallel -k --lb --halt 2 -j1 'bash run_nbs.sh {}' ::: nbs/{,**/}*.ipynb
```
-->

### From your browser

Alternatively, you can start your JupyterLab server by running:

```bash
bash scripts/run_nbs_server.sh
```

Then, go to `http://localhost:8892`, browse the `nbs` folder, and run the
notebooks in the specified order.

## Using Docker

You can also run all the steps below using a Docker image instead of a local installation.

```bash
docker pull miltondp/phenoplier
```

The image only contains the conda environment with the code in this repository, so after pulling the image you need to download the data as well:

```bash
docker run \
  -v "/tmp/phenoplier_data:/opt/phenoplier_data" \
  miltondp/phenoplier \
  python environment/scripts/setup_data.py
```

The `-v` parameter allows to specify a local directory (`/tmp/phenoplier_data`) where the data will be downloaded.
If you want to generate the figures and tables for the manuscript, you need to clone the PhenoPLIER manuscript repo and pass it with `-v [PATH_TO_MANUSCRIPT_REPO]:/opt/phenoplier_manuscript`.

You can run notebooks from the command line, for example:

```bash
docker run \
  -v "/tmp/phenoplier_data:/opt/phenoplier_data" \
  miltondp/phenoplier \
  parallel -k --lb --halt 2 -j1 'bash nbs/run_nbs.sh {}' ::: nbs/01_preprocessing/*.ipynb
```

or start a Jupyter Notebook server with:

```bash
docker run \
  -p 8888:8892 \
  -v "/tmp/phenoplier_data:/opt/phenoplier_data" \
  miltondp/phenoplier
```

and access the interface by going to `http://localhost:8888`.
