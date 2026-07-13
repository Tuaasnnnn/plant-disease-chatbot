"""
Chatbot nhận diện bệnh lá cây - PlantVillage (bản Streamlit)
Deploy trên Streamlit Community Cloud - chạy 24/7 miễn phí, ổn định.
"""

import os
import re
import json
import csv
import tempfile
from datetime import datetime

import numpy as np
import requests
import streamlit as st
import tensorflow as tf
import matplotlib.cm as cm
from PIL import Image
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image as keras_image
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

from disease_info import get_disease_info

FEEDBACK_LOG_PATH = "feedback_log.csv"


def log_feedback(pred_class: str, confidence: float, feedback_value: str):
    """Ghi lại phản hồi đúng/sai của người dùng để dùng cho việc huấn luyện lại sau này."""
    is_new = not os.path.exists(FEEDBACK_LOG_PATH)
    try:
        with open(FEEDBACK_LOG_PATH, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if is_new:
                writer.writerow(["timestamp", "predicted_class", "confidence", "feedback"])
            writer.writerow([datetime.now().isoformat(), pred_class, f"{confidence:.4f}", feedback_value])
    except Exception:
        pass  # Không để lỗi ghi log làm gián đoạn trải nghiệm chat

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
import ipaddress
import socket
from urllib.parse import urlparse

MAX_IMAGE_BYTES = 8 * 1024 * 1024  # Giới hạn 8MB cho ảnh tải từ URL


def is_safe_url(url: str) -> bool:
    """Chặn URL trỏ tới địa chỉ IP nội bộ/private (chống SSRF)."""
    try:
        hostname = urlparse(url).hostname
        if not hostname:
            return False
        if hostname.lower() in ("localhost",):
            return False
        ip = socket.gethostbyname(hostname)
        ip_obj = ipaddress.ip_address(ip)
        if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_reserved:
            return False
        return True
    except Exception:
        return False


def download_image_from_url(url: str) -> str:
    if not is_safe_url(url):
        raise ValueError("URL không hợp lệ hoặc trỏ tới địa chỉ không được phép.")

    response = requests.get(url, timeout=8, stream=True)
    response.raise_for_status()

    content_length = response.headers.get("Content-Length")
    if content_length and int(content_length) > MAX_IMAGE_BYTES:
        raise ValueError("Ảnh quá lớn (giới hạn 8MB).")

    suffix = os.path.splitext(url.split("?")[0])[-1] or ".jpg"
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)

    total = 0
    for chunk in response.iter_content(chunk_size=8192):
        total += len(chunk)
        if total > MAX_IMAGE_BYTES:
            tmp_file.close()
            os.remove(tmp_file.name)
            raise ValueError("Ảnh quá lớn (giới hạn 8MB).")
        tmp_file.write(chunk)

    tmp_file.close()
    return tmp_file.name


def predict_image(img_path: str, top_k: int = 3):
    img = keras_image.load_img(img_path, target_size=IMG_SIZE)
    img_array = keras_image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    preprocessed = preprocess_input(img_array.copy())

    preds = model.predict(preprocessed, verbose=0)[0]
    top_indices = preds.argsort()[-top_k:][::-1]
    results = [(class_names[i], float(preds[i])) for i in top_indices]
    return results, img, preprocessed


# Layer cuối cùng của phần tích chập trong MobileNetV2 (trước GlobalAveragePooling) — dùng cho Grad-CAM
GRADCAM_LAYER_NAME = "out_relu"


