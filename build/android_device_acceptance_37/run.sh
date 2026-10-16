#!/system/bin/sh
set -u
cd "$(dirname "$0")" || exit 90
mkdir -p results || exit 91
chmod 700 ./empty.elf
./empty.elf < ./empty.stdin > ./results/empty.stdout 2> ./results/empty.stderr
printf "%s\n" "$?" > ./results/empty.exitcode
chmod 700 ./binary_echo.elf
./binary_echo.elf < ./binary_echo.stdin > ./results/binary_echo.stdout 2> ./results/binary_echo.stderr
printf "%s\n" "$?" > ./results/binary_echo.exitcode
chmod 700 ./eof_zero.elf
./eof_zero.elf < ./eof_zero.stdin > ./results/eof_zero.stdout 2> ./results/eof_zero.stderr
printf "%s\n" "$?" > ./results/eof_zero.exitcode
chmod 700 ./nested_loops.elf
./nested_loops.elf < ./nested_loops.stdin > ./results/nested_loops.stdout 2> ./results/nested_loops.stderr
printf "%s\n" "$?" > ./results/nested_loops.exitcode
chmod 700 ./page_331.elf
./page_331.elf < ./page_331.stdin > ./results/page_331.stdout 2> ./results/page_331.stderr
printf "%s\n" "$?" > ./results/page_331.exitcode
chmod 700 ./page_672.elf
./page_672.elf < ./page_672.stdin > ./results/page_672.stdout 2> ./results/page_672.stderr
printf "%s\n" "$?" > ./results/page_672.exitcode
chmod 700 ./page_1013.elf
./page_1013.elf < ./page_1013.stdin > ./results/page_1013.stdout 2> ./results/page_1013.stderr
printf "%s\n" "$?" > ./results/page_1013.exitcode
chmod 700 ./page_1355.elf
./page_1355.elf < ./page_1355.stdin > ./results/page_1355.stdout 2> ./results/page_1355.stderr
printf "%s\n" "$?" > ./results/page_1355.exitcode
chmod 700 ./page_1696.elf
./page_1696.elf < ./page_1696.stdin > ./results/page_1696.stdout 2> ./results/page_1696.stderr
printf "%s\n" "$?" > ./results/page_1696.exitcode
chmod 700 ./loop_2000.elf
./loop_2000.elf < ./loop_2000.stdin > ./results/loop_2000.stdout 2> ./results/loop_2000.stderr
printf "%s\n" "$?" > ./results/loop_2000.exitcode
chmod 700 ./max_nesting.elf
./max_nesting.elf < ./max_nesting.stdin > ./results/max_nesting.stdout 2> ./results/max_nesting.stderr
printf "%s\n" "$?" > ./results/max_nesting.exitcode
chmod 700 ./left_trap.elf
./left_trap.elf < ./left_trap.stdin > ./results/left_trap.stdout 2> ./results/left_trap.stderr
printf "%s\n" "$?" > ./results/left_trap.exitcode
chmod 700 ./right_trap.elf
./right_trap.elf < ./right_trap.stdin > ./results/right_trap.stdout 2> ./results/right_trap.stderr
printf "%s\n" "$?" > ./results/right_trap.exitcode
printf "TESTS_FINISHED\n"
