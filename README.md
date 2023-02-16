# NCCUCourse
A set of NCCU Course tools, base on python3

## Environment
- Python 3.9^

## Installation
```sh
pip3 install -r requirement.txt
```

## Setup
As a NCCU student, you have your iNCCU account. Please create a `.env` file and give following informations.
```
USERNAME=*********
PASSWORD=*****

YEAR=111
SEM=2

GOOGLE_APPLICATION_CREDENTIALS=.google.auth
```

If your google credential is store else where, please modify `.env` file.
Be aware of your credential when using git!!

## Execution
```sh
python main.py
```