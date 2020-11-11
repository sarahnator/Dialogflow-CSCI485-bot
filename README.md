# CSCI485 Dialogflow bot
---
## Setup
### 1. Create and activate virtual environment
```shell script
$ virtualenv env
$ source env/bin/activate
```
### 2. Install requirements (I believe it's something like this)
```shell script
$ sudo pip install -r requirements.txt
```
### 3. Populate credentials.json file in setup directory
Provide values for:
- Dialogflow Google authentication file path, Google project id
- mySQL host, database, user, password

## Run
populate_db.py:
```
$ cd scripts
$ python populate_db.py
```
Expected console output: task duration
```shell script
Populated database in 0.25879979133605957 seconds
```

train_df_agent.py:
```shell script
$ cd scripts  # if not already in scripts dir
$ python train_df_agent.py
```
Expected console output: task duration
```shell script
Populated Dialogflow agent in 9.261634111404419 seconds
```

## Implementation details
### Assumptions:
- The user is using the ER diagram model in setup directory, and has populated the database in a fashion similar to the SQL scripts provided, with the question and leads_to tables prepopulated.
- The parameters for what to record in the ER diagram should be labeled as specific as possible, for example, "response" should become "YesOrNo", "count", etc to accurately assign training phrases
- That the user does not wish to add intent parameters with entity types other than @sys.number, @sys.duration, @sys.any
- Severity is on a scale from 1-10, thus this parameter's entity type is @sys.number
- The user's response will be one of the training phrases the agent was trained on (see DFintent after running populate_db.py)

### Brief overview of implementation:
populate_db.py:
The program functions by reading the question and leads_to tables from the mySQL database, then using this data to populate the remaining tables. The script does this by categorizing node by type (root, internal, or terminal), so that setting certain variables such as the end conversation flag or default intent characteristics becomes easier for training the agent, corresponding to the existence/non-existence of a child or parent node. It detects nodes that must be duplicated (these have more than one parent). Taking these duplicates into account, intent IDs are relabeled to differentiate between duplicate nodes with the same child but different parents.
Relationships in the leads_to table between questions are restructured based on the existence of duplicates to form the DFleads_to table. 

train_df_agent.py:
Reads data from database to create intents capturing the sequence and parameters in the decision tree.

