from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# ====== CẤU HÌNH ======
TOKEN = "8062649575:AAFspL7tJbXjldtilTeRjZZk1NpNKeqs6e8"
SUNWIN_API = "https://sunwinsaygex-pcl2.onrender.com/api/sun"
LC79_API = "https://lc79md5-lun8.onrender.com/lc79md5"
N = 20  # số phiên thống kê SUNWIN
# ======================

# ====== MENU ======
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⚙️ Tool", callback_data="tool")]
    ])

def tool_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎯 SUNWIN", callback_data="sunwin")],
        [InlineKeyboardButton("🎰 LC79", callback_data="lc79")],
        [InlineKeyboardButton("⬅️ Quay lại", callback_data="back_main")]
    ])

def sunwin_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎯 Sunwin Tài Xỉu", callback_data="sunwin_tx")],
        [InlineKeyboardButton("⬅️ Quay lại", callback_data="tool")]
    ])

def sunwin_result_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Gửi Phiên Mới", callback_data="sunwin_tx")],
        [
            InlineKeyboardButton("⬅️ Quay lại", callback_data="sunwin"),
            InlineKeyboardButton("🏠 Menu chính", callback_data="back_main")
        ]
    ])

def lc79_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔐 LC79 MD5", callback_data="lc79_md5")],
        [InlineKeyboardButton("⬅️ Quay lại", callback_data="tool")]
    ])

def lc79_result_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Gửi Phiên Mới", callback_data="lc79_md5")],
        [
            InlineKeyboardButton("⬅️ Quay lại", callback_data="tool"),
            InlineKeyboardButton("🏠 Menu chính", callback_data="back_main")
        ]
    ])

# ====== SUNWIN LOGIC (KHÔNG RANDOM) ======
def get_sunwin_stat():
    history = []
    last = None
    for _ in range(N):
        r = requests.get(SUNWIN_API, timeout=5)
        r.raise_for_status()
        data = r.json()
        history.append(data["ket_qua"])
        last = data

    tai = history.count("Tài")
    xiu = history.count("Xỉu")
    tai_pct = round(tai / N * 100)
    xiu_pct = round(xiu / N * 100)
    return last, tai_pct, xiu_pct

def format_sunwin_message():
    last, tai_pct, xiu_pct = get_sunwin_stat()

    # Quyết định theo thuật toán
    if tai_pct > xiu_pct:
        pick = f"TÀI ({tai_pct}%)"
    elif xiu_pct > tai_pct:
        pick = f"XỈU ({xiu_pct}%)"
    else:
        # 50-50 → đảo theo phiên trước
        if last["ket_qua"] == "Tài":
            pick = "XỈU (50%)"
        else:
            pick = "TÀI (50%)"

    text = (
        "🎯 ----- DỰ ĐOÁN SUNWIN PHIÊN HIỆN TẠI -----\n\n"
        "=== KẾT QUẢ PHIÊN TRƯỚC ===\n"
        f"Phiên: {last['phien']}\n"
        f"Xúc Xắc: {last['xuc_xac_1']}-{last['xuc_xac_2']}-{last['xuc_xac_3']}\n"
        f"Tổng: {last['ket_qua']}\n\n"
        "=== DỰ ĐOÁN PHIÊN HIỆN TẠI ===\n"
        f"Phiên: {last['phien_hien_tai']}\n"
        f"Dự đoán: {pick}\n\n"
        "⚠️ Chỉ mang tính tham khảo"
    )
    return text

# ====== LC79 LOGIC ======
def format_lc79_message():
    r = requests.get(LC79_API, timeout=5)
    r.raise_for_status()
    data = r.json()
    text = (
        "🎰 ----- LC79 MD5 -----\n\n"
        f"Phiên: {data.get('phien', 'N/A')}\n"
        f"MD5: {data.get('md5', 'N/A')}\n"
        f"Kết quả: {data.get('ket_qua', 'N/A')}\n\n"
        "⚠️ Chỉ mang tính tham khảo"
    )
    return text

# ====== HANDLERS ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔹 MENU BOT 🔹\nChọn chức năng 👇",
        reply_markup=main_menu()
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    try:
        if q.data == "tool":
            await q.edit_message_text("⚙️ TOOL\nChọn game 👇", reply_markup=tool_menu())

        elif q.data == "sunwin":
            await q.edit_message_text("🎯 SUNWIN\nChọn loại 👇", reply_markup=sunwin_menu())

        elif q.data == "sunwin_tx":
            msg = format_sunwin_message()
            await q.edit_message_text(msg, reply_markup=sunwin_result_menu())

        elif q.data == "lc79":
            await q.edit_message_text("🎰 LC79\nChọn tool 👇", reply_markup=lc79_menu())

        elif q.data == "lc79_md5":
            msg = format_lc79_message()
            await q.edit_message_text(msg, reply_markup=lc79_result_menu())

        elif q.data == "back_main":
            await q.edit_message_text(
                "🔹 MENU BOT 🔹\nChọn chức năng 👇",
                reply_markup=main_menu()
            )
    except Exception as e:
        await q.edit_message_text(
            "❌ Lỗi xử lý. Thử lại.",
            reply_markup=main_menu()
        )

# ====== RUN ======
app = ApplicationBuilder().token(TOKEN).build()
app.add_ha