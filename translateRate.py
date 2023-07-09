import logging
from google.cloud import translate_v2 as translate
from dotenv import load_dotenv

def translateRate(text: str) -> str:
  load_dotenv()
  translate_client = translate.Client()

  if isinstance(text, bytes):
      text = text.decode("utf-8")
  result = translate_client.translate(text, target_language="en")
  logging.debug("Text: {}, Translation: {}".format(result["input"], result["translatedText"]))
  return result["translatedText"]

if __name__ == "__main__":
  res = translateRate("這是一份測試評價")
  print(res)