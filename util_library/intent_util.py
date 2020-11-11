import pandas as pd
import numpy as np
import json
from util_library.db_util import bulk_db_insert

global question_df


def set_question_df(q_df):
    """
    Sets global variables for use by functions in this module.
    :param q_df: dataframe of the Question table in mySQL
    :return: void
    """
    global question_df
    question_df = q_df


def get_child_node_frequency(df):
    """
    Returns the frequency of each childQID
    : param df : Dataframe to analyze
    : return freq : Dictionary of childQIDs and their frequencues
    """
    freq = df['childQID'].value_counts().to_dict()
    return freq


def get_child_node_duplicates(df):
    """
    Filters the frequency count for the child nodes to find nodes with frequency > 1. Returns a dictionary with these nodes.
    : param df : Dataframe to analyze
    : return duplicates : dictionary where K = duplicate nodes, V = frequency count of that child node
    """
    # frequency count dict of childQID
    freq_count = get_child_node_frequency(df)
    # filtered frequency dict
    # find nodes with > 1 parent. These will be our duplicates
    duplicates = dict(filter(lambda elem: elem[1] > 1, freq_count.items()))
    return duplicates


def populate_df_leads_to_table(df):
    """
    Populates the DFleads_to table in mySQL
    : param df : dataframe that is the source of data to populate the mySQL table with
    : return : void
    """
    leads_to = []
    for index, row in df.iterrows():
        leads_to.append((row['parentIID'], row['childIID']))
    bulk_db_insert(leads_to, 'DFleads_to')


def create_intent_leads_to_df(corresponds_to_df, duplicates_df):
    """
    Creates the dataframe of relationships between intents
    : param corresponds_to_df : dataframe of the data in the corresponds_to table
    : param duplicates_df : dataframe of duplicate nodes
    : return relationships_df : dataframe of relationships between intents (parentIID, childIID)
    """
    relationships_df = corresponds_to_df.copy()[['childQID', 'parentQID', "childIID"]]
    relationships_df.sort_values("childQID", inplace=True)

    # isolate childQID with frequency > 1
    duplicates_df.sort_values("childQID", inplace=True)

    # 1. reset child-parent relationships for duplicate nodes (the outgoing relationships from duplicate nodes)
    # (ex we want to set all 5s in child QID for these duplicates to 21)
    reset_child = get_child_node_duplicates(duplicates_df).keys()

    replace_dict = {}
    for item in reset_child:
        child = list(duplicates_df.loc[duplicates_df['parentQID'] == item, 'childQID'].to_dict().values())
        parent = list(duplicates_df.loc[duplicates_df['parentQID'] == item, 'parentQID'].to_dict().values())

        if bool(parent):
            parent = parent[0]
            # (ex find the IID that corresponds to  parent QID 15)
            IID_replace = list(duplicates_df.loc[duplicates_df['parentQID'] == parent, 'childIID'].to_dict().values())[
                0]
            replace_dict[child[0]] = IID_replace

    add_relationship = pd.DataFrame()
    for index, row in duplicates_df.iterrows():
        row.to_dict()

        # get childQID
        q_node = row['childQID']
        intent = row['childIID']

        # find the children of the childQID
        children_df = relationships_df.loc[relationships_df['parentQID'] == q_node, 'childQID']
        children = children_df.to_dict().values()

        # set the nodes after the first to point to each child of the first node (max two rows for yes and no)
        for c in children:
            if c in replace_dict.keys():
                c = replace_dict[c]
            insert_relationship = {'parentQID': f'{intent}', 'childQID': f'{int(c)}'}
            add_relationship = add_relationship.append(insert_relationship, ignore_index=True)

    # 2. set relationships for non-duplicate nodes and those incoming to duplicate nodes
    for index, row in relationships_df.iterrows():
        relationships_df.at[index, 'childQID'] = row['childIID']

    # concatenate the two dataframes and clean up
    relationships_df = pd.concat([relationships_df, add_relationship], ignore_index=True)
    relationships_df.drop(['childIID'], axis=1, inplace=True)
    relationships_df = relationships_df.iloc[1:]  # drop root node?
    relationships_df = relationships_df.rename(
        columns={"childQID": "childIID", "parentQID": "parentIID"})  # relabel columns

    return relationships_df


