#!/usr/bin/env python3
"""Reject broken local documentation links and unsupported current-state numbers.

Editorial voice needs a human. This checks facts and missing files, not jokes.
The incoming project requirements and archived historical notes are immutable inputs.
"""
import hashlib
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
from source_check import check_source, source_digests
PADDING = 0
SOURCE_LIMIT = 16128


def main() -> None:
    source = (ROOT / 'compiler/core.bf').read_bytes()
    code = check_source(source)
    assert code and len(code) == 14859
    sha = hashlib.sha256(source).hexdigest()
    binary = (ROOT / 'build/compiler_x86_64_linux.elf').read_bytes()
    expected_size = 215 + len(code) * 32
    if len(binary) != expected_size:
        raise AssertionError(f'installed compiler size {len(binary)} is not {expected_size}')
    # New experimental Android source stages must keep honest, hash-bound notes.
    for item in ('android_streaming_compact_slots', 'android_dynamic_stack_pairs',
                 'android_pair_event_bridge', 'android_streaming_compact_all8',
                 'android_compact_native_offset_ledger51'):
        new_bf_source = ROOT / 'experiments' / (item + '.bf')
        compiled = ROOT / 'build' / (item + '_x86_64_linux.elf')
        notes = ROOT / 'experiments' / (item + '.bf.notes.md')
        command_stream = check_source(new_bf_source.read_bytes())
        body = notes.read_text(encoding='utf-8')
        if (len(command_stream) > SOURCE_LIMIT or
            hashlib.sha256(new_bf_source.read_bytes()).hexdigest() not in body or
            hashlib.sha256(compiled.read_bytes()).hexdigest() not in body):
            raise AssertionError(f'Android dynamic stage notes out of sync: {item}')
    # Resource-scaled callable stage inputs are still ordinary checked BF.
    for name in ('android_callable_slots58','android_callable_ledger58'):
        bf = ROOT/'experiments'/f'{name}.bf'
        elf = ROOT/'build/iteration58_dynamic'/f'{name}.elf'
        notes = ROOT/'experiments'/f'{name}.bf.notes.md'
        stage_commands = check_source(bf.read_bytes())
        body = notes.read_text()
        if not stage_commands or len(stage_commands)>SOURCE_LIMIT:
            raise AssertionError(f'iteration58 stage source exceeds verified compiler: {name}')
        for digest in (hashlib.sha256(bf.read_bytes()).hexdigest(),
                       hashlib.sha256(elf.read_bytes()).hexdigest()):
            if digest not in body:
                raise AssertionError(f'iteration58 BF stage note hash mismatch: {name}')
    required = (ROOT / 'docs/PROJECT_REQUIREMENTS.md').read_text(encoding='utf-8')
    targets = (ROOT / 'docs/TARGETS.md').read_text(encoding='utf-8')
    if ('Windows x86-64' not in required or 'Android AArch64' not in required or
        'Windows x86-64' not in targets or 'Android AArch64' not in targets):
        raise AssertionError('mandatory target requirements are missing from maintained docs')
    audit = ROOT / 'evidence/compiler_tape_audit.json'
    if not audit.is_file():
        raise AssertionError('compiler tape audit evidence missing')
    docs = sorted(p for p in ROOT.rglob('*.md')
                  if not {'build', 'evidence'}.intersection(p.relative_to(ROOT).parts)
                  and p.name != 'PROJECT_REQUIREMENTS.md')
    for doc in docs:
        content = doc.read_text(encoding='utf-8')
        if not content.startswith('# '):
            raise AssertionError(f'{doc.relative_to(ROOT)} has no title')
        # Markdown links only; bare relative paths are okay as prose.
        for target in re.findall(r'(?<!!)\[[^]]+\]\(([^)]+)\)', content):
            if target.startswith(('https://', 'http://', '#', 'mailto:')):
                continue
            path = (doc.parent / target.split('#')[0]).resolve()
            if not path.is_relative_to(ROOT) or not path.exists():
                raise AssertionError(f'{doc.relative_to(ROOT)} points to missing {target}')
    notes = (ROOT / 'compiler/core.bf.notes.md').read_text()
    ranges = re.findall(r'^\| `(\d+):(\d+)` \|', notes, re.M)
    if (f'Source SHA-256: `{sha}`' not in notes or
            f'Filtered instruction SHA-256: `{hashlib.sha256(code).hexdigest()}`' not in notes or
            not ranges or int(ranges[-1][1]) != len(code)):
        raise AssertionError('annotation hash/last offset is stale')
    for name in ['README.md', 'docs/STATE.md', 'docs/ARCHITECTURE.md',
                 'docs/SELF_HOSTING.md', 'docs/HANDOFF.md']:
        text = (ROOT / name).read_text()
        if f'{len(source):,}' not in text:
            raise AssertionError(f'{name} does not report current source size')
    for name in ['README.md', 'docs/STATE.md', 'docs/HARDENING.md',
                 'docs/HANDOFF.md']:
        text = (ROOT / name).read_text()
        if ('zero' not in text.lower() and '0 bytes' not in text.lower()):
            raise AssertionError(f'{name} does not explain that fixed trailing padding is gone')
    if f'{SOURCE_LIMIT - len(source)}' not in (ROOT / 'docs/STATE.md').read_text():
        raise AssertionError('current headroom is missing')
    if 'docs/STYLE.md' not in (ROOT / 'AGENT.md').read_text():
        raise AssertionError('agent instructions do not point at the documentation style')
    # New opt-in callable policy first real Twitter source acceptance gate.
    gate56 = ROOT / 'evidence/iteration56_policy_clear.json'
    if gate56.exists():
        import json
        proof56 = json.loads(gate56.read_text())
        s56 = ROOT / 'experiments/policy_clear56.bf'
        native56 = ROOT / 'build/iteration56_linux/stages/policy_clear56.elf'
        assert len(check_source(s56.read_bytes())) == proof56['source_commands'] == 3631
        assert hashlib.sha256(s56.read_bytes()).hexdigest() == proof56['source_sha256']
        assert hashlib.sha256(native56.read_bytes()).hexdigest() == proof56['native_elf_sha256']
        assert proof56['twitter_action']['compiled_aarch64_elf_bytes'] == 15300
        assert not proof56['device_executed']
        assert (ROOT / 'docs/ITERATION56_TWITTER_ACTION_CLEAR.md').is_file()
        assert (ROOT / 'docs/ANDROID_APP_ROADMAP_ITERATION56.md').is_file()
        matrix = json.loads((ROOT/'status/CONFORMANCE_MATRIX.json').read_text())
        record56 = matrix['android_twitter_action_callable_iteration56']
        assert record56['original_twitter_policies_compiled'] == 1
        assert not record56['existing_4096_record_ir_ceiling_removed']
        assert not record56['actual_android_device_execution']
    # Iteration 27 is an experimental BF module, not the canonical compiler.
    scan = ROOT / 'experiments/android_source_scan.bf'
    if scan.exists():
        import json
        scan_source = scan.read_bytes()
        scan_stream = check_source(scan_source)
        scan_evidence = json.loads((ROOT / 'evidence/iteration27_source_scan.json').read_text())
        scan_notes = (ROOT / 'experiments/android_source_scan.bf.notes.md').read_text()
        scan_elf = ROOT / 'build/android_source_scan_x86_64_linux.elf'
        digest = hashlib.sha256(scan_source).hexdigest()
        assert scan_evidence['source_sha256'] == digest
        assert scan_evidence['instructions'] == len(scan_stream) == 1170
        assert scan_evidence['native_linux_elf_sha256'] == hashlib.sha256(scan_elf.read_bytes()).hexdigest()
        assert f'Source SHA-256: `{digest}`' in scan_notes
        assert f'Filtered instruction SHA-256: `{hashlib.sha256(scan_stream).hexdigest()}`' in scan_notes
        scan_matrix = json.loads((ROOT / 'status/CONFORMANCE_MATRIX.json').read_text())['android_source_scan_iteration27']
        assert scan_matrix['target_compilation_source_limit_commands'] == 10
        assert scan_matrix['tested_executable_source_commands'] == 300001
    wide = ROOT / 'evidence/iteration28_wide_brackets.json'
    if wide.exists():
        import json
        proof = json.loads(wide.read_text())
        matrix = json.loads((ROOT/'status/CONFORMANCE_MATRIX.json').read_text())
        assert matrix['android_wide_brackets_iteration28']['android_emitter_command_limit'] == 10
        assert matrix['android_wide_brackets_iteration28']['wide_aarch64_branch_encoding'] == 'RECORDS_EXECUTED_LINUX_ONLY'
        assert proof['valid_pairing_cases'] >= 400 and proof['invalid_cases_rejected'] >= 100
        for stage in proof['stages'].values():
            source = ROOT / stage['bf_source']
            binary = ROOT / stage['native_linux_elf']
            executable = check_source(source.read_bytes())
            assert len(executable) == stage['brainfuck_instructions']
            assert hashlib.sha256(source.read_bytes()).hexdigest() == stage['source_sha256']
            assert hashlib.sha256(executable).hexdigest() == stage['filtered_sha256']
            assert hashlib.sha256(binary.read_bytes()).hexdigest() == stage['linux_native_elf_sha256']
            assert len(binary.read_bytes()) == 215 + 32 * len(executable)
            note = (ROOT / (stage['bf_source']+'.notes.md')).read_text()
            assert stage['source_sha256'] in note
            assert stage['filtered_sha256'] in note
    branch = ROOT / 'evidence/iteration28_wide_branch_encoding.json'
    if branch.exists():
        import json
        payload = json.loads(branch.read_text())
        src = ROOT / payload['source']
        native = ROOT / payload['native_linux_elf']
        ops = check_source(src.read_bytes())
        assert len(ops) == payload['brainfuck_instructions'] == 13985
        assert hashlib.sha256(src.read_bytes()).hexdigest() == payload['source_sha256']
        assert hashlib.sha256(ops).hexdigest() == payload['filtered_sha256']
        assert hashlib.sha256(native.read_bytes()).hexdigest() == payload['linux_native_elf_sha256']
        note = (ROOT / (payload['source'] + '.notes.md')).read_text()
        assert payload['source_sha256'] in note and payload['filtered_sha256'] in note
        assert payload['maximum_supported_bracket_separation'] == 2796201
        assert matrix['android_wide_branch_encoding_iteration28']['android_final_emitter_command_limit'] == 10
    patch = ROOT / 'evidence/iteration29_wide_slot_patch.json'
    if patch.exists():
        import json
        result = json.loads(patch.read_text())
        codefile = ROOT / result['source']
        source = codefile.read_bytes()
        commands = check_source(source)
        native = (ROOT / result['native_linux_elf']).read_bytes()
        assert len(commands) == result['bf_instructions'] == 2389
        assert hashlib.sha256(source).hexdigest() == result['source_sha256']
        assert hashlib.sha256(commands).hexdigest() == result['filtered_sha256']
        assert hashlib.sha256(native).hexdigest() == result['native_linux_elf_sha256']
        assert len(native) == result['native_linux_elf_bytes'] == 215 + 32*len(commands)
        assert result['programs_simulated'] == 85 and result['relocated_bracket_pairs_total'] == 390
        notes = (ROOT / (result['source']+'.notes.md')).read_text()
        assert result['source_sha256'] in notes and result['filtered_sha256'] in notes
        status = json.loads((ROOT / 'status/CONFORMANCE_MATRIX.json').read_text())
        target = status['android_wide_74_slot_loop_pipeline']
        assert target['max_source_instructions'] == 74
        assert target['evidence'] == 'evidence/iteration29_wide_slot_patch.json'
        assert not target['android_native_compiler_execution']
        assert not target['android_native_selfhosting']
    # Iteration 30 is a separately evidenced BF native ELF writer, not a claim
    # of Android device execution or dynamic on-disk file size yet.
    dynamic = ROOT / 'evidence/iteration30_dynamic_elf.json'
    if dynamic.exists():
        import json
        proof = json.loads(dynamic.read_text())
        stage = proof['stage']
        bf_src = ROOT / stage['source']
        bf_native = ROOT / stage['native_linux_elf']
        stream = check_source(bf_src.read_bytes())
        assert len(stream) == stage['bf_instructions'] == 9087
        assert hashlib.sha256(bf_src.read_bytes()).hexdigest() == stage['source_sha256']
        assert hashlib.sha256(stream).hexdigest() == stage['filtered_sha256']
        assert hashlib.sha256(bf_native.read_bytes()).hexdigest() == stage['native_linux_elf_sha256']
        assert len(bf_native.read_bytes()) == stage['native_linux_elf_bytes'] == 215 + 32*len(stream)
        assert stage['source_sha256'] in (ROOT / (stage['source']+'.notes.md')).read_text()
        assert stage['filtered_sha256'] in (ROOT / (stage['source']+'.notes.md')).read_text()
        matrix = json.loads((ROOT / 'status/CONFORMANCE_MATRIX.json').read_text())
        record = matrix['android_dynamic_rx_iteration30']
        assert record['evidence'] == 'evidence/iteration30_dynamic_elf.json'
        assert record['maximum_linear_commands'] == 255
        assert record['maximum_commands_with_brackets'] == 74
        assert record['full_elf_bytes_per_supported_size_class'] == 16480
        assert not record['elf_file_size_varies_with_command_count']
        assert not record['android_native_selfhosting']
        assert proof['all_256_count_values_passed']
    # New current-state records are additive; historical iteration records are
    # deliberately not rewritten when later device evidence appears.
    android_v3 = ROOT / 'evidence/android_native_selfhost_20261013_v3/report.json'
    windows_seed = ROOT / 'evidence/iteration38_transition.json'
    if android_v3.exists() and windows_seed.exists():
        import json
        report = json.loads(android_v3.read_text())
        matrix = json.loads((ROOT / 'status/CONFORMANCE_MATRIX.json').read_text())
        android_code = check_source((ROOT / report['source']).read_bytes())
        assert len(android_code) == report['bf_instructions'] == 14575
        assert report['compiler_elf_bytes'] == 933008
        assert matrix['android_native_s2_current']['compiler_native_selfhosting'].startswith('S2_EXECUTED')
        assert 'S2 EXECUTED' in matrix['required_native_targets']['android_aarch64']['selfhosting']
        for n in range(4):
            elf = ROOT / f'evidence/android_native_selfhost_20261013_v3/stage{n}.elf'
            assert hashlib.sha256(elf.read_bytes()).hexdigest() == report['compiler_elf_sha256']
        win = json.loads(windows_seed.read_text())['windows_pe_exit_seed']
        win_src = ROOT / win['source']
        assert len(check_source(win_src.read_bytes())) == win['bf_instructions'] == 6194
        assert hashlib.sha256(win_src.read_bytes()).hexdigest() == win['source_sha256']
        assert hashlib.sha256((ROOT / win['output']).read_bytes()).hexdigest() == win['output_sha256']
        assert matrix['required_native_targets']['windows_x86_64']['native_compiler_execution'] == 'UNIMPLEMENTED'
        assert 'NOT_WINDOWS_EXECUTED' in matrix['windows_pe_exit_seed_iteration38']['classification']
        assert 'archived device evidence audit' in (ROOT / 'docs/ANDROID_NATIVE_S2_AUDIT.md').read_text().lower()
    proof52 = ROOT / 'evidence/iteration52_android_dynamic_elf_tests.json'
    if proof52.exists():
        import json
        test = json.loads(proof52.read_text())
        matrix = json.loads((ROOT/'status/CONFORMANCE_MATRIX.json').read_text())
        record = matrix['android_compact_dynamic_elf_iteration52']
        assert test['program_cases_passed'] >= 55
        assert record['simulated_aarch64_executions'] >= 110
        assert record['android_loader_executed'] is False
        assert record['original_app_policy_sources_compiled'] == 0
        assert record['direct_aarch64_branch_reach_limited'] is True
        for row in test['bf_stages']:
            name = row['stage']
            bf = ROOT / f'experiments/{name}.bf'
            exe = ROOT / f'build/{name}_x86_64_linux.elf'
            note = (ROOT / f'experiments/{name}.bf.notes.md').read_text()
            assert row['source_sha256'] == hashlib.sha256(bf.read_bytes()).hexdigest()
            assert row['linux_native_sha256'] == hashlib.sha256(exe.read_bytes()).hexdigest()
            assert row['source_sha256'] in note and row['linux_native_sha256'] in note
            assert len(check_source(bf.read_bytes())) <= SOURCE_LIMIT
    proof53 = ROOT / 'evidence/iteration53_android_far_elf_tests.json'
    if proof53.exists():
        import json
        proof = json.loads(proof53.read_text())
        large = json.loads((ROOT/'evidence/iteration53_large_synthetic.json').read_text())
        matrix = json.loads((ROOT/'status/CONFORMANCE_MATRIX.json').read_text())
        record = matrix['android_compact_far_elf_iteration53']
        assert record['direct_aarch64_imm26_jump_reach_limit'] is False
        assert record['above_imm26_actual_elf_jump_executed'] is False
        assert record['original_app_policy_sources_compiled'] == 0
        assert record['android_loader_executed'] is False
        assert proof['small_program_cases_passed'] >= 57
        assert proof['aarch64_simulator_runs'] >= 114
        assert large['filtered_bf_commands'] == 296307
        assert large['readelf_passed'] and not large['android_executed']
        for stage in proof['bf_stages']:
            name=stage['stage']
            src=ROOT/f'experiments/{name}.bf'
            binary=ROOT/f'build/{name}_x86_64_linux.elf'
            notes=(ROOT/f'experiments/{name}.bf.notes.md').read_text()
            assert hashlib.sha256(src.read_bytes()).hexdigest()==stage['source_sha256']
            assert hashlib.sha256(binary.read_bytes()).hexdigest()==stage['linux_native_sha256']
            assert stage['source_sha256'] in notes and stage['linux_native_sha256'] in notes
            assert len(check_source(src.read_bytes())) <= SOURCE_LIMIT
    print(f'PASS {len(docs)} maintained Markdown files, local links, source count, annotation hash and ELF size')


if __name__ == '__main__':
    main()
