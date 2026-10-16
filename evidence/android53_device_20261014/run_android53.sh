#!/system/bin/sh
# Execute only on Android AArch64 from an executable filesystem.
# Copy bundle to /data/local/tmp/android53, chmod +x *.elf, then run this script.
set -u
cd "$(dirname "$0")" || exit 10
getprop ro.product.model >device_model.txt 2>/dev/null || true
getprop ro.build.version.sdk >android_api.txt 2>/dev/null || true
getenforce >selinux_mode.txt 2>/dev/null || true
: >results.txt
failures=0
chmod 755 'empty.elf' || exit 11
./'empty.elf' <'empty.stdin' >'empty.got' 2>'empty.stderr'
status=$?
if [ "$status" -eq 0 ] && cmp -s 'empty.got' 'empty.expected'; then
 echo 'PASS empty status='$status >>results.txt
else
 echo 'FAIL empty status='$status >>results.txt
 failures=$((failures+1))
fi
chmod 755 'single-byte.elf' || exit 11
./'single-byte.elf' <'single-byte.stdin' >'single-byte.got' 2>'single-byte.stderr'
status=$?
if [ "$status" -eq 0 ] && cmp -s 'single-byte.got' 'single-byte.expected'; then
 echo 'PASS single-byte status='$status >>results.txt
else
 echo 'FAIL single-byte status='$status >>results.txt
 failures=$((failures+1))
fi
chmod 755 'transfer-loop.elf' || exit 11
./'transfer-loop.elf' <'transfer-loop.stdin' >'transfer-loop.got' 2>'transfer-loop.stderr'
status=$?
if [ "$status" -eq 0 ] && cmp -s 'transfer-loop.got' 'transfer-loop.expected'; then
 echo 'PASS transfer-loop status='$status >>results.txt
else
 echo 'FAIL transfer-loop status='$status >>results.txt
 failures=$((failures+1))
fi
chmod 755 'nested-transfer.elf' || exit 11
./'nested-transfer.elf' <'nested-transfer.stdin' >'nested-transfer.got' 2>'nested-transfer.stderr'
status=$?
if [ "$status" -eq 0 ] && cmp -s 'nested-transfer.got' 'nested-transfer.expected'; then
 echo 'PASS nested-transfer status='$status >>results.txt
else
 echo 'FAIL nested-transfer status='$status >>results.txt
 failures=$((failures+1))
fi
chmod 755 'nul-ff-io.elf' || exit 11
./'nul-ff-io.elf' <'nul-ff-io.stdin' >'nul-ff-io.got' 2>'nul-ff-io.stderr'
status=$?
if [ "$status" -eq 0 ] && cmp -s 'nul-ff-io.got' 'nul-ff-io.expected'; then
 echo 'PASS nul-ff-io status='$status >>results.txt
else
 echo 'FAIL nul-ff-io status='$status >>results.txt
 failures=$((failures+1))
fi
chmod 755 'eof-zero.elf' || exit 11
./'eof-zero.elf' <'eof-zero.stdin' >'eof-zero.got' 2>'eof-zero.stderr'
status=$?
if [ "$status" -eq 0 ] && cmp -s 'eof-zero.got' 'eof-zero.expected'; then
 echo 'PASS eof-zero status='$status >>results.txt
else
 echo 'FAIL eof-zero status='$status >>results.txt
 failures=$((failures+1))
fi
chmod 755 'pointer-underflow.elf' || exit 11
./'pointer-underflow.elf' <'pointer-underflow.stdin' >'pointer-underflow.got' 2>'pointer-underflow.stderr'
status=$?
if [ "$status" -eq 2 ] && cmp -s 'pointer-underflow.got' 'pointer-underflow.expected'; then
 echo 'PASS pointer-underflow status='$status >>results.txt
else
 echo 'FAIL pointer-underflow status='$status >>results.txt
 failures=$((failures+1))
fi
chmod 755 'deep-300.elf' || exit 11
./'deep-300.elf' <'deep-300.stdin' >'deep-300.got' 2>'deep-300.stderr'
status=$?
if [ "$status" -eq 0 ] && cmp -s 'deep-300.got' 'deep-300.expected'; then
 echo 'PASS deep-300 status='$status >>results.txt
else
 echo 'FAIL deep-300 status='$status >>results.txt
 failures=$((failures+1))
fi
chmod 755 'over-old-limit.elf' || exit 11
./'over-old-limit.elf' <'over-old-limit.stdin' >'over-old-limit.got' 2>'over-old-limit.stderr'
status=$?
if [ "$status" -eq 0 ] && cmp -s 'over-old-limit.got' 'over-old-limit.expected'; then
 echo 'PASS over-old-limit status='$status >>results.txt
else
 echo 'FAIL over-old-limit status='$status >>results.txt
 failures=$((failures+1))
fi
cat results.txt
[ "$failures" -eq 0 ]
