# 🌱 PlantDoc AI — Deploy lên Streamlit Community Cloud

Cách này cho link **chạy 24/7 thật sự, miễn phí, không lo sập** — phù hợp để nộp cho ban giám khảo xem tới Chủ nhật.

## Điểm khác biệt quan trọng
Streamlit Cloud deploy từ **GitHub repository**, không upload file trực tiếp như Hugging Face.
Vì vậy cần tạo GitHub repo trước.

---

## Bước 1 — Tải file model từ Kaggle
Từ notebook Kaggle (bản đã Commit), vào tab **Output**, tải về:
- `plant_disease_model.keras`
- `class_names.json`

## Bước 2 — Tạo tài khoản GitHub (nếu chưa có)
Vào https://github.com/join, đăng ký miễn phí (không cần thẻ).

## Bước 3 — Tạo repository mới
1. Vào https://github.com/new
2. Đặt tên repo, ví dụ: `plant-disease-chatbot`
3. Chọn **Public**
4. Bấm **Create repository**

## Bước 4 — Upload file lên GitHub (không cần dùng dòng lệnh git)
Trong trang repo vừa tạo:
1. Bấm **"Add file" → "Upload files"**
2. Kéo thả toàn bộ các file sau vào:
   - `app_streamlit.py` (đổi tên thành `app.py` khi upload, hoặc giữ nguyên tên đều được — chỉ cần nhớ đúng tên khi cấu hình ở Bước 6)
   - `disease_info.py`
   - `requirements_streamlit.txt` (đổi tên thành `requirements.txt`)
   - `plant_disease_model.keras`
   - `class_names.json`
3. Bấm **Commit changes**

> ⚠️ **Nếu GitHub báo lỗi file quá lớn** (model thường vài chục MB, giới hạn thường của web upload là ~25MB/lần,
> giới hạn repo thường là 100MB/file): thử upload riêng model là 1 lần duy nhất, hoặc nếu vẫn lỗi,
> nói cho mình biết dung lượng file `plant_disease_model.keras` để mình hướng dẫn nén/chuyển định dạng nhẹ hơn (`.h5` + quantization).

## Bước 5 — Đăng ký Streamlit Community Cloud
1. Vào https://share.streamlit.io
2. Bấm **Sign up / Continue with GitHub** — đăng nhập bằng chính tài khoản GitHub vừa tạo
3. Cho phép Streamlit truy cập vào repository của bạn khi được hỏi quyền

## Bước 6 — Tạo app mới
1. Bấm **"New app"**
2. Chọn:
   - **Repository:** `<username>/plant-disease-chatbot`
   - **Branch:** `main`
   - **Main file path:** `app_streamlit.py` (hoặc `app.py` nếu bạn đã đổi tên ở Bước 4)
3. Bấm **Deploy**

## Bước 7 — Đợi build (2-5 phút)
Streamlit sẽ tự cài `requirements.txt` và chạy app. Khi xong, bạn có link public dạng:
```
https://<tên-app>-<random>.streamlit.app
```

Gửi link này cho ban giám khảo — **chạy ổn định 24/7**, ai cũng mở được, không cần cài gì.

---

## Lưu ý về giới hạn free tier của Streamlit Cloud
- App sẽ tự "ngủ" (sleep) nếu không có ai truy cập trong ~vài ngày — nhưng chỉ cần bấm vào link,
  app tự "thức dậy" sau khoảng 30-60 giây, hoàn toàn bình thường cho việc chấm điểm
- RAM giới hạn ~1GB cho free tier — model MobileNetV2 nhẹ nên chạy tốt, không lo vấn đề này

## Nếu build bị lỗi
Vào tab **"Manage app" → "Logs"** trên Streamlit Cloud để xem lỗi cụ thể, copy gửi cho mình để debug tiếp.
