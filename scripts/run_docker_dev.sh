#!/bin/bash

# This script is intended to be used by the developer not the end user.
#
# It runs the Docker container of this project by mounting the code and
# manuscript directories inside the container. This makes that any file created
# during the execution is locally available and ready to be pushed to the repo.
# Plus, the code is always run inside the same environment (including the full
# operating system).

# We assume the repo code is in the current directory, so the user has to make
# sure this is right.

echo "Configuration:"

CODE_DIR=`pwd`
echo "  Code dir: ${CODE_DIR}"

# root dir
if [ -z "${PHENOPLIER_ROOT_DIR}" ]; then
  ROOT_DIR="${CODE_DIR}/base"
else
  ROOT_DIR="${PHENOPLIER_ROOT_DIR}"
fi

# manuscript dir
if [ -z "${PHENOPLIER_MANUSCRIPT_DIR}" ]; then
  MANUSCRIPT_DIR="/tmp/phenoplier_manuscript"
  mkdir -p ${MANUSCRIPT_DIR}
else
  MANUSCRIPT_DIR="${PHENOPLIER_MANUSCRIPT_DIR}"
fi

if [ -z "${PHENOPLIER_N_JOBS}" ]; then
  N_JOBS=1
else
  N_JOBS=${PHENOPLIER_N_JOBS}
fi

echo "  Root dir: ${ROOT_DIR}"
echo "  Manuscript dir: ${MANUSCRIPT_DIR}"
echo "  CPU cores: ${N_JOBS}"

echo ""
echo "Waiting 2 seconds before starting"
sleep 2

# always create data directory before running Docker
mkdir -p ${ROOT_DIR}

COMMAND="$@"
PORT_ARG="-p 8888:8892"
if [ -z "${COMMAND}" ]; then
  FULL_COMMAND=()
else
  FULL_COMMAND=(/bin/bash -c "${COMMAND}")
  PORT_ARG=""
fi

echo "${FULL_COMMAND}"

# show commands being executed
set -x

# run
docker run --rm ${PORT_ARG} \
  -e PHENOPLIER_N_JOBS=${N_JOBS} \
  -e NUMBA_NUM_THREADS=${N_JOBS} \
  -e MKL_NUM_THREADS=${N_JOBS} \
  -e OPEN_BLAS_NUM_THREADS=${N_JOBS} \
  -e NUMEXPR_NUM_THREADS=${N_JOBS} \
  -e OMP_NUM_THREADS=${N_JOBS} \
  -v "${CODE_DIR}:/opt/code" \
  -v "${ROOT_DIR}:/opt/data" \
  -v "${MANUSCRIPT_DIR}:/opt/manuscript" \
  --user "$(id -u):$(id -g)" \
  miltondp/clustermatch_gene_expr "${FULL_COMMAND[@]}"
