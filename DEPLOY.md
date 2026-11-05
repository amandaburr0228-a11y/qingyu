# 部署路径

## EdgeOne Pages（当前优先）

项目包含 EdgeOne Python Cloud Functions 入口 `cloud-functions/api/index.py`，复用四 Agent 引擎与 WSGI 会话逻辑。

1. 创建 Pages 项目，连接 GitHub 的 qingyu 仓库。
2. 项目根目录为仓库根；构建命令 `python3 scripts/build_edgeone.py`，静态产物目录 `web`。
3. 配置环境变量 `DEMO_ACCESS_CODE`；需要真实模型时再配置 `LLM_API_KEY`、`LLM_BASE_URL`、`LLM_MODEL`。不要将密钥写进代码。
4. 构建完成后检查 `/api/health` 返回状态，再验证三个场景。
5. 先使用平台提供的测试域名；正式域名的接入另行配置。

Cloud Functions 使用临时内存会话：冷启动、扩容或实例切换可能结束当前会话。服务发现会话丢失时返回错误并要求显式开启新对话，不会静默清除风险状态。正式使用需要外部共享会话存储与统一限流。当前访问码与限流均用于演示。

Python Cloud Functions 是否已在当前腾讯云账号及所选部署区域开放，需要通过控制台构建验证；若不可用，不能只部署静态页面来代替完整后端。

官方参考：https://pages.edgeone.ai/document/python

## 已有 Linux 服务器（备选）


适用于已有 Linux 服务器、Docker Engine 与 Docker Compose。首次上线先用本地规则模式，再配置真实模型；不要在公网使用真实未成年人资料。

## 文件与配置
将完整项目放到服务器一个独立目录，例如 /opt/qingyu。复制 `.env.example` 为 `.env`，设置一个足够长的 `DEMO_ACCESS_CODE`。模型密钥只填在服务器 .env 中，切勿提交 GitHub。

## 启动
```sh
docker compose up -d --build app
curl http://127.0.0.1:8000/health
```
应用仅监听服务器回环地址。没有域名时可通过本机 SSH 隧道预览：
```sh
ssh -L 8765:127.0.0.1:8000 user@server
```
然后打开 http://localhost:8765 。不要为了临时预览直接把模型接口暴露在公网。

## 域名与 HTTPS
把已有域名的 DNS 指向服务器，在 .env 设置 DOMAIN 为域名（不含 https://）。确认该域名可用于此服务器，并核实所在地的域名接入要求。Caddy 配置会为该域名申请 HTTPS 证书：
```sh
docker compose --profile https up -d --build
```
服务器及云防火墙需要允许入站 TCP 80、443；不要开放应用的 8000。若机器已有 Nginx/Caddy 或其他网站，先复用现有反向代理，不要直接启动本项目的 Caddy 抢占端口。

## 更新与回退
更新前记录当前 Git 提交。拉取代码后执行 `docker compose up -d --build app`，再检查 /health 和对话。需要回退时切换到上一已验证提交后重新构建。不要运行会删除卷的清理命令。部署重启会清空当前所有内存会话。

## 运行边界
- 单 Gunicorn worker + 多线程，避免内存会话分散到不同进程。
- 会话保存在服务器内存，闲置一小时后在下次请求时清理；最多 200 个会话。
- 每会话两秒请求间隔，最多 4 个并行模型任务。演示访问码不是正式账户系统，也不是完整的防滥用机制。
- 部署真实用户前仍需完善账户与授权、全局限流、告知与同意、合规数据策略、专家验证与安全评估。
- 未配置真实模型时使用规则与模板；关键词检索不是向量 RAG。
