# AI关键词搜索次数采集器（MVP）

这是一个可直接运行的最小可用版本：

- 通过 API 上报关键词在不同 AI 平台的搜索次数。
- 支持按平台汇总、按关键词汇总。
- 使用 SQLite 持久化，部署简单。

> 说明：目前各家 AI 平台普遍不直接开放“全网关键词搜索次数”公开接口。
> 本项目采用“事件上报 + 聚合统计”方案，即从你自己的业务入口/埋点系统把查询事件写入本服务，再统一统计。

## 支持平台

- chatgpt
- claude
- gemini
- perplexity
- grok
- kimi
- qwen

## 快速启动

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

服务默认地址：`http://127.0.0.1:8000`

文档地址：

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## API 示例

### 1) 上报一次关键词事件

```bash
curl -X POST 'http://127.0.0.1:8000/events' \
  -H 'Content-Type: application/json' \
  -d '{
    "platform": "chatgpt",
    "keyword": "ai agent",
    "count": 3
  }'
```

### 2) 查看全部平台关键词统计

```bash
curl 'http://127.0.0.1:8000/stats'
```

### 3) 查看某个平台关键词统计

```bash
curl 'http://127.0.0.1:8000/stats?platform=gemini'
```

## 下一步建议

1. 在你的产品中接入埋点：用户每次在 AI 上发起搜索/提问时调用 `/events`。
2. 增加鉴权（如 API Key / JWT）。
3. 增加时间维度查询（日/周/月趋势）。
4. 对接可视化面板（Metabase、Superset 或自定义前端）。
