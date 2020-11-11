import time
import json
import sys

sys.path.append('../')
import util_library.db_util as dbu
import util_library.intent_util as iu

startTime = time.time()

# set up mySQL varibles
with open('../setup/credentials.json') as src:
    credentials = json.load(src)
dbu.init_connection(credentials["HOST"], credentials["DATABASE"], credentials["USER"], credentials["PASSWORD"])

# read questions and relationships from mySQL
question_df = dbu.make_df_from_query('question')
iu.set_question_df(question_df)
leads_to_df = dbu.make_df_from_query('leads_to')

# create and populate table corresponds_to
corresponds_to_df, duplicates = iu.create_corresponds_to_df(leads_to_df)
iu.populate_intent_table(corresponds_to_df)
iu.populate_corresponds_to_table(corresponds_to_df)

# create and populate table DFleads_to
relationships_df = iu.create_intent_leads_to_df(corresponds_to_df, duplicates)
iu.populate_df_leads_to_table(relationships_df)

dbu.close_connection()

duration = (time.time() - startTime)
print(f'Populated database in {duration} seconds')
