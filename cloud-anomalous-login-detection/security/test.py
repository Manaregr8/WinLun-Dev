from geoip_enrich import ip_to_geo


test_ips = [
    "8.8.8.8",
    "1.1.1.1",
    "106.219.224.1"
]

for ip in test_ips:
    print(ip_to_geo(ip))