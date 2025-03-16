import os
import subprocess
import telebot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

token = "7606853839:AAE0WbYLjgkCcvwB5-f6F3xndE-MpL7e_ag"
owner_id = 6353114118
admins = set()
allowed_users = {}
bot = telebot.TeleBot(token)

base_dir = "binary_files"
c_files_dir = os.path.join(base_dir, "c_files")
binaries_dir = os.path.join(base_dir, "binaries")
logs_dir = os.path.join(base_dir, "logs")

os.makedirs(c_files_dir, exist_ok=True)
os.makedirs(binaries_dir, exist_ok=True)
os.makedirs(logs_dir, exist_ok=True)

@bot.message_handler(commands=['start'])
def send_welcome(message: Message):
    if message.from_user.id not in allowed_users and message.from_user.id != owner_id:
        bot.reply_to(message, "❌ You don't have access. Contact the owner to get access ✅ @SLAYER_OP7")
        return
    intro_text = (
        "🔥🔥 WELCOME TO THE ULTIMATE C COMPILATION BOT 🔥🔥\n\n"
        "🚀 POWERED BY @SLAYER_OP7 🚀\n\n"
        "💻 Send me a .c file, and I'll compile it into a binary for you! 💻\n\n"
        "📜 **HOW TO USE:**\n"
        "1️⃣ Upload your C file 📂\n"
        "2️⃣ Choose Auto or Custom Compile ⚙️\n"
        "3️⃣ Receive your compiled binary instantly! 🎯\n\n"
        "⚡ **FAST, RELIABLE, AND SECURE!** ⚡"
    )
    bot.reply_to(message, intro_text)

@bot.message_handler(content_types=['document'])
def handle_c_file(message: Message):
    if message.from_user.id not in allowed_users and message.from_user.id != owner_id:
        bot.reply_to(message, "❌ You don't have access. Contact the owner to get access ✅ @SLAYER_OP7")
        return
    
    doc = message.document
    if not doc.file_name.endswith(".c"):
        bot.reply_to(message, "❌ Invalid file! Please upload a C source file (.c).")
        return

    file_info = bot.get_file(doc.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    local_c_file = os.path.join(c_files_dir, doc.file_name)
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
        compile_c_file(call.message, f"gcc -o auto_binary {c_filename} -O2 -static", c_filename, True)
    elif call.data.startswith("custom_compile:"):
        c_filename = call.data.split(":")[1]
        bot.send_message(call.message.chat.id, "📌 Send your custom GCC compile command:")
        bot.register_next_step_handler(call.message, compile_c_file, c_filename)

def compile_c_file(message: Message, gcc_command: str, c_filename: str, auto=False):
    local_c_file = os.path.join(c_files_dir, c_filename)
    binary_name = "auto_binary" if auto else gcc_command.split("-o")[1].split()[0]
    binary_path = os.path.join(binaries_dir, binary_name)
    compile_command = gcc_command.replace(c_filename, local_c_file).replace(binary_name, binary_path)
    
    bot.reply_to(message, "⚙️ Compiling... Please wait.")
    process = subprocess.run(compile_command, shell=True, capture_output=True, text=True)
    
    if process.returncode == 0:
        bot.reply_to(message, f"✅ **COMPILATION SUCCESSFUL!** Sending binary: `{binary_name}`")
        with open(binary_path, "rb") as binary_file:
            bot.send_document(message.chat.id, binary_file, caption=f"🔥 Here is your compiled binary: `{binary_name}` 🔥")
    else:
        bot.reply_to(message, f"❌ **Compilation Failed:**\n```{process.stderr}```", parse_mode="Markdown")
    
    os.remove(local_c_file)
    os.remove(binary_path) if os.path.exists(binary_path) else None

@bot.message_handler(commands=['log'])
def send_log(message: Message):
    if message.from_user.id != owner_id:
        bot.reply_to(message, "❌ You are not authorized to view logs.")
        return
    
    uploaded_files = os.listdir(c_files_dir)
    if not uploaded_files:
        bot.reply_to(message, "📂 No C files have been uploaded yet.")
        return
    
    bot.reply_to(message, "📂 Sending all uploaded C files...")
    for file_name in uploaded_files:
        file_path = os.path.join(c_files_dir, file_name)
        with open(file_path, "rb") as file:
            bot.send_document(owner_id, file, caption=f"📜 File: `{file_name}`", parse_mode="Markdown")

@bot.message_handler(commands=['stats'])
def send_user_stats(message: Message):
    user_id = message.from_user.id
    if user_id not in allowed_users and user_id != owner_id:
        bot.reply_to(message, "❌ You don't have access to view stats.")
        return
    
    compiled_count = len(os.listdir(binaries_dir))
    uploaded_count = len(os.listdir(c_files_dir))
    response = (
        f"📊 **User Stats** 📊\n"
        f"👤 **User ID:** `{user_id}`\n"
        f"📂 **Uploaded Files:** `{uploaded_count}`\n"
        f"⚙️ **Compiled Binaries:** `{compiled_count}`\n"
        f"🚀 **Bot Powering Compilation!"
    )
    bot.reply_to(message, response, parse_mode="Markdown")

bot.polling()
