import json
import helper.responseBuilder as RB
import data.intro as data

def survey_intro_client_session(data, message, image = None):

    result = {}
    buttons = []
    image = image

    for items in data:
        buttons.append({
            'text': data[items]['sort_desc'],
            'value': items
        })

    result['images'] = image
    result['buttons'] = buttons

    return result

def dialog(intent_request, employee):

    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    survey_type = intent_request['currentIntent']['slots']['SurveyTypes']
    source = intent_request['invocationSource']
    session_attributes['employee'] = json.dumps(employee)

    if source == 'DialogCodeHook':
        # Perform basic validation on the supplied input slots.
        # Use the elicitSlot dialog action to re-prompt for the first violation detected.
        slots = intent_request['currentIntent']['slots']

        validation_result = validate_survey(survey_type)
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            return RB.elicit_slot(intent_request['sessionAttributes'],
                               intent_request['currentIntent']['name'],
                               slots,
                               validation_result['violatedSlot'],
                               validation_result['message'])

        if not survey_type:
            session_attributes['client'] = json.dumps(survey_intro_client_session(data.survey_dict, 'What kind of survey you want to launch?'))
            RB.elicit_slot(session_attributes, intent_request['currentIntent']['name'], slots, 'SurveyTypes', {'contentType': 'PlainText', 'content': 'What kind of survey you want to launch?'}, '')

        return RB.delegate(session_attributes, slots)

    return RB.close(intent_request['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': survey_type})

def validate_survey(survey_type):
    return RB.build_validation_result(True, None, None)