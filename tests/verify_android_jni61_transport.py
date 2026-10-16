#!/usr/bin/env python3
"""Exercise device-adapter evidence guards without pretending fake ADB is Android."""
from __future__ import annotations
from pathlib import Path
import subprocess
import tempfile
from unittest.mock import patch

from tools.android_bfp1_bridge import device_acceptance61 as adapter


def exercise():
    with tempfile.TemporaryDirectory(prefix='bfc61-fake-adb-') as tmp:
        bridge=Path(tmp)/'libbrainfuckcc_bridge.so'; bridge.write_bytes(b'host fake bridge')
        dex=Path(tmp)/'test.jar';dex.write_bytes(b'fake dex')
        transferred={}
        call_count=[0]
        expected={f'PASS JNI {case}' for case in adapter.CASES}
        expected.add('PASS JNI transport_guards')
        expected.add('PASS JNI suite 9 policy fixtures')

        def fake_run(cmd,**kwargs):
            assert cmd[:3]==['adb','-s','fake-serial'],cmd
            assert kwargs['check'] and kwargs['capture_output'] and kwargs['text']
            if cmd[3]=='shell' and cmd[4].startswith('mkdir -p '):
                return subprocess.CompletedProcess(cmd,0,'','')
            if cmd[3]=='push':
                local=Path(cmd[4]);remote=cmd[5]
                transferred[remote]=adapter.digest(local)
                return subprocess.CompletedProcess(cmd,0,'1 file pushed','')
            if cmd[3:5]==['shell','-T']:
                call_count[0]+=1
                assert 'app_process' in cmd[5] and 'Bfp1AndroidDeviceTest' in cmd[5]
                # Simulated transport returns a complete, ordered, fixture transcript.
                return subprocess.CompletedProcess(cmd,0,'\n'.join(sorted(expected))+'\n','')
            if cmd[3]=='shell' and cmd[4].startswith('sha256sum '):
                remote=cmd[4][len('sha256sum '):]
                assert remote in transferred
                return subprocess.CompletedProcess(cmd,0,transferred[remote]+'  '+remote+'\n','')
            raise AssertionError(f'unexpected adapter action: {cmd}')

        with patch.object(adapter.subprocess,'run',fake_run):
            record=adapter.run_android_jni('adb','fake-serial',bridge,dex)
        assert record['jni_art_device_execution'] is True
        assert record['apk_execution_verified'] is False
        assert len(record['artifact_sha256'])==11
        assert len(transferred)==11 and call_count[0]==1

        def wrong_hash(cmd,**kwargs):
            if cmd[3]=='shell' and cmd[4].startswith('sha256sum '):
                return subprocess.CompletedProcess(cmd,0,'0'*64+'  fake\n','')
            return fake_run(cmd,**kwargs)
        with patch.object(adapter.subprocess,'run',wrong_hash):
            try:adapter.run_android_jni('adb','fake-serial',bridge,dex)
            except RuntimeError as exc:
                assert 'SHA-256 mismatch' in str(exc)
            else:raise AssertionError('corrupt pushed library was accepted')

        def wrong_transcript(cmd,**kwargs):
            if cmd[3:5]==['shell','-T']:
                return subprocess.CompletedProcess(cmd,0,'PASS JNI empty\n','')
            return fake_run(cmd,**kwargs)
        with patch.object(adapter.subprocess,'run',wrong_transcript):
            try:adapter.run_android_jni('adb','fake-serial',bridge,dex)
            except AssertionError as exc:
                assert 'stdout mismatch' in str(exc)
            else:raise AssertionError('incomplete device transcript was accepted')
    print('PASS simulated ADB transport: exact fixture manifest, hashes, fail-closed output')

if __name__=='__main__':exercise()
