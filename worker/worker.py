import boto3, os, io, time
from PIL import Image


AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-west-2")
AWS_ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL") # http://localstack:4566
INPUT_BUCKET = os.getenv("INPUT_BUCKET", "image-resizer-input")
OUTPUT_BUCKET = os.getenv("OUTPUT_BUCKET", "image-resizer-output")
QUEUE_URL = os.getenv("QUEUE_URL")
SIZE = int(os.getenv("RESIZE", "512"))


s3 = boto3.client("s3", region_name=AWS_REGION, endpoint_url=AWS_ENDPOINT_URL)
sqs = boto3.client("sqs", region_name=AWS_REGION, endpoint_url=AWS_ENDPOINT_URL)




def process(key: str, job_id: str):
buf = io.BytesIO()
s3.download_fileobj(INPUT_BUCKET, key, buf)
buf.seek(0)
img = Image.open(buf).convert("RGB")
img.thumbnail((SIZE, SIZE))
out = io.BytesIO()
img.save(out, format="JPEG", quality=85)
out.seek(0)
s3.upload_fileobj(out, OUTPUT_BUCKET, f"output/{job_id}.jpg")




def main():
if not QUEUE_URL:
print("QUEUE_URL not configured; sleeping")
time.sleep(60)
return
while True:
resp = sqs.receive_message(
QueueUrl=QUEUE_URL,
MaxNumberOfMessages=5,
WaitTimeSeconds=20,
MessageAttributeNames=["All"],
)
for m in resp.get("Messages", []):
attrs = m.get("MessageAttributes", {})
job_id = m["Body"]
key = attrs.get("s3_key", {}).get("StringValue")
try:
if key:
process(key, job_id)
finally:
sqs.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=m["ReceiptHandle"])




if __name__ == "__main__":
main()