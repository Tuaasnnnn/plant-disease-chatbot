"""
Chatbot nhận diện bệnh lá cây - PlantVillage (bản Streamlit)
Deploy trên Streamlit Community Cloud - chạy 24/7 miễn phí, ổn định.
"""

import os
import re
import json
import tempfile

import numpy as np
import requests
import streamlit as st
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image as keras_image
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

from disease_info import get_disease_info

# ============ Cấu hình trang ============
st.set_page_config(
    page_title="PlantDoc AI - Nhận diện bệnh lá cây",
    page_icon="🌱",
    layout="centered"
)

MODEL_PATH = "plant_disease_model.keras"
CLASS_NAMES_PATH = "class_names.json"
IMG_SIZE = (224, 224)
URL_REGEX = re.compile(r"(https?://\S+\.(?:jpg|jpeg|png|webp|bmp))", re.IGNORECASE)


# ============ Load model (cache để không load lại mỗi lần tương tác) ============
@st.cache_resource
def load_plant_model():
    model = load_model(MODEL_PATH)
    with open(CLASS_NAMES_PATH, "r", encoding="utf-8") as f:
        class_names = json.load(f)
    return model, class_names


model, class_names = load_plant_model()


# ============ Hàm xử lý ảnh & dự đoán ============
def download_image_from_url(url: str) -> str:
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    suffix = os.path.splitext(url.split("?")[0])[-1] or ".jpg"
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp_file.write(response.content)
    tmp_file.close()
    return tmp_file.name


def predict_image(img_path: str, top_k: int = 3):
    img = keras_image.load_img(img_path, target_size=IMG_SIZE)
    img_array = keras_image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)

    preds = model.predict(img_array, verbose=0)[0]
    top_indices = preds.argsort()[-top_k:][::-1]
    return [(class_names[i], float(preds[i])) for i in top_indices]


CONFIDENCE_THRESHOLD = 0.60  # Dưới ngưỡng này, cảnh báo model không chắc chắn


def format_reply(results):
    top1_class, top1_conf = results[0]
    info = get_disease_info(top1_class)
    is_healthy = "healthy" in top1_class.lower()

    # Cảnh báo khi độ tin cậy thấp — có thể ảnh không thuộc 14 loại cây model được huấn luyện
    if top1_conf < CONFIDENCE_THRESHOLD:
        reply = (
            f"⚠️ **Mình không đủ tự tin để xác định chính xác** (độ tin cậy chỉ {top1_conf*100:.1f}%, "
            f"dự đoán gần nhất là \"{info['ten_viet']}\").\n\n"
            "Nguyên nhân có thể là:\n"
            "- Ảnh chụp không phải lá cây, hoặc chụp không rõ/quá xa/quá mờ\n"
            "- Cây trong ảnh **không thuộc 14 loại cây** mà mình được huấn luyện nhận diện: "
            "táo, việt quất, cherry, ngô, nho, cam, đào, ớt chuông, khoai tây, mâm xôi, "
            "đậu tương, bí, dâu tây, cà chua\n"
            "- Ảnh chụp góc/ánh sáng khác nhiều so với dữ liệu huấn luyện\n\n"
            "💡 Bạn thử chụp lại rõ nét hơn, cận cảnh lá cây, hoặc nếu đây là loại cây ngoài "
            "danh sách trên thì kết quả sẽ không đáng tin cậy — nên tham khảo thêm nguồn khác "
            "hoặc chuyên gia nông nghiệp nhé.\n\n"
            "---\n_Lưu ý: đây là công cụ hỗ trợ tham khảo dựa trên AI, "
            "không thay thế chẩn đoán của chuyên gia nông nghiệp/bảo vệ thực vật._"
        )
        return reply

    reply = f"🔍 **Kết quả nhận diện:** {info['ten_viet']}\n\n"
    reply += f"📊 **Độ tin cậy:** {top1_conf*100:.1f}%\n\n"

    if is_healthy:
        reply += "✅ Lá cây có vẻ khỏe mạnh, không phát hiện dấu hiệu bệnh rõ ràng.\n\n"
        reply += f"💡 **Lời khuyên:** {info['cach_xu_ly']}"
    else:
        reply += f"🦠 **Nguyên nhân:** {info['nguyen_nhan']}\n\n"
        reply += f"🩺 **Triệu chứng điển hình:** {info['trieu_chung']}\n\n"
        reply += f"💊 **Cách xử lý gợi ý:** {info['cach_xu_ly']}"

    if len(results) > 1:
        second_class, second_conf = results[1]
        if second_conf > 0.15 and (top1_conf - second_conf) < 0.35:
            second_info = get_disease_info(second_class)
            reply += (
                f"\n\n⚠️ *Lưu ý: ảnh cũng có nét giống với "
                f"\"{second_info['ten_viet']}\" ({second_conf*100:.1f}%). "
                f"Nếu triệu chứng thực tế không khớp, bạn nên chụp thêm ảnh rõ nét hơn "
                f"hoặc tham khảo ý kiến chuyên gia nông nghiệp.*"
            )

    reply += (
        "\n\n---\n_Lưu ý: đây là công cụ hỗ trợ tham khảo dựa trên AI, "
        "không thay thế chẩn đoán của chuyên gia nông nghiệp/bảo vệ thực vật._"
    )
    return reply


