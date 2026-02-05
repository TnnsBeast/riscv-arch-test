#!/usr/bin/env bash
set -euo pipefail

# Simple end-to-end H smoke flow:
# 1) regenerate tests
# 2) regenerate ACT makefiles
# 3) compile ELFs (Spike used for signatures)
# 4) run ELFs on Wally via wsim
#
# Optional env overrides:
#   WORKDIR=work-gch
#   EXTENSIONS=H
#   SIM=verilator
#   RUN_SPIKE=0  (set to 1 to run run_tests.py on Spike after build)

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKDIR="${WORKDIR:-${ROOT_DIR}/work-gch}"
EXTENSIONS="${EXTENSIONS:-H}"
SIM="${SIM:-verilator}"
RUN_SPIKE="${RUN_SPIKE:-0}"

cd "${ROOT_DIR}"

echo "[H] Generating tests (${EXTENSIONS})"
uv run testgen testplans -o tests --extensions "${EXTENSIONS}"

echo "[H] Generating ACT makefiles"
uv run act \
  config/cores/cvw/cvw-rv32gch/test_config.yaml \
  config/cores/cvw/cvw-rv64gch/test_config.yaml \
  --workdir "${WORKDIR}" \
  --test-dir tests \
  --extensions "${EXTENSIONS}"

echo "[H] Compiling ELFs in ${WORKDIR}"
make -C "${WORKDIR}" compile

if command -v wsim >/dev/null 2>&1; then
  echo "[H] Running ELFs on Wally (sim=${SIM})"
  wsim rv32gch "${WORKDIR}/cvw-rv32gch/elfs/priv/H/H-00.elf" -s "${SIM}"
  wsim rv64gch "${WORKDIR}/cvw-rv64gch/elfs/priv/H/H-00.elf" -s "${SIM}"
else
  echo "[H] wsim not found on PATH; skipping DUT runs."
fi

if [[ "${RUN_SPIKE}" == "1" ]]; then
  echo "[H] Running ELFs on Spike"
  ./run_tests.py "spike --isa=rv32gch" "${WORKDIR}/cvw-rv32gch/elfs"
  ./run_tests.py "spike --isa=rv64gch" "${WORKDIR}/cvw-rv64gch/elfs"
fi

echo "[H] Done."
