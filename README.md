# Simple crawling data app using `newsdata.io` API and python
# Sample abt Flask and routing
# Simple weather forecast
# Handle natural language
# Multi func tool: convert files to other ext, zip, unzip files, ...
VIDEO 1 DAY 36
## NOTE LẠI
- List Comprehension 
- Trong Python, List Comprehension là cách ngắn gọn để tạo danh sách mới bằng cách lặp qua một danh sách hoặc iterable khác. Cú pháp cơ bản là:

````python
new_list = [expression for item in iterable]
````
Trong đoạn code bạn đưa ra:

````python
    dates = [temp['date'] for temp in forecasts]
````

- forecasts là một list gồm các dictionary (giả sử mỗi dictionary chứa thông tin về dự báo thời tiết).
- temp['date'] là giá trị của key 'date' trong mỗi dictionary temp bên trong forecasts.
- [temp['date'] for temp in forecasts] sẽ tạo một danh sách mới chứa tất cả các giá trị 'date' từ mỗi dictionary trong forecasts.
Nói cách khác, dòng code này sẽ duyệt qua từng phần tử (dictionary) trong forecasts và lấy giá trị của key 'date' rồi lưu tất cả các giá trị đó vào danh sách dates.


| Python         | JS                                          | Desc                                                                 |
|----------------|---------------------------------------------|----------------------------------------------------------------------|
| `list`         | `array`                                     | Danh sách chứa các phần tử có thể lặp lại, có thứ tự.                |
| `dict`         | `object`                                    | Cặp `key value`, dùng để lưu trữ và truy xuất dữ liệu dựa trên khóa. |
| `tuple`        | Không có (hoặc `array` với `Object.freeze`) | Giống list, nhưng không thể thay đổi sau khi tạo.                    |
| `set`          | Không có trực tiếp (có thể dùng `Set`)      | Tập hợp các phần tử duy nhất, không có thứ tự.                       |
| `str `         | `string`                                    | Chuỗi ký tự không thay đổi.                                          |
| `None`         | `null`                                      | Đại diện cho giá trị không tồn tại hoặc giá trị rỗng.                |
| `True`/`False` | `true`/`false`                               | Giá trị boolean cho đúng/sai.                                        |

- `dictionary comprehension`