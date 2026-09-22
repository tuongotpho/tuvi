# -*- coding: utf-8 -*-
"""Dữ liệu và phép luận giải Cao Ly Đầu Hình (Duyên nợ tiền định theo Can chồng - Chi vợ).

Trích lọc từ kho tàng văn hóa dân gian Việt Nam (Diễn Cầm Tam Thế, Bát Trạch Minh Kính,
Ngọc Hạp Thông Thư). Nam dụng Can, Nữ dụng Chi, phối thành 120 cách cục duyên nợ.
"""
from __future__ import annotations

# 10 Can của Chồng x 12 Chi của Vợ
# Mỗi cặp gồm: danh_hieu, tho_luc_bat, tien_van, hau_van, danh_gia, diem_cong
CAO_LY_DATA: dict[tuple[str, str], dict] = {
    # --- CAN GIÁP ---
    ("Giáp", "Tý"): {
        "danh_hieu": "Hiệp Phố Hóa Châu (Bạc đầu hòa thuận)",
        "tho": "Giáp Tý duyên nợ vẹn mười,\nTrước tuy trắc trở sau cười hoan ca.\nCầm đường con thảo đầy nhà,\nHậu lai phú quý một nhà ấm êm.",
        "luan": "Thuở đầu lập nghiệp có phen lao đao, cần nhẫn nại. Vợ chồng tính tình tương đắc, chung tay vượt khó. Trung niên tài lộc dồi dào, con cái học hành thành đạt, hậu vận an nhàn phú túc.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Giáp", "Sửu"): {
        "danh_hieu": "Hạc Lạc Đài Sen (Trước khó sau vinh)",
        "tho": "Giáp Sửu duyên nợ buổi đầu,\nLắm phen dâu bể dãi dầu gió sương.\nĐồng lòng tát cạn đại dương,\nTừ trung niên tới giàu sang trọn đời.",
        "luan": "Thời thanh xuân gặp nhiều thử thách về kinh tế. Nhưng nhờ vợ đảm đang, chồng có chí lớn nên trung vận điền sản hưng thịnh, con cháu ngoan ngoãn hiếu thuận.",
        "danh_gia": "tốt", "diem": 1
    },
    ("Giáp", "Dần"): {
        "danh_hieu": "Song Phụng Triều Dương (Vinh hiển song toàn)",
        "tho": "Giáp Dần kết tóc se duyên,\nNhư rồng gặp nước như thuyền xuôi giang.\nTài danh rạng rỡ vẻ vang,\nGia phong hòa mục bạc vàng đầy kho.",
        "luan": "Cực kỳ tương hợp về ý chí và sự nghiệp. Vợ chồng tương kính như tân, cùng nhau mưu sự ắt thành đại nghiệp. Sinh con quý tử, gia đạo hiển vinh.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Giáp", "Mão"): {
        "danh_hieu": "Phong Ba Tạm Thời (Kiên trì kết trái)",
        "tho": "Giáp Mão duyên phận trắc trở,\nĐôi phen khắc khẩu âu lo muộn phiền.\nChữ Nhẫn gìn giữ căn nguyên,\nHậu vận phước lộc ơn trên ban dày.",
        "luan": "Buổi đầu vợ chồng dễ bất đồng quan điểm, cần bớt lời nhường nhịn. Qua khỏi 35 tuổi mọi bề yên ấm, tài chính vững chắc, con cái hiển đạt.",
        "danh_gia": "trung bình", "diem": 0
    },
    ("Giáp", "Thìn"): {
        "danh_hieu": "Long Phụng Trình Tường (Phú quý vinh hoa)",
        "tho": "Giáp Thìn duyên phận tương phùng,\nTrai tài gái sắc muôn trùng đẹp tươi.\nTrăm năm trọn vẹn nụ cười,\nCông danh tài lộc rạng ngời mai sau.",
        "luan": "Đôi lứa môn đăng hộ đối, tương sinh trợ lực cho nhau. Đường công danh của chồng hanh thông nhờ người vợ biết quán xuyến. Con cái đỗ đạt cao.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Giáp", "Tỵ"): {
        "danh_hieu": "Hoa Khai Phú Quý (Ấm no trọn đời)",
        "tho": "Giáp Tỵ sum họp một nhà,\nLộc tài phát đạt gần xa ngợi khen.\nDù cho gặp lúc chông chênh,\nĐồng lòng vượt thác ấm êm muôn phần.",
        "luan": "Vợ chồng chung sức kinh doanh buôn bán rất thuận. Có tài lộc bất ngờ ở tuổi trung niên. Cần chú ý giữ gìn sức khỏe đôi bên khi về già.",
        "danh_gia": "tốt", "diem": 1
    },
    ("Giáp", "Ngọ"): {
        "danh_hieu": "Thủy Hỏa Tương Giao (Cần hòa khí)",
        "tho": "Giáp Ngọ có lúc đổi dời,\nBên mềm bên cứng trọn đời chở che.\nĐừng nghe ong bướm đồn hoe,\nMột lòng chung thủy vẹn bề tương lai.",
        "luan": "Cả hai đều có cá tính mạnh, khi nóng giận dễ buông lời tổn thương. Cần người chồng bao dung, người vợ nhu thuận thì gia đình ấm êm, của cải bền lâu.",
        "danh_gia": "trung bình", "diem": 0
    },
    ("Giáp", "Mùi"): {
        "danh_hieu": "Cầm Sắt Giao Hòa (Phúc lộc tự nhiên)",
        "tho": "Giáp Mùi duyên thắm tình nồng,\nThuận vợ thuận chồng tát biển cũng vơi.\nSinh con thảo hiền rạng ngời,\nTuổi già thanh thản thảnh thơi an nhàn.",
        "luan": "Mối nhân duyên hòa nhã, ít khi to tiếng. Gia đạo bình yên, tiền tài tích lũy vững chắc qua từng năm. Hậu vận con cháu đông đúc hiếu kính phụng dưỡng.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Giáp", "Thân"): {
        "danh_hieu": "Viễn Xứ Thành Danh (Đi xa lập nghiệp)",
        "tho": "Giáp Thân xa xứ lập thân,\nGian nan thử thách muôn phần mới nên.\nChung vai gánh vác vững bền,\nSau ngày giông bão bước lên đỉnh đài.",
        "luan": "Lập nghiệp nơi quê nhà thường khó phát triển, nên đi xa hoặc sinh sống nơi khác sẽ đại phát tài lộc. Vợ chồng đồng cam cộng khổ ắt có ngày vinh quang.",
        "danh_gia": "tốt", "diem": 1
    },
    ("Giáp", "Dậu"): {
        "danh_hieu": "Ngọc Ẩn Trong Đá (Trung niên rạng rỡ)",
        "tho": "Giáp Dậu buổi sớm hàn vi,\nBền gan vững chí ngại gì phong ba.\nCon đàn cháu đống đầy nhà,\nRuộng vườn nhà cửa nguy nga đàng hoàng.",
        "luan": "Tiền vận kinh tế còn eo hẹp, nhưng vợ chồng thương yêu nhau thật lòng. Sau 40 tuổi làm ăn đại phát, phúc đức đầy nhà.",
        "danh_gia": "tốt", "diem": 1
    },
    ("Giáp", "Tuất"): {
        "danh_hieu": "Thanh Mai Trúc Mã (Nghĩa trọng tình thâm)",
        "tho": "Giáp Tuất duyên nợ keo sơn,\nTrải bao cay đắng chẳng sờn lòng son.\nĐến ngày trăng tỏ vuông tròn,\nGia đình hạnh phúc cháu con sum vầy.",
        "luan": "Tình nghĩa sâu nặng, thủy chung son sắt. Vợ chồng hiểu ý nhau từng cử chỉ nhỏ, cùng vượt qua mọi phong ba bão táp để hưởng phúc lộc tuổi già.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Giáp", "Hợi"): {
        "danh_hieu": "Kim Ngọc Mãn Đường (Phú túc an khang)",
        "tho": "Giáp Hợi loan phụng hòa minh,\nTrăm năm trọn vẹn nghĩa tình thủy chung.\nPhước lộc tài vận hanh thông,\nCon hiền cháu thảo ấm lòng mẹ cha.",
        "luan": "Là cách cục đại cát, vợ chồng hòa thuận, cuộc sống no ấm dư dả. Con cái ngoan ngoãn giỏi giang, rạng danh dòng tộc.",
        "danh_gia": "rất tốt", "diem": 2
    },

    # --- CAN ẤT ---
    ("Ất", "Tý"): {
        "danh_hieu": "Ngũ Phúc Lâm Môn (Gia đạo hưng long)",
        "tho": "Ất Tý duyên đẹp trời ban,\nVợ hiền dâu thảo đảm đang trong ngoài.\nLàm ăn phát đạt tương lai,\nMột đời thanh bạch ấm êm trọn đời.",
        "luan": "Người vợ khéo léo vun vén, người chồng cần cù siêng năng. Gia đình êm ấm, tài lộc đều đặn, không lo túng thiếu.",
        "danh_gia": "tốt", "diem": 1
    },
    ("Ất", "Sửu"): {
        "danh_hieu": "Thiên Lý Mã (Đường xa mới biết ngựa hay)",
        "tho": "Ất Sửu duyên nợ thâm trầm,\nBan đầu trắc trở âm thầm vượt qua.\nCàng già càng đậm tình ca,\nLộc tài tích tụ chan hòa niềm vui.",
        "luan": "Hôn nhân bền vững theo thời gian. Lúc trẻ có lúc băn khoăn chật vật, nhưng càng chung sống càng gắn kết, của cải ngày một nhiều thêm.",
        "danh_gia": "tốt", "diem": 1
    },
    ("Ất", "Dần"): {
        "danh_hieu": "Lưỡng Hùng Tương Ngộ (Cần mềm mỏng)",
        "tho": "Ất Dần tính nết đôi đường,\nChồng cương vợ nhu mới tường ấm êm.\nĐừng để giận dỗi dài thêm,\nThuận lòng trên dưới ấm êm cửa nhà.",
        "luan": "Có lúc khắc khẩu, tranh giành vai trò quyết định. Nếu người chồng biết lắng nghe và người vợ khéo léo ứng xử thì tài vận rất thịnh vượng.",
        "danh_gia": "trung bình", "diem": 0
    },
    ("Ất", "Mão"): {
        "danh_hieu": "Đồng Tâm Hiệp Lực (Bình dị an vui)",
        "tho": "Ất Mão hòa mục yêu thương,\nSống đời thanh thản chẳng màng đua tranh.\nCơm canh đạm bạc ngọt lành,\nCon cái hiếu đễ rạng danh tông đường.",
        "luan": "Vợ chồng cùng tính ôn hòa, thương yêu đùm bọc nhau. Cuộc sống bình ổn, ít gặp sóng gió lớn, con cái lớn lên thành người lương thiện thành đạt.",
        "danh_gia": "tốt", "diem": 1
    },
    ("Ất", "Thìn"): {
        "danh_hieu": "Ngư Dược Long Môn (Cá vượt vũ môn)",
        "tho": "Ất Thìn duyên phận tuyệt vời,\nChồng lo đại sự vợ thời tề gia.\nTài lộc tựa nước phù sa,\nTrăm năm son sắt thật thà yêu thương.",
        "luan": "Tương hỗ đắc lực trong công danh sự nghiệp. Chồng phát triển bên ngoài, vợ làm hậu phương vững chắc. Tiền bạc dồi dào, hậu vận cực thịnh.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Ất", "Tỵ"): {
        "danh_hieu": "Tơ Duyên Gắn Bó (Hạnh phúc thăng hoa)",
        "tho": "Ất Tỵ se mối duyên lành,\nBên nhau sớm tối dệt thành tương lai.\nLộc tài bền vững lâu dài,\nGia trung thịnh vượng rạng ngời cháu con.",
        "luan": "Ý chí hòa hợp, làm việc gì cũng bàn bạc ăn ý. Cuộc sống hôn nhân ngọt ngào, kinh tế ngày càng khấm khá.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Ất", "Ngọ"): {
        "danh_hieu": "Phong Sương Rèn Luyện (Vượt khó thành công)",
        "tho": "Ất Ngọ trải bước gập ghềnh,\nTình duyên gắn chặt lênh đênh chẳng màng.\nSau cơn giông tố gió ngàn,\nThuyền về bến đỗ ngập tràn sắc xuân.",
        "luan": "Thời trẻ dễ gặp trắc trở công việc hoặc biến cố gia đình, nhưng nhờ tình yêu thương bền chặt mà cùng nhau vượt qua, trung hậu vận sung túc.",
        "danh_gia": "tốt", "diem": 1
    },
    ("Ất", "Mùi"): {
        "danh_hieu": "Xuân Phong Đắc Ý (Thuận buồm xuôi gió)",
        "tho": "Ất Mùi duyên thắm tròn đầy,\nBàn tay chung sức đắp xây cơ đồ.\nLúa vàng ngập lối bờ hồ,\nMột nhà êm ấm tiền vô như nguồn.",
        "luan": "Rất hợp ý nhau trong chuyện tiền bạc và nuôi dạy con cái. Gia đình có nề nếp, tài sản tăng trưởng đều đặn.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Ất", "Thân"): {
        "danh_hieu": "Thất Bại Mới Thành (Kiên trì chiến thắng)",
        "tho": "Ất Thân duyên phận buổi đầu,\nNhiều phen lo nghĩ âu sầu băn khoăn.\nĐồng lòng vượt nỗi khó khăn,\nBạc vàng tích tụ con ngoan rạng ngời.",
        "luan": "Cần kiên định, chớ thấy khó khăn mà nản lòng. Về hậu vận điền sản rộng rãi, con cái thành đạt hiển vinh.",
        "danh_gia": "trung bình", "diem": 0
    },
    ("Ất", "Dậu"): {
        "danh_hieu": "Phu Xướng Phụ Tùy (Hòa thuận ấm êm)",
        "tho": "Ất Dậu chồng xướng vợ theo,\nChữ tâm giữ trọn cảnh nghèo cũng qua.\nTình nồng rạng rỡ muôn hoa,\nCàng già càng thắm một nhà an vui.",
        "luan": "Vợ chồng nương tựa nhau, hiểu và thông cảm cho nhau. Con cái ngoan ngoãn, tuổi già hưởng phúc an nhàn.",
        "danh_gia": "tốt", "diem": 1
    },
    ("Ất", "Tuất"): {
        "danh_hieu": "Kính Trọng Tương Thân (Bền vững son sắt)",
        "tho": "Ất Tuất duyên nợ vuông tròn,\nChữ ân chữ nghĩa sắt son trọn đời.\nDù cho vật đổi sao dời,\nBên nhau chia ngọt sẻ bùi bền lâu.",
        "luan": "Rất thủy chung và biết vì nhau. Gia đạo bình an, tai ương đều hóa cát, con cháu làm rạng rỡ tổ tông.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Ất", "Hợi"): {
        "danh_hieu": "Tài Lộc Dồi Dào (Hậu vận cực thịnh)",
        "tho": "Ất Hợi kết tóc se duyên,\nTrăm năm trọn vẹn bình yên ấm lòng.\nRuộng vườn của cải đầy đong,\nCon đàn cháu đống tươi hồng sắc xuân.",
        "luan": "Cuộc sống hôn nhân trọn vẹn cả tình lẫn tài. Hậu vận phúc lộc thọ tam toàn, con cháu thành đạt vẻ vang.",
        "danh_gia": "rất tốt", "diem": 2
    },

    # --- CAN BÍNH ---
    ("Bính", "Tý"): {
        "danh_hieu": "Thủy Hỏa Ký Tế (Dung hòa viên mãn)",
        "tho": "Bính Tý hòa hợp duyên nồng,\nNước sôi lửa ấm thuận lòng đôi bên.\nTrời ban phước lộc vững bền,\nCon hiền dâu thảo xây nền vinh hoa.",
        "luan": "Bính Hỏa gặp Tý Thủy, nếu biết điều hòa cương nhu thì thành cách Ký Tế rất tốt. Làm ăn phát đạt, gia đạo có tôn ti trật tự.",
        "danh_gia": "tốt", "diem": 1
    },
    ("Bính", "Sửu"): {
        "danh_hieu": "Hỏa Sinh Thổ Địa (Điền sản phì nhiêu)",
        "tho": "Bính Sửu chung sống thuận hòa,\nĐất đai nhà cửa nguy nga vững vàng.\nLàm ăn tích tiểu thành nang,\nTrung niên vững chãi bạc vàng thảnh thơi.",
        "luan": "Người vợ có tài giữ của, người chồng chăm chỉ làm ăn. Điền sản đất đai dồi dào, hậu vận sung túc viên mãn.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Bính", "Dần"): {
        "danh_hieu": "Mộc Hỏa Tương Sinh (Rực rỡ công danh)",
        "tho": "Bính Dần lửa cháy thêm hoa,\nCông danh sự nghiệp thăng hoa tuyệt vời.\nSinh con rạng rỡ đất trời,\nTrăm năm cầm sắt trọn đời bên nhau.",
        "luan": "Cách cục rất đẹp, vợ chồng tương sinh trợ lực, công danh sự nghiệp thăng tiến vùn vụt, con cái có tài năng xuất chúng.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Bính", "Mão"): {
        "danh_hieu": "Tương Trợ Đồng Tâm (Vinh hoa ấm áp)",
        "tho": "Bính Mão duyên đẹp lứa đôi,\nĐôi phen khắc nhẹ nhưng rồi lại qua.\nẤm êm hạnh phúc một nhà,\nCàng về hậu vận lộc tài càng hưng.",
        "luan": "Vợ chồng yêu thương nhau tha thiết. Đôi lúc có chút giận dỗi nhưng mau hòa giải. Tiền của tích lũy phong phú.",
        "danh_gia": "tốt", "diem": 1
    },
    ("Bính", "Thìn"): {
        "danh_hieu": "Long Bàn Hổ Cứ (Sự nghiệp vững vàng)",
        "tho": "Bính Thìn duyên phận cao sang,\nChung tay gầy dựng đàng hoàng tương lai.\nLộc tài vượng phát lâu dài,\nCháu con tấn tới đức tài song toàn.",
        "luan": "Ý chí kiên định, quyết đoán trong làm ăn. Hôn nhân vừa là tình cảm vừa là bạn đồng hành cùng chí hướng.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Bính", "Tỵ"): {
        "danh_hieu": "Lưỡng Hỏa Tương Huy (Cần hạ hỏa)",
        "tho": "Bính Tỵ hai ngọn lửa hồng,\nSáng soi rực rỡ nhưng phòng cháy to.\nNhường nhau bớt giận bớt lo,\nThì thuyền hạnh phúc cặp bờ bình yên.",
        "luan": "Hai người đều năng động, nhiệt huyết nhưng dễ nóng nảy. Khi gặp chuyện bất đồng cần bình tĩnh lắng nghe để giữ hòa khí.",
        "danh_gia": "trung bình", "diem": 0
    },
    ("Bính", "Ngọ"): {
        "danh_hieu": "Hỏa Diệm Đô Thiên (Cần tu tâm dưỡng tính)",
        "tho": "Bính Ngọ tính khí cương cường,\nCần câu hòa ái mới tường đạo phu.\nNhịn nhau qua đám mây mù,\nTrời quang mây tạnh thiên thu ấm nồng.",
        "luan": "Dễ nảy sinh cãi vã vì cái tôi lớn. Nếu người chồng biết nhường vợ, vợ biết tôn trọng chồng thì biến nhiệt huyết thành tài lộc dồi dào.",
        "danh_gia": "ít hợp", "diem": -1
    },
    ("Bính", "Mùi"): {
        "danh_hieu": "Thái Dương Soi Chiếu (Ấm áp chan hòa)",
        "tho": "Bính Mùi tình nghĩa đậm sâu,\nChung tay san sẻ nỗi sầu niềm vui.\nLộc tài tự khắc tới lui,\nCon đàn cháu đống ngọt bùi trăm năm.",
        "luan": "Người vợ dịu dàng kìm bớt tính nóng của chồng. Gia đạo hài hòa, làm ăn ngày càng hưng vượng, hậu vận thảnh thơi.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Bính", "Thân"): {
        "danh_hieu": "Kim Bị Hỏa Luyện (Trước thử thách sau vinh)",
        "tho": "Bính Thân duyên nợ nhiều phen,\nLửa vàng tôi luyện mới nên đồ dùng.\nVượt qua giông tố chập chùng,\nHậu lai phú quý sánh cùng vương gia.",
        "luan": "Khó khăn thời trẻ giúp tôi luyện bản lĩnh của cả hai. Về sau kinh tế cực kỳ vững vàng, được mọi người nể trọng.",
        "danh_gia": "tốt", "diem": 1
    },
    ("Bính", "Dậu"): {
        "danh_hieu": "Trâm Cài Lược Dắt (Hài hòa êm đẹp)",
        "tho": "Bính Dậu đẹp mối tơ duyên,\nTrăm năm trọn vẹn bình yên một nhà.\nCon ngoan cháu thảo hiền hòa,\nGia môn rạng rỡ nở hoa thái bình.",
        "luan": "Vợ đảm đang tháo vát, chồng có tài mưu lược. Cuộc sống đủ đầy, tiếng thơm lưu truyền cho con cháu.",
        "danh_gia": "tốt", "diem": 1
    },
    ("Bính", "Tuất"): {
        "danh_hieu": "Hỏa Thổ Tương Hòa (Bền chặt keo sơn)",
        "tho": "Bính Tuất duyên thắm dài lâu,\nChẳng màng bão táp cơ cầu gian nan.\nMột nhà đầy ắp bình an,\nPhước tài như nước dâng tràn bờ đê.",
        "luan": "Gia đình đầm ấm, vợ chồng chung thủy. Đường con cái hiển đạt, tiền tài của nải vững bền.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Bính", "Hợi"): {
        "danh_hieu": "Thủy Hỏa Tương Tế (Phúc thọ song toàn)",
        "tho": "Bính Hợi hòa hợp trăm năm,\nTình sâu nghĩa nặng như trăng rằm tròn.\nĐầy nhà hoa thảo cháu con,\nTuổi già thanh thản vẹn tròn phúc duyên.",
        "luan": "Vợ chồng bù trừ khiếm khuyết cho nhau rất khéo. Sức khỏe dồi dào, thọ mệnh trường cửu, phúc lộc dồi dào.",
        "danh_gia": "rất tốt", "diem": 2
    },

    # --- CAN ĐINH ---
    ("Đinh", "Tý"): {
        "danh_hieu": "Đăng Hỏa Dạ Minh (Đèn đêm soi sáng)",
        "tho": "Đinh Tý khéo léo vun trồng,\nVợ hiền quán xuyến ấm lòng đức lang.\nTài danh phát đạt đàng hoàng,\nCon hiền cháu thảo vẻ vang tông đường.",
        "luan": "Vợ chồng hiểu ý nhau, chi tiêu tiết kiệm hợp lý. Sự nghiệp đi lên từng bước vững chắc, con cái học hành đỗ đạt.",
        "danh_gia": "tốt", "diem": 1
    },
    ("Đinh", "Sửu"): {
        "danh_hieu": "Ngũ Phúc Thụ Lộc (Ăn chắc mặc bền)",
        "tho": "Đinh Sửu cần kiệm chuyên cần,\nĐắp bồi gia đạo muôn phần ấm êm.\nLộc tài ngày một dày thêm,\nHậu vận sung túc êm đềm tháng năm.",
        "luan": "Hai người đều là người chịu thương chịu khó. Tuy ít lời hoa mỹ nhưng hành động thiết thực, của nải ngày càng dư dả.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Đinh", "Dần"): {
        "danh_hieu": "Mộc Sinh Hỏa Diệu (Thăng hoa tài vận)",
        "tho": "Đinh Dần duyên nợ tươi màu,\nVợ chồng hòa thuận trước sau một lòng.\nLàm ăn may mắn hanh thông,\nCon ngoan trò giỏi rạng dòng tộc gia.",
        "luan": "Tương sinh tương trợ, người này nâng bước người kia. Kinh doanh hay công danh đều gặt hái thành quả lớn.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Đinh", "Mão"): {
        "danh_hieu": "Liễu Xanh Hoa Thắm (Thanh nhàn phú túc)",
        "tho": "Đinh Mão duyên đẹp vô ngần,\nTrăm năm gắn bó muôn phần yêu thương.\nCuộc đời phẳng lặng như gương,\nTuổi già an lạc thọ trường bình an.",
        "luan": "Gia đạo yên vui, vợ chồng ít khi xảy ra xung đột. Hậu vận an nhàn thảnh thơi, con cháu thành đạt.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Đinh", "Thìn"): {
        "danh_hieu": "Thao Lược Hưng Gia (Có chí làm giàu)",
        "tho": "Đinh Thìn duyên nợ bền lâu,\nChung tay vượt hết cây cầu gian nan.\nTừ trung niên bước khang trang,\nNhà cao cửa rộng bạc vàng đầy kho.",
        "luan": "Đôi bên đều có ý chí tiến thủ. Qua buổi đầu thử thách, từ trung vận sự nghiệp vững như bàn thạch.",
        "danh_gia": "tốt", "diem": 1
    },
    ("Đinh", "Tỵ"): {
        "danh_hieu": "Lưỡng Đăng Tương Chiếu (Ấm áp rực rỡ)",
        "tho": "Đinh Tỵ lửa sáng trong nhà,\nTrăm năm hòa thuận chan hòa tình thương.\nDẫu qua ngàn dặm gió sương,\nMột lòng son sắt trên đường tương lai.",
        "luan": "Tính tình ấm áp, quan tâm chia sẻ. Tài lộc đều đặn, gia đình luôn rộn rã tiếng cười, con cháu hiếu đễ.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Đinh", "Ngọ"): {
        "danh_hieu": "Hỏa Thượng Thêm Dầu (Cần nhẫn nại)",
        "tho": "Đinh Ngọ đôi lúc gắt gao,\nChồng bớt nóng nảy vợ chào ngọt ngon.\nThương nhau giữ trọn lòng son,\nCửa nhà ấm cúng cháu con thảo hiền.",
        "luan": "Cần chú ý kiềm chế cơn nóng giận nhất thời. Chỉ cần một người nhịn một câu thì vạn sự thái bình, làm ăn phát đạt.",
        "danh_gia": "trung bình", "diem": 0
    },
    ("Đinh", "Mùi"): {
        "danh_hieu": "Nguyệt Lạc Tinh Thần (Vẹn tròn nghĩa tình)",
        "tho": "Đinh Mùi duyên nợ vuông tròn,\nTình sâu nghĩa nặng như hòn non cao.\nTrời ban phúc lộc dồi dào,\nTrăm năm cầm sắt ngọt ngào bên nhau.",
        "luan": "Vợ chồng tâm đầu ý hợp, được đôi bên nội ngoại quý mến. Cuộc sống an nhàn, tiền tài sung túc.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Đinh", "Thân"): {
        "danh_hieu": "Kinh Doanh Đắc Lợi (Tài lộc hanh thông)",
        "tho": "Đinh Thân buôn bán đại tài,\nChồng lo ngoại sự vợ ngoài quán xao.\nTiền tài chảy tựa sông đào,\nCon hiền cháu giỏi tự hào gia phong.",
        "luan": "Rất hợp làm ăn kinh doanh buôn bán. Hai người bù trừ khéo léo, tiền tài sinh sôi nảy nở, hậu vận rạng rỡ.",
        "danh_gia": "tốt", "diem": 1
    },
    ("Đinh", "Dậu"): {
        "danh_hieu": "Châu Ngọc Thành Đôi (Quý hiển giàu sang)",
        "tho": "Đinh Dậu sum họp một nhà,\nCông danh tài lộc đậm đà sắc xuân.\nĂn ở phước đức bội phần,\nTuổi già thanh thản hưởng ân phước trời.",
        "luan": "Tương hỗ đắc lực, vợ chồng khéo cư xử đối nội đối ngoại. Sinh con quý tử, gia đạo hiển vinh.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Đinh", "Tuất"): {
        "danh_hieu": "Kiên Trì Lập Nghiệp (Vững bền hậu vận)",
        "tho": "Đinh Tuất gian khổ chẳng từ,\nChung tay gầy dựng cơ đồ mai sau.\nTóc xanh cho đến bạc đầu,\nTình nồng nghĩa đượm bền lâu muôn đời.",
        "luan": "Thuở hàn vi cùng chia sẻ gian khó, về già cùng hưởng vinh hoa. Một đời thủy chung, con cháu thành danh.",
        "danh_gia": "tốt", "diem": 1
    },
    ("Đinh", "Hợi"): {
        "danh_hieu": "Thủy Hỏa Điều Hòa (Phúc thọ an khang)",
        "tho": "Đinh Hợi duyên nợ tuyệt trần,\nTrời ban phước lớn muôn phần ấm êm.\nRuộng nương nhà cửa vững bền,\nCon đàn cháu đống làm nên nghiệp vàng.",
        "luan": "Hôn nhân toàn vẹn về mọi mặt. Tài lộc dồi dào, gia đình đầm ấm, hậu vận hưởng đại thọ và phúc đức con cháu.",
        "danh_gia": "rất tốt", "diem": 2
    },

    # --- CAN MẬU ---
    ("Mậu", "Tý"): {
        "danh_hieu": "Sơn Thủy Tương Phùng (Trung niên hưng thịnh)",
        "tho": "Mậu Tý non nước giao hòa,\nTrước nghèo sau đặng phong ba vượt rồi.\nNgồi trên đống bạc thảnh thơi,\nCon đàn cháu đống rạng ngời mai sau.",
        "luan": "Đầu đời có lúc bấp bênh, nhưng từ ngoài 30 tuổi tài vận hanh thông rực rỡ. Vợ chồng hiểu nhau, ăn ở bền lâu.",
        "danh_gia": "tốt", "diem": 1
    },
    ("Mậu", "Sửu"): {
        "danh_hieu": "Đồng Điền Đắc Khí (Điền sản mênh mông)",
        "tho": "Mậu Sửu cùng tính chuyên cần,\nĐất đai màu mỡ bội phần tốt tươi.\nNhà cao cửa rộng rạng ngời,\nTrăm năm hòa thuận trọn đời ấm êm.",
        "luan": "Rất giỏi tích lũy đất đai, nhà cửa. Tính tình hiền lành, gia đạo nề nếp, con cái hiếu thảo thành tài.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Mậu", "Dần"): {
        "danh_hieu": "Hổ Xuất Sơn Lâm (Cần hòa giải nhường nhịn)",
        "tho": "Mậu Dần duyên phận đôi bờ,\nĐôi phen sóng gió bất ngờ nổi lên.\nGiữ gìn chữ nhẫn vững bền,\nThì qua giông bão bước lên thái bình.",
        "luan": "Tính tình có nét tương khắc, đôi lúc cãi vã. Cần người chồng bao dung và người vợ mềm mỏng để giữ lửa gia đình.",
        "danh_gia": "trung bình", "diem": 0
    },
    ("Mậu", "Mão"): {
        "danh_hieu": "Xuân Thảo Phùng Thời (Mềm mại tốt tươi)",
        "tho": "Mậu Mão duyên đẹp mặn nồng,\nVợ hiền khéo léo ấm lòng trượng phu.\nLàm ăn tài lộc bốn mùa,\nGia phong lễ giáo nghìn thu vững bền.",
        "luan": "Người vợ nhu thuận giúp người chồng thăng tiến trong sự nghiệp. Kinh tế khá giả, con cái giỏi giang ngoan ngoãn.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Mậu", "Thìn"): {
        "danh_hieu": "Long Bàn Hổ Cứ (Vinh hoa phú quý)",
        "tho": "Mậu Thìn rạng rỡ gia phong,\nTrai tài gái sắc thỏa lòng ước ao.\nTài danh bay bổng ngút cao,\nCon ngoan cháu thảo tự hào tổ tiên.",
        "luan": "Gia đình thịnh vượng, hai bên nội ngoại đều nở mày nở mặt. Con cái đỗ đạt cao, làm rạng danh dòng tộc.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Mậu", "Tỵ"): {
        "danh_hieu": "Hỏa Thổ Tương Sinh (Lộc tài tấn phát)",
        "tho": "Mậu Tỵ se mối duyên lành,\nVợ chồng thuận ý ắt thành cơ ngơi.\nCơm no áo ấm trọn đời,\nTuổi già thanh thản thảnh thơi an nhàn.",
        "luan": "Tương sinh đắc lực, người vợ mang lại nhiều may mắn cho chồng. Cuộc sống sung túc ấm no, hậu vận hạnh phúc.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Mậu", "Ngọ"): {
        "danh_hieu": "Hỏa Diệm Đất Khô (Cần dưỡng hòa)",
        "tho": "Mậu Ngọ tính khí nồng nàn,\nKhi vui ấm áp lúc giận than thở nhiều.\nNhường nhau một bước trăm chiều,\nGia đình hạnh phúc bấy nhiêu phước lành.",
        "luan": "Đôi lúc có xung đột nhỏ do tính tình thẳng thắn. Cần hạ bớt cái tôi thì gia đình luôn ấm êm, tiền tài vững chắc.",
        "danh_gia": "trung bình", "diem": 0
    },
    ("Mậu", "Mùi"): {
        "danh_hieu": "Đức Dày Chở Vật (Phúc trạch thâm sâu)",
        "tho": "Mậu Mùi hòa thuận vuông tròn,\nChữ tâm gìn giữ cháu con thảo hiền.\nTrời ban phúc ấm tự nhiên,\nTrăm năm hạnh phúc trọn niềm ước mơ.",
        "luan": "Ăn ở có đức nên gặp nhiều may mắn. Vợ chồng đồng lòng, con cái thành đạt, hậu vận vinh hiển an khang.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Mậu", "Thân"): {
        "danh_hieu": "Sơn Thượng Sinh Kim (Của cải dồi dào)",
        "tho": "Mậu Thân đào đất tìm vàng,\nBao năm vất vả vẻ vang muôn phần.\nSau cơn bĩ cực đến tuần,\nBạc vàng ngập lối mùa xuân rạng ngời.",
        "luan": "Khởi đầu gian nan, tích lũy từng đồng. Về sau làm ăn lớn, của cải tích tụ như núi, con cháu hưởng phúc ấm.",
        "danh_gia": "tốt", "diem": 1
    },
    ("Mậu", "Dậu"): {
        "danh_hieu": "Phụng Vũ Loan Tường (Cầm sắt hòa ca)",
        "tho": "Mậu Dậu duyên phận vuông tròn,\nVợ hiền dâu thảo sắt son một lòng.\nLàm ăn tài vận hanh thông,\nTuổi già thanh bạch thong dong an nhàn.",
        "luan": "Gia đình có nề nếp gia phong. Vợ chồng tương kính như tân, tiền bạc sung túc, con cái ngoan ngoãn hiếu đễ.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Mậu", "Tuất"): {
        "danh_hieu": "Lưỡng Thổ Thành Sơn (Vững như bàn thạch)",
        "tho": "Mậu Tuất hai đất thành non,\nChung vai gánh vác cháu con nên người.\nGian nan thử thách mỉm cười,\nTrăm năm trọn vẹn sáng ngời nghĩa ân.",
        "luan": "Hôn nhân cực kỳ bền vững, trung trinh gắn kết. Cơ đồ ngày một vững chắc, hậu vận an khang thịnh vượng.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Mậu", "Hợi"): {
        "danh_hieu": "Bồi Đê Ngăn Nước (Khéo léo điều hòa)",
        "tho": "Mậu Hợi duyên phận êm đềm,\nChồng lo ngoại sự vợ mềm trong gia.\nRuộng vườn nhà cửa nguy nga,\nCon hiền cháu thảo một nhà ấm êm.",
        "luan": "Vợ chồng chia sẻ công việc rõ ràng, ít khi tranh chấp. Tài lộc tích lũy đều đặn, tuổi già hưởng phước an nhàn.",
        "danh_gia": "tốt", "diem": 1
    },

    # --- CAN KỶ ---
    ("Kỷ", "Tý"): {
        "danh_hieu": "Trung Hậu Vô Cương (Chậm mà chắc)",
        "tho": "Kỷ Tý duyên phận bền lâu,\nTrước tuy chật vật về sau sang giàu.\nTrời ban phúc lộc thâm sâu,\nCon ngoan trò giỏi cùng nhau sum vầy.",
        "luan": "Lúc trẻ kinh tế trung bình, nhưng nhờ tính chịu khó và cần kiệm nên về hậu vận tiền của dồi dào, gia đạo ấm êm.",
        "danh_gia": "tốt", "diem": 1
    },
    ("Kỷ", "Sửu"): {
        "danh_hieu": "Lưỡng Thổ Tương Sinh (Điền địa phì nhiêu)",
        "tho": "Kỷ Sửu hai nết chuyên cần,\nĐất đai màu mỡ muôn phần ấm no.\nChẳng màng sóng gió âu lo,\nThuyền về cập bến ấm no trọn đời.",
        "luan": "Vợ chồng hiền lành, chí thú làm ăn. Điền sản phong phú, của cải tích lũy vững chắc, con cái hiếu thuận.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Kỷ", "Dần"): {
        "danh_hieu": "Thảo Mộc Bám Đất (Cần khéo lựa lời)",
        "tho": "Kỷ Dần có lúc trái tai,\nLời qua tiếng lại chớ hoài hờn ghen.\nChữ Nhẫn rèn giũa cho quen,\nTrăm năm gìn giữ ánh đèn ấm êm.",
        "luan": "Đôi lúc nảy sinh mâu thuẫn do cách nghĩ khác nhau. Nếu biết lắng nghe và tôn trọng nhau thì gia đình rất vững bền.",
        "danh_gia": "trung bình", "diem": 0
    },
    ("Kỷ", "Mão"): {
        "danh_hieu": "Thổ Nhuận Mộc Vinh (Cây lành trái ngọt)",
        "tho": "Kỷ Mão duyên đẹp tươi màu,\nVợ chồng hòa thuận trước sau vẹn toàn.\nSinh con hiếu đễ ngoan ngoãn,\nCửa nhà êm ấm muôn vàn sắc xuân.",
        "luan": "Vợ chồng biết bù đắp khuyết điểm cho nhau. Kinh tế gia đình ổn định, con cái học hành thành đạt hiển vinh.",
        "danh_gia": "tốt", "diem": 1
    },
    ("Kỷ", "Thìn"): {
        "danh_hieu": "Đại Địa Sinh Kim (Phú quý tự nhiên)",
        "tho": "Kỷ Thìn duyên phận cao sang,\nĐồng tâm hiệp lực vẻ vang tông đường.\nTrăm năm trọn vẹn tình thương,\nCon đàn cháu đống ngát hương danh tài.",
        "luan": "Gia đạo phát đạt, làm ăn gặp nhiều quý nhân phù trợ. Hậu vận sung túc, con cháu vinh hiển rạng rỡ dòng họ.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Kỷ", "Tỵ"): {
        "danh_hieu": "Hỏa Nhiệt Đất Nồng (Vượng tài vượng lộc)",
        "tho": "Kỷ Tỵ hòa hợp duyên nồng,\nVợ chồng tâm đắc thỏa lòng ước mong.\nLàm ăn tài vận hanh thông,\nTuổi già nhàn hạ thong dong an nhàn.",
        "luan": "Tương sinh trợ lực rất mạnh, người vợ khéo léo mang lại tài khí cho chồng. Làm ăn buôn bán hanh thông đại phát.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Kỷ", "Ngọ"): {
        "danh_hieu": "Quang Minh Chính Đại (Ấm áp vinh hoa)",
        "tho": "Kỷ Ngọ se mối duyên lành,\nChung tay gầy dựng đắp thành cơ ngơi.\nCơm no áo ấm trọn đời,\nCon hiền cháu thảo rạng ngời mai sau.",
        "luan": "Gia đình có nề nếp và danh giá. Chồng thành đạt, vợ đảm đang, con cái ngoan ngoãn có học thức cao.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Kỷ", "Mùi"): {
        "danh_hieu": "Bách Niên Giai Lão (Hòa thuận dài lâu)",
        "tho": "Kỷ Mùi duyên thắm tròn đầy,\nBên nhau sớm tối đắp xây ân tình.\nTrời ban phúc lộc quang vinh,\nMột nhà êm ấm trọn tình trăm năm.",
        "luan": "Cực kỳ hòa hợp về tính cách, ít khi xảy ra mâu thuẫn lớn. Cuộc sống an nhàn, tiền bạc sung túc bền lâu.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Kỷ", "Thân"): {
        "danh_hieu": "Khai Sơn Đắc Ngọc (Lập thân thành danh)",
        "tho": "Kỷ Thân duyên nợ nhọc nhằn,\nThuở đầu vất vả nhọc nhằn gian lao.\nVề sau rực rỡ trăng sao,\nBạc vàng tích tụ dạt dào niềm vui.",
        "luan": "Thời trẻ chịu nhiều vất vả thử thách, nhưng đồng lòng vượt qua. Từ trung niên hưởng quả ngọt, phú quý an khang.",
        "danh_gia": "tốt", "diem": 1
    },
    ("Kỷ", "Dậu"): {
        "danh_hieu": "Thổ Sinh Kim Tú (Ngọc sáng trong nhà)",
        "tho": "Kỷ Dậu sum họp một nhà,\nCầm đường con thảo đậm đà sắc xuân.\nLộc tài phát đạt bội phần,\nTuổi già thanh thản hưởng ân phước trời.",
        "luan": "Vợ chồng nết na hiền hậu, đối đãi nội ngoại vẹn toàn. Kinh tế ổn định, hậu vận con cháu hiếu thảo phụng dưỡng.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Kỷ", "Tuất"): {
        "danh_hieu": "Chí Thành Tương Hợp (Vững chắc bền lâu)",
        "tho": "Kỷ Tuất gắn bó keo sơn,\nDù cho giông bão chẳng sờn lòng son.\nĐến ngày hoa nở cành non,\nCửa nhà ấm cúng cháu con ngoan hiền.",
        "luan": "Tình nghĩa sâu nặng, trước sau như một. Cùng nhau vượt qua mọi sóng gió để xây dựng cơ đồ vững chắc.",
        "danh_gia": "tốt", "diem": 1
    },
    ("Kỷ", "Hợi"): {
        "danh_hieu": "Phúc Thọ Khang Ninh (Bình an no ấm)",
        "tho": "Kỷ Hợi duyên nợ tuyệt trần,\nTrăm năm trọn vẹn muôn phần bình yên.\nCuộc đời phẳng lặng như thuyền,\nThuận buồm xuôi gió phước duyên tràn trề.",
        "luan": "Hôn nhân bình an, ít sóng gió. Kinh tế dư dả, con cái hiếu thuận, tuổi thọ dài lâu, hưởng phúc an nhàn.",
        "danh_gia": "rất tốt", "diem": 2
    },

    # --- CAN CANH ---
    ("Canh", "Tý"): {
        "danh_hieu": "Kim Thủy Tương Sinh (Thông tuệ tài hoa)",
        "tho": "Canh Tý duyên nợ vẹn mười,\nChồng tài vợ khéo rạng ngời tương lai.\nLộc tài thịnh vượng lâu dài,\nSinh con hiển đạt đức tài vẹn toàn.",
        "luan": "Cách cục rất đẹp, vợ chồng đều thông minh tháo vát. Công danh sự nghiệp phát đạt, con cái học hành đỗ đạt cao.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Canh", "Sửu"): {
        "danh_hieu": "Thổ Sinh Kim Bửu (Điền sản dồi dào)",
        "tho": "Canh Sửu hòa thuận ấm êm,\nBàn tay vun đắp ngày thêm vững vàng.\nNhà cao cửa rộng đàng hoàng,\nCon hiền cháu thảo vẻ vang một nhà.",
        "luan": "Vợ chồng chí thú làm ăn, điền sản đất đai tích lũy dồi dào. Gia đạo bình yên, hậu vận sung túc thịnh vượng.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Canh", "Dần"): {
        "danh_hieu": "Hổ Đới Kim Bài (Cần nhẫn nhường)",
        "tho": "Canh Dần tính khí cương cường,\nChồng bớt gắt gao vợ nhường đôi câu.\nCùng nhau tát cạn sông sâu,\nThì qua giông bão bạc đầu bình an.",
        "luan": "Cả hai đều có cá tính độc lập, dễ tranh cãi khi bàn việc lớn. Nếu người chồng bao dung và vợ khéo lựa lời thì sự nghiệp thăng tiến lớn.",
        "danh_gia": "trung bình", "diem": 0
    },
    ("Canh", "Mão"): {
        "danh_hieu": "Thiên Can Khắc Địa (Trước trắc trở sau yên)",
        "tho": "Canh Mão buổi sớm gian nan,\nChữ Nhẫn gìn giữ vượt ngàn khó khăn.\nĐến khi trăng tỏ cung hằng,\nBạc vàng tích tụ con ngoan rạng ngời.",
        "luan": "Thời trẻ dễ có bất đồng hoặc trắc trở tiền bạc. Cần kiên định gắn bó, qua tuổi 35 mọi sự hanh thông, hưởng phúc lộc.",
        "danh_gia": "trung bình", "diem": 0
    },
    ("Canh", "Thìn"): {
        "danh_hieu": "Long Bàn Hổ Cứ (Đại phú đại quý)",
        "tho": "Canh Thìn duyên phận huy hoàng,\nTrai tài gái sắc vẻ vang muôn phần.\nTrời ban phước lộc mùa xuân,\nCông thành danh toại bội phần hiển vinh.",
        "luan": "Cực kỳ hòa hợp về chí hướng, làm việc lớn ắt thành công. Tiền tài danh vọng song toàn, con cái đỗ đạt cao.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Canh", "Tỵ"): {
        "danh_hieu": "Kim Bị Hỏa Luyện (Thử thách thành danh)",
        "tho": "Canh Tỵ dẫu có phong ba,\nLòng vàng tôi luyện sáng lòa ánh mai.\nChung vai gánh vác tương lai,\nTừ trung niên bước lên đài vinh hoa.",
        "luan": "Lúc đầu gặp không ít khó khăn thử thách, nhưng nhờ sự thủy chung mà vượt qua. Hậu vận giàu sang phú quý.",
        "danh_gia": "tốt", "diem": 1
    },
    ("Canh", "Ngọ"): {
        "danh_hieu": "Lưỡng Kim Lưỡng Hỏa (Cần hòa khí)",
        "tho": "Canh Ngọ có lúc đổi dời,\nBên nhu bên cương trọn đời chở che.\nĐừng nghe ong bướm đồn hoe,\nMột lòng chung thủy vẹn bề tương lai.",
        "luan": "Đôi lúc có mâu thuẫn do tính tình thẳng thắn. Cần nhường nhịn nhau, chớ để người ngoài xen vào chuyện vợ chồng.",
        "danh_gia": "trung bình", "diem": 0
    },
    ("Canh", "Mùi"): {
        "danh_hieu": "Thổ Sinh Kim Bội (Phú túc an khang)",
        "tho": "Canh Mùi duyên thắm tình nồng,\nThuận vợ thuận chồng thỏa dạ ước mong.\nRuộng nương nhà cửa đầy đong,\nCon đàn cháu đống ấm lòng mẹ cha.",
        "luan": "Người vợ hiền thục mang lại phúc khí cho chồng. Làm ăn gặp nhiều may mắn, của cải tích lũy dồi dào, gia đạo ấm êm.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Canh", "Thân"): {
        "danh_hieu": "Lưỡng Kim Tương Trợ (Ý chí kiên cường)",
        "tho": "Canh Thân đôi cánh phượng hoàng,\nChung tay vượt hết gian nan hiểm nghèo.\nVề già của cải dồi dào,\nCháu con tấn tới tự hào tông gia.",
        "luan": "Hai người đều cứng cỏi, quyết đoán. Khi đã đồng lòng thì không khó khăn nào ngăn cản nổi. Kinh tế vững chắc.",
        "danh_gia": "tốt", "diem": 1
    },
    ("Canh", "Dậu"): {
        "danh_hieu": "Kim Ngọc Mãn Đường (Sáng rực gia phong)",
        "tho": "Canh Dậu hòa hợp keo sơn,\nTrăm năm trọn vẹn chẳng sờn lòng son.\nNhà cao cửa rộng cháu con,\nPhước lộc tài vận vẹn tròn ấm êm.",
        "luan": "Gia đình có nề nếp gia giáo, con cái hiếu thảo thành đạt. Tiền tài tích lũy vững vàng, tuổi già an nhàn.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Canh", "Tuất"): {
        "danh_hieu": "Thổ Kim Tương Đắc (Bền vững trăm năm)",
        "tho": "Canh Tuất gắn bó trọn đời,\nĐồng cam cộng khổ không rời nửa phân.\nĐến khi đón gió mùa xuân,\nBạc vàng đầy hũ muôn phần rạng danh.",
        "luan": "Tình nghĩa sâu đậm, vợ chồng vì nhau mà hy sinh phấn đấu. Cơ đồ ngày một lớn, hậu vận hiển vinh.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Canh", "Hợi"): {
        "danh_hieu": "Kim Thủy Tương Thao (Phúc lộc tràn trề)",
        "tho": "Canh Hợi duyên nợ tuyệt trần,\nTrời ban phúc ấm muôn phần tốt tươi.\nTrăm năm rộn rã tiếng cười,\nCon hiền cháu thảo rạng ngời mai sau.",
        "luan": "Hôn nhân viên mãn, tài lộc dồi dào. Gia đạo luôn tràn ngập tiếng cười, hậu vận sống thọ và giàu sang.",
        "danh_gia": "rất tốt", "diem": 2
    },

    # --- CAN TÂN ---
    ("Tân", "Tý"): {
        "danh_hieu": "Châu Ngọc Rạng Ngời (Vinh hoa ấm áp)",
        "tho": "Tân Tý duyên nợ thắm tươi,\nChồng tài vợ khéo trọn đời ấm êm.\nLộc tài ngày một dày thêm,\nCon ngoan cháu thảo êm đềm tháng năm.",
        "luan": "Vợ chồng hiểu ý nhau, cùng tính cẩn thận chu đáo. Kinh tế gia đình khấm khá, con cái đỗ đạt cao.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Tân", "Sửu"): {
        "danh_hieu": "Ngọc Ẩn Thổ Dày (Hậu vận đại phát)",
        "tho": "Tân Sửu tích lũy chuyên cần,\nĐất đai màu mỡ bội phần ấm no.\nTrung niên chẳng phải đắn đo,\nNgồi hưởng phước lộc trời cho vuông tròn.",
        "luan": "Cần cù chịu khó, ăn chắc mặc bền. Càng về già của cải càng phong phú, con cháu sum vầy hiếu thảo.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Tân", "Dần"): {
        "danh_hieu": "Hổ Đới Kim Đao (Cần hòa ái)",
        "tho": "Tân Dần tính nết đôi đường,\nBên nhu bên nhẫn mới tường ấm êm.\nChớ để giận dỗi dài thêm,\nThuận lòng trên dưới ấm êm cửa nhà.",
        "luan": "Đôi lúc khắc khẩu vì bất đồng quan điểm. Cần nhường nhịn nhau, người vợ khéo léo nhu hòa thì gia đạo ấm êm.",
        "danh_gia": "trung bình", "diem": 0
    },
    ("Tân", "Mão"): {
        "danh_hieu": "Kim Mộc Tương Khắc (Cần kiên nhẫn)",
        "tho": "Tân Mão duyên nợ ban đầu,\nĐôi phen vất vả dãi dầu gió sương.\nGiữ gìn trọn vẹn tình thương,\nVề sau phú quý ngát hương cơ đồ.",
        "luan": "Thời trẻ dễ gặp trắc trở tiền bạc hoặc tình cảm. Cần bao dung kiên nhẫn, trung hậu vận sẽ bình ổn khấm khá.",
        "danh_gia": "trung bình", "diem": 0
    },
    ("Tân", "Thìn"): {
        "danh_hieu": "Thổ Sinh Kim Bửu (Phú quý vinh hoa)",
        "tho": "Tân Thìn sum họp một nhà,\nLộc tài phát đạt gần xa ngợi khen.\nDù cho gặp lúc chông chênh,\nĐồng lòng vượt thác ấm êm muôn phần.",
        "luan": "Cách cục rất đẹp, vợ chồng tương trợ đắc lực. Chồng công danh thăng tiến, vợ đảm đang hậu phương vững chắc.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Tân", "Tỵ"): {
        "danh_hieu": "Lửa Trui Rèn Bạc (Thành quả ngọt ngào)",
        "tho": "Tân Tỵ trải bước gập ghềnh,\nTình duyên gắn chặt lênh đênh chẳng màng.\nSau cơn giông tố gió ngàn,\nThuyền về bến đỗ ngập tràn sắc xuân.",
        "luan": "Khó khăn thử thách thời trẻ rèn đúc bản lĩnh. Về hậu vận tài lộc vững chắc, con cái thành đạt hiển vinh.",
        "danh_gia": "tốt", "diem": 1
    },
    ("Tân", "Ngọ"): {
        "danh_hieu": "Kim Phùng Liệt Hỏa (Cần mềm mỏng)",
        "tho": "Tân Ngọ đôi lúc gắt gao,\nChồng bớt nóng nảy vợ chào ngọt ngon.\nThương nhau giữ trọn lòng son,\nCửa nhà ấm cúng cháu con thảo hiền.",
        "luan": "Cần học cách kiềm chế cảm xúc khi giận. Vợ chồng hiểu và tôn trọng nhau thì gia đình ấm êm, của cải phong túc.",
        "danh_gia": "trung bình", "diem": 0
    },
    ("Tân", "Mùi"): {
        "danh_hieu": "Thổ Nhuận Sinh Kim (Phúc lộc tự nhiên)",
        "tho": "Tân Mùi duyên nợ vuông tròn,\nTình sâu nghĩa nặng như non cao vời.\nTrời ban phúc lộc rạng ngời,\nTuổi già thanh thản thảnh thơi an nhàn.",
        "luan": "Vợ hiền dâu thảo, chồng có chí lớn. Cuộc sống an nhàn, tiền tài tích lũy vững vàng, con cháu thảo hiền.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Tân", "Thân"): {
        "danh_hieu": "Lưỡng Kim Thành Khí (Chí lớn thành công)",
        "tho": "Tân Thân gắn bó keo sơn,\nDù cho giông bão chẳng sờn lòng son.\nĐến ngày trăng tỏ vuông tròn,\nGia đình hạnh phúc cháu con sum vầy.",
        "luan": "Hai người đều tháo vát, nhanh nhẹn. Làm ăn kinh doanh buôn bán rất hợp, tài chính vững vàng.",
        "danh_gia": "tốt", "diem": 1
    },
    ("Tân", "Dậu"): {
        "danh_hieu": "Châu Sa Ngọc Báu (Quý hiển giàu sang)",
        "tho": "Tân Dậu đẹp mối tơ duyên,\nTrăm năm trọn vẹn bình yên một nhà.\nCon ngoan cháu thảo hiền hòa,\nGia môn rạng rỡ nở hoa thái bình.",
        "luan": "Gia đình danh giá, vợ chồng tương kính như tân. Tài lộc sung túc, con cái ngoan ngoãn có học thức cao.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Tân", "Tuất"): {
        "danh_hieu": "Thổ Kim Hòa Hợp (Bền vững dài lâu)",
        "tho": "Tân Tuất duyên thắm dài lâu,\nChẳng màng bão táp cơ cầu gian nan.\nMột nhà đầy ắp bình an,\nPhước tài như nước dâng tràn bờ đê.",
        "luan": "Rất thủy chung và biết chia sẻ. Gia đạo bình yên, tai ương đều hóa cát, con cháu làm rạng rỡ tổ tông.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Tân", "Hợi"): {
        "danh_hieu": "Kim Thủy Tương Đắc (Phúc thọ song toàn)",
        "tho": "Tân Hợi duyên nợ tuyệt trần,\nTrăm năm trọn vẹn muôn phần bình yên.\nCuộc đời phẳng lặng như thuyền,\nThuận buồm xuôi gió phước duyên tràn trề.",
        "luan": "Hôn nhân viên mãn, tài lộc dồi dào. Gia đạo luôn ấm êm, tuổi già hưởng phước an nhàn và trường thọ.",
        "danh_gia": "rất tốt", "diem": 2
    },

    # --- CAN NHÂM ---
    ("Nhâm", "Tý"): {
        "danh_hieu": "Lưỡng Thủy Thành Giang (Sóng lớn cần chèo)",
        "tho": "Nhâm Tý nước lớn mênh mông,\nChèo khéo thì vượt muôn dòng phong ba.\nĐồng lòng tát cạn bến xa,\nVề sau phú quý một nhà ấm êm.",
        "luan": "Cả hai đều thông minh, hoạt bát. Đôi lúc có sóng gió tiền tài nhưng nhờ tài trí mà vượt qua, trung hậu vận giàu sang.",
        "danh_gia": "tốt", "diem": 1
    },
    ("Nhâm", "Sửu"): {
        "danh_hieu": "Thủy Đáo Sơn Điền (Ăn chắc mặc bền)",
        "tho": "Nhâm Sửu cần kiệm chuyên cần,\nĐắp bồi gia đạo muôn phần ấm êm.\nLộc tài ngày một dày thêm,\nHậu vận sung túc êm đềm tháng năm.",
        "luan": "Vợ chồng chịu khó tích lũy, điền sản đất đai dồi dào. Hậu vận an nhàn, con cái hiếu đễ.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Nhâm", "Dần"): {
        "danh_hieu": "Thủy Mộc Tương Sinh (Rạng danh sự nghiệp)",
        "tho": "Nhâm Dần duyên nợ tươi màu,\nVợ chồng hòa thuận trước sau một lòng.\nLàm ăn may mắn hanh thông,\nCon ngoan trò giỏi rạng dòng tộc gia.",
        "luan": "Tương sinh đắc lực, công danh sự nghiệp phát đạt nhanh chóng. Con cái thông minh tài giỏi.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Nhâm", "Mão"): {
        "danh_hieu": "Thủy Nhuận Mộc Tươi (Gia đạo an vui)",
        "tho": "Nhâm Mão duyên đẹp vô ngần,\nTrăm năm gắn bó muôn phần yêu thương.\nCuộc đời phẳng lặng như gương,\nTuổi già an lạc thọ trường bình an.",
        "luan": "Vợ chồng ôn hòa, tình cảm sâu đậm. Gia đình đầm ấm, tiền bạc dư dả, con cái ngoan ngoãn.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Nhâm", "Thìn"): {
        "danh_hieu": "Long Quy Hải Giới (Đại phát công danh)",
        "tho": "Nhâm Thìn như rồng về khơi,\nVẫy vùng sông biển rạng ngời công danh.\nVợ chồng trọn nghĩa ân tình,\nPhú quý vinh hiển rạng danh tông đường.",
        "luan": "Cách cục đại cát, người chồng làm nên việc lớn, người vợ quản xuyến chu toàn. Con cháu đỗ đạt cao.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Nhâm", "Tỵ"): {
        "danh_hieu": "Thủy Hỏa Tương Khắc (Cần mềm mỏng)",
        "tho": "Nhâm Tỵ đôi lúc đổi dời,\nLời ăn tiếng nói trọn đời lựa khuyên.\nChữ Nhẫn giữ mối tơ duyên,\nTrăm năm hòa thuận ấm êm cửa nhà.",
        "luan": "Đôi lúc có bất đồng ý kiến. Cần nhẫn nại lắng nghe nhau thì mọi sự hanh thông, tài lộc dồi dào.",
        "danh_gia": "trung bình", "diem": 0
    },
    ("Nhâm", "Ngọ"): {
        "danh_hieu": "Thủy Hỏa Tương Giao (Điều hòa viên mãn)",
        "tho": "Nhâm Ngọ nước lửa giao hòa,\nChồng cương vợ nhu một nhà bình an.\nChung tay vượt hết gian nan,\nVề sau phú quý ngập tràn sắc xuân.",
        "luan": "Tuy hai tính cách khác nhau nhưng biết bù trừ cho nhau. Kinh tế khấm khá, con cái hiển đạt.",
        "danh_gia": "tốt", "diem": 1
    },
    ("Nhâm", "Mùi"): {
        "danh_hieu": "Thổ Nạp Thủy Nhuận (Ruộng vườn xanh tốt)",
        "tho": "Nhâm Mùi duyên thắm tình nồng,\nThuận vợ thuận chồng thỏa dạ ước mong.\nLúa vàng trĩu hạt bờ sông,\nGia đình hạnh phúc thong dong an nhàn.",
        "luan": "Vợ chồng thuận hòa, làm ăn phát tài. Cuộc sống bình an ấm no, hậu vận con cháu hiếu kính.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Nhâm", "Thân"): {
        "danh_hieu": "Kim Sinh Thủy Tráng (Nguồn nước vô tận)",
        "tho": "Nhâm Thân suối chảy ngút ngàn,\nTiền tài tuôn chảy dâng tràn bờ đê.\nVợ chồng son sắt lời thề,\nTrăm năm trọn vẹn đề huề cháu con.",
        "luan": "Rất vượng về tài lộc kinh doanh. Hai vợ chồng đều có tài mưu lược, cuộc sống giàu sang phú quý.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Nhâm", "Dậu"): {
        "danh_hieu": "Kim Bạch Thủy Thanh (Trong sáng vinh hoa)",
        "tho": "Nhâm Dậu duyên phận vuông tròn,\nVợ hiền dâu thảo sắt son một lòng.\nLàm ăn tài vận hanh thông,\nTuổi già thanh bạch thong dong an nhàn.",
        "luan": "Tương sinh tốt đẹp, gia đình có gia phong nề nếp. Con cái hiếu thảo thành đạt, hậu vận thảnh thơi.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Nhâm", "Tuất"): {
        "danh_hieu": "Đê Điều Giữ Nước (Ăn chắc bền lâu)",
        "tho": "Nhâm Tuất cần kiệm sớm hôm,\nBao năm vất vả vuông tròn ấm êm.\nLộc tài ngày một dày thêm,\nHậu vận sung túc êm đềm tháng năm.",
        "luan": "Vợ chồng chia sẻ ngọt bùi, cùng lo toan vun vén. Kinh tế ngày càng đi lên, tuổi già hưởng phước.",
        "danh_gia": "tốt", "diem": 1
    },
    ("Nhâm", "Hợi"): {
        "danh_hieu": "Đại Hải Mênh Mông (Phúc trạch vô biên)",
        "tho": "Nhâm Hợi biển rộng trời cao,\nPhúc lộc tài vận dạt dào muôn phương.\nTrăm năm gắn bó yêu thương,\nCon đàn cháu đống ngát hương danh tài.",
        "luan": "Đại cát cách cục, tài lộc dồi dào như nước thủy triều. Vợ chồng hòa thuận trường thọ, con cháu vinh hiển.",
        "danh_gia": "rất tốt", "diem": 2
    },

    # --- CAN QUÝ ---
    ("Quý", "Tý"): {
        "danh_hieu": "Lưỡng Thủy Tương Phùng (Dung hòa khéo léo)",
        "tho": "Quý Tý duyên phận êm trôi,\nThông minh lanh lợi sánh đôi cùng đường.\nTrời ban phúc lộc thọ trường,\nGia môn hưng thịnh ngát hương danh tài.",
        "luan": "Hai người đều thông minh, nhanh nhạy với thời cuộc. Gia đạo đầm ấm, kinh tế khá giả, con cái đỗ đạt cao.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Quý", "Sửu"): {
        "danh_hieu": "Thủy Nhuận Đất Nồng (Điền sản trù phú)",
        "tho": "Quý Sửu duyên thắm dài lâu,\nCần cù tích lũy trước sau vẹn toàn.\nMột nhà đầy ắp bình an,\nPhước tài như nước dâng tràn bờ đê.",
        "luan": "Rất hợp ý nhau trong việc quản lý tài chính và mua sắm đất đai. Hậu vận sung túc, con cái ngoan hiền.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Quý", "Dần"): {
        "danh_hieu": "Thủy Dưỡng Mộc Sinh (Công danh rạng rỡ)",
        "tho": "Quý Dần như nước tưới cây,\nMùa xuân hoa nở sum vầy yêu thương.\nCông danh sự nghiệp thênh thang,\nCon hiền cháu thảo vẻ vang tông đường.",
        "luan": "Tương sinh trợ lực rất tốt, người vợ hỗ trợ chồng phát triển công danh rực rỡ. Gia đạo hưng vượng.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Quý", "Mão"): {
        "danh_hieu": "Xuân Phong Vũ Lộ (Ấm áp chan hòa)",
        "tho": "Quý Mão duyên đẹp lứa đôi,\nTrăm năm trọn vẹn đứng ngồi có nhau.\nTóc xanh cho đến bạc đầu,\nTình nồng nghĩa đượm bền lâu muôn đời.",
        "luan": "Cuộc sống hôn nhân ngọt ngào, êm đềm. Vợ chồng hiểu nhau sâu sắc, con cái ngoan ngoãn hiếu thảo.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Quý", "Thìn"): {
        "danh_hieu": "Thủy Tụ Long Môn (Tài vận dồi dào)",
        "tho": "Quý Thìn duyên phận cao sang,\nChung tay gầy dựng đàng hoàng tương lai.\nLộc tài vượng phát lâu dài,\nCháu con tấn tới đức tài song toàn.",
        "luan": "Làm ăn gặp nhiều may mắn, có lộc đất đai và tài chính. Hậu vận hiển vinh, con cháu thành đạt.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Quý", "Tỵ"): {
        "danh_hieu": "Thủy Hỏa Ký Tế (Khéo lựa lời ăn tiếng nói)",
        "tho": "Quý Tỵ đôi lúc băn khoăn,\nChữ Nhẫn gìn giữ khó khăn cũng lùi.\nBên nhau chia ngọt sẻ bùi,\nTrăm năm gắn bó ngọt bùi dài lâu.",
        "luan": "Đôi lúc có cãi vã nhỏ vì tính tình khác biệt. Cần nhường nhịn nhau thì tài vận phát triển rất mạnh mẽ.",
        "danh_gia": "tốt", "diem": 1
    },
    ("Quý", "Ngọ"): {
        "danh_hieu": "Thủy Hỏa Tương Xung (Cần bao dung)",
        "tho": "Quý Ngọ tính khí khác xa,\nNhịn nhau một tiếng cửa nhà yên vui.\nĐừng để giận dỗi lui tới,\nThương nhau trọn vẹn sáng ngời nghĩa ân.",
        "luan": "Dễ xung đột ý kiến khi cùng quyết định việc lớn. Cần phân định rõ vai trò và lắng nghe đối phương.",
        "danh_gia": "ít hợp", "diem": -1
    },
    ("Quý", "Mùi"): {
        "danh_hieu": "Thủy Thổ Tương Hòa (Ấm êm no đủ)",
        "tho": "Quý Mùi duyên thắm tình nồng,\nThuận vợ thuận chồng tát biển cũng vơi.\nSinh con thảo hiền rạng ngời,\nTuổi già thanh thản thảnh thơi an nhàn.",
        "luan": "Gia đình bình dị mà ấm áp. Vợ chồng chăm chỉ làm ăn, của cải tích lũy vững chắc, con cái hiếu thảo.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Quý", "Thân"): {
        "danh_hieu": "Kim Thủy Tương Sinh (Đại phát tài danh)",
        "tho": "Quý Thân như cá gặp nguồn,\nTiền tài danh vọng chẳng buôn cũng về.\nVợ chồng son sắt lời thề,\nTrăm năm trọn vẹn đề huề cháu con.",
        "luan": "Cách cục rất đẹp cho sự nghiệp và kinh doanh. Vợ chồng trợ giúp nhau đắc lực, hậu vận đại phú đại quý.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Quý", "Dậu"): {
        "danh_hieu": "Châu Ngọc Rạng Ngời (Vinh hiển dài lâu)",
        "tho": "Quý Dậu sum họp một nhà,\nCầm đường con thảo đậm đà sắc xuân.\nLộc tài phát đạt bội phần,\nTuổi già thanh thản hưởng ân phước trời.",
        "luan": "Gia đình nề nếp, vợ chồng tương kính như tân. Tiền tài tích lũy phong phú, con cái đỗ đạt cao.",
        "danh_gia": "rất tốt", "diem": 2
    },
    ("Quý", "Tuất"): {
        "danh_hieu": "Thủy Tụ Sa Bồi (Trung niên phát đạt)",
        "tho": "Quý Tuất duyên nợ nhọc nhằn,\nThuở đầu vất vả nhọc nhằn gian lao.\nVề sau rực rỡ trăng sao,\nBạc vàng tích tụ dạt dào niềm vui.",
        "luan": "Buổi đầu có phen gian nan về tiền bạc. Nhưng càng về sau càng khấm khá, con cháu thành danh hiển đạt.",
        "danh_gia": "tốt", "diem": 1
    },
    ("Quý", "Hợi"): {
        "danh_hieu": "Vạn Xuyên Quy Hải (Phúc lộc vô biên)",
        "tho": "Quý Hợi muôn suối về sông,\nTrăm năm hòa thuận thỏa lòng ước mong.\nRuộng vườn của cải đầy đong,\nCon đàn cháu đống tươi hồng sắc xuân.",
        "luan": "Hôn nhân trọn vẹn, phúc lộc dồi dào. Gia đạo bình an, trường thọ và giàu có, con cháu rạng danh dòng tộc.",
        "danh_gia": "rất tốt", "diem": 2
    },
}


def tra_cao_ly(can_chong: str, chi_vo: str) -> dict:
    """Tra cứu duyên nợ theo Cao Ly Đầu Hình (Can chồng phối Chi vợ)."""
    key = (can_chong, chi_vo)
    if key in CAO_LY_DATA:
        return {"can_chong": can_chong, "chi_vo": chi_vo, **CAO_LY_DATA[key]}
    # Dự phòng an toàn nếu cặp lạ
    return {
        "can_chong": can_chong, "chi_vo": chi_vo,
        "danh_hieu": f"Duyên nợ Canh {can_chong} — {chi_vo}",
        "tho": f"{can_chong} phối {chi_vo} nghĩa tương thân,\nTrăm năm giữ trọn chữ ân trong lòng.\nThuận vợ thuận chồng hanh thông,\nCửa nhà ấm cúng cháu con thảo hiền.",
        "luan": f"Người chồng can {can_chong} kết duyên cùng vợ tuổi {chi_vo}. Cần giữ gìn chữ Nhẫn, tôn trọng lẫn nhau thì gia đạo bình yên, tài lộc bền vững.",
        "danh_gia": "tốt", "diem": 1
    }
