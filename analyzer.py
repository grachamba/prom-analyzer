import requests
import yaml
import json
import math

with open("config.yaml") as f:
    config = yaml.safe_load(f)

PROM = config["prometheus_url"]
DAYS = config.get("days", 1)
SAFETY = 1.2


def prom_query(query):
    r = requests.get(
        f"{PROM}/api/v1/query",
        params={"query": query},
        timeout=60
    )
    r.raise_for_status()
    return r.json()["data"]["result"]


# ================= CPU =================

def analyze_cpu():

    result = {}

    cpu_linux = f'''
quantile_over_time(
  0.95,
  sum by (instance,job)(
    rate(node_cpu_seconds_total{{mode!="idle"}}[15m])
  )[{DAYS}d:]
)
'''

    cpu_windows = f'''
quantile_over_time(
  0.95,
  sum by (instance,job)(
    rate(windows_cpu_time_total{{mode!="idle"}}[15m])
  )[{DAYS}d:]
)
'''

    cpu_data = prom_query(cpu_linux) + prom_query(cpu_windows)

    linux_cores = prom_query('''
count by (instance,job)(
  node_cpu_seconds_total{mode="idle"}
)
''')

    windows_cores = prom_query('''
count by (instance,job)(
  windows_cpu_time_total{mode="idle"}
)
''')

    core_map = {}
    for s in linux_cores + windows_cores:
        host = s["metric"]["instance"]
        core_map[host] = int(float(s["value"][1]))

    for s in cpu_data:

        host = s["metric"]["instance"]
        job = s["metric"].get("job","unknown")

        p95 = float(s["value"][1])
        cores = core_map.get(host,1)

        recommended = max(1, math.ceil(p95 * SAFETY))
        reclaim = max(cores - recommended,0)
        grow = max(recommended - cores,0)

        result.setdefault(job,{})[host] = {
            "current": cores,
            "p95": round(p95,2),
            "recommended": recommended,
            "reclaim": reclaim,
            "grow": grow
        }

    return result


# ================= RAM =================

def analyze_ram():

    result = {}

    ram_linux = f'''
quantile_over_time(
  0.95,
  (node_memory_MemTotal_bytes
   -
   node_memory_MemAvailable_bytes)[{DAYS}d:]
)
'''

    ram_windows = f'''
quantile_over_time(
  0.95,
  (windows_cs_physical_memory_bytes
   -
   windows_os_physical_memory_free_bytes)[{DAYS}d:]
)
'''

    ram_data = prom_query(ram_linux) + prom_query(ram_windows)

    total_linux = prom_query("node_memory_MemTotal_bytes")
    total_windows = prom_query("windows_cs_physical_memory_bytes")

    total_map = {}

    for s in total_linux + total_windows:
        host = s["metric"]["instance"]
        total_map[host] = float(s["value"][1]) / 1024**3

    for s in ram_data:

        host = s["metric"]["instance"]
        job = s["metric"].get("job","unknown")

        p95 = float(s["value"][1]) / 1024**3
        total = total_map.get(host,0)

        recommended = math.ceil(p95 * SAFETY * 2) / 2
        reclaim = round(max(total - recommended,0),1)
        grow = round(max(recommended - total,0),1)

        result.setdefault(job,{})[host] = {
            "current": round(total,1),
            "p95": round(p95,2),
            "recommended": recommended,
            "reclaim": reclaim,
            "grow": grow
        }

    return result


# ================= MAIN =================

if __name__ == "__main__":

    cpu = analyze_cpu()
    ram = analyze_ram()

    total_cpu = sum(cpu[j][h]["reclaim"] for j in cpu for h in cpu[j])
    total_ram = sum(ram[j][h]["reclaim"] for j in ram for h in ram[j])
    server_count = sum(len(cpu[j]) for j in cpu)

    data = {
        "groups": {},
        "summary": {
            "servers": server_count,
            "cpu_reclaim": total_cpu,
            "ram_reclaim": round(total_ram,1)
        }
    }

    for job in cpu:
        data["groups"].setdefault(job,{})
        for host in cpu[job]:
            data["groups"][job][host] = {
                "cpu": cpu[job][host],
                "ram": ram.get(job,{}).get(host,{})
            }

    with open("result.json","w") as f:
        json.dump(data,f,indent=2)

    print("result.json updated")
