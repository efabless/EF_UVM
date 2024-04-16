import yaml
import json


def main():
    test_set_yaml = ".github/test_set.yaml"
    output_matrix = {}
    test_set_stream = open(test_set_yaml)
    data = yaml.load(test_set_stream, Loader=yaml.Loader)
    for item in data:
        tests = item["tests"]
        name = item["name"]
        if output_matrix.get(name) is None:
            output_matrix[name] = {"test-names": []}
        url = item["url"]
        output_matrix[name]["url"] = url
        for test in tests:
            output_matrix[name]["test-names"].append(test)

    print(json.dumps(output_matrix), end="")
    test_set_stream.close()


if __name__ == "__main__":
    main()
