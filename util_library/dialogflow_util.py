import dialogflow_v2 as dialogflow

global parent
global intents_client
global contexts_client
global project_id
global path


def set_variables(proj_id, google_auth_fname_path):
    """
    Sets global variables for use by functions in this module.
    : param proj_id : Google project id
    : param google_auth_fname_path : path to json google authentication file
    : return : void
    """
    global parent
    global intents_client
    global contexts_client
    global project_id
    global path

    project_id = proj_id
    intents_client = dialogflow.IntentsClient()
    contexts_client = dialogflow.ContextsClient()
    parent = intents_client.project_agent_path(project_id)
    path = google_auth_fname_path

def get_intent_fields(df_row):
    """
    Parses a row in the intent dataframe and creates a dictionary containing relevant fields for use in create_intent.
    : param df_row : Row of the intent dataframe to parse.
    : return : Dictionary of parsed intent fields (display_name, training_phrases, messages, events, actions, etc)
    """
    import json

    field_dict = {}

    iid = df_row['IID']
    field_dict['display_name'] = f'node_{iid}'  # display_name
    field_dict['training_phrases_parts'] = json.loads(df_row['trainingPhrase'])  # training phrases
    field_dict['message_texts'] = df_row['response']  # messages
    field_dict['parameter_info'] = json.loads(df_row['params'])  # parameter
    field_dict['event'] = json.loads(df_row['dfEvent'])['event']  # events
    field_dict['action'] = json.loads(df_row['dfAction'])['action']  # actions
    field_dict['end_conversation'] = df_row['isConversationEnd']  # end conversation
    field_dict['input_context_info'] = json.loads(df_row['inputCtx'])  # input context
    field_dict['output_context_info'] = json.loads(df_row['outputCtx'])  # output context
    # field_dict['fullfillment'] = json.loads(df_row['fullfillment'])  # fullfillment # unused

    return field_dict


def create_intent(intent_field_dict):
    """
    Creates a dialogflow intent with the given characteristics.
    : param intent_field_dict : Dictionary of fields for an individual intent used in the
    call to the dialogflow intent constructor
    : return : void
    """
    # create training phrases
    training_phrases = []
    for training_phrases_part in intent_field_dict['training_phrases_parts']:
        part = dialogflow.types.Intent.TrainingPhrase.Part(
            text=training_phrases_part)
        training_phrase = dialogflow.types.Intent.TrainingPhrase(parts=[part])
        training_phrases.append(training_phrase)

    # create message
    text = dialogflow.types.Intent.Message.Text(text=[intent_field_dict['message_texts']])
    message = dialogflow.types.Intent.Message(text=text)

    # create output context
    output_contexts = dialogflow.types.Context(
        name=contexts_client.context_path(project_id, "-", intent_field_dict['output_context_info']['name']),
        lifespan_count=intent_field_dict['output_context_info']['lifespan'])

    # create event
    events = intent_field_dict['event']

    # create action
    action = intent_field_dict['action']

    # create intent
    input_context_name = contexts_client.context_path(project_id, "-", intent_field_dict['input_context_info']['name'])

    if intent_field_dict['parameter_info']['name'] == '':
        intent = dialogflow.types.Intent(
            display_name=intent_field_dict['display_name'],
            input_context_names=[input_context_name],
            output_contexts=[output_contexts],
            training_phrases=training_phrases,
            messages=[message],
            events=events,
            action=action,
            reset_contexts=bool(intent_field_dict['end_conversation'])
        )

    else:
        # create intent parameter
        default = f"#{input_context_name}.{intent_field_dict['parameter_info']['name']}"
        parameter = dialogflow.types.Intent.Parameter(display_name=intent_field_dict['parameter_info']['name'],
                                                      value=intent_field_dict['parameter_info']['value'],
                                                      prompts=[intent_field_dict['parameter_info']['prompt']],
                                                      is_list=intent_field_dict['parameter_info']['is_list'],
                                                      mandatory=intent_field_dict['parameter_info']['is_required'],
                                                      default_value=default,
                                                      entity_type_display_name=intent_field_dict['parameter_info'][
                                                          'entity'])

        intent = dialogflow.types.Intent(
            display_name=intent_field_dict['display_name'],
            input_context_names=[
                contexts_client.context_path(project_id, "-", intent_field_dict['input_context_info']['name'])],
            output_contexts=[output_contexts],
            training_phrases=training_phrases,
            messages=[message],
            parameters=[parameter],
            events=events,
            action=action,
            reset_contexts=bool(intent_field_dict['end_conversation'])
        )

    response = intents_client.create_intent(parent, intent)
    # print('Intent created: {}'.format(response))


def update_welcome_intent(intent_field_dict, intent_name='Default Welcome Intent'):
    """
    Updates the default welcome intent to contain the output context and message of our choosing
    : param intent_field_dict : Dictionary of fields for an individual intent used in the
    call to update the dialogflow intent
    : param intent_name : the intent name, Default Welcome Intent
    : return : void
    """
    from google.protobuf import field_mask_pb2

    intents = intents_client.list_intents(parent)
    intent_path = [
        intent.name for intent in intents
        if intent.display_name == intent_name]
    intent = intents_client.get_intent(intent_path[0], intent_view=dialogflow.enums.IntentView.INTENT_VIEW_FULL)

    # remove the default welcome intent message
    intent.messages.pop(0)

    # reset the welcome message
    response_list = [intent_field_dict['message_texts']]
    text = dialogflow.types.Intent.Message.Text(text=response_list)
    message = dialogflow.types.Intent.Message(text=text)
    intent.messages.extend([message])

    # add to output context
    output_contexts = dialogflow.types.Context(
        name=contexts_client.context_path(project_id, "-", intent_field_dict['output_context_info']['name']),
        lifespan_count=intent_field_dict['output_context_info']['lifespan'])
    intent.output_contexts.extend([output_contexts])

    update_mask = field_mask_pb2.FieldMask(paths=['messages', 'output_contexts'])
    response = intents_client.update_intent(intent, language_code='en', update_mask=update_mask)

    # # verification
    # print('Intent created: {}'.format(response))
    # for msg in intent.messages:
    #     print(msg.text.text)
