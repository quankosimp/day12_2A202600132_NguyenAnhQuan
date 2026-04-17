# Day 12 Delivery Checklist (Part 1-5)

> Student Name: _________________________  
> Student ID: _________________________  
> Date: _________________________

---

## 1) Part 1 — Localhost vs Production

### Exercise 1.1: Anti-patterns (01-localhost-vs-production/develop/app.py)
- [ ] Đã tìm ít nhất 5 vấn đề trong bản develop
- [ ] Có nêu rõ vì sao từng vấn đề nguy hiểm trong production

### Exercise 1.2: Run basic version
- [ ] Chạy được app basic và gọi được `POST /ask`
- [ ] Ghi nhận: chạy được local nhưng chưa production-ready

### Exercise 1.3: Compare develop vs production
- [ ] Hoàn thành bảng so sánh `app.py` (Config, Secrets, Port, Health check, Logging, Shutdown)
- [ ] Hiểu vai trò environment variables và graceful shutdown

### Checkpoint Part 1
- [ ] Hiểu vì sao hardcoded secrets nguy hiểm
- [ ] Biết cách dùng env vars
- [ ] Hiểu health check endpoint
- [ ] Hiểu graceful shutdown

---

## 2) Part 2 — Docker Containerization

### Exercise 2.1: Read Dockerfile (02-docker/develop/Dockerfile)
- [ ] Trả lời được: base image, working directory
- [ ] Giải thích được vì sao `COPY requirements.txt` trước source code
- [ ] Phân biệt `CMD` và `ENTRYPOINT`

### Exercise 2.2: Build + Run develop image
- [ ] Build thành công image develop
- [ ] Run thành công container và test được endpoint
- [ ] Ghi nhận được image size

### Exercise 2.3: Multi-stage build (02-docker/production/Dockerfile)
- [ ] Xác định đúng vai trò Stage 1 (builder) và Stage 2 (runtime)
- [ ] Build thành công image production
- [ ] So sánh size develop vs production và nêu lý do giảm kích thước

### Exercise 2.4: Docker Compose stack
- [ ] Đọc `docker-compose.yml` và mô tả architecture
- [ ] Chạy được stack bằng `docker compose`
- [ ] Test được `/health` và `/ask` qua Nginx

### Checkpoint Part 2
- [ ] Hiểu cấu trúc Dockerfile
- [ ] Hiểu lợi ích multi-stage build
- [ ] Hiểu Docker Compose orchestration
- [ ] Biết debug container (`docker logs`, `docker exec`)

---

## 3) Part 3 — Cloud Deployment

### Exercise 3.1: Railway
- [ ] Deploy thành công từ thư mục `03-cloud-deployment/railway`
- [ ] Set được env vars tối thiểu (`PORT`, `AGENT_API_KEY`)
- [ ] Có public URL chạy được
- [ ] Test thành công `/health` và `/ask` trên URL public

### Exercise 3.2: Render
- [ ] Đọc và hiểu `03-cloud-deployment/render/render.yaml`
- [ ] So sánh khác biệt giữa `render.yaml` và `railway.toml`

### Exercise 3.3 (Optional): Cloud Run
- [ ] Đọc `cloudbuild.yaml` và `service.yaml`
- [ ] Giải thích được pipeline CI/CD cơ bản

### Checkpoint Part 3
- [ ] Deploy thành công ít nhất 1 cloud platform
- [ ] Public URL hoạt động
- [ ] Biết set env vars trên cloud
- [ ] Biết xem logs trên platform

---

## 4) Part 4 — API Security

### Exercise 4.1: API Key auth (04-api-gateway/develop/app.py)
- [ ] Xác định đúng nơi validate API key
- [ ] Test được case không có key (401)
- [ ] Test được case key hợp lệ (200)
- [ ] Trả lời được cách rotate key

### Exercise 4.2: JWT auth (04-api-gateway/production)
- [ ] Đọc và hiểu luồng trong `auth.py`
- [ ] Lấy được token từ endpoint cấp token
- [ ] Gọi được `/ask` bằng Bearer token

### Exercise 4.3: Rate limiting
- [ ] Đọc `rate_limiter.py` và xác định thuật toán
- [ ] Xác định limit requests/minute
- [ ] Test spam request và quan sát response 429

### Exercise 4.4: Cost guard
- [ ] Hoàn thiện logic trong `cost_guard.py`
- [ ] Đảm bảo rule budget `$10/user/tháng`
- [ ] Có cơ chế track spending theo tháng (Redis key theo month)

### Checkpoint Part 4
- [ ] Implement API key auth
- [ ] Hiểu JWT flow
- [ ] Implement rate limiting
- [ ] Implement cost guard

---

## 5) Part 5 — Scaling & Reliability

### Exercise 5.1: Health checks (05-scaling-reliability/develop/app.py)
- [ ] Implement `GET /health` (liveness)
- [ ] Implement `GET /ready` (readiness)
- [ ] `ready` trả 200 khi dependency OK, 503 khi chưa sẵn sàng

### Exercise 5.2: Graceful shutdown
- [ ] Implement SIGTERM handler
- [ ] Đảm bảo ngừng nhận request mới, hoàn tất request đang chạy, đóng kết nối
- [ ] Test được hành vi shutdown khi gửi `kill -TERM`

### Exercise 5.3: Stateless design
- [ ] Refactor bỏ state trong memory
- [ ] Lưu state cần thiết ra Redis/shared store
- [ ] Giải thích được vì sao stateless quan trọng khi scale nhiều instance

### Exercise 5.4: Load balancing
- [ ] Chạy `docker compose up --scale agent=3`
- [ ] Xác nhận Nginx phân phối request qua nhiều instance
- [ ] Xác nhận failover khi 1 instance chết

### Exercise 5.5: Stateless test
- [ ] Chạy `test_stateless.py`
- [ ] Xác nhận conversation không mất khi instance bị kill

### Checkpoint Part 5
- [ ] Có health + readiness checks
- [ ] Có graceful shutdown
- [ ] Thiết kế stateless
- [ ] Có load balancing hoạt động

---

## 6) Hồ sơ nộp bắt buộc

### File bắt buộc
- [ ] `MISSION_ANSWERS.md` (đủ câu trả lời Part 1-5)
- [ ] `DEPLOYMENT.md` (public URL + lệnh test + ảnh chụp)
- [ ] Source code đầy đủ trong repo
- [ ] `README.md` hướng dẫn chạy rõ ràng

### Security & hygiene
- [ ] Không commit file `.env` (chỉ giữ `.env.example`)
- [ ] Không hardcode secrets
- [ ] Public URL còn truy cập được tại thời điểm nộp

### Final self-test
- [ ] `GET /health` trả OK
- [ ] Không auth thì bị chặn đúng (401/403)
- [ ] Có auth hợp lệ thì gọi API thành công
- [ ] Vượt limit thì trả 429

---

## 7) Link nộp bài

GitHub repository URL:

`https://github.com/<your-username>/day12-agent-deployment`

Deadline: **17/04/2026**
