import boto3,datetime
from botocore.exceptions import NoCredentialsError

AWS_ACCESS_KEY = 'AKIAVIOZGAKTMWX62NOC'
AWS_SECRET_KEY = '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'
BUCKET_NAME = 'toyuappbucket'

def upload_to_s3(file_path, s3_file_name):
    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
    try:
        s3.upload_file(file_path, BUCKET_NAME, s3_file_name)
        print("Yedekleme başarılı!")
    except FileNotFoundError:
        print("Dosya bulunamadı")
    except NoCredentialsError:
        print("Kimlik bilgileri hatalı")


# Yedekleme dizinini ve dosya adını tanımlayın
BACKUP_DIR = "/home/nazimavci/YEDEK/gunluk"
yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
date_str = yesterday.strftime("%Y-%m-%d")
BACKUP_FILE = f"{BACKUP_DIR}/toyu_db-{date_str}.sqlite3"

file_path = BACKUP_FILE

s3_file_name = "toyu_production_db"+date_str+".sqlite3"

upload_to_s3(file_path, s3_file_name)
