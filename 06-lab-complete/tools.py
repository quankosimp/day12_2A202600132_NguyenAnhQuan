from langchain_core.tools import tool

# =========================================================
# MOCK DATA — Dữ liệu giả lập hệ thống du lịch
# Lưu ý: Giá cả có logic (VD: cuối tuần đắt hơn, hạng cao hơn đắt hơn)
# Sinh viên cần đọc hiểu data để debug test cases.
# =========================================================

FLIGHTS_DB = {
    ("Hà Nội", "Đà Nẵng"): [
        {"airline": "Vietnam Airlines", "departure": "06:00", "arrival": "07:20", "price": 1_450_000, "class": "economy"},
        {"airline": "Vietnam Airlines", "departure": "14:00", "arrival": "15:20", "price": 2_800_000, "class": "business"},
        {"airline": "VietJet Air", "departure": "08:30", "arrival": "09:50", "price": 890_000, "class": "economy"},
        {"airline": "Bamboo Airways", "departure": "11:00", "arrival": "12:20", "price": 1_200_000, "class": "economy"}
    ],
    ("Hà Nội", "Phú Quốc"): [
        {"airline": "Vietnam Airlines", "departure": "07:00", "arrival": "09:15", "price": 2_100_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "10:00", "arrival": "12:15", "price": 1_350_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "16:00", "arrival": "18:15", "price": 1_100_000, "class": "economy"},
    ],
    ("Hà Nội", "Hồ Chí Minh"): [
        {"airline": "Vietnam Airlines", "departure": "06:00", "arrival": "08:10", "price": 1_600_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "07:30", "arrival": "09:40", "price": 950_000, "class": "economy"},
        {"airline": "Bamboo Airways", "departure": "12:00", "arrival": "14:10", "price": 1_300_000, "class": "economy"},
        {"airline": "Vietnam Airlines", "departure": "18:00", "arrival": "20:10", "price": 3_200_000, "class": "business"}
    ],
    ("Hồ Chí Minh", "Đà Nẵng"): [
        {"airline": "Vietnam Airlines", "departure": "09:00", "arrival": "10:20", "price": 1_300_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "13:00", "arrival": "14:20", "price": 780_000, "class": "economy"}
    ],
    ("Hồ Chí Minh", "Phú Quốc"): [
        {"airline": "Vietnam Airlines", "departure": "08:00", "arrival": "09:00", "price": 1_100_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "15:00", "arrival": "16:00", "price": 650_000, "class": "economy"}
    ]
}

HOTELS_DB = {
    "Đà Nẵng": [
        {"name": "Mường Thanh Luxury", "stars": 5, "price_per_night": 1_800_000, "area": "Mỹ Khê", "rating": 4.5},
        {"name": "Sala Danang Beach", "stars": 4, "price_per_night": 1_200_000, "area": "Mỹ Khê", "rating": 4.3},
        {"name": "Fivitel Danang", "stars": 3, "price_per_night": 650_000, "area": "Sơn Trà", "rating": 4.1},
        {"name": "Memory Hostel", "stars": 2, "price_per_night": 250_000, "area": "Hải Châu", "rating": 4.6},
        {"name": "Christina's Homestay", "stars": 2, "price_per_night": 350_000, "area": "An Thượng", "rating": 4.7},
    ],
    "Phú Quốc": [
        {"name": "Vinpearl Resort", "stars": 5, "price_per_night": 3_500_000, "area": "Bãi Dài", "rating": 4.4},
        {"name": "Sol by Meliá", "stars": 4, "price_per_night": 1_500_000, "area": "Bãi Trường", "rating": 4.2},
        {"name": "Lahana Resort", "stars": 3, "price_per_night": 800_000, "area": "Dương Đông", "rating": 4.0},
        {"name": "9Station Hostel", "stars": 2, "price_per_night": 200_000, "area": "Dương Đông", "rating": 4.5},
    ],
    "Hồ Chí Minh": [
        {"name": "Rex Hotel", "stars": 5, "price_per_night": 2_800_000, "area": "Quận 1", "rating": 4.3},
        {"name": "Liberty Central", "stars": 4, "price_per_night": 1_400_000, "area": "Quận 1", "rating": 4.1},
        {"name": "Cochin Zen Hotel", "stars": 3, "price_per_night": 550_000, "area": "Quận 3", "rating": 4.4},
        {"name": "The Common Room", "stars": 2, "price_per_night": 180_000, "area": "Quận 1", "rating": 4.6},
    ]
}


def _unexpected_tool_error(tool_name: str, exc: Exception) -> RuntimeError:
    error = RuntimeError(f"{tool_name} gặp lỗi nội bộ: {exc}")
    error.__cause__ = exc
    return error


