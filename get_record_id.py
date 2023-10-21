import requests
import json

with open(".\\config\\config.json","r",encoding="utf-8") as json_file:
    config = json.load(json_file)
    email = config.get("email")
    global_api_key = config.get("global_api_key")
    zone_id = config.get("zone_id")
    if not email or not global_api_key or not zone_id:
        print("错误: config.json文件中缺少必要的key！")
        exit()

url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?page=1&per_page=20&order=type&direction=asc"
headers = {
    "X-Auth-Email": email,
    "X-Auth-Key": global_api_key,
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)
domains_details = response.json()
results = domains_details.get("result")

with open(".\\config\\domains.txt", "r",encoding="utf-8") as domains:
    try:
        domains_list=[domain.strip() for domain in domains]
    except:
        print("domains.txt文件不存在或格式错误")
        exit()

if not config.get("domains"):
    config["domains"] = {}

for result in results:
    domain = result.get("name")
    if domain in domains_list:
        config["domains"][domain] = result.get("id")

with open("config.json","w",encoding="utf-8") as json_file:
    json.dump(config, json_file, indent=4)

print("config.json文件已完成更新")
