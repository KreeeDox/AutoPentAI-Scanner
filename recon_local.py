# LAB-ONLY: DO NOT RUN AGAINST EXTERNAL TARGETS (V-FINAL with Nikto - Final Syntax Fix)
import nmap, sys, json, subprocess, os
NIKTO_OUTPUT_FILE = 'data/nikto_results.json'

def run_nikto(target_ip):
    print(f"--- Starting Nikto scan on http://{target_ip} ---")
    process = None 
    try:
        command = ['nikto', '-h', f'http://{target_ip}', '-Format', 'json', '-o', NIKTO_OUTPUT_FILE, '-Tuning', '4']
        print(f"CONFIRM: Running command: {' '.join(command)}")
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate(timeout=300) 
        if process.returncode != 0:
            if "Connection refused" in stderr: print("Nikto connection refused."); return False
            elif "0 host(s) tested" in stderr: print("Nikto reported 0 hosts tested.")
            else: print(f"Nikto scan may have failed with error code {process.returncode}:\n{stderr}")
            if not os.path.exists(NIKTO_OUTPUT_FILE): return False 
        print(f"--- Nikto scan process finished. ---")
        # Check if file exists AND has significant content
        if os.path.exists(NIKTO_OUTPUT_FILE) and os.path.getsize(NIKTO_OUTPUT_FILE) > 5: 
            return True
        else:
            # --- CORRECTED BLOCK ---
            print("Nikto output file is empty or minimal, considering scan failed.") 
            if os.path.exists(NIKTO_OUTPUT_FILE): 
                os.remove(NIKTO_OUTPUT_FILE) # Clean up empty file
            return False
            # --- END CORRECTED BLOCK ---
    except subprocess.TimeoutExpired: 
        print("ERROR: Nikto scan timed out.") 
        if process: 
            process.kill()
        return False
    except FileNotFoundError: print("ERROR: 'nikto' command not found."); return False
    except Exception as e: print(f"An unexpected error occurred during Nikto scan: {e}"); return False

def scan_local(target):
    if not (target in ['127.0.0.1', 'localhost'] or target.startswith('192.168.56.')): print(f"Error: Target '{target}' is not allowed."); return None, False
    print(f"Starting safe Nmap scan on {target}..."); nm = nmap.PortScanner()
    ports_to_scan = '21,22,23,80,139,445,443,2121,3306,5432'; nmap_scan_data = None; nikto_ran_successfully = False
    try:
        print(f"CONFIRM: Running 'nmap -sV -p {ports_to_scan} {target}'"); nmap_scan_data = nm.scan(target, ports_to_scan, arguments='-sV')
        if nmap_scan_data is None or not nmap_scan_data.get('scan'): raise nmap.PortScannerError("Nmap scan returned no results.")
        with open('data/scan_results.json', 'w') as f: json.dump(nmap_scan_data, f, indent=2); print(f"Nmap scan complete.")
        web_port_open = False
        if target in nmap_scan_data.get('scan', {}):
            tcp_ports = nmap_scan_data['scan'][target].get('tcp', {}); web_port_open = (80 in tcp_ports and tcp_ports[80]['state'] == 'open') or (443 in tcp_ports and tcp_ports[443]['state'] == 'open')
        else: print(f"Warning: Target {target} not found in Nmap scan results.")
        if os.path.exists(NIKTO_OUTPUT_FILE): os.remove(NIKTO_OUTPUT_FILE)
        if web_port_open: nikto_ran_successfully = run_nikto(target)
        else: print("No open web ports found. Skipping Nikto scan."); nikto_ran_successfully = False
    except nmap.PortScannerError as nmap_err: print(f"Nmap scan failed: {nmap_err}"); return None, False
    except Exception as e: print(f"An error occurred during Nmap scan/Nikto check: {e}"); return None, False
    nikto_ran_successfully = os.path.exists(NIKTO_OUTPUT_FILE) and os.path.getsize(NIKTO_OUTPUT_FILE) > 5
    return nmap_scan_data, nikto_ran_successfully
