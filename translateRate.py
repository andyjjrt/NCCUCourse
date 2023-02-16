import os, json, shutil
from tqdm import tqdm
from google.cloud import translate_v2 as translate

dir_path = os.path.dirname(os.path.realpath(__file__))

def translateRate():
  count = 0
  translate_client = translate.Client()
  teacher_list = tqdm(os.listdir(os.path.join(dir_path, "result")), leave=False)
  for teacher in teacher_list:
    if not os.path.exists(os.path.join(dir_path, "result_en", teacher)):
      os.makedirs(os.path.join(dir_path, "result_en", teacher))
    subject_list = tqdm(os.listdir(os.path.join(dir_path, "result", teacher)), leave=False)
    for subject in subject_list:
      if not os.path.exists(os.path.join(dir_path, "result_en", teacher, subject)):
        os.makedirs(os.path.join(dir_path, "result_en", teacher, subject))
        try:
          shutil.copyfile(os.path.join(dir_path, "result", teacher, subject, "index.json"), os.path.join(dir_path, "result_en", teacher, subject, "index.json"))
        except Exception as e:
          print(e)
      class_list = tqdm(os.listdir(os.path.join(dir_path, "result", teacher, subject)), leave=False)
      for _class in class_list:
        if os.path.isfile(os.path.join(dir_path, "result", teacher, subject, _class)):
          if _class.split(".json")[0] == "index": continue
          with open(os.path.join(dir_path, "result", teacher, subject, _class), "r") as f:
            res = json.loads(f.read())
            translatedRes = list()
            comments = tqdm(res, leave=False)
            for comment in comments:
              result = translate_client.translate(comment, target_language="en")
              translatedRes.append(result["translatedText"])
            with open(os.path.join(dir_path, "result_en", teacher, subject, _class), "w+") as fp:
              json.dump(translatedRes, fp)