def generate_gradcam(preprocessed_img, pred_index, original_img_pil, alpha=0.45):
    """Sinh ảnh heatmap Grad-CAM chồng lên ảnh gốc, cho thấy vùng model tập trung để ra quyết định."""
    try:
        grad_model = tf.keras.models.Model(
            [model.inputs], [model.get_layer(GRADCAM_LAYER_NAME).output, model.output]
        )

        with tf.GradientTape() as tape:
            conv_outputs, predictions = grad_model(preprocessed_img)
            class_channel = predictions[:, pred_index]

        grads = tape.gradient(class_channel, conv_outputs)
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
        conv_outputs = conv_outputs[0]
        heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
        heatmap = tf.squeeze(heatmap)
        heatmap = tf.maximum(heatmap, 0) / (tf.math.reduce_max(heatmap) + 1e-8)
        heatmap = heatmap.numpy()

        # Tô màu heatmap (colormap "jet") và chồng lên ảnh gốc
        heatmap_uint8 = np.uint8(255 * heatmap)
        jet = cm.get_cmap("jet")
        jet_colors = jet(np.arange(256))[:, :3]
        jet_heatmap = jet_colors[heatmap_uint8]
        jet_heatmap = np.uint8(jet_heatmap * 255)

        heatmap_img = Image.fromarray(jet_heatmap).resize(original_img_pil.size)
        base_img = original_img_pil.convert("RGB")
        overlay = Image.blend(base_img, heatmap_img, alpha)
        return overlay
    except Exception:
        return None


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


CARE_KEYWORDS = ["chăm sóc", "cách trị", "cách xử lý", "làm sao", "phải làm gì", "chữa", "điều trị", "khắc phục"]
BUY_KEYWORDS = ["mua thuốc", "mua ở đâu", "loại thuốc", "thuốc gì", "sản phẩm nào", "mua gì"]
GREETING_KEYWORDS = ["chào", "hello", "hi ", "bạn là ai", "giúp được gì"]


def answer_general_question(text: str) -> str:
    """Trả lời câu hỏi dạng chữ, dựa trên bệnh vừa chẩn đoán gần nhất (nếu có)."""
    text_lower = text.lower()
    last = st.session_state.get("last_diagnosis")

    if any(kw in text_lower for kw in GREETING_KEYWORDS):
        return (
            "👋 Chào bạn! Mình là PlantDoc AI. Bạn có thể:\n"
            "- 📎 Upload ảnh lá cây để mình chẩn đoán bệnh\n"
            "- 💬 Hoặc hỏi mình về cách chăm sóc/mua thuốc cho bệnh vừa được chẩn đoán"
        )

    if any(kw in text_lower for kw in CARE_KEYWORDS):
        if last:
            return (
                f"🩺 **Cách chăm sóc/xử lý cho \"{last['ten_viet']}\":**\n\n"
                f"{last['cach_xu_ly']}\n\n"
                "_Lưu ý: đây là gợi ý tham khảo từ AI, mức độ nặng nhẹ thực tế nên được "
                "chuyên gia nông nghiệp đánh giá trực tiếp._"
            )
        return (
            "Bạn muốn hỏi cách chăm sóc cho bệnh nào vậy? Bạn upload ảnh lá cây để mình "
            "chẩn đoán trước, sau đó mình sẽ tư vấn cách xử lý cụ thể cho đúng bệnh đó nhé."
        )

    if any(kw in text_lower for kw in BUY_KEYWORDS):
        if last:
            return (
                f"💊 Với **\"{last['ten_viet']}\"**, hướng xử lý gợi ý là:\n\n"
                f"{last['cach_xu_ly']}\n\n"
                "Bạn có thể tìm mua các loại thuốc bảo vệ thực vật phù hợp tại **cửa hàng "
                "vật tư nông nghiệp** gần nhà, hoặc các sàn TMĐT có bán vật tư nông nghiệp uy tín. "
                "Nên mang theo ảnh lá bệnh khi đi mua để nhân viên tư vấn đúng loại thuốc, "
                "và đọc kỹ hướng dẫn sử dụng/liều lượng trên bao bì.\n\n"
                "_Lưu ý: mình không thể tư vấn tên thuốc thương mại cụ thể, vì điều này cần "
                "chuyên gia đánh giá tình trạng thực tế của cây._"
            )
        return (
            "Bạn muốn mua thuốc cho bệnh nào? Upload ảnh lá cây để mình chẩn đoán trước nhé, "
            "sau đó mình sẽ gợi ý hướng xử lý phù hợp."
        )

    # Không khớp intent nào rõ ràng
    return (
        "🤔 Mình chưa hiểu rõ câu hỏi này. Mình có thể giúp:\n"
        "- 📎 Chẩn đoán bệnh từ ảnh lá cây (upload ảnh hoặc dán link ảnh)\n"
        "- 💬 Tư vấn cách chăm sóc/xử lý cho bệnh vừa chẩn đoán (hỏi \"cách chăm sóc thế nào\")\n"
        "- 💊 Gợi ý hướng mua thuốc phù hợp (hỏi \"nên mua thuốc gì\")\n\n"
        "Bạn thử hỏi lại theo 1 trong các hướng trên nhé!"
    )


