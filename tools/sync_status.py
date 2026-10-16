#!/usr/bin/env python3
"""Synchronize derived status files from executed evidence; never create compiler code."""
import hashlib
import json
import pathlib

from source_check import check_source

ROOT = pathlib.Path(__file__).resolve().parents[1]


def digest(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def jsonfile(name: str):
    return json.loads((ROOT / name).read_text())


def save(name: str, obj) -> None:
    (ROOT / name).write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n')


def main() -> None:
    source = (ROOT / 'compiler/core.bf').read_bytes()
    source_sha = digest(source)
    correctness = jsonfile('evidence/correctness.json')
    bootstrap = jsonfile('evidence/selfhost.json')
    emission = jsonfile('evidence/native_emission.json')
    io_faults = jsonfile('evidence/io_faults.json')
    adversarial = jsonfile('evidence/adversarial.json')
    arithmetic = jsonfile('evidence/elf_size_primitive.json')
    lexer = jsonfile('evidence/command_filter.json')
    stream_lexer = jsonfile('evidence/stream_filter.json')
    filter_equivalence = jsonfile('evidence/stream_filter_equivalence.json')
    filtered_adapter = jsonfile('evidence/filtered_adapter.json')
    filter_contract = jsonfile('evidence/filter_integration_contract.json')
    decoder_prototype = jsonfile('evidence/decoder_compaction_prototype.json')
    integrated = jsonfile('evidence/integrated_filter.json')
    literal_reduction = jsonfile('evidence/header_literal_reduction.json')
    safety = jsonfile('evidence/tape_safety_audit.json')
    compiler_tape = jsonfile('evidence/compiler_tape_audit.json')
    header_scratch = jsonfile('evidence/header_scratch_safety.json')
    release = jsonfile('evidence/release_gate.json')
    android = jsonfile('evidence/android_aarch64_subset.json')
    android_brackets = jsonfile('evidence/android_bracket_relocations.json')
    android_loops = jsonfile('evidence/android_loop_pipeline.json')
    external = jsonfile('status/TARGET_WORKLOADS.json')
    workload_audit = jsonfile('evidence/target_workloads_audit.json')
    comparison = jsonfile('benchmarks/results/nested_affine_stress.json')
    quick_comparison = jsonfile('benchmarks/results/nested_affine.json')
    annotations = jsonfile('evidence/source_comments.json')
    binary = (ROOT / 'build/compiler_x86_64_linux.elf').read_bytes()
    binary_sha = digest(binary)
    commands = check_source(source)
    fixed_padding = 0
    if (correctness.get('source_sha256') != source_sha or
        correctness.get('failed') != 0 or
        correctness.get('passed') != correctness.get('count') or
        bootstrap.get('source_sha256') != source_sha or
        bootstrap.get('artifact_elf_sha256') != binary_sha or
        len(bootstrap.get('stages', [])) < 3 or
        len(set(stage['output_elf_sha256'] for stage in bootstrap['stages'])) != 1 or
        bootstrap.get('independent_seed_agreement', {}).get('same_output_bytes') is not True or
        bootstrap['independent_seed_agreement']['output_elf_sha256'] != binary_sha or
        emission.get('source_sha256') != source_sha or
        emission.get('native_compiler_sha256') != binary_sha or
        emission.get('artifacts_verified', 0) < 1 or
        any(case.get('native_padding_bytes') != fixed_padding for case in emission.get('checks', [])) or
        emission.get('negative_mutations_rejected', 0) < 10 or
        emission.get('artifacts_with_short_rx_file', -1) != 0 or
        io_faults.get('known_defect_cases') != [] or
        adversarial.get('compiler_source_sha256') != source_sha or
        adversarial.get('native_compiler_sha256') != binary_sha or
        adversarial.get('cases_failed') != 0 or
        adversarial.get('cases_passed', 0) < 345 or
        arithmetic.get('passed', 0) < 62 or
        lexer.get('compiler_sha256') != source_sha or
        lexer.get('native_compiler_sha256') != binary_sha or
        lexer.get('cases_failed') != 0 or
        lexer.get('cases_passed', 0) < 135 or
        lexer.get('all_byte_values_covered') is not True or
        stream_lexer.get('compiler_source_sha256') != source_sha or
        stream_lexer.get('native_compiler_sha256') != binary_sha or
        stream_lexer.get('source_sha256') != digest((ROOT/'experiments/stream_filter.bf').read_bytes()) or
        stream_lexer.get('cases_passed', 0) < 189 or
        stream_lexer.get('malformed_transport_rejections', 0) < 6 or
        stream_lexer.get('experimental_filtered_selfhost') is not True or
        filter_equivalence.get('new_source_sha256') != digest((ROOT/'experiments/stream_filter.bf').read_bytes()) or
        filter_equivalence.get('compiler_sha256') != binary_sha or
        filter_equivalence.get('old_source_sha256') != digest((ROOT/'evidence/history/iteration15/stream_filter.bf').read_bytes()) or
        filter_equivalence.get('new_elf_sha256') != digest((ROOT/'build/stream_filter_x86_64_linux.elf').read_bytes()) or
        filter_equivalence.get('new_commands') != 816 or
        filter_equivalence.get('old_commands') != 1031 or
        filter_equivalence.get('valid_cases_passed', 0) < 390 or
        filter_equivalence.get('invalid_cases_rejected', 0) < 10 or
        filter_equivalence.get('exact_output_equivalence') is not True or
        filtered_adapter.get('compiler_source_sha256') != source_sha or
        filtered_adapter.get('compiler_elf_sha256') != binary_sha or
        filtered_adapter.get('filter_source_sha256') != digest((ROOT/'experiments/stream_filter.bf').read_bytes()) or
        filtered_adapter.get('filter_elf_sha256') != digest((ROOT/'build/stream_filter_x86_64_linux.elf').read_bytes()) or
        filtered_adapter.get('cases_passed', 0) < 28 or
        filtered_adapter.get('expanded_annotated_compiler_selfhost_identical') is not True or
        filtered_adapter.get('existing_artifact_preserved_on_failure') is not True or
        filtered_adapter.get('modified_filter_binary_rejected') is not True or
        filter_contract.get('compiler_source_sha256') != source_sha or
        filter_contract.get('compiler_sha256') != binary_sha or
        filter_contract.get('filter_source_sha256') != digest((ROOT/'experiments/stream_filter.bf').read_bytes()) or
        filter_contract.get('adapter_source_sha256') != digest((ROOT/'bootstrap/run_filtered_compiler.py').read_bytes()) or
        filter_contract.get('cases_passed', 0) < 36 or
        filter_contract.get('invalid_inputs_rejected', 0) < 5 or
        filter_contract.get('runtime_bounds_traps_checked', 0) < 2 or
        filter_contract.get('all_filtered_artifacts_verified_by_independent_elf_inspector') is not True or
        filter_contract.get('all_outputs_equal_direct_command_only_compilation') is not True or
        decoder_prototype.get('canonical_source_sha256') != digest((ROOT/'evidence/history/iteration18/core.bf').read_bytes()) or
        decoder_prototype.get('canonical_elf_sha256') != digest((ROOT/'evidence/history/iteration18/compiler_x86_64_linux.elf').read_bytes()) or
        decoder_prototype.get('decoder_patch_source_sha256') != digest((ROOT/'experiments/decoder_compaction_insertion.bf').read_bytes()) or
        decoder_prototype.get('cases_passed') != 85 or
        decoder_prototype.get('patch_bf_instructions') != 1045 or
        decoder_prototype.get('instructions_above_limit') != 824 or
        decoder_prototype.get('decoder_count_lane_audit_cases') != 85 or
        decoder_prototype.get('intentionally_mutated_count_restore_rejected') is not True or
        decoder_prototype.get('derived_compiler_bf_instructions') != 16952 or
        decoder_prototype.get('patched_core_rejected_selfcompilation') is not True or
        decoder_prototype.get('malformed_wire_rejections') != 5 or
        integrated.get('authoritative_source_sha256') != source_sha or
        integrated.get('integrated_native_elf_sha256') != binary_sha or
        integrated.get('independent_archived_native_elf_sha256') != digest((ROOT/'evidence/history/iteration18/compiler_x86_64_linux.elf').read_bytes()) or
        integrated.get('cases_passed', 0) < 91 or
        integrated.get('malformed_transport_rejections', 0) < 5 or
        integrated.get('byte_identical_outputs') is not True or
        literal_reduction.get('current_source_sha256') != source_sha or
        literal_reduction.get('replacements') != 39 or
        literal_reduction.get('source_instructions_saved') != 2093 or
        literal_reduction.get('isolated_arithmetic_cases') != 9984 or
        literal_reduction.get('complete_expected_instruction_stream_matches_authoritative') is not True or
        safety.get('core_sha256') != source_sha or
        safety.get('native_compiler_sha256') != binary_sha or
        safety.get('abstract_guard_transitions_checked') != 131072 or
        safety.get('native_witnesses_passed', 0) < 9 or
        safety.get('negative_mutations_rejected', 0) < 10 or
        compiler_tape.get('source_sha256') != source_sha or
        compiler_tape.get('native_compiler_sha256') != binary_sha or
        compiler_tape.get('cases_passed', 0) < 8 or
        compiler_tape.get('source_oracle_mutations_rejected', 0) < 1 or
        compiler_tape.get('header_scratch_audit', {}).get('cases_with_clean_entry_exit') != 8 or
        header_scratch.get('source_sha256') != source_sha or
        header_scratch.get('checked_mutations_rejected') != 4 or
        header_scratch.get('runtime_entry_exit_witnesses') != 8 or
        header_scratch.get('verified_scratch_multiplication_loops') != 39 or
        header_scratch.get('verified_cell_clear_loops') != 6 or
        header_scratch.get('minimum_pointer') != 60 or
        header_scratch.get('maximum_pointer') != 71 or
        header_scratch.get('scratch_exit_postcondition') != 0 or
        not all(case.get('byte_identical_to_native_compiler') is True for case in compiler_tape.get('cases', [])) or
        not all(case.get('normalized_source_verified_after_decode_and_at_exit') is True for case in compiler_tape.get('cases', [])) or
        not any(case.get('input_bytes') == 16128 for case in compiler_tape.get('cases', [])) or
        release.get('source_sha256') != source_sha or
        release.get('native_compiler_sha256') != binary_sha or
        release.get('command_filter_sha256') != digest((ROOT / 'experiments/command_filter.bf').read_bytes()) or
        release.get('stream_filter_sha256') != digest((ROOT / 'experiments/stream_filter.bf').read_bytes()) or
        release.get('gates_failed') != 0 or
        release.get('gates_passed') != 23 or
        release.get('android_loop_evidence_sha256') != digest((ROOT/'evidence/android_loop_pipeline.json').read_bytes()) or
        android_loops.get('input_source_cases',0) < 160 or
        android_loops.get('invalid_rejections',0) < 11 or
        android_loops.get('independent_seed_cases',0) < 8 or
        android_loops.get('supported_instructions') != '><+-.,[]' or
        len(android_loops.get('stages',{})) != 6 or
        not all(digest((ROOT / name).read_bytes()) == values['source_sha256'] and digest((ROOT / android_loops_stage_path).read_bytes()) == values['elf_sha256']
                for stage, values in android_loops['stages'].items()
                for name, android_loops_stage_path in [dict(filter=('experiments/stream_filter.bf','build/stream_filter_x86_64_linux.elf'), resolve=('experiments/android_bracket_relocations.bf','build/android_bracket_relocations_x86_64_linux.elf'), encode=('experiments/android_branch_encoding.bf','build/android_branch_encoding_x86_64_linux.elf'), mask=('experiments/android_branch_mask.bf','build/android_branch_mask_x86_64_linux.elf'), emit=('experiments/android_aarch64_pie_subset.bf','build/android_pie_emitter_linux_x86_64.elf'), apply=('experiments/android_branch_apply.bf','build/android_branch_apply_x86_64_linux.elf'))[stage]]) or
        release.get('android_bracket_relocations_sha256') != digest((ROOT/'experiments/android_bracket_relocations.bf').read_bytes()) or
        android_brackets.get('source_sha256') != digest((ROOT/'experiments/android_bracket_relocations.bf').read_bytes()) or
        android_brackets.get('linux_native_elf_sha256') != digest((ROOT/'build/android_bracket_relocations_x86_64_linux.elf').read_bytes()) or
        android_brackets.get('brainfuck_instructions') != 2252 or
        android_brackets.get('valid_streams_passed',0) < 448 or
        android_brackets.get('invalid_streams_rejected',0) < 2145 or
        android_brackets.get('independent_interpreter_equivalences',0) < 44 or
        release.get('android_prototype_source_sha256') != digest((ROOT/'experiments/android_aarch64_pie_subset.bf').read_bytes()) or
        android.get('source_sha256') != digest((ROOT/'experiments/android_aarch64_pie_subset.bf').read_bytes()) or
        android.get('host_emitter_sha256') != digest((ROOT/'build/android_pie_emitter_linux_x86_64.elf').read_bytes()) or
        android.get('accepted_sources_tested',0) < 64 or
        android.get('rejected_sources_tested',0) < 12 or
        android.get('independent_seed_comparisons',0) < 16 or
        android.get('supported_commands') != ['+','-','.', '>','<',','] or
        android.get('boundary_witnesses',0) < 4 or
        android.get('read_eof_witnesses',0) < 6 or
        android.get('read_failure_witnesses',0) < 2 or
        jsonfile('evidence/android_aarch64_legacy_equivalence.json').get('identical_image_cases',0) < 128 or
        len(external.get('repositories', [])) != 4 or
        len([p for r in workload_audit.get('repos',[]) for p in r['files'] if p['capacity_status'] == 'EXCEEDS_LIMIT']) != 11 or
        comparison.get('compiler_source_sha256') != source_sha or
        quick_comparison.get('compiler_source_sha256') != source_sha or
        not comparison.get('measured_ratio', 0) > 0.9999 or
        annotations.get('raw_source_sha256') != source_sha or
        annotations.get('filtered_instruction_sha256') != digest(commands) or
        annotations.get('identical_output_comparisons') != 10 or
        io_faults.get('compiler_source_sha256') != source_sha or
        io_faults.get('native_compiler_sha256') != binary_sha or
        io_faults.get('cases_executed', 0) < 10 or
        not all(any(o.get('case') == case and o.get('native_exit') == 0 and o.get('syscall_attempts') == 2
                for o in io_faults.get('observations', []))
                for case in ('injected_write_eintr','injected_read_eintr','injected_read_eintr_then_eof')) or
        len(binary) != 215 + 32 * len(commands) or
        len(commands) > 16128 or
        206 + 16128 * 32 + 9 > 524288):
        raise ValueError('verification evidence does not agree with the source or binary')
    status = {
        'as_of': bootstrap['date'],
        'target': 'x86_64-unknown-linux-elf',
        'project_requirements_sha256': digest((ROOT / 'docs/PROJECT_REQUIREMENTS.md').read_bytes()),
        'required_native_targets': {
            'linux_x86_64': {'artifact': 'static ELF64', 'native_compiler_execution': 'EXECUTED', 'selfhosting': 'S2 EXECUTED'},
            'windows_x86_64': {'artifact': 'PE32+ console', 'native_compiler_execution': 'UNIMPLEMENTED', 'selfhosting': 'UNVERIFIED'},
            'android_aarch64': {'artifact': 'ELF PIE shell executable', 'native_compiler_execution': 'UNIMPLEMENTED', 'selfhosting': 'UNVERIFIED', 'experimental_backend': 'STRUCTURAL AND SIMULATED: six Linux-native BF stages produce AArch64 PIE for all eight commands; 10-command limit; no Android execution'},
        },
        'android_bracket_relocation_prototype': {
            'classification':'EXECUTED on Linux, no Android code emission',
            'source': 'experiments/android_bracket_relocations.bf',
            'native_linux_executable': 'build/android_bracket_relocations_x86_64_linux.elf',
            'valid_cases': android_brackets['valid_streams_passed'],
            'invalid_cases': android_brackets['invalid_streams_rejected'],
            'independent_seeds': android_brackets['independent_interpreter_equivalences'],
            'evidence': 'evidence/android_bracket_relocations.json'},
        'android_aarch64_loop_pipeline': {'classification': 'STRUCTURAL + SIMULATED, NOT Android execution', 'evidence': 'evidence/android_loop_pipeline.json', 'accepted_images': android_loops['input_source_cases'], 'nested_loop_cases': android_loops['loop_containing_cases'], 'invalid_rejections': android_loops['invalid_rejections'], 'seed_comparisons': android_loops['independent_seed_cases'], 'source_limit_commands': 10, 'native_stages': 6},
        'android_aarch64_prototype': {'classification': 'STRUCTURAL + SIMULATED, NOT Android execution', 'supported_commands': android.get('supported_commands', []), 'pointer_bounds_simulation_witnesses': android.get('boundary_witnesses', 0), 'source': 'experiments/android_aarch64_pie_subset.bf', 'host_emitter': 'build/android_pie_emitter_linux_x86_64.elf', 'tested_sources': android['accepted_sources_tested'], 'rejections': android['rejected_sources_tested'], 'source_bf_instructions': android['source_instructions'], 'image_bytes': android['aarch64_image_bytes'], 'evidence': 'evidence/android_aarch64_subset.json'},
        'semantic_profile': 'docs/BRAINFUCK_SPEC.md, V0',
        'authoritative_source': 'compiler/core.bf',
        'source_instruction_count': len(commands),
        'source_sha256': source_sha,
        'filtered_instruction_sha256': digest(commands),
        'source_limit_executable_commands': 16128,
        'noncommand_behavior': 'BF-only in-core filtering discards ignored source bytes; only executable commands use tape records or native slots',
        'loop_depth_limit': 255,
        'source_byte_protocol': 'raw source bytes stuffed as FF01 for NUL and FF02 for FF; EOF terminates stream',
        'native_elf_sha256': binary_sha,
        'native_compiler_elf_bytes': len(binary),
        'source_purity': 'EXECUTED: only original eight executable BF commands; safe ignored inline comments checked',
        'parser': 'EXECUTED: BF-owned command compaction, 16128-command input ceiling, 255 bracket nesting, strict malformed escape handling',
        'native_code_generation': 'EXECUTED: Linux x86-64 static ELF, 32-byte slots, RX p_filesz equals exact output size, 512-KiB p_memsz; read/write EINTR retry',
        'bf_emitted_padding_bytes': fixed_padding,
        'elf_file_size_contract': 'exact: 215 + 32 * executable source commands; fixed padding is zero',
        'self_hosting': 'EXECUTED: Stage 0, 1 and 2 identical ELF bytes',
        'bootstrap_seed_trust': 'EXECUTED: two independently written C BF seeds agree; seed trust still unproven',
        'bootstrap_reproducibility': 'EXECUTED: identical stage output hashes',
        'tape_memory_safety': 'EXECUTED: pointer bounds traps, no formal proof',
        'native_io': 'EXECUTED: ordinary/EOF I/O and read/write EINTR retry; negative read exits(4), unsuccessful write exits(3), EAGAIN fails fast; default SIGPIPE',
        'native_emission_slots_verified': emission['templates_verified'],
        'native_emission_branches_verified': emission['branch_displacements_verified'],
        'native_emission_artifacts_verified': emission['artifacts_verified'],
        'native_io_fault_cases_executed': io_faults['cases_executed'],
        'adversarial_tests_passed': adversarial['cases_passed'],
        'independent_bf_size_reference_cases': arithmetic['passed'],
        'native_io_known_defect_cases': io_faults['known_defect_cases'],
        'rx_segment_file_short_cases_observed': emission['artifacts_with_short_rx_file'],
        'command_filter_prototype': 'EXECUTED standalone eight-instruction BF lexer, 135 cases covering all 256 byte values; NOT integrated',
        'command_filter_source': 'experiments/command_filter.bf',
        'stream_filter_prototype': 'EXECUTED: 189 BF-native streamed/escaped transport cases, 6 malformed escape rejections, experimental filtered BF compiler selfhost; separate executable only',
        'stream_filter_source': 'experiments/stream_filter.bf',
        'stream_filter_command_count': filter_equivalence['new_commands'],
        'stream_filter_native_elf_bytes': filter_equivalence['new_elf_bytes'],
        'stream_filter_historical_equivalence': 'EXECUTED: 390 valid and 10 malformed inputs equal to previous 1031-command native BF source; independent measurements, not compiler speed parity',
        'stream_filter_equivalence_evidence': 'evidence/stream_filter_equivalence.json',
        'optional_filtered_adapter': 'EXECUTED: historical optional two native BF executable adapter, 28 program comparisons, atomic output; not required now that core.bf filters directly',
        'optional_filtered_adapter_evidence': 'evidence/filtered_adapter.json',
        'filtered_integration_contract': 'EXECUTED: 36 comment-interleaving and native relocation/runtime checks, 5 rejected boundary inputs; optional two-BF process path only',
        'filtered_integration_contract_evidence': 'evidence/filter_integration_contract.json',
        'optional_adapter_raw_limit_bytes': filter_contract['raw_adapter_input_limit'],
        'decoder_compaction_prototype': 'HISTORICAL: 1045 BF instruction patch validated on older compiler; integrated in Iteration 19 after 2093 instruction header reductions',
        'decoder_compaction_prototype_evidence': 'evidence/decoder_compaction_prototype.json',
        'source_annotations': 'EXECUTED: safe source annotations and independent seed invariance; user-source comment-independent ELF artifact generation now integrated',
        'static_tape_safety_audit': 'STRUCTURAL conditional invariant audit: 131072 pointer-state transitions, 9 executed native witnesses, 10 rejected template mutations; compiler-internal proof absent',
        'compiler_tape_audit': 'EXECUTED: 8 compiler-tape witnesses, compacted source checks, header scratch entry/exit preconditions and observed high-water 64601; compiler-wide proof absent',
        'header_scratch_proof': 'CONDITIONAL STATIC PROOF: header block BF offsets 2848..4277, 45 balanced loops, 39 scratch-counter loops; touches cells 60..71, returns at cell 60 with cell 61 zero if entered with those values; entry condition only witnessed dynamically',
        'header_scratch_evidence': 'evidence/header_scratch_safety.json',
        'internal_source_byte_normalization': 'Escaped 00 and FF are ignored source text and discarded before command storage',
        'optimization': 'LIMITED: 39 verified BF compiler-source literal constructions shortened; no general generated-code optimizer',
        'simd': 'UNIMPLEMENTED',
        'bare_metal': 'UNIMPLEMENTED',
        'performance_vs_native_c_rust': 'MEASURED C only: two Category B small algorithm workloads; stress BF/C ratio exceeds 0.9999; Rust UNMEASURED',
        'external_application_workloads': 'SOURCE AUDIT: 11 policy BF sources confirmed beyond 16128 commands, G29 19.48MB raw source size only; none compiled by this toolchain',
        'external_application_workloads_manifest': 'status/TARGET_WORKLOADS.json',
        'external_application_workloads_evidence': 'evidence/target_workloads_audit.json',
        'native_c_comparison_evidence': ['benchmarks/results/nested_affine.json', 'benchmarks/results/nested_affine_stress.json'],
        'correctness_tests_passed': correctness['passed'],
        'correctness_tests_failed': correctness['failed'],
        'highest_conformance_level': 'S2 EXECUTED, memory-safety regression tests partial S3 evidence',
        'evidence': ['evidence/correctness.json', 'evidence/selfhost.json',
                     'evidence/native_emission.json', 'evidence/io_faults.json',
                     'evidence/adversarial.json', 'evidence/elf_size_primitive.json',
                     'evidence/iteration6_change.json', 'evidence/iteration7_change.json',
                     'evidence/iteration8_change.json', 'evidence/iteration9_change.json',
                     'evidence/command_filter.json', 'evidence/tape_safety_audit.json',
                     'evidence/compiler_tape_audit.json', 'evidence/header_scratch_safety.json', 'evidence/iteration20_change.json',
                     'evidence/android_aarch64_subset.json', 'evidence/android_aarch64_legacy_equivalence.json', 'evidence/android_bracket_relocations.json', 'evidence/android_loop_pipeline.json', 'evidence/iteration25_change.json', 'evidence/iteration24_change.json', 'evidence/iteration23_change.json', 'evidence/iteration21_change.json',
                     'evidence/source_comments.json', 'evidence/stream_filter.json',
                     'evidence/stream_filter_equivalence.json', 'evidence/iteration16_change.json',
                     'evidence/decoder_compaction_prototype.json', 'evidence/integrated_filter.json', 'evidence/header_literal_reduction.json', 'evidence/iteration19_change.json', 'evidence/iteration17_change.json',
                     'evidence/iteration18_change.json',
                     'evidence/iteration13_change.json', 'evidence/filtered_adapter.json', 'evidence/iteration14_change.json',
                     'evidence/filter_integration_contract.json', 'evidence/iteration15_change.json',
                     'evidence/release_gate.json'],
        'known_issues': [
            'fixed 32-byte native slots remain expensive; no general optimizer for generated programs',
            'required Windows x86-64 and Android AArch64 native selfhosting unimplemented; six-stage BF AArch64 PIE pipeline emits all eight instructions for ten commands but has no Android execution evidence',
            'safe inline BF source annotations work; comment-independent compiled artifacts now pass native differential checks',
            'native C baseline measured for only two toy algorithms; stress ratio fails 0.9999x, Rust and all four real application workloads unmeasured',
            'all eleven inspected Android policy BF sources exceed compiler 16128-command limit; G29 checked signed int32 incompatible with V0',
            'read and write retry EINTR; nonblocking EAGAIN fails fast; no eventual delivery guarantee',
            'memory safety includes conditional generated-code template checks and executed compiler-tape traces; complete compiler-internal region separation remains unproven',
            f'source input remains 16128 executable commands excluding comments, nesting bounded to 255; {16128-len(commands)} instruction slots remain for self-compilation',
        ],
    }
    # Later iterations have separate evidence; regenerating the legacy status
    # must not discard those records or promote their historical simulations.
    experiments = [
        ('android_source_scan_iteration27', 'iteration27_source_scan', {
            'target_compilation_source_limit_commands': 10,
            'tested_executable_source_commands': 300001}),
        ('android_wide_brackets_iteration28', 'iteration28_wide_brackets', {
            'android_emitter_command_limit': 10,
            'wide_aarch64_branch_encoding': 'RECORDS_EXECUTED_LINUX_ONLY'}),
        ('android_wide_branch_encoding_iteration28', 'iteration28_wide_branch_encoding', {
            'android_final_emitter_command_limit': 10}),
        ('android_wide_74_slot_loop_pipeline', 'iteration29_wide_slot_patch', {
            'max_source_instructions': 74, 'android_native_compiler_execution': False,
            'android_native_selfhosting': False}),
        ('android_dynamic_rx_iteration30', 'iteration30_dynamic_elf', {
            'maximum_linear_commands': 255, 'maximum_commands_with_brackets': 74,
            'full_elf_bytes_per_supported_size_class': 16480,
            'elf_file_size_varies_with_command_count': False, 'android_native_selfhosting': False}),
        ('android_page_class_iteration31', 'iteration31_page_class_elf', {}),
        ('android_wide_slot_255_iteration32', 'iteration32_wide_slot_patch_255', {}),
        ('android_wide_slot_512_iteration33', 'iteration33_wide_slot_patch_512', {}),
        ('android_multiclass_iteration34', 'iteration34_multiclass_elf', {}),
        ('android_tape_rebase_iteration35', 'iteration35_tape_rebase', {}),
        ('android_wide_loops_iteration36', 'iteration36_wide_loops_2000', {}),
        ('android_device_preflight_iteration37', 'iteration37_android_acceptance_preflight', {}),
    ]
    for key, stem, fields in experiments:
        path = f'evidence/{stem}.json'
        proof = jsonfile(path)
        stages = list(proof.get('stages', {}).values()) or [proof.get('stage', proof)]
        for stage in stages:
            source_path = stage.get('source', stage.get('bf_source'))
            if source_path and stage.get('source_sha256'):
                if digest((ROOT / source_path).read_bytes()) != stage['source_sha256']:
                    raise ValueError(f'Android experimental source changed: {source_path}')
            native_path = stage.get('native_linux_elf')
            native_hash = stage.get('native_linux_elf_sha256', stage.get('linux_native_elf_sha256'))
            if native_path and native_hash and digest((ROOT / native_path).read_bytes()) != native_hash:
                raise ValueError(f'Android experimental artifact changed: {native_path}')
        status[key] = dict(proof, evidence=path, **fields)
    device_report = ROOT / 'benchmarks/results/android_transfer.json'
    if device_report.exists():
        device = jsonfile('benchmarks/results/android_transfer.json')
        stage_sources = {
            'filter': 'experiments/stream_filter.bf',
            'resolve': 'experiments/android_bracket_relocations.bf',
            'encode': 'experiments/android_branch_encoding.bf',
            'mask': 'experiments/android_branch_mask.bf',
            'emit': 'experiments/android_aarch64_pie_subset.bf',
            'apply': 'experiments/android_branch_apply.bf',
        }
        if (device['compiler_source_sha256'] != source_sha or
                not device['independent_bf_seed_images_identical'] or
                not device['archived_native_image_identical'] or
                device['correctness_checks'] < 48 or
                any(device['bf_stages'][name] != digest((ROOT / path).read_bytes())
                    for name, path in stage_sources.items())):
            raise ValueError('Android device evidence is stale or incomplete')
        status['android_device_execution'] = {
            'classification': 'EXECUTED bounded native ELF on Android; compiler stages interpreted, no native selfhosting',
            'device': {key: device['device'][key] for key in ('model', 'android', 'api', 'benchmark_cpu')},
            'source_limit_commands': 10,
            'correctness_checks': device['correctness_checks'],
            'witnesses': device['device_witnesses'],
            'performance_objective': device['objective_status'],
            'speed_ratio_to_fastest_baseline': device['speed_ratio_baseline_ms_over_bf_ms'],
            'fastest_baseline': device['fastest_baseline'],
            'evidence': 'benchmarks/results/android_transfer.json',
        }
        status['required_native_targets']['android_aarch64']['experimental_backend'] = (
            f"EXECUTED on {device['device']['model']}: bounded all-eight-command ELF; ten-command limit; no native compiler selfhosting")
    optimizer_report = ROOT / 'evidence/android_native_optimization.json'
    if optimizer_report.exists():
        optimized = jsonfile('evidence/android_native_optimization.json')
        for name, source, binary in [
                ('optimize', 'experiments/android_native_optimize.bf', 'build/android_native_optimize_x86_64_linux.elf'),
                ('resources', 'experiments/android_resource_optimize.bf', 'build/android_resource_optimize_x86_64_linux.elf')]:
            row = optimized['optimizers'][name]
            if (row['source_sha256'] != digest((ROOT / source).read_bytes()) or
                    row['source_instructions'] != len(check_source((ROOT / source).read_bytes())) or
                    row['linux_optimizer_sha256'] != digest((ROOT / binary).read_bytes())):
                raise ValueError('Android optimizer evidence is stale')
        if (optimized['compiler_source_sha256'] != source_sha or
                optimized['android_executions'] != 1032 or optimized['simulated_comparisons'] != 444):
            raise ValueError('Android optimizer verification incomplete')
        status['android_native_optimization'] = optimized
        status['optimization'] = 'LIMITED: BF-owned clear/adjacent transfer folding and proven small stack tape in ten-command Android prototype; production Linux optimizer absent'
        status['known_issues'][1] = 'Windows native target and Android compiler selfhosting unimplemented; bounded ten-command Android ELF executes on Pixel 8 Pro'
    optimized_benchmark = ROOT / 'benchmarks/results/android_optimized.json'
    if optimized_benchmark.exists():
        performance = jsonfile('benchmarks/results/android_optimized.json')
        if (performance['compiler_source_sha256'] != source_sha or
                performance['rounds'] != 101 or performance['correctness_checks'] != 1542 or
                performance['builds']['brainfuck_optimized']['sha256'] != digest((ROOT / 'build/android_optimization/brainfuck_optimized').read_bytes()) or
                performance['raw_process_samples_sha256'] != digest((ROOT / 'build/android_optimization/raw_process_samples.txt').read_bytes()) or
                any(len(row['raw_ms']) != 101 for row in performance['data'].values()) or
                any(value != optimized['optimizers'][name]['source_sha256']
                    for name, value in performance['optimizer_source_sha256'].items())):
            raise ValueError('Android optimized benchmark evidence is stale or incomplete')
        status['android_device_execution']['optimized_performance'] = {
            'status': performance['status'], 'speed_ratio_to_fastest_baseline': performance['bf_speed_ratio'],
            'bootstrap_95_percent_interval': performance['bootstrap_95_percent_interval'],
            'fastest_baseline': performance['fastest_baseline'], 'evidence': 'benchmarks/results/android_optimized.json'}
    gm_apk_report = ROOT / 'benchmarks/results/gm_apk_baseline.json'
    if gm_apk_report.exists():
        gm_apk = jsonfile('benchmarks/results/gm_apk_baseline.json')
        if (gm_apk['instrumentation_tests_passed'] != 16 or gm_apk['bf_java_parity_comparisons'] != 634229 or
                gm_apk['apk_sha256'] != digest((ROOT / 'build/android_optimization/gm_baseline.apk').read_bytes()) or
                gm_apk['test_apk_sha256'] != digest((ROOT / 'build/android_optimization/gm_baseline_test.apk').read_bytes()) or
                any(value != digest((ROOT / 'build/android_optimization' / name).read_bytes())
                    for name, value in gm_apk['logs_sha256'].items())):
            raise ValueError('GM APK evidence is stale or incomplete')
        status['gm_apk_baseline'] = {
            'classification': gm_apk['classification'], 'status': gm_apk['status'],
            'instrumentation_tests_passed': 16, 'bf_java_parity_comparisons': 634229,
            'evidence': 'benchmarks/results/gm_apk_baseline.json'}
    expanded_report = ROOT / 'evidence/android_device_20261013/device_verification.json'
    if expanded_report.exists():
        from android_device_acceptance import audit, inspect_elf
        executed = json.loads(expanded_report.read_text())
        bundle = ROOT / 'build/android_device_acceptance_37'
        manifest = json.loads((bundle / 'manifest.json').read_text())
        actual = audit(manifest, expanded_report.parent)
        if (executed.get('evidence_class') != 'ANDROID_DEVICE_EXECUTED' or
                not executed.get('adb_pushed_files_pulled_and_hash_verified') or
                executed.get('manifest_sha256') != digest((bundle / 'manifest.json').read_bytes()) or
                not actual['all_passed'] or actual['passed'] != 13 or
                executed.get('cases') != actual['cases']):
            raise ValueError('expanded Android device evidence is incomplete or corrupted')
        for row in manifest['cases']:
            elf = (bundle / (row['id'] + '.elf')).read_bytes()
            if (digest(elf) != row['elf_sha256'] or
                    digest((bundle / (row['id'] + '.stdin')).read_bytes()) != row['stdin_sha256']):
                raise ValueError('expanded Android acceptance fixture changed')
            inspect_elf(elf, row['command_count'])
        status['android_expanded_device_acceptance'] = {
            'classification': 'ANDROID_DEVICE_EXECUTED generated AArch64 PIE; no Android-native compiler or S2',
            'cases_passed': actual['passed'], 'source_limit_commands': 2000,
            'device_properties': executed['device_properties'],
            'evidence': str(expanded_report.relative_to(ROOT)),
        }
        status['required_native_targets']['android_aarch64']['experimental_backend'] = (
            'EXECUTED 13 BF-generated AArch64 PIE fixtures through 2,000 commands including loops; no native compiler or S2')
        status['known_issues'][1] = 'Windows native target and Android compiler selfhosting unimplemented; 13 generated Android fixtures through 2000 commands executed on Pixel 8 Pro'
    followup_path = ROOT / 'evidence/android_followup_20261013/summary.json'
    if followup_path.exists():
        followup = json.loads(followup_path.read_text())
        for name, expected in followup['evidence_sha256'].items():
            witness = ROOT / name
            archived_harness = followup_path.parent / 'android_apk_followup.py'
            if name == 'benchmarks/android_apk_followup.py' and archived_harness.exists():
                witness = archived_harness
            if digest(witness.read_bytes()) != expected:
                raise ValueError(f'Android follow-up evidence changed: {name}')
        status['android_latest_device_performance'] = {
            'classification': 'MEASURED single USB device session; separate native process and existing GM APK workloads',
            'native_status': followup['native_status'],
            'native_fastest_baseline': followup['native_fastest_baseline'],
            'native_speed_ratio_baseline_over_bf': followup['native_speed_ratio_baseline_over_bf'],
            'native_paired_bootstrap_95_percent_interval': followup['native_paired_bootstrap_95_percent_interval'],
            'apk_status': followup['apk_status'],
            'apk_instrumentation_tests_passed': followup['apk_instrumentation_tests_passed'],
            'apk_parity_comparisons': followup['apk_parity_comparisons'],
            'general_performance_objective': 'NOT_ESTABLISHED',
            'evidence': str(followup_path.relative_to(ROOT)),
        }
    # Current bounded Android-native S2 is a later archived device run than the
    # historical experimental records above. Authenticate its persisted files.
    v3base = ROOT / 'evidence/android_native_selfhost_20261013_v3'
    fresh_native = ROOT / 'evidence/android_native_selfhost_20261014_v2'
    if (fresh_native / 'report.json').exists():
        v3base = fresh_native
    if (v3base / 'report.json').exists():
        latest = json.loads((v3base / 'report.json').read_text())
        android_bf = (ROOT / latest['source']).read_bytes()
        decoded = check_source(android_bf)
        if (digest(android_bf) != latest['source_sha256'] or
            digest(decoded) != latest['filtered_sha256'] or
            len(decoded) != latest['bf_instructions'] or
            len(decoded) > latest['source_cap_commands'] or
            latest.get('independent_seeds_identical') is not True or
            latest.get('native_stage0_1_2_3_identical') is not True or
            len(latest['stages']) != 3 or len(latest['corpus']) != 14 or
            len(latest['rejections']) != 7):
            raise ValueError('Android native S2 source or archive report invalid')
        for n in range(4):
            image = (v3base / f'stage{n}.elf').read_bytes()
            if (digest(image) != latest['compiler_elf_sha256'] or
                len(image) != latest['compiler_elf_bytes'] or
                (n and (v3base / f'stage{n}.stream').read_bytes() != image + b'\0')):
                raise ValueError(f'Android native compiler stage {n} changed')
        for n, case in enumerate(latest['corpus']):
            image = (v3base / f'case{n}.elf').read_bytes()
            stream = (v3base / f'case{n}.stream').read_bytes()
            if (digest(image) != case['elf_sha256'] or stream != image+b'\0' or
                (v3base / f'case{n}.stdout').read_bytes().hex() != case['stdout_hex'] or
                int((v3base / f'case{n}.exitcode').read_text().strip()) != case['status']):
                raise ValueError(f'Android native compiled case {n} changed')
        status['android_native_s2_current'] = {
            'classification': 'EXECUTED_ON_ANDROID_DEVICE_PERSISTED_RESULTS_AUDITED',
            'evidence': (v3base / 'report.json').relative_to(ROOT).as_posix(),
            'compiler_source': latest['source'],
            'source_sha256': latest['source_sha256'],
            'compiler_image_sha256': latest['compiler_elf_sha256'],
            'compiler_image_bytes': latest['compiler_elf_bytes'],
            'compiler_bf_instructions': latest['bf_instructions'],
            'compiler_source_limit_commands': latest['source_cap_commands'],
            'device_properties': latest['device_properties'],
            'compiler_native_selfhosting': 'S2_EXECUTED_BOUNDED_ARCHIVED_STAGES_0_1_2_3',
            'programs_executed_on_device_in_record': len(latest['corpus']),
            'fresh_device_rerun_in_this_iteration': v3base == fresh_native,
            'general_300000_compiler': 'UNIMPLEMENTED',
        }
        status['required_native_targets']['android_aarch64']['native_compiler_execution'] = (
            'EXECUTED recorded Pixel 8 Pro/API37; source bounded to 16128 BF commands')
        status['required_native_targets']['android_aarch64']['selfhosting'] = (
            'S2 EXECUTED recorded native Stages 0-3, archive audited offline')
        status['required_native_targets']['android_aarch64']['experimental_backend'] = (
            'EXECUTED bounded AArch64 BF-native compiler and emitted programs on Pixel 8 Pro/API37; '
            '300000-command target not implemented')
        status['known_issues'][1] = (
            'Windows PE32+ general native compiler/S2 unimplemented; Android native bounded S2 '
            'recorded on Pixel 8 Pro but 300000-command target not implemented')
    windows_proof = ROOT / 'evidence/iteration38_transition.json'
    if windows_proof.exists():
        event = json.loads(windows_proof.read_text())['windows_pe_exit_seed']
        bf = (ROOT / event['source']).read_bytes()
        code = check_source(bf)
        image = (ROOT / event['output']).read_bytes()
        native = (ROOT / event['native_linux_emitter']).read_bytes()
        if (digest(bf) != event['source_sha256'] or
            len(code) != event['bf_instructions'] or
            digest(image) != event['output_sha256'] or
            digest(native) != event['native_linux_emitter_sha256'] or
            len(image) != event['pe_bytes'] or
            image[:2] != b'MZ'):
            raise ValueError('Windows BF PE primitive changed after validation')
        status['windows_pe_exit_seed_iteration38'] = event
        status['required_native_targets']['windows_x86_64']['artifact'] = (
            'PE32+ console structural BF-emitted exit prototype; not Windows executed')
        status['required_native_targets']['windows_x86_64']['native_compiler_execution'] = 'UNIMPLEMENTED'
        status['required_native_targets']['windows_x86_64']['selfhosting'] = 'UNVERIFIED'
    # Iteration 50: verify the opt-in dynamic-stage sources and the native Linux
    # binaries before labeling evidence. These stages are not Android ELF output.
    compact50 = jsonfile('evidence/iteration50_android_compact_stream.json')
    stack50 = jsonfile('evidence/iteration50_android_dynamic_stack.json')
    million50 = jsonfile('evidence/iteration50_million_linear.json')
    for path, bf, binary in (
        ('experiments/android_streaming_compact_slots.bf', 5764,
         'build/android_streaming_compact_slots_x86_64_linux.elf'),
        ('experiments/android_dynamic_stack_pairs.bf', 1576,
         'build/android_dynamic_stack_pairs_x86_64_linux.elf'),
        ('experiments/android_pair_event_bridge.bf', 658,
         'build/android_pair_event_bridge_x86_64_linux.elf')):
        raw = (ROOT / path).read_bytes()
        native = (ROOT / binary).read_bytes()
        if len(check_source(raw)) != bf or not native.startswith(b'\x7fELF'):
            raise ValueError(f'Iteration 50 BF native stage not intact: {path}')
        evidence_stage = (compact50 if 'compact' in path else
                          stack50['bf_stages'][path])
        if (digest(raw) != (evidence_stage.get('source_sha256')) or
            digest(native) != (evidence_stage.get('native_sha256') or
                               evidence_stage.get('linux_native_sha256'))):
            raise ValueError(f'Iteration 50 recorded hashes mismatch: {path}')
    if (compact50['tested_large_linear_source_commands'] != 300001 or
        compact50['aarch64_instruction_simulations'] != 150 or
        stack50['verified_nesting_depth'] != 4096 or
        stack50['scanner_source_offset_bits'] != 32 or
        stack50['pair_event_offset_bits'] != 64 or
        million50['generated_native_code_bytes'] != 12000000 or
        million50['source_commands'] != 1000000):
        raise ValueError('Iteration 50 capacity claims do not match the evidence')
    status['android_dynamic_compact_iteration50'] = {
        'classification': compact50['classification'],
        'bf_source': compact50['bf_source'],
        'tested_million_linear_source_commands': million50['source_commands'],
        'tested_native_code_bytes': million50['generated_native_code_bytes'],
        'machine_code_only': True,
        'brackets_supported': False,
        'real_android_elf_emitted': False,
        'evidence': 'evidence/iteration50_android_compact_stream.json'}
    status['android_dynamic_stack_iteration50'] = {
        'classification': stack50['classification'],
        'bf_owned_pairing_control': True,
        'host_stack': 'GENERIC_DYNAMIC_FILE_BACKED_8_BYTE_RECORD_STORAGE',
        'max_nesting_tested': stack50['verified_nesting_depth'],
        'source_scanner_position_bits': 32,
        'generic_pair_storage_bits': 64,
        'wide_span_source_position': stack50['source_100m_closing_index'],
        'relocation_integrated_into_elf': False,
        'evidence': 'evidence/iteration50_android_dynamic_stack.json'}
    # Iteration 51 is a streaming raw code + matching-coordinate gate, NOT ELF.
    proof51 = jsonfile('evidence/iteration51_android_compact_relocation_bundle.json')
    for path, stage in proof51['stage_integrity'].items():
        code = check_source((ROOT/path).read_bytes())
        binary = ROOT / ('build/' + pathlib.Path(path).stem + '_x86_64_linux.elf')
        if (len(code) != stage['bf_commands'] or
            digest((ROOT/path).read_bytes()) != stage['source_sha256'] or
            digest(binary.read_bytes()) != stage['linux_native_sha256'] or
            binary.stat().st_size != stage['linux_native_bytes']):
            raise ValueError('Iteration 51 BF source/binary changed without verification: '+path)
    if (proof51['total_accepted_cases'] < 86 or
        proof51['maximum_source_commands_tested'] < 7502 or
        proof51['maximum_nesting_depth_tested'] < 1025 or
        proof51['total_bracket_pairs_checked'] < 1901 or
        proof51['expected_atomic_rejections'] < 5 or
        proof51['native_branch_words_patched'] or
        proof51['dynamic_loadable_elf_generated']):
        raise ValueError('Iteration 51 evidence classification mismatch')
    status['android_compact_code_and_pair_ledger_iteration51'] = {
        'classification': proof51['classification'],
        'bf_owned_eight_command_native_code': True,
        'bf_owned_64bit_native_word_position_ledger': True,
        'bf_owned_dynamic_file_backed_bracket_pairs': True,
        'tested_commands_in_one_source': proof51['maximum_source_commands_tested'],
        'tested_maximum_nesting_depth': proof51['maximum_nesting_depth_tested'],
        'patched_branches': False, 'loadable_android_elf': False,
        'android_device_executed': False,
        'verified_complete_elf_ceiling_unchanged': 2719,
        'original_app_policy_sources_compiled': 0,
        'evidence': 'evidence/iteration51_android_compact_relocation_bundle.json'}
    # Iteration 52: BF-owned compact branch encoding and ELF metadata.
    # This is Linux-hosted structural/simulator proof, NOT Android loader proof.
    proof52 = jsonfile('evidence/iteration52_android_dynamic_elf_tests.json')
    big52 = jsonfile('evidence/iteration52_large_synthetic.json')
    if (proof52.get('program_cases_passed', 0) < 55 or
        proof52.get('simulator_runs_at_two_load_biases', 0) < 110 or
        proof52.get('bracket_pairs_verified', 0) < 1165 or
        proof52.get('atomic_output_rejections', 0) < 4 or
        proof52.get('android_loader_executed') is not False or
        big52.get('bf_native_instructions') != 296307 or
        big52.get('bracket_pairs_relocated') != 1 or
        big52.get('readelf_passed') is not True or
        big52.get('android_executed') is not False):
        raise ValueError('Iteration 52 complete-ELF evidence is missing or overstated')
    for stage in proof52['bf_stages']:
        name = stage['stage']
        src = ROOT / f'experiments/{name}.bf'
        native = ROOT / f'build/{name}_x86_64_linux.elf'
        if (not src.is_file() or not native.is_file() or
            len(check_source(src.read_bytes())) != stage['bf_commands'] or
            stage['bf_commands'] > 16128 or
            digest(src.read_bytes()) != stage['source_sha256'] or
            digest(native.read_bytes()) != stage['linux_native_sha256'] or
            len(native.read_bytes()) != stage['linux_native_bytes']):
            raise ValueError('Iteration 52 BF source/binary verification mismatch: '+name)
    status['android_compact_dynamic_elf_iteration52'] = {
        'classification': 'LINUX_EXECUTED_BF_STAGES_PLUS_AARCH64_SIMULATOR_NOT_ANDROID_DEVICE',
        'all_eight_bf_instructions_emitted': True,
        'bf_owned_native_branch_words_and_patch_indices': True,
        'bf_owned_elf_headers_segment_sizes_and_startup': True,
        'dynamically_growing_compact_code': True,
        'legacy_fixed_2719_elf_route_unchanged': True,
        'small_program_differentials': proof52['program_cases_passed'],
        'simulated_aarch64_executions': proof52['simulator_runs_at_two_load_biases'],
        'largest_synthetic_source_commands_structurally_checked': big52['bf_native_instructions'],
        'synthetic_elf_file_bytes': big52['elf_bytes'],
        'direct_aarch64_branch_reach_limited': True,
        'android_loader_executed': False,
        'original_app_policy_sources_compiled': 0,
        'jni_shared_library_integration': False,
        'android_native_s2_on_new_backend': False,
        'small_suite_evidence': 'evidence/iteration52_android_dynamic_elf_tests.json',
        'synthetic_large_evidence': 'evidence/iteration52_large_synthetic.json'}
    # Iteration 53: all-eight-instruction dynamic ELF, BF-owned signed-64
    # PC-relative indirect loop jumps. Linux/AArch64 simulator only.
    proof53 = jsonfile('evidence/iteration53_android_far_elf_tests.json')
    big53 = jsonfile('evidence/iteration53_large_synthetic.json')
    if (proof53.get('small_program_cases_passed', 0) < 57 or
        proof53.get('aarch64_simulator_runs', 0) < 114 or
        proof53.get('bracket_pairs_checked', 0) < 1466 or
        proof53.get('independent_bf_interpreter_comparisons', 0) < 2 or
        proof53.get('fresh_stage_rebuilds_identical') != 4 or
        proof53.get('atomic_invalid_source_rejections', 0) < 4 or
        proof53.get('real_android_loader_execution') is not False or
        proof53.get('real_app_policy_compilations') != 0 or
        big53.get('filtered_bf_commands') != 296307 or
        big53.get('readelf_passed') is not True or
        big53.get('android_executed') is not False):
        raise ValueError('Iteration 53 long-range PC-relative proof missing or overstated')
    for stage in proof53['bf_stages']:
        name = stage['stage'];source = ROOT / f'experiments/{name}.bf'
        binary = ROOT / f'build/{name}_x86_64_linux.elf'
        if (not source.is_file() or not binary.is_file() or
            len(check_source(source.read_bytes())) != stage['bf_commands'] or
            stage['bf_commands'] > 16128 or
            digest(source.read_bytes()) != stage['source_sha256'] or
            digest(binary.read_bytes()) != stage['linux_native_sha256'] or
            binary.stat().st_size != stage['linux_native_bytes']):
            raise ValueError('Iteration 53 BF source or native stage integrity failed: '+name)
    status['android_compact_far_elf_iteration53'] = {
        'classification':proof53['classification'],
        'bf_owned_pc_relative_signed64_branch_literals':True,
        'bf_owned_far_branch_patch_positions':True,
        'direct_aarch64_imm26_jump_reach_limit':False,
        'above_imm26_actual_elf_jump_executed':False,
        'small_program_simulator_runs':proof53['aarch64_simulator_runs'],
        'small_program_bracket_pairs':proof53['bracket_pairs_checked'],
        'large_synthetic_commands_structurally_accepted':big53['filtered_bf_commands'],
        'large_synthetic_elf_bytes':big53['compiler_metadata']['elf_bytes'],
        'android_loader_executed':False,
        'original_app_policy_sources_compiled':0,
        'jni_library_integration':False,
        'universal_100m_native_compilation':False,
        'evidence':'evidence/iteration53_android_far_elf_tests.json',
        'synthetic_evidence':'evidence/iteration53_large_synthetic.json'}
    current = ROOT / 'evidence/android_execution_20261014.json'
    if current.exists():
        device = json.loads(current.read_text())
        for path, expected in device['evidence_sha256'].items():
            if digest((ROOT / path).read_bytes()) != expected:
                raise ValueError('Current Android device evidence changed: ' + path)
        build = jsonfile('evidence/gm_native_20261014_v4/build.json')
        for name, info in build['stages'].items():
            if digest((ROOT / f'experiments/{name}.bf').read_bytes()) != info['source_sha256']:
                raise ValueError('Current native GM compiler stage changed: ' + name)
        status['android_device_followup_20261014'] = device
    # Iteration 54: independently executed Linux replay of *original* GM
    # standard-BF policy compiler stages. This is not fresh Android execution.
    replay_path = ROOT / 'evidence/iteration54_linux_gm_policy_replay.json'
    if replay_path.exists():
        replay = jsonfile('evidence/iteration54_linux_gm_policy_replay.json')
        native54 = jsonfile('evidence/iteration54_linux_native_stage_parity.json')
        seeds54 = jsonfile('evidence/iteration54_seed_differentials.json')
        archived54 = jsonfile('evidence/gm_native_20261014_v4/build.json')
        if (replay.get('device_executed_in_this_run') is not False or
            replay.get('android_device_runtime_performance_retested') is not False or
            seeds54.get('cases_passed', 0) < 152 or
            len(native54.get('stages', [])) != 3):
            raise ValueError('Iteration 54 replay evidence has an unsupported classification')
        for name in ('row', 'scope'):
            record = replay['original_policy_images'][name]
            if (not record['exact_android_image_match'] or
                record['source_sha256'] != archived54['sources'][name]['source_sha256'] or
                record['elf_sha256'] != archived54['sources'][name]['elf_sha256'] or
                record['elf_bytes'] != archived54['sources'][name]['elf_bytes'] or
                digest((ROOT / 'evidence/gm_native_20261014_v4' / (name+'.elf')).read_bytes())
                != record['elf_sha256']):
                raise ValueError('Iteration 54 GM native image evidence mismatch: ' + name)
        for stage in native54['stages']:
            source = ROOT / f"experiments/{stage['stage']}.bf"
            binary = (ROOT / 'build/iteration54_linux/native_parity/android_source_scan.elf'
                      if stage['stage'] == 'android_source_scan' else
                      ROOT / 'build/iteration54_linux/stages' / (stage['stage']+'.elf'))
            if (not source.exists() or digest(binary.read_bytes()) != stage['elf_sha256'] or
                not stage['output_sha256']):
                raise ValueError('Iteration 54 native stage hash mismatch')
        status['android_gm_linux_replay_iteration54'] = {
            'classification':replay['classification'],
            'original_gm_policy_images_byte_identical':2,
            'early_linux_native_bf_stage_matches':len(native54['stages']),
            'independent_interpreter_differentials':seeds54['cases_passed'],
            'fresh_android_execution':False,
            'new_performance_claim':False,
            'twitter_threads_compiled':False,
            'hundred_million_command_compilation':False,
            'evidence':'evidence/iteration54_linux_gm_policy_replay.json',
            'stage_parity_evidence':'evidence/iteration54_linux_native_stage_parity.json',
            'seed_differential_evidence':'evidence/iteration54_seed_differentials.json',
        }
    # Iteration 55: opt-in callable Android policy optimization, executed on
    # Linux only. Archived GM stage hashes and Android device evidence stay pinned.
    report55 = ROOT / 'evidence/iteration55_policy_valuefold.json'
    if report55.exists():
        evidence55 = jsonfile('evidence/iteration55_policy_valuefold.json')
        semantics55 = jsonfile('evidence/iteration55_policy_semantics.json')
        selfhost55 = jsonfile('evidence/iteration55_linux_selfhost.json')
        if (evidence55['tests_passed'] < 109 or
            evidence55['independent_bf_interpreter_cases'] < 2 or
            evidence55['full_original_gmail_source_to_native_images'] != 2 or
            evidence55['device_executed'] is not False or
            evidence55['apk_parity_rerun'] is not False or
            semantics55['original_vs_valuefold_frames_completed_equal'] < 480 or
            len(selfhost55['native_stage_runs']) != 2):
            raise ValueError('Iteration 55 evidence insufficient')
        for stage in evidence55['stages']:
            source = ROOT / 'experiments' / (stage['stage']+'.bf')
            binary55 = ROOT / 'build/iteration55_linux/stages' / (stage['stage']+'.elf')
            if (digest(source.read_bytes()) != stage['source_sha256'] or
                digest(binary55.read_bytes()) != stage['elf_sha256'] or
                len(check_source(source.read_bytes())) != stage['source_commands'] or
                stage['source_commands'] > 16128):
                raise ValueError('Iteration 55 standard-BF stage mismatch: '+stage['stage'])
        for name in ('row','scope'):
            old = ROOT / 'evidence/gm_native_20261014_v4' / (name+'.elf')
            new = ROOT / 'build/iteration55_linux/gmail' / (name+'.elf')
            obj = evidence55['gmail'][name]
            if (digest(old.read_bytes()) != obj['original_sha256'] or
                digest(new.read_bytes()) != obj['new_sha256'] or
                len(new.read_bytes()) != obj['new_bytes'] or
                obj['new_bytes'] >= obj['original_bytes']):
                raise ValueError('Iteration 55 Gmail ELF artifact mismatch')
        status['android_gm_policy_valuefold_iteration55'] = {
            'classification':evidence55['classification'],
            'optional_production_implementation':'STANDARD_BRAINFUCK_STAGES',
            'original_gmail_policies_compiled':2,
            'gmail_ir_cases':semantics55['original_vs_valuefold_frames_completed_equal'],
            'source_to_image_differentials':evidence55['tests_passed'],
            'independent_interpreter_cases':evidence55['independent_bf_interpreter_cases'],
            'device_executed_this_iteration':False,
            'runtime_speedup_established':False,
            'new_apk_parity':False,
            'baseline_android_artifacts_unchanged':True,
            'twitter_threads_compiled':False,
            'universal_100m_compilation':False,
            'evidence':'evidence/iteration55_policy_valuefold.json',
            'semantics_evidence':'evidence/iteration55_policy_semantics.json',
        }
    # Iteration 56 is a real first Twitter policy source-to-image compilation,
    # not a general removal of the bounded callable tape or Android execution.
    report56 = ROOT / 'evidence/iteration56_policy_clear.json'
    if report56.exists():
        proof = jsonfile('evidence/iteration56_policy_clear.json')
        src56 = ROOT / 'experiments/policy_clear56.bf'
        native56 = ROOT / 'build/iteration56_linux/stages/policy_clear56.elf'
        twitter_source = ROOT / 'tests/fixtures/real_apps/twitter_action_filtered.bf'
        twitter_elf = ROOT / 'build/iteration56_linux/twitter_action/action.elf'
        tw = proof['twitter_action']
        if (proof['classification'] != 'LINUX_NATIVE_BF_CANONICAL_CLEAR_RLE_PREPASS' or
            proof['source_commands'] != len(check_source(src56.read_bytes())) or
            proof['source_commands'] != 3631 or
            proof['source_sha256'] != digest(src56.read_bytes()) or
            proof['native_elf_sha256'] != digest(native56.read_bytes()) or
            proof['native_elf_bytes'] != native56.stat().st_size or
            proof['differential_cases'] < 136 or
            proof['independent_bf_interpreter_cases'] < 4 or
            not proof['large_shape_resolver_accepted'] or
            tw['effective_source_sha256'] != digest(twitter_source.read_bytes()) or
            tw['effective_source_commands'] != len(check_source(twitter_source.read_bytes())) or
            tw['effective_source_commands'] != 24616 or
            (tw['original_rle_records'],tw['canonical_rle_records']) != (4723,3819) or
            tw['compiled_aarch64_sha256'] != digest(twitter_elf.read_bytes()) or
            tw['compiled_aarch64_elf_bytes'] != twitter_elf.stat().st_size or
            tw['compiled_aarch64_elf_bytes'] != 15300 or
            not tw['independent_native_byte_oracle'] or
            tw['independent_source_bf_vs_optimized_ir_frame_parity'] < 10 or
            tw['real_android_loader_executed'] is not False or
            tw['android_jni_or_apk_tested'] is not False):
            raise ValueError('Iteration 56 Twitter original-policy evidence mismatch')
        for name in ('row','scope'):
            item = proof['gmail_regression'][name]
            base = ROOT / f'evidence/gm_native_20261014_v4/{name}.elf'
            folded = ROOT / f'build/iteration55_linux/gmail/{name}.elf'
            if (not item['previous_android_image_byte_identical'] or
                not item['iteration55_optimized_image_byte_identical'] or
                item['baseline_sha256'] != digest(base.read_bytes()) or
                item['valuefold_sha256'] != digest(folded.read_bytes())):
                raise ValueError('Iteration 56 Gmail regression evidence mismatch')
        status['android_twitter_action_callable_iteration56'] = {
            'classification':proof['classification'],
            'source_language':'STRICT_EIGHT_INSTRUCTION_BRAINFUCK',
            'optional_bf_prepass':'experiments/policy_clear56.bf',
            'original_twitter_policies_compiled':1,
            'first_policy':'TwitterHideAds/brainfuck/src/action.bf',
            'source_commands':tw['effective_source_commands'],
            'rle_records_before':tw['original_rle_records'],
            'rle_records_after':tw['canonical_rle_records'],
            'callable_aarch64_elf_bytes':tw['compiled_aarch64_elf_bytes'],
            'independent_ir_frame_comparisons':tw['independent_source_bf_vs_optimized_ir_frame_parity'],
            'existing_4096_record_ir_ceiling_removed':False,
            'actual_android_device_execution':False,
            'twitter_apk_jni_integration':False,
            'universal_100m_native_compilation':False,
            'evidence':'evidence/iteration56_policy_clear.json'}
    # Iteration 57: the new callable lane is dynamic for linear sources only.
    # Do not promote it to an all-eight-operator or Android-device capability.
    proof57 = jsonfile('evidence/iteration57_dynamic_callable_linear.json')
    if (proof57.get('classification') != 'LINUX_NATIVE_BF_DYNAMIC_CALLABLE_LINEAR_PLUS_AARCH64_SIMULATOR'
        or proof57.get('small_cases', 0) < 60
        or proof57.get('simulator_runs', 0) < 240
        or proof57.get('elf_header_wide_sizes', 0) < 14
        or proof57.get('loops_supported') is not False
        or proof57.get('large_record_cases', {}).get('raw_beyond_legacy_1m', {}).get('raw_source_bytes', 0) <= 1048576
        or proof57.get('full_dynamic_callable_complete') is not False
        or proof57.get('android_device_executed') is not False):
        raise ValueError('Iteration 57 dynamic callable evidence mismatch')
    for stage in ('android_callable_linear57', 'android_callable_header57'):
        item = proof57['source_purity'][stage]
        raw = (ROOT / 'experiments' / (stage + '.bf')).read_bytes()
        native = (ROOT / 'build/iteration57_dynamic' / (stage + '.elf')).read_bytes()
        if (len(check_source(raw)) != item['bf_commands']
            or digest(raw) != item['source_sha256']
            or digest(native) != item['native_stage_sha256']
            or not item['BF_compiler_rebuild_byte_identical']):
            raise ValueError('Iteration 57 BF stage hash mismatch: ' + stage)
    status['android_dynamic_callable_linear_iteration57'] = {
        'classification': proof57['classification'],
        'source_language': 'EIGHT_STANDARD_BF_INSTRUCTIONS',
        'native_target': 'AARCH64_ET_DYN_BFP1_CALLABLE',
        'BF_owned_native_emitter': 'experiments/android_callable_linear57.bf',
        'BF_owned_64bit_elf_header': 'experiments/android_callable_header57.bf',
        'test_sources': proof57['small_cases'],
        'simulated_AArch64_executions': proof57['simulator_runs'],
        'large_linear_sources': proof57['large_record_cases'],
        'old_IR_record_ceiling_applies': False,
        'has_implicit_100m_goal': False,
        'brackets': 'NOT_IMPLEMENTED_ON_DYNAMIC_CALLABLE_LANE',
        'android_device_execution': 'NOT_TESTED',
        'JNI_shared_library_and_APK': 'NOT_IMPLEMENTED',
        'previous_paths': 'FALLBACK_UNTIL_VERIFIED_FULL_DYNAMIC_REPLACEMENT',
        'evidence': 'evidence/iteration57_dynamic_callable_linear.json'}
    save('status/CONFORMANCE_MATRIX.json', status)
    keep = sorted(path for path in ROOT.rglob('*')
                  if path.is_file()
                  and 'build/COMPILER_SOURCE_SHA256.txt' not in str(path)
                  and 'status/BUILD_MANIFEST.json' not in str(path)
                  and '__pycache__' not in str(path)
                  and path.suffix not in ('.pyc', '.zip'))
    manifest = {
        'as_of': bootstrap['date'],
        'canonical_compiler': 'compiler/core.bf',
        'canonical_source_sha256': source_sha,
        'project_requirements_sha256': digest((ROOT / 'docs/PROJECT_REQUIREMENTS.md').read_bytes()),
        'native_compiler_elf_sha256': binary_sha,
        'stage0_stage1_stage2_identical': True,
        'correctness_test_count': correctness['passed'],
        'build_accepted_as': 'S2 EXECUTED under bounded semantics; read/write EINTR retry; EAGAIN fails fast',
        'files': {str(p.relative_to(ROOT)): digest(p.read_bytes()) for p in keep},
    }
    save('status/BUILD_MANIFEST.json', manifest)
    print(f"Derived status: S2, {correctness['passed']} tests, {len(manifest['files'])} files")


if __name__ == '__main__':
    main()
