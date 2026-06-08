from core import config
from core.schemas import SentimentBase, TranscriptCreate, TranscriptResponse

print("App Name:", config.Settings().APP_NAME)
print("API Host:", config.Settings().API_HOST)
print("AWS Region:", config.Settings().AWS_REGION)
print("AWS Bedrock LLM Model:", config.Settings().BEDROCK_LLM_MODEL)
print("aws sceret access key:", config.Settings().AWS_SECRET_ACCESS_KEY)