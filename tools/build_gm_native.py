"""Build an isolated GM APK with BF-owned callable native policy code."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from bootstrap.run_policy_native import PolicyCompiler


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--gm', type=Path, default=Path(r'D:\Android\AndroidStudioProjects\GM'))
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--serial')
    parser.add_argument('--proof', type=Path)
    parser.add_argument('--no-affine', action='store_true', help='Diagnostic unoptimized build; may exhaust GM loop budgets')
    args = parser.parse_args()
    out = args.output.resolve()
    if out.exists() and any(out.iterdir()): parser.error('output must be absent or empty')
    out.mkdir(parents=True, exist_ok=True)
    compiler = PolicyCompiler(out / 'pipeline', args.serial, args.proof)
    sources = {}
    for name in ('row', 'scope'):
        path = args.gm / 'brainfuck/src' / (name + '.bf')
        image = compiler.compile(path.read_bytes(), not args.no_affine)
        if (image[:4] != b'\x7fELF' or image[120:124] != b'BFP1' or
                not 0 < int.from_bytes(image[124:126], 'little') <= 32 or image[126:128] != b'\1\0'):
            raise ValueError('GM policy must carry a proved 32-cell callable ABI')
        (out / (name + '.elf')).write_bytes(image)
        sources[name] = {'source_sha256': sha(path), 'elf_sha256': sha(out / (name + '.elf')),
                         'elf_bytes': len(image)}
        print(f'{name}: BF-owned callable ELF, {len(image)} bytes', flush=True)
    app = out / 'GM'
    shutil.copytree(args.gm, app, ignore=shutil.ignore_patterns('build', '.gradle', '.git', '.idea', '__pycache__'))
    cpp = app / 'app/src/main/cpp'
    shutil.copyfile(ROOT / 'tools/gm_native/bf_jni.c', cpp / 'bf_native_jni.c')
    shutil.copyfile(ROOT / 'tools/gm_native/CMakeLists.txt', cpp / 'CMakeLists.txt')
    assembly = ['.section .text.bf,"ax",%progbits']
    for name in ('row', 'scope'):
        shutil.copyfile(out / (name + '.elf'), cpp / (name + '.elf'))
        assembly += ['.balign 16', f'.global bf_{name}', f'.hidden bf_{name}',
                     f'bf_{name}:', f'.incbin "{(cpp / (name + ".elf")).as_posix()}"']
    assembly += ['.section .note.GNU-stack,"",%progbits']
    (cpp / 'bf_native.S').write_text('\n'.join(assembly) + '\n')
    init = out / 'native.init.gradle'
    init.write_text('gradle.afterProject { p, state ->\n'
                   "  if (p.path == ':app') {\n"
                   "    def a = p.extensions.getByName('android')\n"
                   "    a.defaultConfig.applicationId = 'io.github.mrxsin.gmailhideads.nativebf'\n"
                   "    a.defaultConfig.ndk.abiFilters.add('arm64-v8a')\n"
                   '  }\n}\n')
    env = dict(os.environ, JAVA_HOME=r'C:\Program Files\Android\Android Studio\jbr')
    command = [str(app / 'gradlew.bat'), '--offline', '-I', str(init), '-PbenchmarkRelease',
               ':app:assembleRelease', ':app:assembleReleaseAndroidTest', '--console=plain']
    with (out / 'gradle.log').open('wb') as log:
        subprocess.run(command, cwd=app, env=env, stdout=log, stderr=subprocess.STDOUT,
                       check=True, timeout=900)
    apk = app / 'app/build/outputs/apk/release/GmailHideAds-v2.1.0.apk'
    test = app / 'app/build/outputs/apk/androidTest/release/app-release-androidTest.apk'
    shutil.copyfile(apk, out / 'app.apk'); shutil.copyfile(test, out / 'test.apk')
    with zipfile.ZipFile(apk) as archive:
        native = archive.read('lib/arm64-v8a/libgmailbf.so')
        for name in sources: assert (out / (name + '.elf')).read_bytes() in native
    report = {'backend': 'STANDARD_BRAINFUCK_CALLABLE_AARCH64_WITH_NEW_PLATFORM_JNI_BRIDGE',
              'original_gm_modified': False, 'old_bf_to_c_backend_linked': False,
              'compiler_stages_android_native': bool(args.serial), 'affine_fusion': not args.no_affine,
              'proved_single_iteration_loops': not args.no_affine,
              'sources': sources, 'stages': compiler.inventory,
              'apk_sha256': sha(out / 'app.apk'), 'test_apk_sha256': sha(out / 'test.apk'),
              'native_library_sha256': hashlib.sha256(native).hexdigest(),
              'bf_elf_bytes_embedded_unchanged': True,
              'build_command': command, 'device_tests_executed': False}
    (out / 'build.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Built isolated direct-native GM APK and test APK', flush=True)


if __name__ == '__main__': main()