def create_corresponds_to_df(leads_to_df):
    """
    Creates the dataframe for the corresponds_to relationship and the nodes for the intents table.
    Eliminates duplicate nodes from the leads_to table
    and reassigns new IIDs to these nodes. Labels nodes with their node type {root, internal, terminal}.
    Also adds the root node.
    : param leads_to_df : the dataframe of our leads_to table from mySQL
    : return no_duplicates_df : the dataframe to populate our corresponds_to relationship and intents table in mySQL
    : return duplicate_nodes_df : the duplicate nodes removed from the leads_to_df, which may be useful
    """
    with_duplicates_df = leads_to_df.copy()    # temp copy of leads_to that contains duplicate nodes

    # remove rows with a childQID in our list that is not the first occurrence
    with_duplicates_df.sort_values("childQID", inplace=True)
    no_duplicates_df = with_duplicates_df.drop_duplicates(subset="childQID",
                                                          keep='first', inplace=False)
    no_duplicates_df = no_duplicates_df.assign(childIID=no_duplicates_df['childQID'])
    no_duplicates_df = no_duplicates_df.assign(is_duplicate=False)

    # extract duplicate nodes
    duplicate_nodes_df = with_duplicates_df[~with_duplicates_df.isin(no_duplicates_df).all(1)]

    # assign childQID to a different set of numbers
    next_QID = len(no_duplicates_df.index) + 2
    upper_bound = len(duplicate_nodes_df)
    new_IID = list(np.arange(next_QID, upper_bound + next_QID))

    # assign IIDs
    duplicate_nodes_df = duplicate_nodes_df.assign(childIID=new_IID)
    duplicate_nodes_df = duplicate_nodes_df.assign(is_duplicate=True)

    # we removed the duplicates leads_to table, now we can assign node types
    no_duplicates_df = pd.concat([no_duplicates_df, duplicate_nodes_df], ignore_index=True)
    no_duplicates_df.sort_values("childIID", inplace=True)
    no_duplicates_df['node_type'] = 'internal'  # temporarily set all to internal

    # find nodes in child not in parent and assign root type to terminal
    assign_terminal_df = no_duplicates_df[~no_duplicates_df['childQID'].isin(no_duplicates_df['parentQID'])]
    # drop these nodes, assign the terminal type, then add them back
    no_duplicates_df = pd.concat([no_duplicates_df, assign_terminal_df, assign_terminal_df]).drop_duplicates(keep=False)
    assign_terminal_df = assign_terminal_df.assign(node_type='terminal')

    no_duplicates_df = pd.concat([no_duplicates_df, assign_terminal_df])

    # Add root node
    no_duplicates_df.loc[-1] = [None, 1, '', 1, False, 'root']  # adding a row
    no_duplicates_df.index = no_duplicates_df.index + 1  # shifting index
    no_duplicates_df = no_duplicates_df.sort_index()  # sorting by index

    return no_duplicates_df, duplicate_nodes_df


def populate_corresponds_to_table(df):
    """
    Populates the corresponds_to table in mySQL
    : param df : dataframe with the source of data to populate the mySQL table
    : return : void
    """
    correspondence = []
    for index, row in df.iterrows():
        correspondence.append((row['childQID'], row['childIID']))

    bulk_db_insert(correspondence, 'corresponds_to')


def populate_intent_table(df):
    """
    Populates the DFintent table in mySQL.
    : param df : dataframe with the source of data to populate the mySQL table
    : return : void
    """
    intents_list = []

    # generate internal nodes, append to data
    for index, row in df.iterrows():
        row.to_dict()
        intents_list.append(generate_intent(row))

    bulk_db_insert(intents_list, 'DFintent')


def generate_intent(row, end_conv=False, fullfillment=[False, False], df_event=None, action=None):
    """
    Inserts intent into db
    : param row : dictionary of values
    : return intent:
    """
    # generate IID
    IID = row['childIID']

    # generate response text
    response_txt = list(question_df.loc[question_df['QID'] == row['childQID'], 'qText'].to_dict().values())[0]

    # generate inputCtx, generate outputCtx
    ctx = generate_ctx(row)
    input_ctx = ctx[0]
    output_ctx = ctx[1]

    # generate params
    params = generate_params(row['response'])

    # generate fullfillment
    fullfillment = json.dumps({"intent_web_hook_call": fullfillment[0], "slot_filling": fullfillment[1]})

    # generate isDuplicate
    is_duplicate = row['is_duplicate']

    # generate isConversationEnd
    if row['node_type'] == 'terminal':
        end_conv = True

    # generate dfEvent
    if row['node_type'] == 'root':
        df_event = 'Welcome'
    df_event = json.dumps({"event": df_event})

    # generate action
    if row['node_type'] == 'root':
        action = 'input.welcome'
    action = json.dumps({"action": action})

    # generate trainingPhrase
    start = params.find(r'entity": ') + len(r'entity": "')  # find entity type for parameter
    end = params.find(r'", "prompt"')
    param_type = params[start:end]
    training_phrase = generate_training_phrase(row['response'], param_type)

    intent = (IID, response_txt, input_ctx, output_ctx, params,
              fullfillment, end_conv, is_duplicate, df_event, action, training_phrase)
    return intent


