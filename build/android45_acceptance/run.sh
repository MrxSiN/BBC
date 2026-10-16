#!/system/bin/sh
set -u
cd "$(dirname "$0")" || exit 90
mkdir -p results || exit 91
chmod 700 ./page_2378.elf
./page_2378.elf < ./page_2378.stdin > ./results/page_2378.stdout 2> ./results/page_2378.stderr
printf "%s\n" "$?" > ./results/page_2378.exitcode
chmod 700 ./page_2379.elf
./page_2379.elf < ./page_2379.stdin > ./results/page_2379.stdout 2> ./results/page_2379.stderr
printf "%s\n" "$?" > ./results/page_2379.exitcode
chmod 700 ./nested_2400.elf
./nested_2400.elf < ./nested_2400.stdin > ./results/nested_2400.stdout 2> ./results/nested_2400.stderr
printf "%s\n" "$?" > ./results/nested_2400.exitcode
chmod 700 ./loop_2719.elf
./loop_2719.elf < ./loop_2719.stdin > ./results/loop_2719.stdout 2> ./results/loop_2719.stderr
printf "%s\n" "$?" > ./results/loop_2719.exitcode
chmod 700 ./binary_2719.elf
./binary_2719.elf < ./binary_2719.stdin > ./results/binary_2719.stdout 2> ./results/binary_2719.stderr
printf "%s\n" "$?" > ./results/binary_2719.exitcode
chmod 700 ./eof_2719.elf
./eof_2719.elf < ./eof_2719.stdin > ./results/eof_2719.stdout 2> ./results/eof_2719.stderr
printf "%s\n" "$?" > ./results/eof_2719.exitcode
chmod 700 ./trap_2719.elf
./trap_2719.elf < ./trap_2719.stdin > ./results/trap_2719.stdout 2> ./results/trap_2719.stderr
printf "%s\n" "$?" > ./results/trap_2719.exitcode
printf "TESTS_FINISHED\n"
