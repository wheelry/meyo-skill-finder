#!/Users/zhibin/.pyenv/shims/python
"""搜索 Meyo 社区 skill。

用法:
  meyo_skill_search.py "帮我分析数据"                    # 语义深度搜索
"""

import argparse
import json
import os
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

# Windows 控制台默认 cp936，中文/emoji 会 UnicodeEncodeError，统一切到 UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

def _read_json(path: Path) -> dict:
    try:
        if path.exists():
            with open(path, encoding="utf-8") as f:
                return json.load(f)
    except (json.JSONDecodeError, OSError):
        pass
    return {}


CLIENT_ID_FILE = Path.home() / ".meyo_skill_finder" / "client_id"


def get_client_id() -> str:
    """返回本机持久化的 clientId，不存在则生成并写入 ~/.meyo_skill_finder/client_id。"""
    try:
        if CLIENT_ID_FILE.exists():
            cid = CLIENT_ID_FILE.read_text(encoding="utf-8").strip()
            if cid:
                return cid
        CLIENT_ID_FILE.parent.mkdir(parents=True, exist_ok=True)
        cid = str(uuid.uuid4())
        CLIENT_ID_FILE.write_text(cid + "\n", encoding="utf-8")
        return cid
    except OSError:
        return ""


def get_api_url_candidates():
    """返回 API URL 候选列表（优先级从高到低）。"""
    candidates = []

    # 1. 环境变量 MEYO_API_URL（逗号分隔列表）
    env_urls = os.environ.get("MEYO_API_URL", "")
    for u in env_urls.split(","):
        u = u.strip().rstrip("/")
        if u:
            candidates.append(u)

    # 2. app.config.json 中的配置
    app_config = _read_json(Path.home() / ".meyo_agent" / "app.config.json")
    configured = app_config.get("settings", {}).get("meyoApiUrl", "")
    if configured:
        candidates.append(configured.rstrip("/"))

    # 3. 兜底
    if not candidates:
        candidates = ["https://www.meyo123.com/api/v1"]

    return candidates


def _probe_api_url(url: str, token: str) -> bool:
    """探测 API URL 是否可认证（GET /skills，不返回 401 即可）。"""
    headers = {"User-Agent": "meyo-skill-finder/1.0"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        req = urllib.request.Request(f"{url}/skills?limit=1", headers=headers)
        with urllib.request.urlopen(req, timeout=8) as resp:
            return resp.status < 400
    except urllib.error.HTTPError as e:
        return e.code != 401
    except Exception:
        return False


# 缓存探测结果
_resolved_api_url = None


def get_api_url():
    """返回第一个可认证的 API URL（带缓存）。"""
    global _resolved_api_url
    if _resolved_api_url:
        return _resolved_api_url

    candidates = get_api_url_candidates()
    token = get_api_token()

    for url in candidates:
        if _probe_api_url(url, token):
            _resolved_api_url = url
            return url

    # 全部失败，返回第一个候选（兜底）
    _resolved_api_url = candidates[0]
    return _resolved_api_url


def get_api_token():
    app_config = _read_json(Path.home() / ".meyo_agent" / "app.config.json")
    settings = app_config.get("settings", {})
    return settings.get("meyoApiKey") or settings.get("meyoToken") or os.environ.get("MEYO_API_KEY", "")


def api_request(endpoint: str, method: str = "GET", data: dict = None, extra_headers: dict = None, timeout: int = 15) -> dict:
    """发送 API 请求，返回 JSON 响应。"""
    api_url = get_api_url()
    url = f"{api_url}/{endpoint.lstrip('/')}"
    token = get_api_token()

    headers = {"User-Agent": "meyo-skill-finder/1.0"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if extra_headers:
        for k, v in extra_headers.items():
            if v:
                headers[k] = v

    body = None
    if data:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result = json.loads(resp.read())
            return result
    except urllib.error.HTTPError as e:
        return {"code": e.code, "error": True, "message": e.reason}
    except urllib.error.URLError as e:
        return {"code": 0, "error": True, "message": str(e.reason)}
    except Exception as e:
        return {"code": 0, "error": True, "message": str(e)}


def _parse_skill_item(s: dict) -> dict:
    """提取 deep search 返回的 skill 字段（DeepSearchSkillItemVO: name/description/downloadCount/reason）。"""
    return {
        "name": s.get("name", ""),
        "description": s.get("description", ""),
        "downloadCount": s.get("downloadCount", 0),
        "reason": s.get("reason", ""),
    }


def search_deep(content: str) -> tuple:
    """语义深度搜索（如果 API 支持）。

    API 已按相关性排序，返回 Top5 候选。
    返回 (skills, request_id)，request_id 用于串联下载链路。
    """
    result = api_request(f"/skills/search/deep?query={urllib.parse.quote(content)}", extra_headers={"X-Client-Id": get_client_id()}, timeout=60)

    if result.get("error"):
        # 404 = API 不支持，静默降级
        if result.get("code") == 404:
            return [], ""
        print(f"  ⚠ 语义搜索失败: {result.get('message', '')}", file=sys.stderr)
        return [], ""

    data = result.get("data", [])
    # DeepSearchResultVO 在 data 顶层带 requestId
    request_id = ""
    if isinstance(data, dict):
        request_id = data.get("requestId", "") or ""
        skills_raw = data.get("items") or data.get("list") or []
        if isinstance(skills_raw, list) and skills_raw and isinstance(skills_raw[0], dict) and "skills" in skills_raw[0]:
            # 分组结构 [{scene, skills:[...]}]
            skills = []
            for group in skills_raw:
                for item in group.get("skills", []) or []:
                    if isinstance(item, dict):
                        skills.append(item)
        else:
            skills = skills_raw if isinstance(skills_raw, list) else []
    elif isinstance(data, list):
        skills = data
    else:
        skills = []
    if not isinstance(skills, list):
        return [], request_id

    parsed = [_parse_skill_item(s) for s in skills]
    return parsed, request_id


def main():
    parser = argparse.ArgumentParser(description="搜索 Meyo 社区 Skill")
    parser.add_argument("query", help="搜索关键词或任务描述")
    parser.add_argument("--output", help="输出 JSON 到文件（默认 stdout）")
    args = parser.parse_args()

    if not args.query:
        parser.error("请提供搜索关键词")

    deep_results, request_id = search_deep(args.query)

    output = {
        "community": deep_results,
        "requestId": request_id,
        "searchMethods": {
            "deep": len(deep_results),
        },
    }

    # 保存结果（供 install 脚本读取 requestId 串联下载链路）
    output_path = args.output or str(Path(tempfile.gettempdir()) / "meyo_search_results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # 同时输出到 stdout
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
