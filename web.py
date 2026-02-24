from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import json

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def index():

    with open("result.json") as f:
        data = json.load(f)

    cpu_total = data["summary"]["cpu_reclaim"]
    ram_total = data["summary"]["ram_reclaim"]
    servers = data["summary"]["servers"]

    html = f"""
<html>
<head>
<title>Resource Optimizer</title>

<style>
body {{
    font-family: Arial;
    padding:20px;
}}

summary {{
    cursor:pointer;
    font-size:18px;
    font-weight:bold;
}}

.job {{
    margin-top:15px;
}}

.server {{
    margin-left:25px;
}}

.box {{
    background:#f5f5f5;
    padding:10px;
    margin-top:5px;
    white-space:pre-line;
}}

.total {{
    background:#eaeaea;
    padding:15px;
    margin-bottom:20px;
    font-size:18px;
}}

.reclaim {{ color:green; font-weight:bold }}
.grow {{ color:red; font-weight:bold }}
</style>

</head>

<body>

<h1>Resource Optimizer</h1>

<div class="total">
Total servers: {servers}<br>
CPU reclaim: {cpu_total} cores<br>
RAM reclaim: {ram_total} GB
</div>
"""

    for job in sorted(data["groups"]):

        html += f"""
<details class="job">
<summary>📁 {job}</summary>
"""

        for host in sorted(data["groups"][job]):

            srv = data["groups"][job][host]
            cpu = srv["cpu"]
            ram = srv["ram"]

            cpu_line = f"<span class='reclaim'>Reclaim: {cpu['reclaim']} cores</span>" if cpu["reclaim"]>0 else (
                       f"<span class='grow'>Need add: {cpu['grow']} cores</span>" if cpu["grow"]>0 else "Optimal")

            ram_line = f"<span class='reclaim'>Reclaim: {ram.get('reclaim',0)} GB</span>" if ram.get("reclaim",0)>0 else (
                       f"<span class='grow'>Need add: {ram.get('grow',0)} GB</span>" if ram.get("grow",0)>0 else "Optimal")

            html += f"""
<div class="server">
<details>
<summary>🖥 {host}</summary>

<div class="box">

CPU:
Current: {cpu['current']}
p95 usage: {cpu['p95']}
Recommended: {cpu['recommended']}
{cpu_line}

RAM:
Current: {ram.get('current','-')} GB
p95 usage: {ram.get('p95','-')} GB
Recommended: {ram.get('recommended','-')} GB
{ram_line}

</div>

</details>
</div>
"""

        html += "</details>"

    html += "</body></html>"

    return html
