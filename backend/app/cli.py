"""Try mission generation from the terminal, without the frontend.

    python3 -m app.cli --time 30 --need surprise

Handy for checking that Ollama + Gemma work before you start the web app.
"""
import argparse
import asyncio
import json

from .models.mission import ENVIRONMENT_OPTIONS, NEED_OPTIONS, TIME_OPTIONS
from .services.mission_generator import generate_mission


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate one OFFLINE mission.")
    parser.add_argument("--time", type=int, choices=TIME_OPTIONS, default=30)
    parser.add_argument("--need", choices=NEED_OPTIONS, default="surprise")
    parser.add_argument("--environment", choices=ENVIRONMENT_OPTIONS, default="unsure")
    args = parser.parse_args()
    result = asyncio.run(generate_mission(args.time, args.need, args.environment))
    print(json.dumps(result.to_dict(), indent=2))


if __name__ == "__main__":
    main()
