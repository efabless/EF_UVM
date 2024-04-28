import yaml

bus_mapping = {
    "generic": "APB AHB WISHBONE",
    "WB": "WISHBONE",
    "AHBL": "AHB",
    "APB": "APB",
}
supported_buses = []

stream = open("/home/karim/work/EF_GPIO/EF_GPIO8.yaml")
data = yaml.load(stream, Loader=yaml.Loader)
bus_info = data["info"]["bus"]
for bus in bus_info:
    supported_buses.append(bus_mapping[bus])

print(" ".join(supported_buses))
stream.close()
