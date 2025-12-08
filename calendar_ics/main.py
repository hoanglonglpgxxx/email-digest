import pandas as pd
from ics import Calendar, Event
from datetime import datetime, timedelta
import re
import pytz

# Cấu hình giờ học (Theo khung giờ phổ biến của KMA)
# Format: Tiết: (Giờ bắt đầu, Phút bắt đầu)
# Lưu ý: Đây là giờ giả định chuẩn, có thể lệch 5-10p tùy quy định cụ thể từng năm
TIME_SLOTS = {
    1: (7, 0), 2: (7, 50), 3: (8, 40), 4: (9, 35), 5: (10, 25), 6: (11, 15),
    7: (12, 30), 8: (13, 20), 9: (14, 10), 10: (15, 0), 11: (15, 50), 12: (16, 40),
    13: (18, 0), 14: (18, 50), 15: (19, 40), 16: (20, 30), 17: (21, 20)
}

DAY_MAPPING = {
    'Thứ 2': 0, 'Thứ 3': 1, 'Thứ 4': 2, 'Thứ 5': 3,
    'Thứ 6': 4, 'Thứ 7': 5, 'Chủ nhật': 6
}


def parse_schedule_text(text):
    """
    Phân tích chuỗi thời gian địa điểm phức tạp.
    Ví dụ: "Từ 08/12/2025 đến 08/02/2026:\n Thứ 7 tiết 1,2,3,4,5 tại 102-TA1..."
    """
    if pd.isna(text):
        return []

    # Tách các khối thời gian (nếu môn học có nhiều đợt học)
    # Pattern: Tìm chuỗi "Từ dd/mm/yyyy"
    blocks = re.split(r'(?=Từ \d{2}/\d{2}/\d{4})', text)
    parsed_data = []

    for block in blocks:
        if not block.strip():
            continue

        # Lấy ngày bắt đầu và kết thúc
        date_range = re.search(r'Từ (\d{2}/\d{2}/\d{4}) đến (\d{2}/\d{2}/\d{4})', block)
        if not date_range:
            continue

        start_date = datetime.strptime(date_range.group(1), '%d/%m/%Y')
        end_date = datetime.strptime(date_range.group(2), '%d/%m/%Y')

        # Lấy thứ, tiết, phòng
        # Regex tìm: Thứ X (hoặc Chủ nhật) ... tiết 1,2,3 ... tại ABC
        schedule_info = re.search(r'(Thứ \d|Chủ nhật).*?tiết\s*([\d,]+).*?tại\s*(.*)', block, re.DOTALL)

        if schedule_info:
            dow_str = schedule_info.group(1)
            periods_str = schedule_info.group(2)
            location = schedule_info.group(3).strip()

            dow = DAY_MAPPING.get(dow_str)
            periods = [int(p) for p in periods_str.split(',') if p.isdigit()]

            if periods:
                parsed_data.append({
                    'start_date': start_date,
                    'end_date': end_date,
                    'dow': dow,
                    'periods': periods,
                    'location': location
                })
    return parsed_data


def create_ics(file_path, output_path):
    # Kiểm tra đuôi file để dùng hàm đọc phù hợp
    if file_path.endswith('.xls') or file_path.endswith('.xlsx'):
        # Nếu là file Excel, dùng read_excel
        # Cần cài thư viện: pip install xlrd openpyxl
        df = pd.read_excel(file_path, skiprows=9)
    else:
        # Nếu là file CSV, thử các encoding phổ biến của Excel
        try:
            df = pd.read_csv(file_path, skiprows=9, encoding='utf-8')
        except UnicodeDecodeError:
            # File CSV từ Excel tiếng Việt thường dùng utf-16
            df = pd.read_csv(file_path, skiprows=9, encoding='utf-16', sep='\t')

    # Xóa khoảng trắng ở tên cột
    df.columns = df.columns.str.strip()

    c = Calendar()
    timezone = pytz.timezone('Asia/Ho_Chi_Minh')

    for index, row in df.iterrows():
        subject_name = row['Tên học phần']
        raw_schedule = row['Thời gian địa điểm']

        # Bỏ qua nếu không có tên môn hoặc lịch
        if pd.isna(subject_name) or pd.isna(raw_schedule):
            continue

        schedules = parse_schedule_text(raw_schedule)

        for sched in schedules:
            current_date = sched['start_date']
            end_date = sched['end_date']

            # Duyệt qua từng ngày trong khoảng thời gian
            while current_date <= end_date:
                if current_date.weekday() == sched['dow']:
                    # Xác định giờ bắt đầu và kết thúc
                    periods = sorted(sched['periods'])
                    if not periods: continue

                    start_period = periods[0]
                    end_period = periods[-1]

                    if start_period in TIME_SLOTS:
                        h_start, m_start = TIME_SLOTS[start_period]
                        event_start = current_date.replace(hour=h_start, minute=m_start, second=0)

                        h_end_base, m_end_base = TIME_SLOTS[end_period]
                        event_end_temp = current_date.replace(hour=h_end_base, minute=m_end_base, second=0)
                        event_end = event_end_temp + timedelta(minutes=45)

                        # Tạo Event
                        e = Event()
                        e.name = str(subject_name)
                        e.begin = timezone.localize(event_start)
                        e.end = timezone.localize(event_end)
                        e.location = sched['location']
                        e.description = f"Tiết: {','.join(map(str, periods))}\nLớp: {row.get('Lớp học phần', '')}"

                        c.events.add(e)

                current_date += timedelta(days=1)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(c.serialize())

    return output_path

input_csv = "ThoiKhoaBieuSinhVien.xls"
output_ics = "ThoiKhoaBieu_KMA.ics"

try:
    create_ics(input_csv, output_ics)
    print("Success")
except Exception as e:
    print(f"Error: {e}")