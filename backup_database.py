import os
import shutil
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import schedule
import time
from dotenv import load_dotenv

# Load thông tin từ file .env
load_dotenv()

# Đọc thông tin từ file .env
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
MAIL_RECEIVER = os.getenv('MAIL_RECEIVER')

# Định nghĩa thư mục chứa file database và thư mục backup
DB_FOLDER = '/path/to/database/files/'  # Đường dẫn tới thư mục chứa các file cơ sở dữ liệu
BACKUP_FOLDER = '/path/to/backup/folder/'  # Đường dẫn tới thư mục backup

# Hàm sao lưu cơ sở dữ liệu
def backup_database():
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d_%H-%M-%S")
    success = True
    message = ""

    # Tìm các file có đuôi .sql hoặc .sqlite3
    for filename in os.listdir(DB_FOLDER):
        if filename.endswith('.sql') or filename.endswith('.sqlite3'):
            src_file = os.path.join(DB_FOLDER, filename)
            dest_file = os.path.join(BACKUP_FOLDER, f"{current_time}_{filename}")
            try:
                shutil.copy(src_file, dest_file)
                message += f"Backup thành công: {filename}\n"
            except Exception as e:
                message += f"Backup thất bại: {filename} - Lỗi: {str(e)}\n"
                success = False

    # Gửi email thông báo
    if success:
        send_email("Backup thành công", message)
    else:
        send_email("Backup thất bại", message)

# Hàm gửi email thông báo
def send_email(subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = MAIL_USERNAME
        msg['To'] = MAIL_RECEIVER
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.sendmail(MAIL_USERNAME, MAIL_RECEIVER, msg.as_string())

    except Exception as e:
        print(f"Lỗi khi gửi email: {str(e)}")

# Lên lịch sao lưu vào lúc 00:00 AM mỗi ngày
schedule.every().day.at("00:00").do(backup_database)

# Chạy lịch trình
while True:
    schedule.run_pending()
    time.sleep(60)
