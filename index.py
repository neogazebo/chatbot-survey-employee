import time
import os
import logging
import json
import helper.responseBuilder as RB
import intent.intro as intro

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def try_ex(func):
    try:
        return func()
    except KeyError:
        return None

intents_available_dict = {
        'SurveyIntro': {
            'handler': intro,
            'login': True
        },
        'EngagementSurvey': {
            'handler': 'engagement',
            'login': True
        }
    }

def dispatch(intent_request):
    logger.debug(
        'dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    session_attributes.pop('client', None)

    employee = try_ex(lambda: session_attributes['employee'])
    if employee:
        employee = json.loads(employee)
    # testing only , remove when production
    else:
        employee = json.loads('{"name":"febri pratama", "id":1, "company_id":1}')
    # end testing

    intent_name = intent_request['currentIntent']['name']
    curr_intent = intents_available_dict[intent_name]

    logger.debug(curr_intent)
    logger.debug(employee)

    # Dispatch to your bot's intent handlers
    if curr_intent['login']:
        if employee is not None:
            return curr_intent['handler'].dialog(intent_request, employee)
        else:
            return RB.close(session_attributes, 'Fulfilled', {'contentType': 'PlainText', 'content': 'please login first'})
    else:
        return curr_intent['handler'].dialog(intent_request, employee)

    raise Exception('Intent with name ' + intent_name + ' not supported')


""" --- Main handler --- """


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)
