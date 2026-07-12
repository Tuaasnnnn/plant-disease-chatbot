# disease_info.py
# Cơ sở dữ liệu kiến thức về các bệnh lá cây trong bộ PlantVillage (38 lớp)
# Dùng để bot trả lời giải thích + lời khuyên mà KHÔNG cần gọi API bên ngoài (miễn phí, luôn hoạt động)

DISEASE_INFO = {
    "Apple___Apple_scab": {
        "ten_viet": "Bệnh ghẻ táo (Apple Scab)",
        "nguyen_nhan": "Nấm Venturia inaequalis, phát triển mạnh trong điều kiện ẩm ướt, mưa nhiều.",
        "trieu_chung": "Đốm nâu/ô liu sẫm màu trên lá và quả, lá có thể biến dạng và rụng sớm.",
        "cach_xu_ly": "Cắt tỉa và tiêu hủy lá bệnh rụng dưới gốc; phun thuốc gốc đồng hoặc captan vào đầu mùa xuân; chọn giống kháng bệnh nếu trồng mới."
    },
    "Apple___Black_rot": {
        "ten_viet": "Bệnh thối đen quả táo",
        "nguyen_nhan": "Nấm Botryosphaeria obtripa, xâm nhập qua vết thương hoặc cành chết.",
        "trieu_chung": "Đốm nâu hình tròn đồng tâm trên lá (giống mắt ếch), quả thối đen, cành khô.",
        "cach_xu_ly": "Cắt bỏ cành/quả bị bệnh, khử trùng dụng cụ cắt tỉa, phun thuốc diệt nấm định kỳ."
    },
    "Apple___Cedar_apple_rust": {
        "ten_viet": "Bệnh gỉ sắt táo-tùng",
        "nguyen_nhan": "Nấm Gymnosporangium juniperi-virginianae, cần cả cây táo và cây tùng để hoàn thành vòng đời.",
        "trieu_chung": "Đốm vàng cam trên lá, sau chuyển nâu, có thể xuất hiện gai nhỏ mặt dưới lá.",
        "cach_xu_ly": "Loại bỏ cây tùng gần vườn táo nếu có thể; phun thuốc diệt nấm (myclobutanil) vào đầu mùa."
    },
    "Apple___healthy": {
        "ten_viet": "Lá táo khỏe mạnh",
        "nguyen_nhan": "Không có bệnh.",
        "trieu_chung": "Lá xanh đều, không đốm, không biến dạng.",
        "cach_xu_ly": "Tiếp tục chăm sóc bình thường: tưới đủ nước, bón phân cân đối, theo dõi định kỳ."
    },
    "Blueberry___healthy": {
        "ten_viet": "Lá việt quất khỏe mạnh",
        "nguyen_nhan": "Không có bệnh.",
        "trieu_chung": "Lá xanh đều, không đốm, không héo úa.",
        "cach_xu_ly": "Duy trì chăm sóc bình thường, đảm bảo đất thoát nước tốt, độ pH hơi chua (4.5-5.5)."
    },
    "Cherry_(including_sour)___Powdery_mildew": {
        "ten_viet": "Bệnh phấn trắng trên cherry",
        "nguyen_nhan": "Nấm Podosphaera clandestina, phát triển mạnh khi độ ẩm cao, thông gió kém.",
        "trieu_chung": "Lớp bột trắng như phấn phủ trên bề mặt lá, lá có thể xoăn lại và còi cọc.",
        "cach_xu_ly": "Cắt tỉa để tăng thông thoáng, phun lưu huỳnh hoặc thuốc diệt nấm gốc dầu neem."
    },
    "Cherry_(including_sour)___healthy": {
        "ten_viet": "Lá cherry khỏe mạnh",
        "nguyen_nhan": "Không có bệnh.",
        "trieu_chung": "Lá xanh đều, không có lớp phấn trắng hay đốm bệnh.",
        "cach_xu_ly": "Tiếp tục chăm sóc bình thường, cắt tỉa để cây thông thoáng."
    },
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": {
        "ten_viet": "Bệnh đốm xám lá ngô",
        "nguyen_nhan": "Nấm Cercospora zeae-maydis, phát triển trong điều kiện ẩm, ấm, cây trồng dày.",
        "trieu_chung": "Đốm chữ nhật màu xám/nâu chạy song song gân lá, lan rộng khi bệnh nặng.",
        "cach_xu_ly": "Luân canh cây trồng, cày vùi tàn dư sau thu hoạch, phun thuốc diệt nấm gốc strobilurin khi cần."
    },
    "Corn_(maize)___Common_rust_": {
        "ten_viet": "Bệnh gỉ sắt thông thường trên ngô",
        "nguyen_nhan": "Nấm Puccinia sorghi.",
        "trieu_chung": "Các đốm nhỏ màu nâu đỏ (gỉ sắt) rải rác trên cả hai mặt lá.",
        "cach_xu_ly": "Chọn giống kháng bệnh; phun thuốc diệt nấm nếu bệnh xuất hiện sớm và nặng."
    },
    "Corn_(maize)___Northern_Leaf_Blight": {
        "ten_viet": "Bệnh cháy lá lớn ở ngô (đốm bắc)",
        "nguyen_nhan": "Nấm Exserohilum turcicum.",
        "trieu_chung": "Vết bệnh dài hình thoi, màu xám-nâu, có thể lan khắp lá khi nặng.",
        "cach_xu_ly": "Luân canh, cày vùi tàn dư cây bệnh, dùng giống kháng, phun thuốc diệt nấm khi cần thiết."
    },
    "Corn_(maize)___healthy": {
        "ten_viet": "Lá ngô khỏe mạnh",
        "nguyen_nhan": "Không có bệnh.",
        "trieu_chung": "Lá xanh đều, không đốm, không cháy lá.",
        "cach_xu_ly": "Tiếp tục chăm sóc bình thường."
    },
    "Grape___Black_rot": {
        "ten_viet": "Bệnh thối đen nho",
        "nguyen_nhan": "Nấm Guignardia bidwellii.",
        "trieu_chung": "Đốm nâu tròn viền sẫm trên lá, quả co lại thành dạng khô đen (như nho khô).",
        "cach_xu_ly": "Cắt bỏ và tiêu hủy phần bị bệnh, phun thuốc diệt nấm từ đầu vụ, đảm bảo giàn thông thoáng."
    },
    "Grape___Esca_(Black_Measles)": {
        "ten_viet": "Bệnh Esca (đốm sởi đen) trên nho",
        "nguyen_nhan": "Phức hợp nhiều loại nấm gây hại gỗ nho lâu năm.",
        "trieu_chung": "Lá có vệt sọc vàng/đỏ giữa các gân (dạng \"hổ vằn\"), quả có đốm nâu nhỏ.",
        "cach_xu_ly": "Chưa có thuốc đặc trị hiệu quả cao; nên cắt bỏ cành/cây bệnh nặng, tránh vết thương lớn khi cắt tỉa."
    },
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": {
        "ten_viet": "Bệnh cháy lá nho (đốm Isariopsis)",
        "nguyen_nhan": "Nấm Pseudocercospora vitis (Isariopsis).",
        "trieu_chung": "Đốm nâu đỏ không đều trên lá, lá có thể khô và rụng sớm khi nặng.",
        "cach_xu_ly": "Vệ sinh vườn, thu gom lá rụng, phun thuốc diệt nấm gốc đồng khi cần."
    },
    "Grape___healthy": {
        "ten_viet": "Lá nho khỏe mạnh",
        "nguyen_nhan": "Không có bệnh.",
        "trieu_chung": "Lá xanh đều, không đốm.",
        "cach_xu_ly": "Tiếp tục chăm sóc bình thường."
    },
    "Orange___Haunglongbing_(Citrus_greening)": {
        "ten_viet": "Bệnh vàng lá gân xanh (Greening) trên cam quýt",
        "nguyen_nhan": "Vi khuẩn Candidatus Liberibacter, lây truyền qua rầy chổng cánh (psyllid).",
        "trieu_chung": "Lá vàng loang lổ không đối xứng qua gân chính, quả nhỏ méo, vị đắng.",
        "cach_xu_ly": "Bệnh chưa có thuốc chữa khỏi hoàn toàn; cần nhổ bỏ cây bệnh nặng, kiểm soát rầy chổng cánh, dùng cây giống sạch bệnh."
    },
    "Peach___Bacterial_spot": {
        "ten_viet": "Bệnh đốm vi khuẩn trên đào",
        "nguyen_nhan": "Vi khuẩn Xanthomonas arboricola pv. pruni.",
        "trieu_chung": "Đốm nhỏ góc cạnh màu nâu/tím trên lá, có thể thủng lỗ (hiệu ứng \"shot-hole\"), quả có vết lõm.",
        "cach_xu_ly": "Phun thuốc gốc đồng vào đầu vụ, tránh tưới lên tán lá, chọn giống kháng bệnh."
    },
    "Peach___healthy": {
        "ten_viet": "Lá đào khỏe mạnh",
        "nguyen_nhan": "Không có bệnh.",
        "trieu_chung": "Lá xanh đều, không đốm, không lỗ thủng.",
        "cach_xu_ly": "Tiếp tục chăm sóc bình thường."
    },
    "Pepper,_bell___Bacterial_spot": {
        "ten_viet": "Bệnh đốm vi khuẩn trên ớt chuông",
        "nguyen_nhan": "Vi khuẩn Xanthomonas campestris pv. vesicatoria.",
        "trieu_chung": "Đốm nhỏ sũng nước, sau chuyển nâu, viền vàng, có thể lan ra quả.",
        "cach_xu_ly": "Dùng hạt giống/cây con sạch bệnh, phun thuốc gốc đồng, tránh làm ướt lá khi tưới."
    },
    "Pepper,_bell___healthy": {
        "ten_viet": "Lá ớt chuông khỏe mạnh",
        "nguyen_nhan": "Không có bệnh.",
        "trieu_chung": "Lá xanh đều, không đốm.",
        "cach_xu_ly": "Tiếp tục chăm sóc bình thường."
    },
    "Potato___Early_blight": {
        "ten_viet": "Bệnh đốm vòng (cháy sớm) trên khoai tây",
        "nguyen_nhan": "Nấm Alternaria solani.",
        "trieu_chung": "Đốm nâu hình tròn có vòng đồng tâm như bia bắn, thường bắt đầu từ lá già phía dưới.",
        "cach_xu_ly": "Luân canh cây trồng, bón phân cân đối (tránh thiếu đạm), phun thuốc diệt nấm gốc chlorothalonil hoặc mancozeb."
    },
    "Potato___Late_blight": {
        "ten_viet": "Bệnh mốc sương (cháy muộn) trên khoai tây",
        "nguyen_nhan": "Nấm Phytophthora infestans — chính là tác nhân gây nạn đói khoai tây Ireland lịch sử.",
        "trieu_chung": "Đốm sũng nước màu xanh đen loang nhanh, mặt dưới lá có lớp mốc trắng khi ẩm, lan rất nhanh trong thời tiết ẩm mát.",
        "cach_xu_ly": "Đây là bệnh nguy hiểm, lây lan nhanh — cần phun thuốc diệt nấm phòng ngừa sớm, tiêu hủy cây bệnh ngay, tránh tưới lên lá vào chiều tối."
    },
    "Potato___healthy": {
        "ten_viet": "Lá khoai tây khỏe mạnh",
        "nguyen_nhan": "Không có bệnh.",
        "trieu_chung": "Lá xanh đều, không đốm.",
        "cach_xu_ly": "Tiếp tục chăm sóc bình thường."
    },
    "Raspberry___healthy": {
        "ten_viet": "Lá mâm xôi khỏe mạnh",
        "nguyen_nhan": "Không có bệnh.",
        "trieu_chung": "Lá xanh đều, không đốm.",
        "cach_xu_ly": "Tiếp tục chăm sóc bình thường."
    },
    "Soybean___healthy": {
        "ten_viet": "Lá đậu tương khỏe mạnh",
        "nguyen_nhan": "Không có bệnh.",
        "trieu_chung": "Lá xanh đều, không đốm.",
        "cach_xu_ly": "Tiếp tục chăm sóc bình thường."
    },
    "Squash___Powdery_mildew": {
        "ten_viet": "Bệnh phấn trắng trên bí",
        "nguyen_nhan": "Nấm Erysiphe cichoracearum / Podosphaera xanthii.",
        "trieu_chung": "Lớp bột trắng phủ trên bề mặt lá và thân, lá có thể vàng và khô dần.",
        "cach_xu_ly": "Tăng khoảng cách trồng để thông thoáng, phun lưu huỳnh hoặc thuốc diệt nấm gốc dầu neem, tưới gốc thay vì tưới lá."
    },
    "Strawberry___Leaf_scorch": {
        "ten_viet": "Bệnh cháy lá dâu tây",
        "nguyen_nhan": "Nấm Diplocarpon earlianum.",
        "trieu_chung": "Đốm tím/nâu nhỏ trên lá, dần lan rộng khiến lá như bị cháy khô.",
        "cach_xu_ly": "Cắt bỏ lá bệnh sau thu hoạch, đảm bảo thông thoáng, phun thuốc diệt nấm khi cần."
    },
    "Strawberry___healthy": {
        "ten_viet": "Lá dâu tây khỏe mạnh",
        "nguyen_nhan": "Không có bệnh.",
        "trieu_chung": "Lá xanh đều, không đốm.",
        "cach_xu_ly": "Tiếp tục chăm sóc bình thường."
    },
    "Tomato___Bacterial_spot": {
        "ten_viet": "Bệnh đốm vi khuẩn trên cà chua",
        "nguyen_nhan": "Vi khuẩn Xanthomonas spp.",
        "trieu_chung": "Đốm nhỏ sũng nước, viền vàng, sau chuyển nâu đen, có thể xuất hiện trên cả quả.",
        "cach_xu_ly": "Dùng giống/hạt sạch bệnh, phun thuốc gốc đồng, tránh làm ướt lá, luân canh cây trồng."
    },
    "Tomato___Early_blight": {
        "ten_viet": "Bệnh đốm vòng (cháy sớm) trên cà chua",
        "nguyen_nhan": "Nấm Alternaria solani.",
        "trieu_chung": "Đốm nâu hình tròn có vòng đồng tâm, thường xuất hiện ở lá già phía dưới trước.",
        "cach_xu_ly": "Cắt bỏ lá bệnh, bón phân cân đối, phun thuốc diệt nấm gốc chlorothalonil hoặc mancozeb định kỳ."
    },
    "Tomato___Late_blight": {
        "ten_viet": "Bệnh mốc sương (cháy muộn) trên cà chua",
        "nguyen_nhan": "Nấm Phytophthora infestans.",
        "trieu_chung": "Đốm sũng nước xanh đen loang nhanh, mặt dưới lá có mốc trắng khi ẩm, lan cực nhanh.",
        "cach_xu_ly": "Bệnh nguy hiểm — cần phun thuốc phòng ngừa sớm, loại bỏ cây bệnh ngay, tránh tưới ướt lá vào chiều tối."
    },
    "Tomato___Leaf_Mold": {
        "ten_viet": "Bệnh mốc lá cà chua",
        "nguyen_nhan": "Nấm Passalora fulva (Cladosporium fulvum), phát triển mạnh trong nhà kính ẩm thấp thông gió kém.",
        "trieu_chung": "Đốm vàng mặt trên lá, mặt dưới có lớp mốc nhung màu ô liu/nâu.",
        "cach_xu_ly": "Tăng thông gió, giảm độ ẩm, phun thuốc diệt nấm nếu bệnh nặng."
    },
    "Tomato___Septoria_leaf_spot": {
        "ten_viet": "Bệnh đốm lá Septoria trên cà chua",
        "nguyen_nhan": "Nấm Septoria lycopersici.",
        "trieu_chung": "Nhiều đốm nhỏ tròn, tâm xám viền sẫm, thường xuất hiện dày đặc trên lá già trước.",
        "cach_xu_ly": "Cắt bỏ lá bệnh, tránh tưới ướt lá, luân canh, phun thuốc diệt nấm khi cần."
    },
    "Tomato___Spider_mites Two-spotted_spider_mite": {
        "ten_viet": "Nhện đỏ hai chấm gây hại cà chua",
        "nguyen_nhan": "Nhện đỏ (Tetranychus urticae) — là côn trùng gây hại, không phải nấm/vi khuẩn.",
        "trieu_chung": "Lá có các chấm nhỏ li ti màu vàng/trắng (như bị châm kim), có thể thấy tơ nhện mảnh mặt dưới lá khi nặng.",
        "cach_xu_ly": "Phun nước mạnh để rửa trôi nhện, dùng dầu neem hoặc xà phòng diệt côn trùng, tăng độ ẩm không khí (nhện đỏ ưa khô)."
    },
    "Tomato___Target_Spot": {
        "ten_viet": "Bệnh đốm mắt cua (Target Spot) trên cà chua",
        "nguyen_nhan": "Nấm Corynespora cassiicola.",
        "trieu_chung": "Đốm nâu tròn có vòng đồng tâm giống mắt bia, dễ nhầm với Early Blight.",
        "cach_xu_ly": "Cắt tỉa thông thoáng, phun thuốc diệt nấm gốc chlorothalonil, luân canh cây trồng."
    },
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "ten_viet": "Bệnh virus xoăn vàng lá cà chua",
        "nguyen_nhan": "Virus TYLCV, lây truyền qua bọ phấn trắng (whitefly).",
        "trieu_chung": "Lá nhỏ, xoăn cong lên, mép lá vàng, cây còi cọc, ít đậu quả.",
        "cach_xu_ly": "Chưa có thuốc trị virus; cần kiểm soát bọ phấn trắng (dùng bẫy dính vàng, thuốc trừ côn trùng), nhổ bỏ cây bệnh nặng để tránh lây lan."
    },
    "Tomato___Tomato_mosaic_virus": {
        "ten_viet": "Bệnh virus khảm cà chua",
        "nguyen_nhan": "Virus ToMV, lây qua tiếp xúc cơ học (dụng cụ, tay người chăm sóc), hạt giống nhiễm bệnh.",
        "trieu_chung": "Lá có đốm khảm xanh đậm/xanh nhạt loang lổ, lá có thể biến dạng nhăn nheo.",
        "cach_xu_ly": "Chưa có thuốc trị virus; khử trùng dụng cụ thường xuyên, rửa tay trước khi chăm cây, loại bỏ cây bệnh, dùng giống kháng nếu có."
    },
    "Tomato___healthy": {
        "ten_viet": "Lá cà chua khỏe mạnh",
        "nguyen_nhan": "Không có bệnh.",
        "trieu_chung": "Lá xanh đều, không đốm, không biến dạng.",
        "cach_xu_ly": "Tiếp tục chăm sóc bình thường."
    },
}


def get_disease_info(class_name: str) -> dict:
    """Lấy thông tin bệnh theo tên lớp; trả về dict rỗng an toàn nếu không tìm thấy."""
    return DISEASE_INFO.get(class_name, {
        "ten_viet": class_name,
        "nguyen_nhan": "Chưa có dữ liệu chi tiết cho lớp này.",
        "trieu_chung": "Không xác định.",
        "cach_xu_ly": "Vui lòng tham khảo thêm nguồn chuyên môn khác."
    })