def handle_user_input(image_path=None, url_text=None):
    """Xử lý 1 lượt hỏi-đáp, trả về (bot_reply, heatmap_image_hoặc_None)."""
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
            return "❌ Mình không tìm thấy ảnh hợp lệ. Vui lòng upload ảnh hoặc dán link ảnh kết thúc bằng .jpg/.png...", None

        results, original_img, preprocessed = predict_image(img_path)
        top1_class, top1_conf = results[0]

        # Lưu lại để hiện nút phản hồi 👍/👎 sau khi trả lời xong
        st.session_state.pending_feedback = {"class": top1_class, "confidence": top1_conf}

        heatmap_img = None
        if top1_conf >= CONFIDENCE_THRESHOLD:
            st.session_state.last_diagnosis = get_disease_info(top1_class)
            top1_index = class_names.index(top1_class)
            heatmap_img = generate_gradcam(preprocessed, top1_index, original_img)

        return format_reply(results), heatmap_img

    except ValueError as e:
        return f"❌ {str(e)} Bạn thử upload ảnh trực tiếp thay vì dùng link nhé.", None
    except requests.exceptions.RequestException:
        return "❌ Mình không tải được ảnh từ link đó. Kiểm tra lại link (phải là link ảnh trực tiếp) hoặc thử upload ảnh trực tiếp nhé.", None
    except Exception as e:
        return f"❌ Có lỗi khi xử lý ảnh: {str(e)}", None
    finally:
        if temp_to_cleanup and os.path.exists(temp_to_cleanup):
            os.remove(temp_to_cleanup)


# ============ Giao diện chat ============
st.title("🌱 PlantDoc AI")
st.caption(
    "Chatbot nhận diện bệnh lá cây — huấn luyện trên bộ PlantVillage (38 loại cây/bệnh) "
    "bằng MobileNetV2 (transfer learning)."
)

if "last_diagnosis" not in st.session_state:
    st.session_state.last_diagnosis = None

if "pending_feedback" not in st.session_state:
    st.session_state.pending_feedback = None

