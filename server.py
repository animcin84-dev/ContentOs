import asyncio
import json
import urllib.request
import urllib.error
import threading
import subprocess
import sys
import os
import time
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def run_holehe(email, results):
    """Use holehe via subprocess with CSV output for better parsing"""
    try:
        # Get the venv bin directory
        venv_bin = os.path.dirname(sys.executable)
        holehe_path = os.path.join(venv_bin, 'holehe')
        
        print(f"Running holehe for {email}")
        
        # Run holehe with CSV output
        cmd = [holehe_path, email, '--only-used', '--csv']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        print(f"Holehe exit code: {result.returncode}")
        
        # Try parsing stdout as fallback first
        output = result.stdout + result.stderr
        for line in output.split("\n"):
            line = line.strip()
            if line.startswith("[+]") and not line.startswith("[+] Email used"):
                site = line.replace("[+]", "").strip()
                if site:
                    print(f"Found via stdout: {site}")
                    results.append({
                        'name': site,
                        'domain': site,
                        'method': 'register/login check',
                        'source': 'holehe',
                        'verified': True
                    })
        
        # Try to read the CSV file that holehe generates
        import csv
        import glob
        
        # Wait a moment for CSV to be written
        time.sleep(1)
        
        # Find the most recent CSV file
        csv_files = glob.glob(f"holehe_*_{email.replace('@', '_')}_results.csv")
        print(f"Found CSV files: {csv_files}")
        
        if csv_files:
            latest_csv = max(csv_files, key=os.path.getctime)
            print(f"Reading CSV: {latest_csv}")
            try:
                with open(latest_csv, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row.get('exists') == 'True':
                            domain = row.get('domain', '')
                            name = row.get('name', domain)
                            if domain:
                                print(f"Found via CSV: {name} ({domain})")
                                results.append({
                                    'name': name,
                                    'domain': domain,
                                    'method': row.get('method', 'unknown'),
                                    'source': 'holehe',
                                    'verified': True
                                })
            except Exception as csv_error:
                print(f"CSV parsing error: {csv_error}")
    except Exception as e:
        print(f"Holehe error: {e}")

def run_xposed(email, results):
    """Check XposedOrNot breach database"""
    try:
        req = urllib.request.Request(f"https://api.xposedornot.com/v1/check-email/{email}", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read())
            if "breaches" in data and data["breaches"]:
                for breach in data["breaches"]:
                    results.append({
                        'name': breach.get('breachName', 'Unknown'),
                        'domain': breach.get('domain', breach.get('breachName', '')),
                        'method': 'breach',
                        'source': 'xposedornot',
                        'breachData': breach
                    })
    except Exception as e:
        print(f"XposedOrNot error: {e}")

def run_hibp(email, results):
    """Check Have I Been Pwned breach database"""
    try:
        req = urllib.request.Request(f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}?truncateResponse=false", headers={'User-Agent': 'Mozilla/5.0', 'hibp-api-key': ''})
        with urllib.request.urlopen(req, timeout=10) as response:
            breaches = json.loads(response.read())
            for breach in breaches:
                results.append({
                    'name': breach.get('Name', 'Unknown'),
                    'domain': breach.get('Domain', ''),
                    'method': 'breach',
                    'source': 'hibp',
                    'breachData': breach
                })
    except urllib.error.HTTPError as e:
        if e.code == 404:
            pass  # No breaches found
        else:
            print(f"HIBP HTTP error: {e}")
    except Exception as e:
        print(f"HIBP error: {e}")

def run_breachdirectory(email, results):
    """Check BreachDirectory for breached accounts"""
    try:
        req = urllib.request.Request(f"https://breachdirectory.com/api/v1/breaches?email={email}", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read())
            if data and isinstance(data, list):
                for breach in data:
                    results.append({
                        'name': breach.get('name', 'Unknown'),
                        'domain': breach.get('domain', ''),
                        'method': 'breach',
                        'source': 'breachdirectory',
                        'breachData': breach
                    })
    except Exception as e:
        print(f"BreachDirectory error: {e}")

def run_leaklookup(email, results):
    """Check LeakLookup for email leaks"""
    try:
        req = urllib.request.Request(f"https://leak-lookup.com/api/search", 
                                    data=json.dumps({'email': email}).encode(),
                                    headers={'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/json'},
                                    method='POST')
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read())
            if data.get('success'):
                for leak in data.get('results', []):
                    results.append({
                        'name': leak.get('service', 'Unknown'),
                        'domain': leak.get('domain', ''),
                        'method': 'leak',
                        'source': 'leaklookup',
                        'leakData': leak
                    })
    except Exception as e:
        print(f"LeakLookup error: {e}")

