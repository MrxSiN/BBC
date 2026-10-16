#!/system/bin/sh
# Android ARM64 device acceptance runner for experimental freestanding PIE.
# Use after copying this directory into /data/local/tmp; nothing is asserted
# about Android loader support until this script actually runs on a device.
cd "$(dirname "$0")" || exit 98
failed=0
chmod 700 empty.elf
./empty.elf < empty.stdin > empty.got 2> empty.stderr
code=$?
got=$(sha256sum empty.got | cut -d ' ' -f1)
if [ "$code" -ne 0 ] || [ "$got" != "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" ]; then
  echo "FAIL empty status=$code stdout_sha=$got"; failed=$((failed+1))
else
  echo "PASS empty"
fi
chmod 700 ascii_A.elf
./ascii_A.elf < ascii_A.stdin > ascii_A.got 2> ascii_A.stderr
code=$?
got=$(sha256sum ascii_A.got | cut -d ' ' -f1)
if [ "$code" -ne 0 ] || [ "$got" != "559aead08264d5795d3909718cdd05abd49572e84fe55590eef31a88a08fdffd" ]; then
  echo "FAIL ascii_A status=$code stdout_sha=$got"; failed=$((failed+1))
else
  echo "PASS ascii_A"
fi
chmod 700 simple_loop.elf
./simple_loop.elf < simple_loop.stdin > simple_loop.got 2> simple_loop.stderr
code=$?
got=$(sha256sum simple_loop.got | cut -d ' ' -f1)
if [ "$code" -ne 0 ] || [ "$got" != "559aead08264d5795d3909718cdd05abd49572e84fe55590eef31a88a08fdffd" ]; then
  echo "FAIL simple_loop status=$code stdout_sha=$got"; failed=$((failed+1))
else
  echo "PASS simple_loop"
fi
chmod 700 nested_loop.elf
./nested_loop.elf < nested_loop.stdin > nested_loop.got 2> nested_loop.stderr
code=$?
got=$(sha256sum nested_loop.got | cut -d ' ' -f1)
if [ "$code" -ne 0 ] || [ "$got" != "67586e98fad27da0b9968bc039a1ef34c939b9b8e523a8bef89d478608c5ecf6" ]; then
  echo "FAIL nested_loop status=$code stdout_sha=$got"; failed=$((failed+1))
else
  echo "PASS nested_loop"
fi
chmod 700 binary_io.elf
./binary_io.elf < binary_io.stdin > binary_io.got 2> binary_io.stderr
code=$?
got=$(sha256sum binary_io.got | cut -d ' ' -f1)
if [ "$code" -ne 0 ] || [ "$got" != "06eb7d6a69ee19e5fbdf749018d3d2abfa04bcbd1365db312eb86dc7169389b8" ]; then
  echo "FAIL binary_io status=$code stdout_sha=$got"; failed=$((failed+1))
else
  echo "PASS binary_io"
fi
chmod 700 eof_zero.elf
./eof_zero.elf < eof_zero.stdin > eof_zero.got 2> eof_zero.stderr
code=$?
got=$(sha256sum eof_zero.got | cut -d ' ' -f1)
if [ "$code" -ne 0 ] || [ "$got" != "6e340b9cffb37a989ca544e6bb780a2c78901d3fb33738768511a30617afa01d" ]; then
  echo "FAIL eof_zero status=$code stdout_sha=$got"; failed=$((failed+1))
else
  echo "PASS eof_zero"
fi
chmod 700 pointer_underflow.elf
./pointer_underflow.elf < pointer_underflow.stdin > pointer_underflow.got 2> pointer_underflow.stderr
code=$?
got=$(sha256sum pointer_underflow.got | cut -d ' ' -f1)
if [ "$code" -ne 2 ] || [ "$got" != "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" ]; then
  echo "FAIL pointer_underflow status=$code stdout_sha=$got"; failed=$((failed+1))
else
  echo "PASS pointer_underflow"
fi
chmod 700 large_transfer.elf
./large_transfer.elf < large_transfer.stdin > large_transfer.got 2> large_transfer.stderr
code=$?
got=$(sha256sum large_transfer.got | cut -d ' ' -f1)
if [ "$code" -ne 0 ] || [ "$got" != "1dd8312636f6a0bf3d21fa2855e63072507453e93a5ced4301b364e91c9d87d6" ]; then
  echo "FAIL large_transfer status=$code stdout_sha=$got"; failed=$((failed+1))
else
  echo "PASS large_transfer"
fi
chmod 700 deep_nesting.elf
./deep_nesting.elf < deep_nesting.stdin > deep_nesting.got 2> deep_nesting.stderr
code=$?
got=$(sha256sum deep_nesting.got | cut -d ' ' -f1)
if [ "$code" -ne 0 ] || [ "$got" != "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" ]; then
  echo "FAIL deep_nesting status=$code stdout_sha=$got"; failed=$((failed+1))
else
  echo "PASS deep_nesting"
fi
echo "Failures: $failed"
[ "$failed" -eq 0 ]
