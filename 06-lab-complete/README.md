# TravelBuddy Agent

Project này là một demo agent tư vấn du lịch bằng Python, dùng `LangGraph` để điều phối hội thoại và `tool calling` để xử lý các tác vụ nghiệp vụ như tìm chuyến bay, tìm khách sạn và tính ngân sách.

## Thành phần chính

- `agent.py`: khởi tạo model, nạp system prompt, bind tool và chạy graph hội thoại.
- `tools.py`: chứa dữ liệu mock và 3 tool nghiệp vụ:
  - `search_flights`
  - `search_hotels`
  - `calculate_budget`
- `system_prompt.txt`: prompt hệ thống cho persona, guardrail và format phản hồi.
- `usercases.md`: các test case mẫu để kiểm tra hành vi agent.
- `test.py`: chạy toàn bộ prompt trong `usercases.md` và lưu kết quả vào `test_results.md`.

## Luồng hoạt động

Người dùng nhập yêu cầu du lịch, agent sẽ phân tích intent rồi quyết định:

- trả lời trực tiếp nếu chỉ cần hỏi đáp
- gọi một hoặc nhiều tool nếu cần tra cứu chuyến bay, khách sạn hoặc tính chi phí
- tổng hợp kết quả cuối thành câu trả lời tiếng Việt

## Cài đặt

Tạo file `.env`:

```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
```

Cài dependency:

```bash
venv/bin/pip install -r requirements.txt
```

## Cách chạy

Chạy agent dạng CLI:

```bash
venv/bin/python agent.py
```

Chạy API local:

```bash
venv/bin/python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

Mở giao diện chat:

```bash
http://localhost:8000/
```

Healthcheck:

```bash
curl http://localhost:8000/health
```

Trạng thái service dạng JSON:

```bash
curl http://localhost:8000/status
```

Chat API:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Tư vấn chuyến đi Đà Nẵng 3 ngày từ Hà Nội"}'
```

Chạy test cases và ghi kết quả:

```bash
venv/bin/python test.py
```

## Ghi chú

- Dữ liệu chuyến bay và khách sạn hiện là mock data trong `tools.py`.
- Kết quả agent phụ thuộc vào model và prompt hiện tại.
- `test_results.md` giúp quan sát trace tool call và phản hồi cuối để debug hành vi agent.

## Deploy Railway

1. Push code lên GitHub.
2. Trên Railway: `New Project` -> `Deploy from GitHub repo`.
3. Railway sẽ dùng:
   - `requirements.txt` để cài dependency
   - `runtime.txt` để chọn Python version
   - `Procfile` để chạy service web
4. Thêm biến môi trường trên Railway:
   - `OPENAI_API_KEY` (bắt buộc)
   - `OPENAI_MODEL` (khuyến nghị, mặc định `gpt-4o-mini`)
   - `LOG_LEVEL` (tuỳ chọn)
5. Sau khi deploy, kiểm tra:
   - `GET /health` trả `{ "status": "ok" }`
   - `POST /chat` trả `reply` và `trace_id`

## Chạy bằng Docker Compose (local)

1. Tạo `.env` (ít nhất có `OPENAI_API_KEY`).
2. Build và chạy:

```bash
docker compose up --build
```

3. Kiểm tra:

```bash
curl http://localhost:8000/health
```

4. Dừng dịch vụ:

```bash
docker compose down
```

## Deploy Railway bằng Dockerfile

- Railway **không dùng trực tiếp** `docker-compose.yml` để deploy một service.
- Railway sẽ build từ `Dockerfile` trong repo.
- Steps:
  1. Push code lên GitHub.
  2. Trên Railway tạo project từ repo.
  3. Set biến môi trường:
     - `OPENAI_API_KEY` (bắt buộc)
     - `OPENAI_MODEL` (khuyến nghị, mặc định `gpt-4o-mini`)
     - `LOG_LEVEL` (tuỳ chọn)
  4. Deploy và kiểm tra `/health`, `/chat`.
