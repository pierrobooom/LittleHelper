import subprocess
import requests
from littlehelper.config import settings

def is_ollama_running(host: str = settings.ollama_host) -> bool:
    try:
        r = requests.get(host)
        return r.status_code == 200
    except Exception:
        return False


def stop_all_models():
    subprocess.run(["ollama", "ps"], check=False)
    subprocess.run(["ollama", "stop", f"{settings.model}"], check=False)


def stop_ollama_server():
    subprocess.run(
        ["powershell", "-Command", "Stop-Process -Name ollama -Force"],
        check=False
    )