set -e
printf "c_direct_echo "; taskset -c 8 /data/local/tmp/bfc_followup_20261013/sample 173 /data/local/tmp/bfc_followup_20261013/c_direct_echo
printf "c_freestanding_o3 "; taskset -c 8 /data/local/tmp/bfc_followup_20261013/sample 173 /data/local/tmp/bfc_followup_20261013/c_freestanding_o3
printf "c_static "; taskset -c 8 /data/local/tmp/bfc_followup_20261013/sample 173 /data/local/tmp/bfc_followup_20261013/c_static
printf "java_art_interpreted "; taskset -c 8 /data/local/tmp/bfc_followup_20261013/sample 173 dalvikvm -Xint -cp /data/local/tmp/bfc_followup_20261013/classes.dex AndroidTransfer
printf "c_freestanding_oz "; taskset -c 8 /data/local/tmp/bfc_followup_20261013/sample 173 /data/local/tmp/bfc_followup_20261013/c_freestanding_oz
printf "brainfuck "; taskset -c 8 /data/local/tmp/bfc_followup_20261013/sample 173 /data/local/tmp/bfc_followup_20261013/brainfuck
printf "rust_std "; taskset -c 8 /data/local/tmp/bfc_followup_20261013/sample 173 /data/local/tmp/bfc_followup_20261013/rust_std
printf "java_art_jit_enabled "; taskset -c 8 /data/local/tmp/bfc_followup_20261013/sample 173 dalvikvm -Xusejit:true -cp /data/local/tmp/bfc_followup_20261013/classes.dex AndroidTransfer
printf "c_dynamic "; taskset -c 8 /data/local/tmp/bfc_followup_20261013/sample 173 /data/local/tmp/bfc_followup_20261013/c_dynamic
printf "rust_direct_echo "; taskset -c 8 /data/local/tmp/bfc_followup_20261013/sample 173 /data/local/tmp/bfc_followup_20261013/rust_direct_echo
