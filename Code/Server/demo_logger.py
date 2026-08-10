import logging

# Cấu hình: Vừa in ra màn hình Terminal, vừa tự ghi vào file 'server.log'
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    handlers=[
        logging.FileHandler("server.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

def log(msg):
    logging.info(msg)