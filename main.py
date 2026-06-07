import boto3

import boto3

bedrock = boto3.client(
    "IAMBedrockRuntime",
    region_name="us-east-1"
)

PRINT_BEDROCK_MODELS = True