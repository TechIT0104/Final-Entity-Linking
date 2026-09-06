#!/usr/bin/env python3
"""
TR2016 Benchmark Executor - Handles SSH authentication with paramiko
"""

import paramiko
import sys
import time
from io import StringIO

def execute_tr2016_benchmark(host, username, password, server_name, languages):
    """Execute TR2016 evaluation on remote server"""
    
    print(f"\n{'='*70}")
    print(f"Connecting to {server_name} ({host})...")
    print(f"Languages: {languages}")
    print(f"{'='*70}\n")
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # Connect
        print(f"[*] Authenticating as {username}...")
        client.connect(host, username=username, password=password, timeout=30)
        print(f"[✓] Connected successfully!\n")
        
        # Build the evaluation command
        work_dir = "/DATA/kmpooja/mrefined_option1" if host == "172.20.70.80" else "/home/kmpooja/mrefined_170"
        
        cmd = f"""
cd {work_dir}
source venv/bin/activate
export PYTHONUNBUFFERED=1
export CUDA_VISIBLE_DEVICES=0

echo "========================================" 
echo "TR2016 Evaluation on {server_name}"
echo "Start time: $(date)"
echo "========================================"

python3 -u ReFinED/src/refined/evaluation/multilingual_e2e_evaluation_tr2016.py \\
  --lang_title2wikidata "assets/data_combine_11_languages_wikidata_all_eng_label_desc/additional_data" \\
  --mention2wikidata "assets/data_combine_11_languages_wikidata_all_eng_label_desc/additional_data" \\
  --model "assets/finetune_models/mReFinED_Recall_9343" \\
  --data "assets/data_combine_11_languages_wikidata_all_eng_label_desc" \\
  --datasets_root "assets/tr2016"

echo ""
echo "========================================"
echo "Evaluation completed at: $(date)"
echo "========================================"
"""
        
        print(f"[*] Executing TR2016 evaluation...\n")
        print("="*70)
        
        stdin, stdout, stderr = client.exec_command(cmd, get_pty=False)
        
        # Stream output in real-time
        for line in stdout:
            print(line.rstrip())
            sys.stdout.flush()
        
        # Check for errors
        stderr_output = stderr.read().decode('utf-8')
        if stderr_output:
            print("\n[STDERR]")
            print(stderr_output)
        
        exit_code = stdout.channel.recv_exit_status()
        
        print("="*70)
        print(f"\n[✓] Evaluation completed with exit code: {exit_code}\n")
        
        return exit_code == 0
        
    except paramiko.AuthenticationException:
        print(f"[✗] Authentication failed for {username}@{host}")
        return False
    except paramiko.SSHException as e:
        print(f"[✗] SSH error: {e}")
        return False
    except Exception as e:
        print(f"[✗] Error: {e}")
        return False
    finally:
        client.close()

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 tr2016_executor_paramiko.py <password>")
        sys.exit(1)
    
    password = sys.argv[1]
    
    servers = [
        {
            'host': '172.20.70.80',
            'server_name': 'Server 80 (German + Spanish)',
            'languages': 'de, es'
        },
        {
            'host': '172.20.70.170',
            'server_name': 'Server 170 (French + Italian)',
            'languages': 'fr, it'
        }
    ]
    
    print("\n" + "="*70)
    print("TR2016 BENCHMARK EXECUTOR")
    print("mReFinED Multilingual Entity Linking - Paper Reproduction")
    print("="*70)
    
    results = {}
    start_time = time.time()
    
    for server in servers:
        result = execute_tr2016_benchmark(
            host=server['host'],
            username='kmpooja',
            password=password,
            server_name=server['server_name'],
            languages=server['languages']
        )
        results[server['server_name']] = result
        
        # Wait between servers
        print("\n[*] Waiting 30 seconds before next server...")
        time.sleep(30)
    
    elapsed = (time.time() - start_time) / 60
    
    print("\n" + "="*70)
    print("EXECUTION SUMMARY")
    print("="*70)
    for server_name, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{server_name:50} {status}")
    
    print(f"\nTotal elapsed time: {elapsed:.1f} minutes")
    print("="*70 + "\n")
    
    # Check if all succeeded
    all_success = all(results.values())
    return 0 if all_success else 1

if __name__ == '__main__':
    sys.exit(main())