# Sidebar: cho phép tải log phản hồi (dùng để huấn luyện lại model sau này)
with st.sidebar:
    st.markdown("### 📋 Dữ liệu phản hồi")
    st.caption("Log các lượt đánh giá 👍/👎 của người dùng, dùng để cải thiện model trong tương lai.")
    if os.path.exists(FEEDBACK_LOG_PATH):
        with open(FEEDBACK_LOG_PATH, "rb") as f:
            st.download_button("⬇️ Tải feedback_log.csv", f, file_name="feedback_log.csv", mime="text/csv")
    else:
        st.caption("_Chưa có phản hồi nào._")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {
            "role": "assistant",
            "content": (
                "👋 Chào bạn! Mình là bot nhận diện bệnh trên lá cây.\n\n"
                "Bạn có thể:\n"
                "- 📎 **Upload ảnh** lá cây ở khung bên dưới, hoặc **dán link ảnh** vào ô chat\n"
                "- 💬 **Hỏi thêm bằng chữ** sau khi có kết quả, ví dụ: \"cách chăm sóc thế nào\", "
                "\"nên mua thuốc gì\"\n"
                "- 🔥 Mình sẽ kèm ảnh **Grad-CAM** cho thấy vùng lá mà AI tập trung để ra kết luận\n\n"
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

user_text = st.chat_input(
    "Dán link ảnh, hỏi cách chăm sóc/mua thuốc, hoặc để trống nếu đã upload ảnh ở trên rồi bấm Enter..."
)

# Xử lý khi có upload ảnh mới hoặc người dùng gửi tin nhắn
trigger = False
image_path_to_use = None
display_image = None

if uploaded_file is not None and st.session_state.get("last_uploaded") != uploaded_file.name:
    if uploaded_file.size > MAX_IMAGE_BYTES:
        st.error(f"⚠️ Ảnh quá lớn ({uploaded_file.size/1024/1024:.1f}MB). Giới hạn 8MB, vui lòng chọn ảnh nhỏ hơn.")
    else:
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
        has_image_url = bool(user_text and URL_REGEX.search(user_text))
        heatmap_img = None
        if image_path_to_use is None and not has_image_url:
            # Không có ảnh/link ảnh -> đây là câu hỏi bằng chữ (chăm sóc, mua thuốc...)
            with st.spinner("Đang suy nghĩ..."):
                reply = answer_general_question(user_text)
        else:
            with st.spinner("Đang phân tích ảnh..."):
                reply, heatmap_img = handle_user_input(image_path=image_path_to_use, url_text=user_text)
        st.markdown(reply)
        if heatmap_img is not None:
            st.image(
                heatmap_img,
                width=250,
                caption="🔥 Vùng ảnh AI tập trung để đưa ra kết luận (Grad-CAM)"
            )

    # Hiện nút đánh giá 👍/👎 cho lần chẩn đoán gần nhất

if st.session_state.pending_feedback is not None:

    pf = st.session_state.pending_feedback

    st.divider()

    col1, col2 = st.columns([4, 1])

    with col1:
        st.caption(
            f'Kết quả "{get_disease_info(pf["class"])["ten_viet"]}" có chính xác không?'
        )

    with col2:
        fb = st.feedback(
            "thumbs",
            key=f"fb_{len(st.session_state.chat_history)}"
        )

        if fb is not None:

            log_feedback(
                pf["class"],
                pf["confidence"],
                "positive" if fb == 1 else "negative"
            )

            st.session_state.pending_feedback = None

            st.success(
                "Cảm ơn phản hồi của bạn! 🙏",
                icon="✅"
            )
        )
"""
Chatbot nhận diện bệnh lá cây - PlantVillage (bản Streamlit)
Deploy trên Streamlit Community Cloud - chạy 24/7 miễn phí, ổn định.
"""

import os
import re
import json
import csv
import tempfile
from datetime import datetime

import numpy as np
import requests
import streamlit as st
import tensorflow as tf
import matplotlib.cm as cm
from PIL import Image
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image as keras_image
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

from disease_info import get_disease_info

FEEDBACK_LOG_PATH = "feedback_log.csv"


def log_feedback(pred_class: str, confidence: float, feedback_value: str):
    """Ghi lại phản hồi đúng/sai của người dùng để dùng cho việc huấn luyện lại sau này."""
    is_new = not os.path.exists(FEEDBACK_LOG_PATH)
    try:
        with open(FEEDBACK_LOG_PATH, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if is_new:
                writer.writerow(["timestamp", "predicted_class", "confidence", "feedback"])
            writer.writerow([datetime.now().isoformat(), pred_class, f"{confidence:.4f}", feedback_value])
    except Exception:
        pass  # Không để lỗi ghi log làm gián đoạn trải nghiệm chat

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
import ipaddress
import socket
from urllib.parse import urlparse

MAX_IMAGE_BYTES = 8 * 1024 * 1024  # Giới hạn 8MB cho ảnh tải từ URL


def is_safe_url(url: str) -> bool:
    """Chặn URL trỏ tới địa chỉ IP nội bộ/private (chống SSRF)."""
    try:
        hostname = urlparse(url).hostname
        if not hostname:
            return False
        if hostname.lower() in ("localhost",):
            return False
        ip = socket.gethostbyname(hostname)
        ip_obj = ipaddress.ip_address(ip)
        if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_reserved:
            return False
        return True
    except Exception:
        return False


def download_image_from_url(url: str) -> str:
    if not is_safe_url(url):
        raise ValueError("URL không hợp lệ hoặc trỏ tới địa chỉ không được phép.")

    response = requests.get(url, timeout=8, stream=True)
    response.raise_for_status()

    content_length = response.headers.get("Content-Length")
    if content_length and int(content_length) > MAX_IMAGE_BYTES:
        raise ValueError("Ảnh quá lớn (giới hạn 8MB).")

    suffix = os.path.splitext(url.split("?")[0])[-1] or ".jpg"
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)

    total = 0
    for chunk in response.iter_content(chunk_size=8192):
        total += len(chunk)
        if total > MAX_IMAGE_BYTES:
            tmp_file.close()
            os.remove(tmp_file.name)
            raise ValueError("Ảnh quá lớn (giới hạn 8MB).")
        tmp_file.write(chunk)

    tmp_file.close()
    return tmp_file.name


def predict_image(img_path: str, top_k: int = 3):
    img = keras_image.load_img(img_path, target_size=IMG_SIZE)
    img_array = keras_image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    preprocessed = preprocess_input(img_array.copy())

    preds = model.predict(preprocessed, verbose=0)[0]
    top_indices = preds.argsort()[-top_k:][::-1]
    results = [(class_names[i], float(preds[i])) for i in top_indices]
    return results, img, preprocessed


# Layer cuối cùng của phần tích chập trong MobileNetV2 (trước GlobalAveragePooling) — dùng cho Grad-CAM
GRADCAM_LAYER_NAME = "out_relu"


def generate_gradcam(preprocessed_img, pred_index, original_img_pil, alpha=0.45):
    """Sinh ảnh heatmap Grad-CAM chồng lên ảnh gốc, cho thấy vùng model tập trung để ra quyết định."""
    try:
        grad_model = tf.keras.models.Model(
            [model.inputs], [model.get_layer(GRADCAM_LAYER_NAME).output, model.output]
        )

        with tf.GradientTape() as tape:
            conv_outputs, predictions = grad_model(preprocessed_img)
            class_channel = predictions[:, pred_index]

        grads = tape.gradient(class_channel, conv_outputs)
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
        conv_outputs = conv_outputs[0]
        heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
        heatmap = tf.squeeze(heatmap)
        heatmap = tf.maximum(heatmap, 0) / (tf.math.reduce_max(heatmap) + 1e-8)
        heatmap = heatmap.numpy()

        # Tô màu heatmap (colormap "jet") và chồng lên ảnh gốc
        heatmap_uint8 = np.uint8(255 * heatmap)
        jet = cm.get_cmap("jet")
        jet_colors = jet(np.arange(256))[:, :3]
        jet_heatmap = jet_colors[heatmap_uint8]
        jet_heatmap = np.uint8(jet_heatmap * 255)

        heatmap_img = Image.fromarray(jet_heatmap).resize(original_img_pil.size)
        base_img = original_img_pil.convert("RGB")
        overlay = Image.blend(base_img, heatmap_img, alpha)
        return overlay
    except Exception:
        return None


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


CARE_KEYWORDS = ["chăm sóc", "cách trị", "cách xử lý", "làm sao", "phải làm gì", "chữa", "điều trị", "khắc phục"]
BUY_KEYWORDS = ["mua thuốc", "mua ở đâu", "loại thuốc", "thuốc gì", "sản phẩm nào", "mua gì"]
GREETING_KEYWORDS = ["chào", "hello", "hi ", "bạn là ai", "giúp được gì"]


def answer_general_question(text: str) -> str:
    """Trả lời câu hỏi dạng chữ, dựa trên bệnh vừa chẩn đoán gần nhất (nếu có)."""
    text_lower = text.lower()
    last = st.session_state.get("last_diagnosis")

    if any(kw in text_lower for kw in GREETING_KEYWORDS):
        return (
            "👋 Chào bạn! Mình là PlantDoc AI. Bạn có thể:\n"
            "- 📎 Upload ảnh lá cây để mình chẩn đoán bệnh\n"
            "- 💬 Hoặc hỏi mình về cách chăm sóc/mua thuốc cho bệnh vừa được chẩn đoán"
        )

    if any(kw in text_lower for kw in CARE_KEYWORDS):
        if last:
            return (
                f"🩺 **Cách chăm sóc/xử lý cho \"{last['ten_viet']}\":**\n\n"
                f"{last['cach_xu_ly']}\n\n"
                "_Lưu ý: đây là gợi ý tham khảo từ AI, mức độ nặng nhẹ thực tế nên được "
                "chuyên gia nông nghiệp đánh giá trực tiếp._"
            )
        return (
            "Bạn muốn hỏi cách chăm sóc cho bệnh nào vậy? Bạn upload ảnh lá cây để mình "
            "chẩn đoán trước, sau đó mình sẽ tư vấn cách xử lý cụ thể cho đúng bệnh đó nhé."
        )

    if any(kw in text_lower for kw in BUY_KEYWORDS):
        if last:
            return (
                f"💊 Với **\"{last['ten_viet']}\"**, hướng xử lý gợi ý là:\n\n"
                f"{last['cach_xu_ly']}\n\n"
                "Bạn có thể tìm mua các loại thuốc bảo vệ thực vật phù hợp tại **cửa hàng "
                "vật tư nông nghiệp** gần nhà, hoặc các sàn TMĐT có bán vật tư nông nghiệp uy tín. "
                "Nên mang theo ảnh lá bệnh khi đi mua để nhân viên tư vấn đúng loại thuốc, "
                "và đọc kỹ hướng dẫn sử dụng/liều lượng trên bao bì.\n\n"
                "_Lưu ý: mình không thể tư vấn tên thuốc thương mại cụ thể, vì điều này cần "
                "chuyên gia đánh giá tình trạng thực tế của cây._"
            )
        return (
            "Bạn muốn mua thuốc cho bệnh nào? Upload ảnh lá cây để mình chẩn đoán trước nhé, "
            "sau đó mình sẽ gợi ý hướng xử lý phù hợp."
        )

    # Không khớp intent nào rõ ràng
    return (
        "🤔 Mình chưa hiểu rõ câu hỏi này. Mình có thể giúp:\n"
        "- 📎 Chẩn đoán bệnh từ ảnh lá cây (upload ảnh hoặc dán link ảnh)\n"
        "- 💬 Tư vấn cách chăm sóc/xử lý cho bệnh vừa chẩn đoán (hỏi \"cách chăm sóc thế nào\")\n"
        "- 💊 Gợi ý hướng mua thuốc phù hợp (hỏi \"nên mua thuốc gì\")\n\n"
        "Bạn thử hỏi lại theo 1 trong các hướng trên nhé!"
    )


def handle_user_input(image_path=None, url_text=None):
    """Xử lý 1 lượt hỏi-đáp, trả về (bot_reply, heatmap_image_hoặc_None)."""
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
            return "❌ Mình không tìm thấy ảnh hợp lệ. Vui lòng upload ảnh hoặc dán link ảnh kết thúc bằng .jpg/.png...", None

        results, original_img, preprocessed = predict_image(img_path)
        top1_class, top1_conf = results[0]

        # Lưu lại để hiện nút phản hồi 👍/👎 sau khi trả lời xong
        st.session_state.pending_feedback = {"class": top1_class, "confidence": top1_conf}

        heatmap_img = None
        if top1_conf >= CONFIDENCE_THRESHOLD:
            st.session_state.last_diagnosis = get_disease_info(top1_class)
            top1_index = class_names.index(top1_class)
            heatmap_img = generate_gradcam(preprocessed, top1_index, original_img)

        return format_reply(results), heatmap_img

    except ValueError as e:
        return f"❌ {str(e)} Bạn thử upload ảnh trực tiếp thay vì dùng link nhé.", None
    except requests.exceptions.RequestException:
        return "❌ Mình không tải được ảnh từ link đó. Kiểm tra lại link (phải là link ảnh trực tiếp) hoặc thử upload ảnh trực tiếp nhé.", None
    except Exception as e:
        return f"❌ Có lỗi khi xử lý ảnh: {str(e)}", None
    finally:
        if temp_to_cleanup and os.path.exists(temp_to_cleanup):
            os.remove(temp_to_cleanup)


# ============ Giao diện chat ============
st.title("🌱 PlantDoc AI")
st.caption(
    "Chatbot nhận diện bệnh lá cây — huấn luyện trên bộ PlantVillage (38 loại cây/bệnh) "
    "bằng MobileNetV2 (transfer learning)."
)

if "last_diagnosis" not in st.session_state:
    st.session_state.last_diagnosis = None

if "pending_feedback" not in st.session_state:
    st.session_state.pending_feedback = None

# Sidebar: cho phép tải log phản hồi (dùng để huấn luyện lại model sau này)
with st.sidebar:
    st.markdown("### 📋 Dữ liệu phản hồi")
    st.caption("Log các lượt đánh giá 👍/👎 của người dùng, dùng để cải thiện model trong tương lai.")
    if os.path.exists(FEEDBACK_LOG_PATH):
        with open(FEEDBACK_LOG_PATH, "rb") as f:
            st.download_button("⬇️ Tải feedback_log.csv", f, file_name="feedback_log.csv", mime="text/csv")
    else:
        st.caption("_Chưa có phản hồi nào._")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {
            "role": "assistant",
            "content": (
                "👋 Chào bạn! Mình là bot nhận diện bệnh trên lá cây.\n\n"
                "Bạn có thể:\n"
                "- 📎 **Upload ảnh** lá cây ở khung bên dưới, hoặc **dán link ảnh** vào ô chat\n"
                "- 💬 **Hỏi thêm bằng chữ** sau khi có kết quả, ví dụ: \"cách chăm sóc thế nào\", "
                "\"nên mua thuốc gì\"\n"
                "- 🔥 Mình sẽ kèm ảnh **Grad-CAM** cho thấy vùng lá mà AI tập trung để ra kết luận\n\n"
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

user_text = st.chat_input(
    "Dán link ảnh, hỏi cách chăm sóc/mua thuốc, hoặc để trống nếu đã upload ảnh ở trên rồi bấm Enter..."
)

# Xử lý khi có upload ảnh mới hoặc người dùng gửi tin nhắn
trigger = False
image_path_to_use = None
display_image = None

if uploaded_file is not None and st.session_state.get("last_uploaded") != uploaded_file.name:
    if uploaded_file.size > MAX_IMAGE_BYTES:
        st.error(f"⚠️ Ảnh quá lớn ({uploaded_file.size/1024/1024:.1f}MB). Giới hạn 8MB, vui lòng chọn ảnh nhỏ hơn.")
    else:
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
        has_image_url = bool(user_text and URL_REGEX.search(user_text))
        heatmap_img = None
        if image_path_to_use is None and not has_image_url:
            # Không có ảnh/link ảnh -> đây là câu hỏi bằng chữ (chăm sóc, mua thuốc...)
            with st.spinner("Đang suy nghĩ..."):
                reply = answer_general_question(user_text)
        else:
            with st.spinner("Đang phân tích ảnh..."):
                reply, heatmap_img = handle_user_input(image_path=image_path_to_use, url_text=user_text)
        st.markdown(reply)
        if heatmap_img is not None:
            st.image(
                heatmap_img,
                width=250,
                caption="🔥 Vùng ảnh AI tập trung để đưa ra kết luận (Grad-CAM)"
            )

    st.session_state.chat_history.append({
        "role": "assistant",
        "content": reply,
        "image": heatmap_img,
    })

    if image_path_to_use and os.path.exists(image_path_to_use):
        os.remove(image_path_to_use)

# Hiện nút đánh giá 👍/👎 cho lần chẩn đoán gần nhất (đặt ngoài khối trigger để widget không biến mất giữa chừng)
if st.session_state.pending_feedback is not None:
    pf = st.session_state.pending_feedback
    st.divider()
    col1, col2 = st.columns([4, 1])
    with col1:
        st.caption(f"Kết quả \"{get_disease_info(pf['class'])['ten_viet']}\" có chính xác không?")
    with col2:
        fb = st.feedback("thumbs", key=f"fb_{len(st.session_state.chat_history)}")
    if fb is not None:
        log_feedback(pf["class"], pf["confidence"], "positive" if fb == 1 else "negative")
        st.session_state.pending_feedback = None
        st.success("Cảm ơn phản hồi của bạn! 🙏", icon="✅")