@tool
def search_flights(origin: str, destination: str) -> str:
    """
    Tìm kiếm các chuyến bay giữa hai thành phố.
    Tham số:
    - origin: thành phố khởi hành (VD: 'Hà Nội', 'Hồ Chí Minh')
    - destination: thành phố đến (VD: 'Đà Nẵng', 'Phú Quốc')
    Trả về danh sách chuyến bay với hãng, giờ bay, giá vé.
    Nếu không tìm thấy tuyến bay, trả về thông báo không có chuyến.
    """
    try:
        flights = FLIGHTS_DB.get((origin, destination))
        route_label = f"{origin} -> {destination}"

        if flights is None:
            reverse_flights = FLIGHTS_DB.get((destination, origin))
            if reverse_flights is None:
                return f"Không tìm thấy chuyến bay từ {origin} đến {destination}."
            flights = reverse_flights
            route_label = f"{destination} -> {origin}"

        lines = [f"Danh sách chuyến bay {route_label}:"]
        for idx, flight in enumerate(flights, start=1):
            price = f"{flight['price']:,}".replace(",", ".") + "đ"
            lines.append(
                f"{idx}. {flight['airline']} | {flight['departure']} - {flight['arrival']} | "
                f"{flight['class']} | {price}"
            )
        return "\n".join(lines)
    except Exception as exc:
        raise _unexpected_tool_error("search_flights", exc)


@tool
def search_hotels(city: str, max_price_per_night: int = 99999999) -> str:
    """
    Tìm kiếm khách sạn tại một thành phố, có thể lọc theo giá tối đa mỗi đêm.
    Tham số:
    - city: tên thành phố (VD: 'Đà Nẵng', 'Phú Quốc', 'Hồ Chí Minh')
    - max_price_per_night: giá tối đa mỗi đêm (VND), mặc định không giới hạn
    Trả về danh sách khách sạn phù hợp với tên, số sao, giá, khu vực, rating.
    """
    try:
        hotels = HOTELS_DB.get(city, [])
        filtered_hotels = [
            hotel for hotel in hotels if hotel["price_per_night"] <= max_price_per_night
        ]
        filtered_hotels.sort(key=lambda hotel: hotel["rating"], reverse=True)

        budget = f"{max_price_per_night:,}".replace(",", ".") + "đ"
        if not filtered_hotels:
            return (
                f"Không tìm thấy khách sạn tại {city} với giá dưới "
                f"{budget}/đêm. Hãy thử tăng ngân sách."
            )

        lines = [f"Danh sách khách sạn tại {city}:"]
        for idx, hotel in enumerate(filtered_hotels, start=1):
            price = f"{hotel['price_per_night']:,}".replace(",", ".") + "đ"
            lines.append(
                f"{idx}. {hotel['name']} | {hotel['stars']} sao | "
                f"{hotel['area']} | Rating: {hotel['rating']} | {price}/đêm"
            )
        return "\n".join(lines)
    except Exception as exc:
        raise _unexpected_tool_error("search_hotels", exc)


@tool
def calculate_budget(total_budget: int, expenses: str) -> str:
    """
    Tính toán ngân sách còn lại sau khi trừ các khoản chi phí.
    Tham số:
    - total_budget: tổng ngân sách ban đầu (VND)
    - expenses: chuỗi mô tả các khoản chi, mỗi khoản cách nhau bởi dấu phẩy,
      định dạng 'tên_khoản:số_tiền' (VD: 'vé_máy_bay:890000,khách_sạn:650000')
    Trả về bảng chi tiết các khoản chi và số tiền còn lại.
    Nếu vượt ngân sách, cảnh báo rõ ràng số tiền thiếu.
    """
    try:
        def format_money(amount: int) -> str:
            return f"{amount:,}".replace(",", ".") + "đ"

        if not expenses or not expenses.strip():
            return (
                "Bảng chi phí:\n"
                "---\n"
                f"Tổng chi: {format_money(0)}\n"
                f"Ngân sách: {format_money(total_budget)}\n"
                f"Còn lại: {format_money(total_budget)}"
            )

        parsed_expenses = []
        for item in expenses.split(","):
            entry = item.strip()
            if not entry:
                return (
                    "Dữ liệu expenses không hợp lệ. Vui lòng nhập theo định dạng "
                    "'tên_khoản:số_tiền'."
                )

            name, separator, amount_text = entry.partition(":")
            name = name.strip()
            amount_text = amount_text.strip()

            if separator != ":" or not name or not amount_text:
                return (
                    f"Khoản chi '{entry}' không hợp lệ. Vui lòng nhập theo định dạng "
                    "'tên_khoản:số_tiền'."
                )

            try:
                amount = int(amount_text)
            except ValueError:
                return f"Số tiền của khoản '{name}' không hợp lệ: '{amount_text}'."

            if amount < 0:
                return f"Số tiền của khoản '{name}' phải là số không âm."

            parsed_expenses.append((name, amount))

        total_expenses = sum(amount for _, amount in parsed_expenses)
        remaining_budget = total_budget - total_expenses

        lines = ["Bảng chi phí:"]
        for name, amount in parsed_expenses:
            label = name.replace("_", " ").strip()
            if label:
                label = label[0].upper() + label[1:]
            lines.append(f"- {label}: {format_money(amount)}")

        lines.extend(
            [
                "---",
                f"Tổng chi: {format_money(total_expenses)}",
                f"Ngân sách: {format_money(total_budget)}",
                f"Còn lại: {format_money(remaining_budget)}",
            ]
        )

        if remaining_budget < 0:
            lines.append(
                f"Vượt ngân sách {format_money(-remaining_budget)}! Cần điều chỉnh."
            )

        return "\n".join(lines)
    except Exception as exc:
        raise _unexpected_tool_error("calculate_budget", exc)
