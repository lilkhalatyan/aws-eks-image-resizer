from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import boto3, uuid, os


app = FastAPI(title="Image Resizer API", version="1.0.0")


app.add_middleware(
CORSMiddleware,
allow_origins=["*"],
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)


AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-west-2")
AWS_ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL") # e.g., http://localstack:4566
INPUT_BUCKET = os.getenv("INPUT_BUCKET", "image-resizer-input")
OUTPUT_BUCKET = os.getenv("OUTPUT_BUCKET", "image-resizer-output")
QUEUE_URL = os.getenv("QUEUE_URL") # set by Helm bootstrap


s3 = boto3.client("s3", region_name=AWS_REGION, endpoint_url=AWS_ENDPOINT_URL)
sqs = boto3.client("sqs", region_name=AWS_REGION, endpoint_url=AWS_ENDPOINT_URL)


@app.get("/")
def root():
return {"service": "image-resizer-api", "status": "ok"}


@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
if not QUEUE_URL:
return {"error": "QUEUE_URL not configured"}
job_id = str(uuid.uuid4())
key = f"input/{job_id}-{file.filename}"
s3.upload_fileobj(file.file, INPUT_BUCKET, key)
sqs.send_message(
QueueUrl=QUEUE_URL,
MessageBody=job_id,
MessageAttributes={"s3_key": {"DataType": "String", "StringValue": key}},
)
return {"job_id": job_id, "message": "queued"}


@app.get("/result/{job_id}")
def get_result(job_id: str):
# For demo: we return the S3 key path. In real cloud, you might pre-sign a URL.
return {"s3": f"s3://{OUTPUT_BUCKET}/output/{job_id}.jpg"}