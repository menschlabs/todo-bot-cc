"""
This module is powered by Wit.ai
author: Sai Madhu Bhargav
"""
from wit import Wit
import os

ACCESS_TOKEN = os.environ['WIT_ACCESS_TOKEN']

client = Wit(access_token=ACCESS_TOKEN)


def getFunctionality(message):
    resp = client.message(message)
    intent = None
    reminder = None
    number = None
    if resp['entities']:
        if 'intent' in resp['entities']:
            inte = resp['entities']['intent']
            intent = inte[0]['value']
        if 'reminder' in resp['entities']:
            remi = resp['entities']['reminder']
            reminder = remi[0]['value']
        if 'number' in resp['entities']:
            numb = resp['entities']['number']
            number = numb[0]['value']
    return intent, reminder, number
