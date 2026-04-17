# Test Results - TravelBuddy Agent

- Generated at: `2026-04-07 17:15:12`
- Total cases: `5`

## Test 1 - Test 1 – Direct Answer (Không cần tool)

- Trace ID: `2923fcb95b88`

**Prompt:**

> Xin chào! Tôi đang muốn đi du lịch nhưng chưa biết đi đâu.

**Kỳ vọng:**

- Agent chào hỏi, hỏi thêm về sở thích/ngân sách/thời gian.  
- Không gọi tool nào.

**Tool calls:**

- Không có tool call

**Tool outputs:**

- Không có tool output

**Agent response:**

```text
Chào bạn! Đi du lịch thật thú vị! Bạn có ý định đi đâu trong nước hay quốc tế? Ngoài ra, bạn có ngân sách cụ thể nào cho chuyến đi này không? Mình có thể giúp bạn lên kế hoạch phù hợp với sở thích và ngân sách của bạn!
```

## Test 2 - Test 2 – Single Tool Call

- Trace ID: `db0efa3c11f5`

**Prompt:**

> Tìm giúp tôi chuyến bay từ Hà Nội đi Đà Nẵng

**Kỳ vọng:**

- Gọi `search_flights("Hà Nội", "Đà Nẵng")`  
- Liệt kê 4 chuyến bay.

**Tool calls:**

- `search_flights` với args: `{'origin': 'Hà Nội', 'destination': 'Đà Nẵng'}`

**Tool outputs:**

- `search_flights`
```text
Danh sách chuyến bay Hà Nội -> Đà Nẵng:
1. Vietnam Airlines | 06:00 - 07:20 | economy | 1.450.000đ
2. Vietnam Airlines | 14:00 - 15:20 | business | 2.800.000đ
3. VietJet Air | 08:30 - 09:50 | economy | 890.000đ
4. Bamboo Airways | 11:00 - 12:20 | economy | 1.200.000đ
```

**Agent response:**

```text
Dưới đây là danh sách chuyến bay từ Hà Nội đi Đà Nẵng:

1. **Vietnam Airlines**: 06:00 - 07:20 | Hạng phổ thông | 1.450.000đ
2. **Vietnam Airlines**: 14:00 - 15:20 | Hạng thương gia | 2.800.000đ
3. **VietJet Air**: 08:30 - 09:50 | Hạng phổ thông | 890.000đ
4. **Bamboo Airways**: 11:00 - 12:20 | Hạng phổ thông | 1.200.000đ

Nếu bạn cần thêm thông tin hoặc muốn đặt vé, hãy cho mình biết nhé!
```

## Test 3 - Test 3 – Multi-Step Tool Chaining

- Trace ID: `94aa08b07bed`

**Prompt:**

> Tôi ở Hà Nội, muốn đi Phú Quốc 2 đêm, budget 5 triệu. Tư vấn giúp!

**Kỳ vọng:**

Agent phải tự chuỗi nhiều bước:

1. `search_flights("Hà Nội", "Phú Quốc")` → tìm vé rẻ nhất (1.100.000đ)  
2. `search_hotels("Phú Quốc", max_price phù hợp)` → gợi ý trong tầm giá  
3. `calculate_budget(5000000, "vé_bay:1100000,khách_sạn:...")` → tính còn lại  

→ Sau đó tổng hợp thành gợi ý hoàn chỉnh với bảng chi phí.

**Tool calls:**

- `search_flights` với args: `{'origin': 'Hà Nội', 'destination': 'Phú Quốc'}`
- `search_hotels` với args: `{'city': 'Phú Quốc', 'max_price_per_night': 2500000}`

**Tool outputs:**

- `search_flights`
```text
Danh sách chuyến bay Hà Nội -> Phú Quốc:
1. Vietnam Airlines | 07:00 - 09:15 | economy | 2.100.000đ
2. VietJet Air | 10:00 - 12:15 | economy | 1.350.000đ
3. VietJet Air | 16:00 - 18:15 | economy | 1.100.000đ
```
- `search_hotels`
```text
Danh sách khách sạn tại Phú Quốc:
1. 9Station Hostel | 2 sao | Dương Đông | Rating: 4.5 | 200.000đ/đêm
2. Sol by Meliá | 4 sao | Bãi Trường | Rating: 4.2 | 1.500.000đ/đêm
3. Lahana Resort | 3 sao | Dương Đông | Rating: 4.0 | 800.000đ/đêm
```

**Agent response:**

```text
Chuyến bay:
1. Vietnam Airlines | 07:00 - 09:15 | economy | 2.100.000đ
2. VietJet Air | 10:00 - 12:15 | economy | 1.350.000đ
3. VietJet Air | 16:00 - 18:15 | economy | 1.100.000đ 

Khách sạn:
1. 9Station Hostel | 2 sao | Dương Đông | Rating: 4.5 | 200.000đ/đêm
2. Sol by Meliá | 4 sao | Bãi Trường | Rating: 4.2 | 1.500.000đ/đêm
3. Lahana Resort | 3 sao | Dương Đông | Rating: 4.0 | 800.000đ/đêm

Tổng chi phí ước tính (chọn chuyến bay VietJet Air 1.350.000đ và ở 9Station Hostel):
- Vé máy bay: 1.350.000đ
- Khách sạn: 200.000đ x 2 đêm = 400.000đ
- Tổng: 1.350.000 + 400.000 = 1.750.000đ

Gợi ý thêm:
- Nếu bạn muốn ở khách sạn 4 sao như Sol by Meliá, tổng chi phí sẽ là 2.100.000đ (vé máy bay VietJet Air 1.350.000đ và khách sạn 1.500.000đ cho 2 đêm). Bạn nên lựa chọn tùy theo sở thích và ngân sách. 
- Ngoài ra, bạn có thể khám phá các hoạt động tại Phú Quốc như lặn biển, tham quan các bảo tàng hoặc đi tour khám phá đảo. 
Nếu cần thêm thông tin hay hỗ trợ gì, đừng ngần ngại nhé!
```

## Test 4 - Test 4 – Missing Info / Clarification

- Trace ID: `a3c6cf20dee6`

**Prompt:**

> Tôi muốn đặt khách sạn

**Kỳ vọng:**

- Agent hỏi lại:
  - Thành phố nào?
  - Bao nhiêu đêm?
  - Ngân sách bao nhiêu?
- Không gọi tool vội.

**Tool calls:**

- Không có tool call

**Tool outputs:**

- Không có tool output

**Agent response:**

```text
Bạn muốn đặt khách sạn ở đâu và ngân sách của bạn là bao nhiêu mỗi đêm?
```

## Test 5 - Test 5 – Guardrail / Refusal

- Trace ID: `ffc332106d30`

**Prompt:**

> Giải giúp tôi bài tập lập trình Python về linked list

**Kỳ vọng:**

- Từ chối lịch sự  
- Nói rõ chỉ hỗ trợ về du lịch

**Tool calls:**

- Không có tool call

**Tool outputs:**

- Không có tool output

**Agent response:**

```text
Xin lỗi, nhưng mình chỉ có thể hỗ trợ với các thông tin liên quan đến du lịch, đặt phòng hay đặt vé. Nếu bạn có kế hoạch du lịch nào đó, mình rất vui lòng giúp bạn!
```
