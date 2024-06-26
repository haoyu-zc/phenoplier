#!/bin/bash

# It uses the HWE stats to remove variants that deviate too much from this test.

N_JOBS="${PHENOPLIER_GENERAL_N_JOBS}"
INPUT_DIR="${PHENOPLIER_A1000G_GENOTYPES_DIR}"
SUBSETS_DIR="${PHENOPLIER_A1000G_GENOTYPES_DIR}/subsets"
PLINK2="${PHENOPLIER_PLINK_EXECUTABLE_VERSION_2}"
PLINK19="${PHENOPLIER_PLINK_EXECUTABLE_VERSION_1_9}"

# hwe
$PLINK19 --bfile ${SUBSETS_DIR}/all_phase3.3 \
    --threads ${N_JOBS} \
    --hwe 1e-6 'include-nonctrl' \
    --make-bed \
    --out ${SUBSETS_DIR}/all_phase3.4
