#!/bin/bash
# Fix the Python script to handle errors better
WORKDIR_VAR="\$WORKDIR"
sed -i "/python3 - <<PY | tee \"\$WORKDIR\/01_prom_gate.txt\"/,/^PY$/c\
python3 - <<PY | tee \"\$WORKDIR/01_prom_gate.txt\"\
import json\
import sys\
def ok(p):\
    try:\
        with open(p, \"r\") as f:\
            content = f.read().strip()\
            if not content:\
                return False\
            d = json.loads(content)\
            return len(d.get(\"data\", {}).get(\"result\", [])) > 0\
    except:\
        return False\
files = [\"01_q_cpu.json\", \"01_q_mem.json\", \"01_q_disk.json\", \"01_q_net.json\"]\
oks = sum(ok(\"$WORKDIR_VAR/\" + f) for f in files)\
print(\"prom_queries_ok\", oks, \"/4\")\
PY" exec_prompt_07.sh
