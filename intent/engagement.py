import json
import helper.responseBuilder as RB
import data.engagement as data


def survey_engagement_client_session(data, message, image=None):
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
    source = intent_request['invocationSource']
    session_attributes['employee'] = json.dumps(employee)
    intent_name = intent_request['currentIntent']['name']

    employee_experience = intent_request['currentIntent']['slots']['EmployeeExperience']
    employee_supervisor = intent_request['currentIntent']['slots']['EmployeeSupervisor']
    employee_encourage = intent_request['currentIntent']['slots']['EmployeeEncourage']
    employee_shortcoming = intent_request['currentIntent']['slots']['EmployeeShortcoming']

    if source == 'DialogCodeHook':
        # Perform basic validation on the supplied input slots.
        # Use the elicitSlot dialog action to re-prompt for the first violation detected.
        slots = intent_request['currentIntent']['slots']

        validation_result = validate_survey(employee_experience, employee_supervisor, employee_encourage,
                                            employee_shortcoming)
        if not validation_result['isValid']:
            session_attributes['client'] = json.dumps(survey_engagement_client_session(validation_result['client_data'], validation_result['message']))
            slots[validation_result['violatedSlot']] = None
            return RB.elicit_slot(session_attributes,
                                  intent_request['currentIntent']['name'],
                                  slots,
                                  validation_result['violatedSlot'],
                                  validation_result['message'])

        if not employee_experience:
            session_attributes['client'] = json.dumps(survey_engagement_client_session(data.employee_experience_dict, 'How were your last 6 months working in this company?'))
            RB.elicit_slot(session_attributes, intent_name, slots, 'EmployeeExperience', {'contentType': 'PlainText', 'content': 'How were your last 6 months working in this company?'})

        if not employee_experience:
            session_attributes['client'] = json.dumps(survey_engagement_client_session(data.employee_supervisor_dict, 'How were your last 6 months working in this company?'))
            RB.elicit_slot(session_attributes, intent_name, slots, 'EmployeeSupervisor', {'contentType': 'PlainText', 'content': 'How were your last 6 months working in this company?'})

        return RB.delegate(session_attributes, slots)

    return RB.close(intent_request['sessionAttributes'],
                    'Fulfilled',
                    {'contentType': 'PlainText',
                     'content': 'Thanks for your participation'})


def validate_survey(employee_experience, employee_encourage, employee_shortcoming, employee_supervisor):

    if employee_experience and employee_experience not in data.employee_experience_dict:
        return RB.build_validation_result(False, 'EmployeeExperience', 'How were your last 6 months working in this company?', data.employee_experience_dict)

    return RB.build_validation_result(True, None, None)
