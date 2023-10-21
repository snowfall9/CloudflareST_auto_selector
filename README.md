## 项目概述

**项目名称**: CloudflareSpeedTest_Auto_Selector

**描述**: 简单的自动优选第三方反代IP的工具，配合定时任务实现Windows平台上的自动优选第三方反代IP。该项目利用 [XIU2](https://github.com/XIU2) 大佬的开源项目 [CloudflareSpeedTest](https://github.com/XIU2/CloudflareSpeedTest) ，自动从一个第三方资源下载中转节点IP，筛选出活跃的IP，然后自动更新到Cloudflare的DNS记录。

------

## 开始前的准备

### Cloudflare配置获取:

1. 初次配置`config.json` 文件前，请在Cloudflare上创建一定数量的域名解析(10个以下)，并将域名按行排列复制到 domains.txt 文件中，**注意不要开启域名代理服务(小云朵）！**
2. `config.json`文件填写时，请在Cloudflare官网的  [用户API 令牌](https://dash.cloudflare.com/profile/api-tokens)  界面查看并复制自己的Global API Key 复制到`global_api_key`，在对应域名管理概述页面的右下角找到区域 ID复制到`zone_id`，`email`为你的Cloudflare账户邮箱。

### 前提条件:

- Python
- `requests` 库
- [CloudflareSpeedTest](https://github.com/XIU2/CloudflareSpeedTest/releases)

### 安装:

1. 克隆项目到本地。
2. 使用pip安装所需的Python库: `pip install requests`
3. 确保 `CloudflareST.exe` 在项目的根目录或在系统PATH中，请通过 [CloudflareSpeedTest](https://github.com/XIU2/CloudflareSpeedTest/releases) 下载合适的版本

------

## 使用说明

### 基本使用:

1. 确保所有依赖库和工具都已安装。
2. 确认`config.json`配置文件前三项 `email` `global_api_key` `zone_id` 已正确填写，且将已添加解析的域名按行排列复制到 domains.txt 文件。
3. 在项目根目录下运行 `python get_record_id.py` 获取`domains.txt` 中所有域名对应的record id并自动添加到 `config.json` 配置文件的"domains" 中。
4. `cmd.txt` 存放默认的  `CloudflareST.exe` 执行指令，可根据需求自行更改，指令文档  [CloudflareSpeedTest](https://github.com/XIU2/CloudflareSpeedTest)  ,需注意 `-f 3ip.txt -p 0` 指令为必须存在的指令，分别指向了IP文件与程序结束指令，其中-url 后面的参数可自行替换为自己常用的测速地址。
5. 在项目根目录下运行 `python cf_dns_updater.py`。
6. 程序将自动下载中转节点、筛选IP、测速，并更新Cloudflare的DNS记录。

------

## 配置

在 `domains.txt` 中，你需要填写:

​	在Cloudflare上添加好解析的域名，一行填写一个

在 `config.json` 中，你需要配置以下信息:

- `email`: 你的Cloudflare账户邮箱。
- `global_api_key`: 你的Cloudflare Global API Key。
- `zone_id`: 你的Cloudflare Zone ID。
- `domains`: 你希望更新的域名及其对应的记录ID。

------

## 第三方工具说明

该项目使用了 `CloudflareST.exe`，一个开源的Cloudflare CDN节点测速筛选工具。该工具提供了测速并将结果输出到CSV文件的功能，为本项目的DNS记录更新提供了支持。

**使用链接**: [CloudflareSpeedTest](https://github.com/XIU2/CloudflareSpeedTest) 



感谢大佬提供的第三方反代IP

**第三方中转节点来源**: https://zip.baipiao.eu.org 

------

## 常见问题 (FAQ)
**Q**: 如何实现自动优选？

**A**: 配置好所有内容后打包 `cf_dns_updater.py` 为可执行文件，或者设置一个bat批处理文件执行python脚本，
       然后在Windows的任务计划程序中添加定时/开机运行任务，或者借助一些第三方定时运行程序的工具实现此目的。


**Q**: 程序执行时出现错误怎么办?

**A**: 请检查你的`config.json`是否已按照文档中的说明进行了正确配置。



**Q**: `CloudflareST.exe`程序应该怎么放置?

**A**: 放置在根目录即可，仅需要`CloudflareST.exe` 一个可执行文件即可。

------

## 贡献

如果你发现了bug或有新的功能建议，请通过GitHub的Issues提交。欢迎任何形式的贡献。

------

## 联系信息

- **GitHub**: [snowfall9](https://github.com/snowfall9) 

------

## 更新日志

- v1.0 - 初始版本，支持自动下载中转节点、筛选IP、测速并更新Cloudflare的DNS记录。
