import csv
import time
import requests
import json
import subprocess
import zipfile
import os
from datetime import datetime
import re
import socket

# 清除代理环境变量
os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)
os.environ.pop("http_proxy", None)
os.environ.pop("https_proxy", None)

# Part1.下载中转节点
def is_valid_ipv4(ip): 
    """检查一个字符串是否是有效的IPv4地址"""
    pattern = re.compile(r'^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)$')
    return bool(pattern.match(ip))

def get_previously_selected_ips(): #获取上一次优选的ip
    with open(".\\config\\config.json","r",encoding="utf-8") as config:
        domains = json.load(config).get("domains")
        ip_list=[]
        for key in domains:
            #获取该域名的ip地址
            ip = socket.gethostbyname(key)
            ip_list.append(ip)
        print("上一次优选的ip已添加到此次优选")
        return ip_list
    
#获取固定ip,可根据喜好添加
def get_fixed_ips():
    with open (".\\config\\fixed_ips.txt","r",encoding="utf-8") as file:
        ip_list= [ip.strip() for ip in file.readlines()]
        ip_list=filter(is_valid_ipv4,ip_list)
        return list(ip_list)

def fetch_ips(): #下载并生成3ip.txt文件
    print("下载并生成第三方中转IP列表...")
    # 设置日期格式
    current_date = datetime.now().strftime('%Y%m%d')
    download_folder = os.path.join('3ip_file', current_date)

    # 使用requests下载文件
    response = requests.get("https://zip.baipiao.eu.org/")
    with open("3ip_file.zip", "wb") as file:
        file.write(response.content)

    # 使用zipfile解压缩到特定目录
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    with zipfile.ZipFile('3ip_file.zip', 'r') as archive:
        archive.extractall(download_folder)

    # 整合.txt文件
    valid_ips = []

    for file_name in os.listdir(download_folder):
        if file_name.endswith('.txt'):
            with open(os.path.join(download_folder, file_name), 'r') as infile:
                for line in infile:
                    if line=="\n":
                        continue
                    ip = line.strip()
                    if is_valid_ipv4(ip):
                        valid_ips.append(ip)

    # 添加上一次优选的IP
    valid_ips = get_previously_selected_ips() + get_fixed_ips() + valid_ips
    valid_ips = list(set(valid_ips))
    print(f"共获取{len(valid_ips)}个IP")
    

    with open(os.path.join(download_folder, 'combined.txt'), 'w') as outfile:
        outfile.write('\n'.join(valid_ips))

    # 如果3ip.txt已经存在，删除它
    if os.path.exists('3ip.txt'):
        os.remove('3ip.txt')

    # 移动到根目录并重命名
    os.rename(os.path.join(download_folder, 'combined.txt'), '3ip.txt')

    print("此次优选IP已保存到3ip.txt")
    

# Part3.生成result.csv
def run_cloudflare_speedtest():
    print("测速并生成result.csv...")
    with open('.\\config\\cmd.txt', 'r') as file:
        cmd = file.readline().strip().split()
    cmd.extend(['-p', '0'])
    subprocess.run(cmd)

    print("测速完成，生成result.csv文件")

def get_ips():  # 读取result.csv文件中的IPs
    ips = []
    with open("result.csv", "r",encoding="utf-8") as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)  # skip header
        for row in csvreader:
            ips.append(row[0])
        return ips


# Part4.更新Cloudflare DNS记录
def load_config(): # 读取config.json文件
    with open("config\\config.json", "r", encoding="utf-8") as file:
        config = json.load(file)
        email = config.get("email")
        global_api_key = config.get("global_api_key")
        zone_id = config.get("zone_id")
        domains = config.get("domains")
        if not email or not global_api_key or not zone_id or not domains:
            print("错误: config.json文件中缺少必要的key！")
            exit()
    return email, global_api_key, zone_id, domains

def update_cloudflare_dns(email, global_api_key, zone_id, domains):
    print("更新Cloudflare DNS记录...")
    ips = get_ips()  # 读取result.csv文件中的IPs
    if len(ips)>20: #下载速度为0，请尝试更换测速地址
        return domains
    res_domains=domains.copy() #复制domains字典
    for idx, (domain, record_id) in enumerate(domains.items()):
        if idx >= len(ips):
            print(f"可用ip数量不足，截至域名: {domain}")
            #将剩余domains字典中的域名添加到not_updated_domains字典中
            break

        ip = ips[idx]
        print(f"Processing Domain[{idx + 1}] : {domain} with IP: {ip}")

        headers = {
            "X-Auth-Email": email,
            "X-Auth-Key": global_api_key,
            "Content-Type": "application/json"
        }
        data = {
            "type": "A",
            "name": domain,
            "content": ip,
            "ttl": 60,
            "proxied": False
        }

        url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
        response = requests.put(url, headers=headers, data=json.dumps(data))
        res_domains.pop(domain, None)  # 从domains字典中删除已更新的域名
        print(response.json())
    return res_domains  # 返回未更新的域名

def main():
    fetch_ips()  # 下载并生成3ip.txt文件
    print("中转节点下载完成，开始筛选...")
    run_cloudflare_speedtest()  # 生成result.csv文件

    email, global_api_key, zone_id, domains = load_config() # 读取config.json文件
    domains = update_cloudflare_dns(email, global_api_key, zone_id, domains)
    while domains:
        print("未更新的域名: ", domains)
        print("正在重新测速并更新...")
        run_cloudflare_speedtest()  # 生成result.csv文件
        domains = update_cloudflare_dns(email, global_api_key, zone_id, domains)
    


if __name__=="__main__":
    main()
    print("10秒后自动退出程序")
    time.sleep(10)
    
