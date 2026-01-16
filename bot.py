import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

# ====== CẤU HÌNH ======
TOKEN = os.getenv("8392947840:AAEqDR_DXzwvoxiIg6Ze7AHtFgJm---fDRg")  # Token lấy từ Environment Variables trên Render
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


# ====== SUNWIN LOGIC ======
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

    if tai_pct > xiu_pct:
        pick = f"TÀI ({tai_pct}%)"
    elif xiu_pct > tai_pct:
        pick = f"XỈU ({xiu_pct}%)"
    else:
        pick = "TÀI hoặc XỈU (50%)"

    text = (
        "🎯 ----- SUNWIN (DEMO) -----\n\n"
        "=== KẾT QUẢ GẦN NHẤT ===\n"
        f"Phiên: {last.get('phien', 'N/A')}\n"
        f"Xúc Xắc: {last.get('xuc_xac_1','?')}-"
        f"{last.get('xuc_xac_2','?')}-"
        f"{last.get('xuc_xac_3','?')}\n"
        f"Kết quả: {last.get('ket_qua','N/A')}\n\n"
        "=== THỐNG KÊ ===\n"
        f"Tài: {tai_pct}%\n"
        f"Xỉu: {xiu_pct}%\n\n"
        "=== GỢI Ý (CHỈ THAM KHẢO) ===\n"
        f"{pick}\n\n"
        "⚠️ Chỉ dùng cho học tập, không dùng cho cá cược!"
    )
    return text


# ====== LC79 LOGIC ======
def format_lc79_message():
    r = requests.get(LC79_API, timeout=5)
    r.raise_for_status()
    data = r.json()

    text = (
        "🎰 ----- LC79 MD5 (DEMO) -----\n\n"
        f"Phiên: {data.get('phien', 'N/A')}\n"
        f"MD5: {data.get('md5', 'N/A')}\n"
        f"Kết quả: {data.get('ket_qua', 'N/A')}\n\n"
        "⚠️ Chỉ dùng cho học tập, không dùng cho cá cược!"
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
            "❌ Có lỗi xảy ra, thử lại.",
            reply_markup=main_menu()
        )


# ====== RUN BOT ======
def main():
    if not TOKEN:
        print("❌ Chưa có BOT_TOKEN trong Environment Variables")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    print("🤖 Bot is running...")
    app.run_polling()
import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

# ====== CẤU HÌNH ======
TOKEN = os.getenv("BOT_TOKEN")  # Token lấy từ Environment Variables trên Render
SUNWIN_API = "https://sunwinsaygex-pcl2.onrender.com/api/sun"
LC79_API = "https://lc79md5-lun8.onrender.com/lc79md5"
N = 5  # giảm xuống để tránh spam API
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


# ====== SUNWIN LOGIC ======
def get_sunwin_stat():
    history = []
    last = None

    for _ in range(N):
        try:
            r = requests.get(SUNWIN_API, timeout=5)
            r.raise_for_status()
            data = r.json()
            history.append(data.get("ket_qua", "N/A"))
            last = data
        except:
            continue

    if not history or not last:
        return None, 0, 0

    tai = history.count("Tài")
    xiu = history.count("Xỉu")
    tai_pct = round(tai / len(history) * 100)
    xiu_pct = round(xiu / len(history) * 100)

    return last, tai_pct, xiu_pct


def format_sunwin_message():
    last, tai_pct, xiu_pct = get_sunwin_stat()

    if not last:
        return "❌ Không lấy được dữ liệu SUNWIN, thử lại sau."

    if tai_pct > xiu_pct:
        pick = f"TÀI ({tai_pct}%)"
    elif xiu_pct > tai_pct:
        pick = f"XỈU ({xiu_pct}%)"
    else:
        pick = "TÀI hoặc XỈU (50%)"

    text = (
        "🎯 ----- SUNWIN (DEMO) -----\n\n"
        "=== KẾT QUẢ GẦN NHẤT ===\n"
        f"Phiên: {last.get('phien', 'N/A')}\n"
        f"Xúc Xắc: {last.get('xuc_xac_1','?')}-"
        f"{last.get('xuc_xac_2','?')}-"
        f"{last.get('xuc_xac_3','?')}\n"
        f"Kết quả: {last.get('ket_qua','N/A')}\n\n"
        "=== THỐNG KÊ ===\n"
        f"Tài: {tai_pct}%\n"
        f"Xỉu: {xiu_pct}%\n\n"
        "=== GỢI Ý (CHỈ THAM KHẢO) ===\n"
        f"{pick}\n\n"
        "⚠️ Chỉ dùng cho học tập, không dùng cho cá cược!"
    )
    return text


# ====== LC79 LOGIC ======
def format_lc79_message():
    try:
        r = requests.get(LC79_API, timeout=5)
        r.raise_for_status()
        data = r.json()
    except:
        return "❌ Không lấy được dữ liệu LC79, thử lại sau."

    text = (
        "🎰 ----- LC79 MD5 (DEMO) -----\n\n"
        f"Phiên: {data.get('phien', 'N/A')}\n"
        f"MD5: {data.get('md5', 'N/A')}\n"
        f"Kết quả: {data.get('ket_qua', 'N/A')}\n\n"
        "⚠️ Chỉ dùng cho học tập, không dùng cho cá cược!"
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
    except Exception:
        await q.edit_message_text(
            "❌ Có lỗi xảy ra, thử lại.",
            reply_markup=main_menu()
        )


# ====== RUN BOT ======
def main():
    if not TOKEN:
        print("❌ Chưa có BOT_TOKEN trong Environment Variables")
        return

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    print("🤖 Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
