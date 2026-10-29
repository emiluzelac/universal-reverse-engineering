#!/usr/bin/env python3
"""Harmless offline black-box exercise: run the file first, inspect the source later."""
import argparse
import json


def calculate(n: int) -> dict:
    if not -20 <= n <= 20:
        return {"status": "out_of_range", "input": n}
    if n == 0:
        return {"status": "idle", "input": n, "value": 0}
    if n % 2 == 0:
        value = n * n + 2
        path = "A"
    else:
        value = 3 * n + 1
        path = "B"
    return {"status": "ok", "input": n, "channel": path, "value": value}


def main() -> None:
    parser = argparse.ArgumentParser(description="Offline number-machine reverse engineering exercise")
    parser.add_argument("number", type=int)
    args = parser.parse_args()
    print(json.dumps(calculate(args.number), sort_keys=True))


if __name__ == "__main__":
    main()
