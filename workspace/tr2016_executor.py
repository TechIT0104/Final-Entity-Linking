#!/usr/bin/env python3
"""
TR2016 Benchmark Executor
Executes mReFinED TR2016 evaluation on remote servers with password authentication
"""

import subprocess
import sys
import time
import threading
from pathlib import Path

class TR2016Executor:
    def __init__(self, password: str):
        self.password = password
        self.servers = [
            {
                'host': '172.20.70.80',
                'user': 'kmpooja',
                'languages': 'DE + ES',
                'timeout': 7200  # 2 hours
            },
            {
                'host': '172.20.70.170',
                'user': 'kmpooja',
                'languages': 'FR + IT',
                'timeout': 7200  # 2 hours
            }
        ]
        self.results = {}
    
    def execute_server(self, server_config):
        """Execute evaluation on a single server"""
        host = server_config['host']
        user = server_config['user']
        languages = server_config['languages']
        timeout = server_config['timeout']
        
        print(f"\n{'='*70}")
        print(f"🚀 Starting TR2016 on {host} ({languages})")
        print(f"{'='*70}")
        
        # Build SSH command
        ssh_cmd = [
            'ssh',
            '-o', 'StrictHostKeyChecking=no',
            '-o', 'ConnectTimeout=10',
            f'{user}@{host}',
            'cd /DATA/kmpooja/mrefined_option1 && bash remote_cmd_tr2016_server80.sh' if host == '172.20.70.80' else 'cd /home/kmpooja/mrefined_170 && bash remote_cmd_tr2016_server170.sh'
        ]
        
        try:
            # Use Popen to capture output in real-time
            process = subprocess.Popen(
                ssh_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            # Send password when prompted
            stdout, _ = process.communicate(input=f"{self.password}\n", timeout=timeout)
            
            # Print live output
            print(stdout)
            
            if process.returncode == 0:
                print(f"✅ {host} ({languages}) completed successfully!")
                self.results[host] = 'SUCCESS'
            else:
                print(f"⚠️  {host} exited with code {process.returncode}")
                self.results[host] = f'FAILED (code {process.returncode})'
                
        except subprocess.TimeoutExpired:
            print(f"❌ {host} timed out after {timeout} seconds")
            process.kill()
            self.results[host] = 'TIMEOUT'
        except Exception as e:
            print(f"❌ Error on {host}: {str(e)}")
            self.results[host] = f'ERROR: {str(e)}'
    
    def run_parallel(self):
        """Execute both servers in parallel"""
        threads = []
        
        print("\n" + "="*70)
        print("🚀 TR2016 BENCHMARK EXECUTOR")
        print("="*70)
        print(f"Starting {len(self.servers)} servers in parallel...")
        print(f"Estimated runtime: 2 hours")
        print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        # Start each server in a separate thread
        for server in self.servers:
            thread = threading.Thread(target=self.execute_server, args=(server,))
            thread.start()
            threads.append(thread)
            time.sleep(1)  # Stagger the starts by 1 second
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Print summary
        self._print_summary()
    
    def _print_summary(self):
        """Print execution summary"""
        print("\n" + "="*70)
        print("📊 EXECUTION SUMMARY")
        print("="*70)
        
        for server in self.servers:
            host = server['host']
            languages = server['languages']
            status = self.results.get(host, 'NOT STARTED')
            
            status_icon = "✅" if status == "SUCCESS" else "❌" if "ERROR" in status or "FAILED" in status else "⚠️"
            print(f"{status_icon} {host} ({languages:8}): {status}")
        
        print("="*70)
        print("Expected Results (if successful):")
        print("  German (de):     28.2% recall")
        print("  Spanish (es):    34.4% recall")
        print("  French (fr):     25.3% recall")
        print("  Italian (it):    25.8% recall")
        print("  Macro-avg:       28.4% recall")
        print("="*70)
        
        all_success = all(status == "SUCCESS" for status in self.results.values())
        if all_success:
            print("\n🎉 ALL SERVERS COMPLETED SUCCESSFULLY! 🎉")
            print("Check logs for detailed metrics:")
            print("  /DATA/kmpooja/mrefined_option1/logs/tr2016_server80_*.log")
            print("  /DATA/kmpooja/mrefined_option1/logs/tr2016_server170_*.log")
        else:
            print("\n⚠️  Some servers did not complete successfully. Check output above.")
        
        print("="*70 + "\n")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 tr2016_executor.py <password>")
        print("\nExample:")
        print('  python3 tr2016_executor.py "kmpooja123"')
        sys.exit(1)
    
    password = sys.argv[1]
    
    executor = TR2016Executor(password)
    executor.run_parallel()

if __name__ == '__main__':
    main()
