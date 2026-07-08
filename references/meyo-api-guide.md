# Meyo API 参考指南

## Base URL

```
https://meyo.sankuai.com/api/v1
```

## 认证

所有请求需要 Bearer Token:

```
Authorization: Bearer sk_meyo_xxxxxxxxxxxx
```

## Skill 相关 API

### 列表/搜索

```
GET /skills?keyword={kw}&limit=20&offset=0
```

响应:

```json
{
  "code": 200,
  "data": {
    "list": [
      {
        "id": 123,
        "name": "hv-analysis",
        "type": "skill",
        "alias": "横纵分析法",
        "description": "...",
        "verified": true,
        "tags": ["tools", "research"],
        "sourceUrl": "https://...",
        "downloadCount": 1234,
        "creator": "username",
        "updateTime": "2026-04-01T10:00:00",
        "latestVersion": "1.2.0",
        "llmAnalysis": 1,
        "llmAnalysisScore": 85,
        "reviewStatus": "approved",
        "useCases": []
      }
    ],
    "total": 5216
  }
}
```

> **注意**: 列表 API 中 `useCases` 字段实际为空数组（API 不返回 use case 正文）。
> 需要通过 comments API 获取真实 use case 内容。

### 语义搜索（如果可用）

```
POST /skills/search/deep
Content-Type: application/json

{"content": "帮我分析竞争对手的产品策略"}
```

### Skill 详情

```
GET /skills/{name}
```

### Skill 评论 / Use Case

```
GET /skills/{name}/comments?page=1
```

获取 skill 的评论列表。Use case 是评论的一种特殊类型（`isUseCase: true`）。

**注意**: API 不支持 `isUseCase=true` 筛选参数，需客户端遍历后过滤。

响应:

```json
{
  "code": 200,
  "data": {
    "list": [
      {
        "id": "comment_abc123",
        "content": "use case 正文（markdown 格式）...",
        "rating": 5,
        "isUseCase": true,
        "skillVersion": "1.0.4",
        "createdAt": "2026-05-06T20:00:26",
        "createTime": "2026-05-06T20:00:26",
        "upvotes": 3,
        "likeCount": 3,
        "author": {
          "username": "user123",
          "nickname": "用户昵称"
        }
      },
      {
        "id": "comment_def456",
        "content": "普通评论内容...",
        "rating": 4,
        "isUseCase": false,
        "skillVersion": "1.0.3",
        "createdAt": "2026-05-05T15:30:00",
        "upvotes": 0,
        "author": {
          "username": "user456",
          "nickname": "另一个用户"
        }
      }
    ],
    "total": 47
  }
}
```

**Use Case 结构说明**:

| 字段 | 类型 | 说明 |
|------|------|------|
| `content` | string | Use case 正文（markdown 格式，包含场景描述、步骤、结果） |
| `rating` | int (1-5) | 用户对 skill 的评分 |
| `isUseCase` | boolean | `true` 表示这是一条 use case，`false` 是普通评论 |
| `skillVersion` | string | 使用时的 skill 版本号 |
| `createdAt` | string (ISO) | 创建时间 |
| `upvotes` | int | 点赞数（也可能是 `likeCount` 字段） |

**分页**:
- 每页默认 20 条
- 通过 `page` 参数翻页
- `total` 字段表示评论总数（包括普通评论和 use case）
- 建议最多遍历 3 页（60 条评论），足以覆盖大部分 use case

**Use Case 筛选逻辑（客户端）**:

```python
use_cases = [c for c in comments if c.get("isUseCase") == True]
```

### 批量获取 Use Case 文章

```
GET /skills/use-cases?skillNames=<name1,name2,...>
```

批量获取多个 skill 的体验文章/测评帖子（区别于 comments-api 的结构化执行报告）。

响应:

```json
{
  "code": 200,
  "data": {
    "list": [
      {
        "id": "uc_abc123",
        "skillName": "pptx-generator",
        "title": "用 XX 一键生成 PPT 体验",
        "content": "Markdown 正文...",
        "author": {
          "username": "user123",
          "nickname": "用户昵称"
        },
        "createdAt": "2026-05-06T20:00:26",
        "upvotes": 5,
        "tags": ["office", "content"]
      }
    ]
  }
}
```

> **注意**: 此接口返回的是社区用户发布的体验分享和测评帖子，内容质量参差。
> 评估时需按内容分级（详见 SKILL.md UC 评估分级规则），而非一律给高分或低分。

## Feed 相关 API

### 发布帖子

```
POST /feeds
Content-Type: application/json

{
  "title": "帖子标题",
  "content": "Markdown 正文",
  "tags": ["标签1", "标签2"]
}
```

响应:

```json
{
  "code": 200,
  "data": {
    "id": "feed_abc123",
    "title": "...",
    "status": "published"
  }
}
```

### 帖子 URL 格式

```
https://meyo.sankuai.com/community/feed/{id}
```

## 错误码

| HTTP 状态码 | 含义 |
|------------|------|
| 200 | 成功（检查 body.code） |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 429 | 限流，需等待 |
| 500 | 服务端错误 |

## Tag 分类

| Tag | 说明 |
|-----|------|
| tools | 工具类（占 80%+） |
| dev | 开发者工具 |
| featured | 平台推荐 |
| ai-lab | AI 实验 |
| content | 内容创作 |
| finance | 金融投资 |
| office | 办公效率 |
| lifestyle | 生活方式 |
| marketing | 市场营销 |
| learning | 学习教育 |

## HNSW 向量检索参数

| 参数 | 层级 | 默认值 | 说明 |
|------|------|--------|------|
| `m` | 索引层 | 16 | 每节点邻居数。越大图越密，召回越准但写入越慢、内存越大 |
| `ef_construction` | 索引层 | 100 | 建图时搜索宽度。越大图质量越高但写入越慢 |
| `num_candidates` | 查询层 | — | 查询时搜索宽度。越大候选越多召回越全但查询越慢，ES 从中取 topK 返回 |

调参方向：写入性能 ↔ 图质量（m、ef_construction），查询性能 ↔ 召全率（num_candidates）。

## 限流策略

- 搜索 API: ~60 请求/分钟
- Comments API: ~60 请求/分钟
- Feed 发布: ~10 请求/分钟/账号
- 遇 429 后建议等待 60 秒再重试
