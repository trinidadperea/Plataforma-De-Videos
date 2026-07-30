import os
import boto3

client = boto3.client(
    "s3",
    endpoint_url=os.getenv("R2_ENDPOINT"),
    aws_access_key_id=os.getenv("R2_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("R2_SECRET_KEY"),
    region_name="auto",
)

BUCKET = os.getenv("R2_BUCKET_NAME")

def listar_bucket():

    return client.list_objects_v2(
        Bucket=BUCKET
    )


def initiate_upload(filename: str):

    response = client.create_multipart_upload(
        Bucket=BUCKET,
        Key=filename
    )

    return response["UploadId"]


def upload_part(
    filename: str,
    upload_id: str,
    part_number: int,
    data: bytes
):

    response = client.upload_part(
        Bucket=BUCKET,
        Key=filename,
        UploadId=upload_id,
        PartNumber=part_number,
        Body=data
    )

    return response["ETag"]


def complete_upload(
    filename: str,
    upload_id: str,
    parts: list[dict]
):

    client.complete_multipart_upload(
        Bucket=BUCKET,
        Key=filename,
        UploadId=upload_id,
        MultipartUpload={
            "Parts": parts
        }
    )

# link de descarga que dura 1 hora
def generate_download_url(filename: str):

    url = client.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": BUCKET,
            "Key": filename,
            "ResponseContentDisposition": f'attachment; filename="{filename}"'
        },
        ExpiresIn=3600
    )

    return url

def create_upload_url(filename: str):

    url = client.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": BUCKET,
            "Key": filename,
            "ContentType": "video/mp4"
        },
        ExpiresIn=3600
    )

    return url

def abort_upload(filename, upload_id):

    client.abort_multipart_upload(
        Bucket=R2_BUCKET,
        Key=filename,
        UploadId=upload_id
    )


def list_files():

    response = client.list_objects_v2(
        Bucket=BUCKET
    )

   # for obj in response.get("Contents", []):
   #     print(
   #         "ARCHIVO R2:",
   #         repr(obj["Key"])
   #     )