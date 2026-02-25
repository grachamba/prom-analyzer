# Prom Rightsizer

Lightweight infrastructure rightsizing tool for Prometheus.

Calculates CPU and RAM p95 usage using PromQL, applies safety margin, and shows
how many resources can be reclaimed or need to be added — with simple Web UI.

Supports Linux and Windows exporters.

---

## Features

- CPU & RAM p95 rightsizing
- Safety margin (20%)
- Reclaim / Grow recommendations
- Linux + Windows support
- PromQL compatible backends (Prometheus)
- Web UI
- Lightweight queries (quantile_over_time)

---

## Architecture

Prometheus → Analyzer → JSON → FastAPI → HTML

---

## Quick start

```bash
git clone https://github.com/grachamba/prom-analyzer
cd prom-analyzer
python3 install.py
```

Follow installer prompts.

After installation open:

http://localhost:8000

## Configuration

Installer will ask:

Prometheus URL

Days to analyze

Config is stored in config.yaml.

Example:
prometheus_url: "http://localhost:9090"
days: 14

## Screenshot 
<img width="783" height="718" alt="image" src="https://github.com/user-attachments/assets/7f5581d6-6f7a-497e-bfbc-ed23ef75b221" />


## Methodology

CPU: p95 of summed non-idle CPU cores

RAM: p95 of used memory

Safety margin: +20%

CPU minimum: 1 core

RAM rounded to 0.5 GB

If recommended < current → reclaim
If recommended > current → grow

Project status

v0.1 — MVP

## License

MIT License
