# Quy trình Build và Phân phối Ứng dụng

Đây là tài liệu ghi chú nhanh về quy trình mã hóa file cấu hình và phân phối ứng dụng cho người dùng cuối.

---

### PHẦN 1: Dành cho Developer (Khi cần cập nhật và build ứng dụng)

Mỗi khi bạn thay đổi thông tin trong `database_config.ini` hoặc cần tạo lại file mã hóa, hãy làm theo các bước sau:

1.  **Chuẩn bị file cấu hình:**
    *   Mở và chỉnh sửa file `database_config.ini` với các thông tin database chính xác.

2.  **Chạy Script mã hóa:**
    *   Mở Terminal trong thư mục gốc của dự án.
    *   Thực thi lệnh:
        ```bash
        python encrypt_config.py
        ```

3.  **Nhập mật khẩu:**
    *   Script sẽ yêu cầu bạn nhập một mật khẩu. Hãy nhập một mật khẩu đủ mạnh và **ghi nhớ nó**. Mật khẩu này chính là "chìa khóa" để người dùng cuối có thể truy cập ứng dụng.

4.  **Kiểm tra kết quả:**
    *   Một file mới tên là `config.encrypted` sẽ được tạo ra. Đây chính là file cấu hình đã được mã hóa.

---

### PHẦN 4: Build ứng dụng (.exe)

Sau khi chuẩn bị file cấu hình mã hóa, bạn có thể build ứng dụng thành file `.exe` để phân phối.

1.  **Cài đặt PyInstaller (nếu chưa có):**
    ```bash
    pip install pyinstaller
    ```

2.  **Chạy lệnh build:**
    *   Mở Terminal trong thư mục gốc của dự án.
    *   Thực thi lệnh sau:
        ```bash
        pyinstaller --onefile --windowed --name "CTS_Tool_Client" main.py
        ```
    *   Lệnh này sẽ tạo ra một file `.exe` duy nhất trong thư mục `dist/` với tên `CTS_Tool_Client.exe`.

---

### PHẦN 2: Dành cho Việc Phân phối (Gửi cho người dùng)

Sau khi bạn đã build ứng dụng thành công (tạo ra file `.exe`), bạn sẽ gửi cho người dùng cuối **CHỈ 2 FILE**:

1.  File thực thi của ứng dụng (ví dụ: `app.exe`)
2.  File cấu hình đã mã hóa: `config.encrypted`

**TUYỆT ĐỐI KHÔNG GỬI** các file sau:
*   `database_config.ini` (file cấu hình gốc)
*   `encrypt_config.py` (script mã hóa)
*   Các file mã nguồn `.py` khác.

---

### PHẦN 3: Hướng dẫn cho Người dùng cuối

Khi người dùng cuối chạy ứng dụng, họ sẽ cần:

1.  Chạy file `.exe`.
2.  Nhập **System Name** (Tên hệ thống) mà họ muốn kết nối.
3.  Nhập **Password** (chính là mật khẩu bạn đã dùng ở PHẦN 1, BƯỚC 3).

Nếu mật khẩu chính xác, ứng dụng sẽ giải mã file cấu hình và kết nối thành công.
