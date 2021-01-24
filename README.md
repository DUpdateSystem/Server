# [UpgradeAll Server](https://github.com/DUpdateSystem/Server)

[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg?style=flat-square)](https://github.com/RichardLitt/standard-readme)

UpgradeAll 服务端代码仓库

该项目旨在为 [UpgradeAll 项目](https://github.com/DUpdateSystem/UpgradeAll) 提供数据支持。
它由以下部分构成
1. 服务端主体。
2. 软件源脚本仓库。

## 内容列表

- [背景](#背景)
- [安装](#安装)
- [使用说明](#使用说明)
   - [运行这个项目](#运行这个项目)
      - [Docker](#docker)
      - [已安装 Docker 的 Linux 环境](#已安装-docker-的-linux-环境)
      - [手动安装并运行](#手动安装并运行适用于-termux)
   - [示例](#示例)
      - [Docker](#docker-1)
      - [Shell script](#shell-script)
      - [手动运行](#手动运行)
   - [命令参数](#命令参数)
- [相关仓库](#相关仓库)
- [维护者](#维护者)
- [如何贡献](#如何贡献)
- [使用许可](#使用许可)

## 背景

`UpgradeAll 服务端` 最开始因为 [@yah](https://github.com/wangxiaoerYah) 在维护脚本时发觉本地爬虫的效率问题而被提出，并于 [0.1.2 版本（
客户端版本）](https://github.com/DUpdateSystem/UpgradeAll/releases/tag/0.1.2-rc.2)的开发阶段实现。


## 安装

这个项目使用 [Python 3](https://www.python.org/)。请确保你本地安装了它们。


## 使用说明

克隆仓库，这样你就可以开始使用该项目了

```sh
$ git clone --depth=1 https://github.com/DUpdateSystem/Server.git
# 获取你的调试/开发的基础环境
$ cd server
# 进入 Server 主体代码文件夹
```

### 运行这个项目

#### Docker
```sh
$ docker pull xiangzhedev/upgradeall-server
# 更新镜像
$ docker run --rm -p 5255:5255 xiangzhedev/upgradeall-server
# 单次运行
$ docker run --rm -v $PWD/app:/app -p 5255:5255 xiangzhedev/upgradeall-server
# 测试运行（在该项目的根目录下运行）
$ docker run --rm -p 5255:5255 xiangzhedev/upgradeall-server --help
# 查看参数帮助
$ docker run -dit --restart unless-stopped --name=update-server -d -p 5255:5255 xiangzhedev/upgradeall-server
# 服务部署
$ docker stop update-server && docker container rm update-server
# 停止服务
```

#### 已安装 Docker 的 Linux 环境
```sh
$ ./startup.sh --help
# 查看使用帮助
# 使用 debug 模式运行时，将直接挂载 app 文件夹到相关目录下，因此，在修改本项目代码时，请尽管测试你的代码。
```

#### 手动安装并运行（适用于 Termux）
> 因为我**没有 Windows 开发环境**，所以我只以 Linux 作为示例，命令可能不完全相同
```sh
$ pip3 install -r app/requirements.txt
# 安装 Python 依赖
$ python3 -m app --help
# 查看命令帮助
```

### 示例
#### Docker
```sh
$ docker run -dit --restart unless-stopped --name=update-server -d -p 5255:5255 xiangzhedev/upgradeall-server
# 服务部署
$ docker run --rm xiangzhedev/upgradeall-server --debug 6a6d590b-1809-41bf-8ce3-7e3f6c8da945 android_app_package com.nextcloud.client
# 测试软件源
```

#### Shell script
该脚本只用于调试，脚本会自动本地编译新的 Docker 镜像并挂载代码文件夹以便调试
```sh
$ ./startup.sh
# 部署服务端
$ ./startup.sh --debug 6a6d590b-1809-41bf-8ce3-7e3f6c8da945 android_app_package com.nextcloud.client
# 测试软件源
```
#### 手动运行
```sh
$ python3 -m app
# 部署服务端
$ python3 -m app --debug 6a6d590b-1809-41bf-8ce3-7e3f6c8da945 android_app_package com.nextcloud.client
# 测试软件源
```
### 命令参数
```text
usage: DUpdateSystem Server [-h] [--normal] [--debug]
                            [hub_uuid] [hub_options [hub_options ...]]

DUpdateSystem 服务端

positional arguments:
  hub_uuid     测试的软件源脚本的 UUID
  hub_options  测试软件源脚本的运行选项，以 key value 为组，例如：android_app_package
               net.xzos.upgradeall

optional arguments:
  -h, --help   show this help message and exit
  --normal     以 config.ini 配置正常运行服务端
  --debug      运行软件源脚本测试
```

## 相关仓库

- [UpgradeAll](https://github.com/DUpdateSystem/UpgradeAll) — UpgradeAll 的安卓实现。
- [UpgradeAll-rules](https://github.com/DUpdateSystem/UpgradeAll-rules) — UpgradeAll 的配置文件仓库。

## 维护者

[@xz-dev](https://github.com/xz-dev)。

## 如何贡献

非常欢迎你的加入！[官方文档-参与我们](https://upgradeall.now.sh/joinus/)  
你已经有一个明确的想法了?请 [提一个 Issue](https://github.com/DUpdateSystem/Server/issues/new/choose) 或者提交一个 Pull Request。


## 使用许可

[GPL-3.0](LICENSE) © xz-dev
