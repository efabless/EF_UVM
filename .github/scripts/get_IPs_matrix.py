import yaml
import json


def main():
    test_set_yaml = ".github/test_set.yaml"
    output_matrix = {"IPs": []}
    test_set_stream = open(test_set_yaml)
    data = yaml.load(test_set_stream, Loader=yaml.Loader)
    for item in data:
        tests = item["tests"]
        name = item["name"]
        url = item["url"]
        bus = item["bus"]
        output_matrix["IPs"].append(
            {
                "name": name,
                "url": url,
                "test-names": ",".join(tests),
                "buses": " ".join(bus),
            }
        )

    print(json.dumps(output_matrix))
    test_set_stream.close()


if __name__ == "__main__":
    main()
