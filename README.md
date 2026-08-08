# [UDM_05] - [ Điều khiển và thực thi lệnh từ xa]

## Thành viên

| STT |      MSSV    |      Họ và tên      |         Vai trò         |
|---: |--------------|---------------------|-------------------------|
|  1  | 080206005119 | Nguyễn Minh Hưng    | Command Execution       |
|  2  | 075207013475 | Trần Minh Đức       | Client & GUI            |
|  3  | 2251120375   | Nguyễn Hoàng Phúc   | Architecture & Protocol |
|  4  | 082206002720 | Trần Ngọc Đăng Khoa | Server & Connection     |
|  5  | 049206000438 | Võ Văn Tùng         | Timeout & Error Handling|
|  6  | 075206021667 |Trần Đức Long       | Logging & Testing       |

## Giới thiệu

Ứng dụng cho phép người dùng kết nối đến một máy Client từ xa sau khi được người dùng tại máy đích cho phép. Khi đã kết nối thành công, người dùng có thể thực thi các lệnh cơ bản nằm trong danh sách cho phép, xem kết quả thực thi, thông báo lỗi và mã kết thúc ngay trên giao diện ứng dụng.

## Kiến trúc hệ thống

- Mô hình: Client–Server
- Protocol: TCP Socket
- Port mặc định: 5000 (có thể thay đổi)
- Cấu trúc message:  Sử dụng mô hình Request/Response, bao gồm các loại message cho yêu cầu kết nối, thực thi lệnh, trả kết quả và yêu cầu dừng lệnh.

## Yêu cầu môi trường

- Hệ điều hành: Windows 10/11
- Ngôn ngữ và phiên bản: Python 3.13
- GUI: Tkinter
- IDE: Visual Studio Code
- Dependency: Python Standard Library

## Cài đặt

1. Cài đặt môi trường
- Cài đặt Python 3.13.
- Cài đặt Visual Studio Code.
2. Clone project

Mở Terminal hoặc Git Bash và chạy:

git clone https://github.com/KaoKen22/UDM_05.git

Sau đó mở thư mục project bằng Visual Studio Code.

3. Kiểm tra Python

Mở Terminal và chạy:

python --version

Kết quả mong đợi:

Python 3.13.x
4. Chạy chương trình

Chạy Client hoặc Server theo hướng dẫn trong mục Hướng dẫn chạy.

    Project sử dụng các thư viện có sẵn trong Python Standard Library, không yêu cầu cài đặt thêm dependency bên ngoài.

## Hướng dẫn chạy

### Server

```text
Lệnh hoặc các bước chạy Server
```

### Client

```text
Lệnh hoặc các bước chạy Client
```

## Cấu hình

Mô tả cách thay đổi IP, port và các tham số mạng. Không ghi password hoặc secret vào repository.

## Chức năng

- [ ] Chức năng 1
- [ ] Chức năng 2
- [ ] Chức năng 3

## Kiểm thử

- Functional test:
- Test dữ liệu không hợp lệ:
- Test mất kết nối:
- Stress test:
- Performance test:

Bằng chứng kiểm thử lưu tại `Extra/`.

## Demo

- Video: [Public hoặc Unlisted URL]
- Slide: `PPTX/`
- Báo cáo: `DOCX/`

## Giới hạn

Liệt kê chức năng chưa hỗ trợ và giới hạn hiện tại của sản phẩm.(Sẽ cập nhật sau khi hoàn thành dự án.)
