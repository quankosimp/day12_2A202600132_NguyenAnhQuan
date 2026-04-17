# Mission Answers — Part 1-5

## Part 1 — Localhost vs Production

### Exercise 1.1: Anti-patterns trong `01-localhost-vs-production/develop/app.py`
1. Hardcoded secrets (`OPENAI_API_KEY`, `DATABASE_URL`) -> lộ credentials khi commit/log.
2. `DEBUG=True` cố định -> tăng risk lộ thông tin nội bộ.
3. Dùng `print()` thay structured logging -> khó observability trên cloud.
4. Log thẳng secret (`Using key`) -> leak nghiêm trọng.
5. Không có `/health` và `/ready` -> platform không auto-restart/route đúng.
6. Bind `host="localhost"` -> container/cloud không truy cập được từ ngoài.
7. Port hardcoded `8000` -> không tương thích `PORT` env var của Railway/Render.
8. `reload=True` trong runtime chính -> không phù hợp production.

### Exercise 1.2: Basic run
- `POST /ask` chạy được local.
- Kết luận: chạy local được nhưng chưa production-ready do thiếu config/security/health/shutdown.

### Exercise 1.3: So sánh develop vs production
| Feature | Basic | Advanced | Vì sao quan trọng |
|---|---|---|---|
| Config | Hardcode | `config.py` đọc env vars | Không phải sửa code theo từng môi trường |
| Secrets | Trong source code | Lấy từ env | Tránh lộ key, rotate dễ |
| Port/Host | `localhost:8000` cố định | `HOST/PORT` từ env | Tương thích container/cloud |
| Health/Ready | Không có | Có `/health`, `/ready` | Auto-healing + readiness routing |
| Logging | `print()` | JSON structured logging | Dễ parse/monitor/alert |
| Shutdown | Đột ngột | Graceful qua lifecycle/SIGTERM | Giảm request fail khi deploy/scale down |

## Part 2 — Docker Containerization

### Exercise 2.1: `02-docker/develop/Dockerfile`
1. Base image: `python:3.11`.
2. Working directory: `/app`.
3. `COPY requirements.txt` trước để tận dụng Docker layer cache, code đổi không phải cài lại deps.
4. `CMD` là default command có thể override; `ENTRYPOINT` cố định executable chính.

### Exercise 2.2 + 2.3
- Develop: single-stage, đơn giản, image lớn hơn.
- Production: multi-stage (`builder` + `runtime`), runtime mỏng hơn và chạy non-root user.

### Exercise 2.4: Compose architecture
- Stack gồm `agent`, `redis`, `qdrant`, `nginx`.
- `nginx` nhận traffic public, proxy vào `agent`.
- `agent` gọi Redis/Qdrant qua network nội bộ.

## Part 3 — Cloud Deployment

### Exercise 3.1 Railway
- Đã chuẩn bị đầy đủ `railway.toml` với `startCommand`, `healthcheckPath`, restart policy.
- Env tối thiểu cần set: `PORT`, `AGENT_API_KEY` (và key LLM nếu dùng thật).

### Exercise 3.2 Render vs Railway config
- `render.yaml`: Blueprint IaC chi tiết service + redis + env policy (`sync: false`, `generateValue`).
- `railway.toml`: gọn hơn, tập trung build/deploy/runtime settings.

### Exercise 3.3 Cloud Run
- `cloudbuild.yaml`: pipeline test -> build -> push -> deploy.
- `service.yaml`: runtime IaC (autoscaling, resources, probes, secrets).

## Part 4 — API Security

### Exercise 4.1 API key auth
- Validate ở dependency `verify_api_key` trong `04-api-gateway/develop/app.py`.
- Thiếu key -> `401`, sai key -> `403`, đúng key -> cho vào endpoint.
- Rotate key bằng env var (`AGENT_API_KEY`) không cần sửa code.

### Exercise 4.2 JWT flow
- `/auth/token` cấp JWT từ username/password.
- Endpoint protected dùng `Depends(verify_token)`.
- Token mang `username`, `role`, expiry.

### Exercise 4.3 Rate limiting
- Thuật toán: Sliding Window (deque timestamps).
- Limit mặc định: user `10 req/60s`, admin `100 req/60s`.
- Vượt limit trả `429` + `Retry-After`.

### Exercise 4.4 Cost guard (đã hoàn thiện)
- Refactor `04-api-gateway/production/cost_guard.py`:
  - Budget: `$10/user/tháng`.
  - Track usage theo key Redis `budget:{user_id}:{YYYY-MM}`.
  - TTL 32 ngày để tự dọn key cũ.
  - `check_budget(...)` raise `402` khi projected cost vượt budget.
- Cập nhật `04-api-gateway/production/app.py`:
  - Ước lượng cost trước call LLM để chặn sớm.
  - Sửa `budget_remaining_usd` trả đúng phần còn lại.

## Part 5 — Scaling & Reliability

### Exercise 5.1 + 5.2
- `05-scaling-reliability/develop/app.py` đã có đủ `/health`, `/ready`, graceful shutdown và in-flight tracking.

### Exercise 5.3 Stateless
- `05-scaling-reliability/production/app.py` lưu session/history trong Redis (`session:{id}`), không lưu state conversation theo instance.

### Exercise 5.4 Load balancing (đã hoàn thiện cấu hình)
- Sửa `05-scaling-reliability/production/docker-compose.yml`:
  - Trỏ đúng Dockerfile: `05-scaling-reliability/production/Dockerfile`.
  - Bỏ `env_file` bị thiếu để tránh compose fail.
- Bổ sung mới:
  - `05-scaling-reliability/production/Dockerfile`
  - `05-scaling-reliability/production/requirements.txt`
- Thêm endpoint alias `POST /ask` trong production app để đồng bộ luồng test các part trước.

### Exercise 5.5 Stateless test
- Script `test_stateless.py` có thể dùng để xác nhận session không mất khi request đi qua nhiều instance.

## Files đã chỉnh để hoàn thiện Part 1-5
- `04-api-gateway/production/cost_guard.py`
- `04-api-gateway/production/app.py`
- `05-scaling-reliability/production/docker-compose.yml`
- `05-scaling-reliability/production/app.py`
- `05-scaling-reliability/production/Dockerfile` (new)
- `05-scaling-reliability/production/requirements.txt` (new)

## Quick verify đã chạy
- `python3 -m py_compile 04-api-gateway/production/cost_guard.py 04-api-gateway/production/app.py 05-scaling-reliability/production/app.py` -> pass.
