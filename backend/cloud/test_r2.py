import boto3
from botocore.config import Config
from dotenv import load_dotenv
import os

load_dotenv()  # lee las variables del .env

R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
R2_ACCESS_KEY = os.getenv("R2_ACCESS_KEY")
R2_SECRET_KEY = os.getenv("R2_SECRET_KEY")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME")

s3 = boto3.client(
    "s3",
    endpoint_url=f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
    aws_access_key_id=R2_ACCESS_KEY,
    aws_secret_access_key=R2_SECRET_KEY,
    config=Config(signature_version="s3v4"),
    region_name="auto",
)

# 1. Crear un archivo de prueba local
with open("prueba.txt", "w") as f:
    f.write("Hola desde mi proyecto FastAPI!")

# 2. Subirlo a R2
s3.upload_file("prueba.txt", R2_BUCKET_NAME, "prueba.txt")
print("✅ Archivo subido correctamente")

# 3. Listar los archivos del bucket para confirmar
response = s3.list_objects_v2(Bucket=R2_BUCKET_NAME)
print("Archivos en el bucket:")
for obj in response.get("Contents", []):
    print(" -", obj["Key"])