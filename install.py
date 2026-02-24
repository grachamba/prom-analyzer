import subprocess
import yaml

print("\n=== Prom Rightsizer installer ===\n")

prom = input("Prometheus URL: ").strip()
days = input("Days to analyze (default 14): ").strip()

if not days:
    days = "7"

config = {
    "prometheus_url": prom,
    "days": int(days)
}

with open("config.yaml","w") as f:
    yaml.dump(config,f)

print("\nCreating virtualenv...")
subprocess.run(["python3","-m","venv","venv"])

pip = "./venv/bin/pip"
python = "./venv/bin/python"

print("Installing dependencies...")
subprocess.run([pip,"install","-r","requirements.txt"])

print("\nRunning analysis...")
subprocess.run([python,"analyzer.py"])

print("\nStarting web UI...")
print("\nOpen browser: http://localhost:8000\n")

subprocess.Popen(["./venv/bin/uvicorn","web:app","--host","0.0.0.0","--port","8000"])

input("Press ENTER to exit installer")
