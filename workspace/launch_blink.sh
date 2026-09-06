#!/bin/bash
cd /home/kmpooja
nohup bash /home/kmpooja/blink_eval_pretrained.sh > /home/kmpooja/blink_nohup.log 2>&1 &
echo "BLINK PID=$!"
sleep 2
tail -5 /home/kmpooja/blink_nohup.log 2>/dev/null
ps aux | grep blink_eval | grep -v grep
