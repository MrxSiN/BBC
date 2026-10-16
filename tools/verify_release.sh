#!/bin/sh
set -eu
cd "$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
python3 tools/annotate.py --check
python3 tests/verify_source_comments.py
python3 tests/verify_compiler_tape.py
python3 tests/verify_header_scratch.py
python3 tests/verify_selfhost.py
python3 tests/verify.py
python3 tests/verify_adversarial.py
python3 tests/verify_emission.py
python3 tests/verify_io_faults.py
python3 tests/verify_elf_size_primitive.py
python3 tests/verify_command_filter.py
python3 tests/verify_stream_filter.py
python3 tests/verify_stream_filter_equivalence.py
python3 tests/verify_filtered_adapter.py
python3 tests/verify_filter_integration_contract.py
python3 tests/verify_integrated_filter.py
python3 tests/verify_header_literal_reduction.py
python3 tests/verify_tape_safety.py
python3 tests/verify_android_aarch64_subset.py
python3 tests/verify_android_aarch64_legacy_equivalence.py
python3 tests/verify_android_bracket_relocations.py
python3 tests/verify_android_aarch64_loops.py
python3 tests/verify_android_contract_v1.py
python3 tests/verify_iteration26_native_stages.py
python3 tools/check_docs.py
python3 tools/verify_release.py --finalize-after-gates
