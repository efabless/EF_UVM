import json
import sys


def main():
    tests = sys.argv[1:]
    tests = " ".join(tests).split(",")
    output_matrix = {"tests": []}
    for test in tests:
        output_matrix["tests"].append({"test": test, "tag": "RTL"})
        gl_tests = []
        for name in test.split():
            gl_tests.append(f"gl_{name}")
        output_matrix["tests"].append({"test": " ".join(gl_tests), "tag": "GL"})
    print(json.dumps(output_matrix))


if __name__ == "__main__":
    main()
