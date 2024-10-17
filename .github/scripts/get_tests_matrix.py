import json
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tests", nargs="*")
    parser.add_argument("--buses", nargs="*")
    parser.add_argument("--skip-gl")
    args = parser.parse_args()
    tests = args.tests
    buses = args.buses
    tests = " ".join(tests).split(",")
    output_matrix = {"tests": []}
    for test in tests:
        output_matrix["tests"].append({"test": test, "tag": "RTL"})
        if args.skip_gl.lower() != "yes":
            gl_tests = []
            for name in test.split():
                gl_tests.append(f"gl_{name}")
            output_matrix["tests"].append({"test": " ".join(gl_tests), "tag": "GL"})

    output_matrix_with_buses = {"tests": []}
    for bus in buses:
        for test in output_matrix["tests"]:
            output_matrix_with_buses["tests"].append({**test, **{"bus": bus}})
    print(json.dumps(output_matrix_with_buses))


if __name__ == "__main__":
    main()
