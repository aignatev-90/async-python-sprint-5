import os
from pathlib import Path
from dotenv import load_dotenv


FILENAME = '.env.sample'
DIR = Path(os.getcwd())
PATH = os.path.join((DIR.absolute()), FILENAME)

# load_dotenv(PATH)
print(PATH)
load_dotenv(PATH)

TEST_DB_URL = str(os.getenv('TEST_DB_URL'))

print(TEST_DB_URL)