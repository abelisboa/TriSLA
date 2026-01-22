from flask import Flask, Response
import json, time, os, subprocess, requests

app = Flask(__name__)

def get_iperf_data():
    # Tenta ler de volume compartilhado primeiro
    try:
        with open("/shared/iperf.json") as f:
            data = json.load(f)
            end = data["end"]
            return {
                "throughput": end["sum_received"]["bits_per_second"] / 1e6,
                "packet_loss": end["sum_received"].get("lost_percent", 0.0),
                "latency": end.get("streams", [{}])[0].get("sender", {}).get("mean_rtt", 10)
            }
    except:
        # Fallback: valores padrão
        return {
            "throughput": 100.0,
            "packet_loss": 0.0,
            "latency": 5.0
        }

@app.route("/metrics")
def metrics():
    m = get_iperf_data()
    return Response(f"""
trisla_network_throughput_mbps {m['throughput']}
trisla_network_packet_loss_ratio {m['packet_loss']}
trisla_network_latency_ms {m['latency']}
""", mimetype="text/plain")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9105)
