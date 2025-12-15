import pandas as pd
from ics import Calendar, Event
from datetime import datetime, timedelta
import re
import pytz
import os

# --- CẤU HÌNH ---
INPUT_FILE = "ThoiKhoaBieuSinhVien.xls"
OUTPUT_FILE = "ThoiKhoaBieu_KMA_Final.ics"

# 1. Bảng giờ BẮT ĐẦU (Đã mở rộng thêm tiết 17, 18 dự phòng)
TIME_START_SLOTS = {
    # Sáng
    1: (7, 0), 2: (7, 50), 3: (8, 40),
    4: (9, 35), 5: (10, 25), 6: (11, 15),
    # Chiều
    7: (13, 0), 8: (13, 50), 9: (14, 40),
    10: (15, 35), 11: (16, 25), 12: (17, 15),
    # Tối
    13: (18, 15), 14: (19, 5), 15: (19, 55), 16: (20, 45),
    17: (21, 20), 18: (22, 10)  # Dự phòng
}

# 2. Bảng giờ KẾT THÚC (Tương ứng 45p/tiết)
TIME_END_SLOTS = {
    # Sáng
    1: (7, 45), 2: (8, 35), 3: (9, 25),
    4: (10, 20), 5: (11, 10), 6: (12, 0),
    # Chiều
    7: (13, 45), 8: (14, 35), 9: (15, 25),
    10: (16, 20), 11: (17, 10), 12: (18, 0),
    # Tối
    13: (19, 0), 14: (19, 50), 15: (20, 40), 16: (21, 30),
    17: (22, 5), 18: (22, 55)  # Dự phòng
}


def parse_schedule_original(text):
    """Sử dụng lại chính xác logic parse của bạn để đảm bảo đủ event"""
    if pd.isna(text): return []
    blocks = re.split(r'(?=Từ \d{2}/\d{2}/\d{4})', str(text))
    parsed_data = []

    for block in blocks:
        if not block.strip(): continue
        date_range = re.search(r'Từ (\d{2}/\d{2}/\d{4}) đến (\d{2}/\d{2}/\d{4})', block)
        if not date_range: continue

        start_date = datetime.strptime(date_range.group(1), '%d/%m/%Y')
        end_date = datetime.strptime(date_range.group(2), '%d/%m/%Y')

        lines = block.split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.startswith("Từ"): continue

            match = re.search(r'(Thứ \d|Chủ nhật).*?tiết\s*([\d,]+)(?:.*?tại\s*(.*))?', line, re.IGNORECASE)
            if match:
                dow_str = match.group(1).lower()
                periods_str = match.group(2)
                location = match.group(3).strip() if match.group(3) else "Chưa cập nhật địa điểm"

                dow = None
                if 'chủ nhật' in dow_str:
                    dow = 6
                elif 'thứ 2' in dow_str:
                    dow = 0
                elif 'thứ 3' in dow_str:
                    dow = 1
                elif 'thứ 4' in dow_str:
                    dow = 2
                elif 'thứ 5' in dow_str:
                    dow = 3
                elif 'thứ 6' in dow_str:
                    dow = 4
                elif 'thứ 7' in dow_str:
                    dow = 5

                periods = [int(p) for p in periods_str.split(',') if p.isdigit()]
                if periods and dow is not None:
                    parsed_data.append({
                        'start_date': start_date, 'end_date': end_date,
                        'dow': dow, 'periods': periods, 'location': location
                    })
    return parsed_data


def create_ics(file_path, output_path):
    # Đọc file an toàn
    try:
        if file_path.endswith('.xls') or file_path.endswith('.xlsx'):
            try:
                df = pd.read_excel(file_path, skiprows=9)
            except:
                df = pd.read_csv(file_path, skiprows=9, encoding='utf-16', sep='\t')
        else:
            df = pd.read_csv(file_path, skiprows=9)
    except Exception as e:
        print(f"Lỗi đọc file: {e}")
        df = pd.read_csv(file_path, skiprows=9, encoding='utf-8')

    df.columns = df.columns.str.strip()
    c = Calendar()
    timezone = pytz.timezone('Asia/Ho_Chi_Minh')
    total_events = 0

    print("Đang xử lý...")
    for index, row in df.iterrows():
        subject_name = row.get('Tên học phần')
        raw_schedule = row.get('Thời gian địa điểm')

        if pd.isna(subject_name) or pd.isna(raw_schedule): continue

        schedules = parse_schedule_original(raw_schedule)

        for sched in schedules:
            current_date = sched['start_date']
            end_date = sched['end_date']

            while current_date <= end_date:
                if current_date.weekday() == sched['dow']:
                    periods = sorted(sched['periods'])
                    if not periods: continue

                    start_period = periods[0]
                    end_period = periods[-1]

                    # --- KHỐI XỬ LÝ LỖI (Try/Catch) ---
                    try:
                        # Kiểm tra xem tiết học có trong từ điển không
                        if start_period not in TIME_START_SLOTS:
                            print(f"⚠️ Cảnh báo: Tiết bắt đầu '{start_period}' không xác định. Môn: {subject_name}")
                            # Fallback: Tính thủ công
                            h_start = 7 + (start_period // 2)  # Ước lượng
                            m_start = 0
                            event_start = current_date.replace(hour=h_start, minute=m_start, second=0)
                        else:
                            h_start, m_start = TIME_START_SLOTS[start_period]
                            event_start = current_date.replace(hour=h_start, minute=m_start, second=0)

                        if end_period not in TIME_END_SLOTS:
                            # Nếu không có giờ kết thúc trong bảng -> Dùng logic cũ của bạn (cộng 45p)
                            event_end = event_start + timedelta(minutes=45 * len(periods))
                        else:
                            h_end, m_end = TIME_END_SLOTS[end_period]
                            event_end = current_date.replace(hour=h_end, minute=m_end, second=0)

                        e = Event()
                        e.name = str(subject_name)
                        e.begin = timezone.localize(event_start)
                        e.end = timezone.localize(event_end)
                        e.location = sched['location']
                        e.description = f"Tiết: {','.join(map(str, periods))}\nLớp: {row.get('Lớp học phần', '')}"
                        c.events.add(e)
                        total_events += 1

                    except Exception as err:
                        print(f"❌ Lỗi khi tạo event môn {subject_name}: {err}")

                current_date += timedelta(days=1)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(c.serialize())
    return total_events


if __name__ == "__main__":
    if os.path.exists(INPUT_FILE):
        try:
            count = create_ics(INPUT_FILE, OUTPUT_FILE)
            print(f"\n✅ THÀNH CÔNG! Tạo được {count} sự kiện.")
            print(f"File: {OUTPUT_FILE}")
        except Exception as e:
            print(f"Lỗi: {e}")
    else:
        print("Không tìm thấy file đầu vào.")