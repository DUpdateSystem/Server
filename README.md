# UpgradeAll Server

[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg?style=flat-square)](https://github.com/RichardLitt/standard-readme)

UpgradeAll 服务端代码仓库

该项目旨在为 [UpgradeAll 项目](https://github.com/DUpdateSystem/UpgradeAll) 提供数据支持。
它由以下部分构成
1. 服务端主体。
2. 软件源脚本仓库。

## 内容列表

- [背景](#背景)
- [安装](#安装)
- [运行这个项目](#运行这个项目)
   - [已安装 Docker 的 Linux 环境](#已安装Docker的Linux环境)
   - [手动安装并运行](#手动安装并运行（适用于Termux）)
- [示例](#示例)
- [相关仓库](#相关仓库)
- [维护者](#维护者)
- [如何贡献](#如何贡献)
- [使用许可](#使用许可)

## 背景

`UpgradeAll 服务端` 最开始因为 [@yah](https://github.com/wangxiaoerYah) 在维护脚本时发觉本地爬虫的效率问题而被提出，并于 0.1.2 （
客户端版本）版本的开发阶段实现。


## 安装

这个项目使用 [Python 3](https://www.python.org/)。请确保你本地安装了它们。


## 使用说明

克隆仓库，这样你就可以开始修改该项目了

```sh
$ git clone --depth=1 https://github.com/DUpdateSystem/Server.git
# 获取你的调试/开发的基础环境
```

### 运行这个项目

#### 已安装 Docker 的 Linux 环境
```sh
$ ./startup.sh --help
# 查看使用帮助
# 使用 debug 模式运行，将直接挂载 app 文件夹到相关目录下，因此，在修改本项目代码时，请尽管运行以测试你的代码。
```

#### 手动安装并运行（适用于 Termux）
因为我**没有 Windows 开发环境**，所以我只以 Linux 作为示例，命令可能不完全相同
```sh
$ pip3 install -r app/requirements.txt
# 安装 Python 依赖
$ python3 -m app --help
# 查看命令帮助
```

## 示例

想了解我们建议的规范是如何被应用的，请参考 [example-readmes](example-readmes/)。

## 相关仓库

- [UpgradeAll](https://github.com/DUpdateSystem/UpgradeAll) — UpgradeAll 的安卓实现。
- [UpgradeAll-rules](https://github.com/DUpdateSystem/UpgradeAll-rules) — UpgradeAll 的配置文件仓库。

## 维护者

[@xz-dev](https://github.com/xz-dev)。

## 如何贡献

非常欢迎你的加入！[官方文档-参与我们](https://upgradeall.now.sh/joinus/)
如果你已经有一个明确的想法了？请把它告诉我们 [提一个 Issue](https://github.com/DUpdateSystem/Server/issues/new) 或者提交一个 Pull Request。


## 使用许可

[GPL-3.0](LICENSE) © xz-dev
