import pandas as pd
from ics import Calendar, Event
from datetime import datetime, timedelta
import re
import pytz
import os

# --- CẤU HÌNH ---
INPUT_FILE = "ThoiKhoaBieuSinhVien.xls"  # Đổi tên file đầu vào của bạn tại đây
OUTPUT_FILE = "ThoiKhoaBieu_KMA.ics"

# Khung giờ học
TIME_SLOTS = {
    1: (7, 0), 2: (7, 50), 3: (8, 40), 4: (9, 35), 5: (10, 25), 6: (11, 15),
    7: (12, 30), 8: (13, 20), 9: (14, 10), 10: (15, 0), 11: (15, 50), 12: (16, 40),
    13: (18, 0), 14: (18, 50), 15: (19, 40), 16: (20, 30), 17: (21, 20)
}


def parse_schedule_robust_v2(text):
    if pd.isna(text): return []

    # 1. Tách các block thời gian
    blocks = re.split(r'(?=Từ \d{2}/\d{2}/\d{4})', str(text))
    parsed_data = []

    for block in blocks:
        if not block.strip(): continue

        # Tìm ngày bắt đầu/kết thúc
        date_range = re.search(r'Từ (\d{2}/\d{2}/\d{4}) đến (\d{2}/\d{2}/\d{4})', block)
        if not date_range: continue

        start_date = datetime.strptime(date_range.group(1), '%d/%m/%Y')
        end_date = datetime.strptime(date_range.group(2), '%d/%m/%Y')

        # 2. Duyệt từng dòng
        lines = block.split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.startswith("Từ"): continue

            # --- CẢI TIẾN REGEX ---
            # Cho phép phần "tại ..." là tùy chọn (optional)
            # Pattern: (Thứ/CN) ... tiết (số) ... [tại (địa điểm)]?
            match = re.search(r'(Thứ \d|Chủ nhật).*?tiết\s*([\d,]+)(?:.*?tại\s*(.*))?', line, re.IGNORECASE)

            if match:
                dow_str = match.group(1).lower()
                periods_str = match.group(2)

                # Lấy địa điểm (nếu không có thì để mặc định)
                location = match.group(3)
                if location:
                    location = location.strip()
                else:
                    location = "Chưa cập nhật địa điểm"

                # Map thứ
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
                        'start_date': start_date,
                        'end_date': end_date,
                        'dow': dow,
                        'periods': periods,
                        'location': location
                    })
    return parsed_data


def create_ics(file_path, output_path):
    # Đọc file (xử lý cả xls giả và csv)
    try:
        if file_path.endswith('.xls') or file_path.endswith('.xlsx'):
            # Cần cài: pip install xlrd openpyxl
            try:
                df = pd.read_excel(file_path, skiprows=9)
            except:
                # Nếu đuôi xls nhưng thực chất là csv (trường hợp của bạn)
                df = pd.read_csv(file_path, skiprows=9, encoding='utf-16', sep='\t')
        else:
            df = pd.read_csv(file_path, skiprows=9)
    except Exception as e:
        print(f"Lỗi đọc file ban đầu: {e}")
        # Thử fallback cuối cùng cho csv thông thường
        df = pd.read_csv(file_path, skiprows=9, encoding='utf-8')

    df.columns = df.columns.str.strip()
    c = Calendar()
    timezone = pytz.timezone('Asia/Ho_Chi_Minh')

    total_events = 0

    print("Đang xử lý...")
    for index, row in df.iterrows():
        subject_name = row.get('Tên học phần')
        raw_schedule = row.get('Thời gian địa điểm')

        if pd.isna(subject_name) or pd.isna(raw_schedule):
            continue

        schedules = parse_schedule_robust_v2(raw_schedule)

        for sched in schedules:
            current_date = sched['start_date']
            end_date = sched['end_date']

            while current_date <= end_date:
                if current_date.weekday() == sched['dow']:
                    periods = sorted(sched['periods'])
                    if not periods: continue

                    start_period = periods[0]
                    end_period = periods[-1]

                    if start_period in TIME_SLOTS:
                        h_start, m_start = TIME_SLOTS[start_period]
                        event_start = current_date.replace(hour=h_start, minute=m_start, second=0)

                        h_end_base, m_end_base = TIME_SLOTS.get(end_period, (h_start, m_start))
                        event_end_temp = current_date.replace(hour=h_end_base, minute=m_end_base, second=0)
                        event_end = event_end_temp + timedelta(minutes=45)

                        e = Event()
                        e.name = str(subject_name)
                        e.begin = timezone.localize(event_start)
                        e.end = timezone.localize(event_end)
                        e.location = sched['location']
                        e.description = f"Tiết: {','.join(map(str, periods))}\nLớp: {row.get('Lớp học phần', '')}"

                        c.events.add(e)
                        total_events += 1

                current_date += timedelta(days=1)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(c.serialize())

    return total_events


# --- CHẠY ---
if __name__ == "__main__":
    if not os.path.exists(INPUT_FILE):
        print(f"Không tìm thấy file: {INPUT_FILE}")
    else:
        try:
            count = create_ics(INPUT_FILE, OUTPUT_FILE)
            print(f"Thành công! Đã tạo {count} sự kiện (Expected: 64).")
            print(f"File lưu tại: {OUTPUT_FILE}")
        except Exception as e:
            print(f"Lỗi: {e}")