def handle_user_input(image_path=None, url_text=None):
    """Xử lý 1 lượt hỏi-đáp, trả về (user_display, bot_reply, image_to_show)."""
    img_path = None
    temp_to_cleanup = None

    try:
        if image_path is not None:
            img_path = image_path
        elif url_text:
            url_match = URL_REGEX.search(url_text)
            if url_match:
                img_path = download_image_from_url(url_match.group(1))
                temp_to_cleanup = img_path

        if img_path is None:
            return "❌ Mình không tìm thấy ảnh hợp lệ. Vui lòng upload ảnh hoặc dán link ảnh kết thúc bằng .jpg/.png..."

        results = predict_image(img_path)
        return format_reply(results)

    except requests.exceptions.RequestException:
        return "❌ Mình không tải được ảnh từ link đó. Kiểm tra lại link (phải là link ảnh trực tiếp) hoặc thử upload ảnh trực tiếp nhé."
    except Exception as e:
        return f"❌ Có lỗi khi xử lý ảnh: {str(e)}"
    finally:
        if temp_to_cleanup and os.path.exists(temp_to_cleanup):
            os.remove(temp_to_cleanup)


# ============ Giao diện chat ============
st.title("🌱 PlantDoc AI")
st.caption(
    "Chatbot nhận diện bệnh lá cây — huấn luyện trên bộ PlantVillage (38 loại cây/bệnh) "
    "bằng MobileNetV2 (transfer learning)."
)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {
            "role": "assistant",
            "content": (
                "👋 Chào bạn! Mình là bot nhận diện bệnh trên lá cây.\n\n"
                "Bạn có thể **upload ảnh** ở khung bên dưới, hoặc **dán link ảnh** vào ô chat. "
                "Mình sẽ phân tích và cho bạn biết cây có bị bệnh không, nguyên nhân và cách xử lý!"
            ),
            "image": None,
        }
    ]

# Hiển thị lịch sử chat
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        if msg.get("image") is not None:
            st.image(msg["image"], width=250)
        st.markdown(msg["content"])

# Khu vực upload ảnh (nằm trên khung chat để dễ thao tác trên mobile)
uploaded_file = st.file_uploader(
    "📎 Upload ảnh lá cây (hoặc dán link ảnh vào ô chat bên dưới)",
    type=["jpg", "jpeg", "png", "webp"],
    key="uploader"
)

user_text = st.chat_input("Dán link ảnh vào đây, hoặc để trống nếu đã upload ảnh ở trên rồi bấm Enter...")

# Xử lý khi có upload ảnh mới hoặc người dùng gửi tin nhắn
trigger = False
image_path_to_use = None
display_image = None

if uploaded_file is not None and st.session_state.get("last_uploaded") != uploaded_file.name:
    st.session_state.last_uploaded = uploaded_file.name
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[-1])
    tmp.write(uploaded_file.getvalue())
    tmp.close()
    image_path_to_use = tmp.name
    display_image = uploaded_file
    trigger = True
elif user_text:
    trigger = True
    display_image = None

if trigger:
    user_msg_text = user_text if user_text else "(đã upload ảnh)"
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_msg_text,
        "image": display_image,
    })
    with st.chat_message("user"):
        if display_image is not None:
            st.image(display_image, width=250)
        st.markdown(user_msg_text)

    with st.chat_message("assistant"):
        with st.spinner("Đang phân tích ảnh..."):
            reply = handle_user_input(image_path=image_path_to_use, url_text=user_text)
        st.markdown(reply)

    st.session_state.chat_history.append({
        "role": "assistant",
        "content": reply,
        "image": None,
    })

    if image_path_to_use and os.path.exists(image_path_to_use):
        os.remove(image_path_to_use)
