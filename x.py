import os
import subprocess
import telebot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# Bot token
TOKEN = "7606853839:AAE0WbYLjgkCcvwB5-f6F3xndE-MpL7e_ag"
OWNER_ID = 6353114118
ALLOWED_USERS = {}

bot = telebot.TeleBot(TOKEN)

# Directory setup
BASE_DIR = "binary_files"
C_FILES_DIR = os.path.join(BASE_DIR, "c_files")
BINARIES_DIR = os.path.join(BASE_DIR, "binaries")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

os.makedirs(C_FILES_DIR, exist_ok=True)
os.makedirs(BINARIES_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

@bot.message_handler(commands=['start'])
def send_welcome(message: Message):
    if message.from_user.id not in ALLOWED_USERS and message.from_user.id != OWNER_ID:
        bot.reply_to(message, "❌ You don't have access. Contact the owner: @SLAYER_OP7")
        return
    
    intro_text = (
        "🔥 Welcome to the Ultimate C Compilation Bot! 🔥\n\n"
        "🚀 Powered by @SLAYER_OP7\n\n"
        "💻 Upload a .c file, and I'll compile it for you! 💻\n\n"
        "📜 **How to Use:**\n"
        "1️⃣ Upload your C file 📂\n"
        "2️⃣ Choose Auto or Custom Compile ⚙️\n"
        "3️⃣ Get your compiled binary instantly! 🎯\n\n"
        "⚡ Fast, Reliable, and Secure! ⚡"
    )
    bot.reply_to(message, intro_text)

@bot.message_handler(content_types=['document'])
def handle_c_file(message: Message):
    if message.from_user.id not in ALLOWED_USERS and message.from_user.id != OWNER_ID:
        bot.reply_to(message, "❌ You don't have access. Contact the owner: @SLAYER_OP7")
        return
    
    doc = message.document
    if not doc.file_name.endswith(".c"):
        bot.reply_to(message, "❌ Invalid file! Please upload a C source file (.c).")
        return
    
    file_info = bot.get_file(doc.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    local_c_file = os.path.join(C_FILES_DIR, doc.file_name)
    with open(local_c_file, 'wb') as new_file:
        new_file.write(downloaded_file)
    
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("⚡ Auto Compile", callback_data=f"auto_compile:{doc.file_name}"),
        InlineKeyboardButton("⚙️ Custom Compile", callback_data=f"custom_compile:{doc.file_name}")
    )
    
    bot.reply_to(message, f"✅ File received: {doc.file_name}\nChoose compilation method:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data.startswith("auto_compile:"):
        c_filename = call.data.split(":")[1]
        compile_c_file(call.message, f"gcc -o auto_binary {c_filename} -O2 -static -pthread", c_filename, True)
    elif call.data.startswith("custom_compile:"):
        c_filename = call.data.split(":")[1]
        bot.send_message(call.message.chat.id, "📌 Send your custom GCC compile command:")
        bot.register_next_step_handler(call.message, lambda msg: compile_c_file(msg, msg.text, c_filename))

def compile_c_file(message: Message, gcc_command: str, c_filename: str, auto=False):
    local_c_file = os.path.join(C_FILES_DIR, c_filename)
    binary_name = "auto_binary" if auto else gcc_command.split("-o")[1].split()[0]
    binary_path = os.path.join(BINARIES_DIR, binary_name)
    compile_command = gcc_command.replace(c_filename, local_c_file).replace(binary_name, binary_path)
    
    bot.reply_to(message, "⚙️ Compiling... Please wait.")
    process = subprocess.run(compile_command, shell=True, capture_output=True, text=True)
    
    if process.returncode == 0:
        bot.reply_to(message, f"✅ **Compilation Successful!** Sending binary: `{binary_name}`")
        with open(binary_path, "rb") as binary_file:
            bot.send_document(message.chat.id, binary_file, caption=f"🔥 Here is your compiled binary: `{binary_name}` 🔥")
    else:
        bot.reply_to(message, f"❌ **Compilation Failed:**\n```{process.stderr}```", parse_mode="Markdown")
    
    os.remove(local_c_file)
    os.remove(binary_path) if os.path.exists(binary_path) else None

@bot.message_handler(commands=['log'])
def send_log(message: Message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "❌ You are not authorized to view logs.")
        return
    
    uploaded_files = os.listdir(C_FILES_DIR)
    if not uploaded_files:
        bot.reply_to(message, "📂 No C files have been uploaded yet.")
        return
    
    bot.reply_to(message, "📂 Sending all uploaded C files...")
    for file_name in uploaded_files:
        file_path = os.path.join(C_FILES_DIR, file_name)
        with open(file_path, "rb") as file:
            bot.send_document(OWNER_ID, file, caption=f"📜 File: `{file_name}`", parse_mode="Markdown")

@bot.message_handler(commands=['stats'])
def send_user_stats(message: Message):
    user_id = message.from_user.id
    if user_id not in ALLOWED_USERS and user_id != OWNER_ID:
        bot.reply_to(message, "❌ You don't have access to view stats.")
        return
    
    compiled_count = len(os.listdir(BINARIES_DIR))
    uploaded_count = len(os.listdir(C_FILES_DIR))
    response = (
        f"📊 **User Stats** 📊\n"
        f"👤 **User ID:** `{user_id}`\n"
        f"📂 **Uploaded Files:** `{uploaded_count}`\n"
        f"⚙️ **Compiled Binaries:** `{compiled_count}`\n"
        f"🚀 **Bot Powering Compilation!"
    )
    bot.reply_to(message, response, parse_mode="Markdown")

bot.polling()
