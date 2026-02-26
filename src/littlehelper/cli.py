import argparse

from littlehelper.config import settings
from littlehelper.llm.ollama_client import OllamaClient
from littlehelper.system.ollama_control import stop_all_models

DEFAULT_SYSTEM = "You are LittleHelper named voyd. Be concise, accurate, practical and above all friendly."

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="voyd")
    parser.add_argument(
        "text",
        nargs="*",
        help='Prompt text to send. Special command: "exit" to stop Ollama.'
    )
    args = parser.parse_args(argv)

    # No args at all -> show help
    if not args.text:
        parser.print_help()
        return 1

    # Special command: voyd exit
    if len(args.text) == 1 and args.text[0].lower() == "exit":
        print(stop_all_models())
        return 0

    # Otherwise: everything is the prompt
    prompt = " ".join(args.text)

    client = OllamaClient(settings.ollama_host, settings.timeout_s)
    output = client.generate(
        model=settings.model,
        prompt=prompt,
        system=DEFAULT_SYSTEM
    )
    print(output.strip())
    return 0