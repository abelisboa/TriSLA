from flask import Flask, Response
import json, time, os, subprocess

app = Flask(__name__)

def read_iperf():
    try:
        with open("/tmp/iperf.json") as f:
            data = json.load(f)
        end = data["end"]
        return {
            "throughput": end["sum_received"]["bits_per_second"] / 1e6,
            "packet_loss": end["sum_received"].get("lost_percent", 0.0),
            "latency": end.get("streams", [{}])[0].get("sender", {}).get("mean_rtt", 10)
        }
    except Exception:
        return None

@app.route("/metrics")
def metrics():
    m = read_iperf()
    if not m:
        return Response("", mimetype="text/plain")

    return Response(f"""
trisla_network_throughput_mbps {m['throughput']}
trisla_network_packet_loss_ratio {m['packet_loss']}
trisla_network_latency_ms {m['latency']}
""", mimetype="text/plain")

app.run(host="0.0.0.0", port=9105)
