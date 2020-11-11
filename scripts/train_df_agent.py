import time
import os
import json
import sys
sys.path.append('../')
import util_library.db_util as dbu
import util_library.dialogflow_util as dfu

startTime = time.time()

# set up dialogflow varibles
with open('../setup/credentials.json') as src:
    credentials = json.load(src)
GOOGLE_AUTHENTICATION_FILE_NAME = credentials["GOOGLE_AUTHENTICATION_FILE_NAME"]
current_directory = os.path.dirname(os.path.realpath(__file__))
path = os.path.join(current_directory, GOOGLE_AUTHENTICATION_FILE_NAME)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = path
PROJECT_ID = credentials["PROJECT_ID"]
HOST = credentials["HOST"]
DATABASE = credentials["DATABASE"]
USER = credentials["USER"]
PASSWORD = credentials["PASSWORD"]

dfu.set_variables(PROJECT_ID, path)

# connect to question database and read data
dbu.init_connection(HOST, DATABASE, USER, PASSWORD)
intents_df = dbu.make_df_from_query('DFintent')
dbu.close_connection()

for index, row in intents_df.iterrows():
    intent_dict = dfu.get_intent_fields(row)
    if row['IID'] == 1:  # update the default welcome intent to contain the response we want
        dfu.update_welcome_intent(intent_dict)
    else:
        dfu.create_intent(intent_dict)

duration = (time.time() - startTime)
print(f'Populated Dialogflow agent in {duration} seconds')