def generate_params(user_response):
    """
    Generates parameters based on the expected user response to the parent entity of a child entity (child entity's input parameters).

    # example format for entity with no params:
    # {"name": null, "is_required": false, "value": null, "entity": null, "prompt": [null], "is_list": false}

    : param user_response : The expected input from the user. A field in the Question table.
    : return params_jobj : json object corresponding to the parameter and its properties
    """
    # presets
    name = ''
    is_required = False
    value = ''
    param_type = ''
    prompt = ''
    is_list = False

    if 'Record:' in user_response:
        is_required = True
        name = user_response[8:]
        value = f'${name}'
        prompt = 'Please give a value to the previous question :)'

        # param type
        if name == 'duration':
            param_type = '@sys.duration'
        elif name == 'name':
            param_type = '@sys.given-name'
        elif name == 'count' or name == 'severity':
            param_type = '@sys.number'
        else:
            param_type = '@sys.any'  # generic

    params_jobj = json.dumps({"name": name, "is_required": is_required, "value": value,
                              "entity": param_type, "prompt": prompt, "is_list": is_list})
    return params_jobj


def generate_training_phrase(user_response, param_type):
    """
    Generates training phrases for intents trained on yes/no phrases or @sys.any, @sys.number, @sys.duration parameters.
    If user_response=None and param_type=None, generates training phrases for a welcome intent.
    : param user_response : Expected user input. A field in the Question table.
    : param param_type : type of dialogflow parameter (entity)
    : return training_phrase : json object with training phrases
    """
    if user_response is not None:
        user_response = user_response.lower()

    if param_type is not None:
        param_type = param_type.lower()

    if user_response == 'yes':
        training_phrase = json.dumps(
            ["yes", "ya", "yeah", "yep", "sure", "maybe", "i think so", "definitely", "ok", "yea"])

    elif user_response == 'no':
        training_phrase = json.dumps(["nooo", "meh", "no", "nope", "nah", "naw", "never", "na"])

    elif 'medicine' in user_response:
        training_phrase = json.dumps(['Advil', 'tylenol', 'aspirin', 'ibuprofen', 'motrin', 'naproxen', 'Aleve'])

    elif param_type == '@sys.any' or ('YesOrNo' in user_response):  # yes and no are both valid responses
        training_phrase = json.dumps(
            ["yes", "ya", "yeah", "yep", "sure", "maybe", "i think so", "definitely", "ok", "yes no", "yesn't",
             "no yes", "yea", "nooo", "meh", "no", "nope", "nah", "naw", "never", "na"])

    elif param_type == '@sys.number':
        training_phrase = json.dumps(['4', '2062397', '21', '6', '0', '5', '3', '2', '1', '10', '9', '8', '7'])

    elif param_type == '@sys.given-name':
        training_phrase = json.dumps(
            ["Mary", "Frank", "Sarah", "Alexander", "James", "Anna", "Bob", "Joe"])

    elif param_type == '@sys.duration':
        training_phrase = json.dumps(
            ["one hour", "30 seconds", "5 minutes", "10 days", "6 weeks", "1 year", "7 months"])

    else:  # welcome intent
        training_phrase = json.dumps(
            ["just going to say hi", "heya", "hi", "hello", "howdy", "hey there", "hi there", "hey", "long time no see",
             "hello", "greetings", "i greet you", "hello again", "hello there", "a good day", "lovely day isnt it",
             "hello there"])

    return training_phrase


def generate_ctx(row, input_lifespan=0, output_lifespan=2):
    """
    Generates json objects for the input and output contexts, containing their names and lifespans,
    from a dictionary corresponding to a row in a dataframe.

    Example format:
    {"name": "await_18", "lifespan": 0}

    : param row : dicitonary of a single row in the dataframe
                (parentQID, childQID, response, childIID, is_duplicate, node_type)
    : param node_type : defines the position in the intent flow {root, fallback, internal, terminal}
    : param input_lifespan=0 : lifespan of the input context. Default = 0
    : param output_lifespan=1 : lifespan of the output context. Default = 1
    : return json_obj : the json object in the format above
    """
    node_type = row['node_type']

    if node_type == 'root':
        input_ctx = 'None'
        output_ctx = f"await_{row['childQID']}"  # output ctx is childQID

    elif node_type == 'terminal':
        input_ctx = f"await_{row['parentQID']}"  # input ctx is parentQID
        output_ctx = 'None'

    else:  # internal node

        input_ctx = f"await_{row['parentQID']}"  # input ctx is parentQID
        output_ctx = f"await_{row['childQID']}"  # output ctx is childQID

    input_jobj = json.dumps({"name": input_ctx, "lifespan": input_lifespan})

    output_jobj = json.dumps({"name": output_ctx, "lifespan": output_lifespan})
    return input_jobj, output_jobj
