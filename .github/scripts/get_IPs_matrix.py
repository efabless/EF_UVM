import json
import sys


def main():
    tests = sys.argv[1:]
    tests = " ".join(tests).split(",")
    output_matrix = {"IPs": []}
    for test in tests:
        output_matrix["IPs"].append({"test": test})
    print(json.dumps(output_matrix))


if __name__ == "__main__":
    main()
