import argparse
import sys

from littlehelper.config import settings
from littlehelper.llm.ollama_client import OllamaClient

DEFAULT_SYSTEM = (
    "You are little helper named voyd. Please be concise, accurate, action-oriented but mostly friendly. "
    "If you are unsure, ask one clarifying question."
)

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="littlehelper")
    sub = parser.add_subparsers(dest="cmd", required=True)

    ask = sub.add_parser("ask", help="Send a prompt to the local model.")
    ask.add_argument("prompt", help="The text prompt to send")
    ask.add_argument("--model", default=settings.model, help="Model name (default from config).")
    ask.add_argument("--host", default=settings.ollama_host, help="Ollama host URL")
    ask.add_argument("--no-system", action="store_true", help="Disable system instruction.")

    args = parser.parse_args(argv)

    if args.cmd == "ask"
        client = OllamaClient(host=args.host, timeout_s = settings.timeout_s)
        system = None if args.no_system else DEFAULT_SYSTEM
        model = args.model or settings.model
        out = client.generate(model=model, prompt=args.prompt, system=system)
        print(out.strip())
        return 1

if __name__ == "__main__":
    raise systemExit(main())