def run_sherlock(email, results):
    """Check Sherlock social media detection"""
    try:
        # Get the venv bin directory
        venv_bin = os.path.dirname(sys.executable)
        sherlock_path = os.path.join(venv_bin, 'sherlock')
        
        print(f"Running sherlock for {email}")
        
        # Run sherlock with simple output (note: sherlock takes username, not email)
        username = email.split('@')[0]
        cmd = [sherlock_path, '--no-color', '--print-found', '--timeout', '10', username]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        print(f"Sherlock exit code: {result.returncode}")
        
        # Parse stdout line by line
        output = result.stdout + result.stderr
        for line in output.split('\n'):
            if '[+]' in line and ':' in line:
                # Parse line like "[+] Instagram: https://www.instagram.com/username"
                parts = line.split(':', 1)
                if len(parts) == 2:
                    site_name = parts[0].replace('[+]', '').strip()
                    url = parts[1].strip()
                    domain = url.replace('https://', '').replace('http://', '').split('/')[0]
                    results.append({
                        'name': site_name,
                        'domain': domain,
                        'method': 'social media detection',
                        'source': 'sherlock',
                        'verified': True
                    })
    except Exception as e:
        print(f"Sherlock error: {e}")

def run_theharvester(email, results):
    """Check theHarvester for email-related accounts"""
    try:
        domain = email.split('@')[1]
        # Run theHarvester with specific sources to avoid timeout
        cmd = ['theHarvester', '-d', domain, '-b', 'bing,google,linkedin', '-l', '20', '-f', 'json']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        # Parse JSON output
        try:
            data = json.loads(result.stdout)
            if 'emails' in data:
                for found_email in data['emails']:
                    if found_email.lower() == email.lower():
                        # Email found, add the domain as a service
                        results.append({
                            'name': domain,
                            'domain': domain,
                            'method': 'email harvesting',
                            'source': 'theharvester',
                            'verified': True
                        })
        except json.JSONDecodeError:
            pass
    except FileNotFoundError:
        print("theHarvester not installed, skipping")
    except Exception as e:
        print(f"theHarvester error: {e}")

@app.route('/scan', methods=['GET'])
def scan():
    email = request.args.get('email')
    if not email:
        return jsonify({"error": "No email provided"}), 400

    print(f"Starting scan for {email}")
    found_sites = []
    
    # Run all OSINT sources in parallel
    t1 = threading.Thread(target=run_holehe, args=(email, found_sites))
    t2 = threading.Thread(target=run_xposed, args=(email, found_sites))
    t3 = threading.Thread(target=run_hibp, args=(email, found_sites))
    t4 = threading.Thread(target=run_sherlock, args=(email, found_sites))
    t5 = threading.Thread(target=run_theharvester, args=(email, found_sites))
    t6 = threading.Thread(target=run_breachdirectory, args=(email, found_sites))
    t7 = threading.Thread(target=run_leaklookup, args=(email, found_sites))
    
    print("Starting threads...")
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t5.start()
    t6.start()
    t7.start()
    
    print("Waiting for threads to complete...")
    t1.join()
    t2.join()
    t3.join()
    t4.join()
    t5.join()
    t6.join()
    t7.join()

    print(f"All threads completed. Total results: {len(found_sites)}")

    # Deduplicate by domain
    seen_domains = set()
    unique_sites = []
    for site in found_sites:
        domain = site.get('domain', '')
        if domain and domain not in seen_domains:
            seen_domains.add(domain)
            unique_sites.append(site)
    
    print(f"Found {len(unique_sites)} REAL sites for {email}")
    for site in unique_sites:
        print(f"  - {site['name']} ({site['domain']}) from {site['source']}")
    
    return jsonify({"email": email, "found": unique_sites})

if __name__ == '__main__':
    print("Starting REAL OSINT Backend via Leak Databases + Holehe on Port 5000")
    app.run(host='127.0.0.1', port=5000, debug=False)
