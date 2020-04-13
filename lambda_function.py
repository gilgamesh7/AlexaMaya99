# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

import requests
from lxml import html
import random

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def getQuote(url, what):
    logger.info(f"URL - {url}, What - {what}")
    if not url :
        imdbUrl = 'https://www.imdb.com/title/tt2467372/' # Default to Brooklyn 99 IMDB page
    else:
        imdbUrl = url   # URL of season/episode

    # send request and get response
    imdbHeaders={'Accept': 'application/html'}
    imdbResponse=requests.get(imdbUrl,headers=imdbHeaders)
    logger.info(f"Call to IMDB returned {imdbResponse.status_code}")
    imdbResponseHTML = imdbResponse.text
    # generate lxml tree from response html
    imdbResponseTree = html.fromstring(imdbResponseHTML)

    # set up xpath search string based on whats being asked
    if what=='seasons':
        xpathVariable="//div[contains(@class,'seasons-and-year-nav')]/div[3]/a/@href"
    elif what=='episodes':
        xpathVariable="//div[contains(@class,'info')]/strong/a/@href"
    elif what=='quotes':
        # xpathVariable=f"(//div[@class='list']/div[starts-with(@class,'quote soda sodavote')]/div[@class='sodatext'])[{number}]/p/text()"
        xpathVariable=f"(//div[@class='list']/div[starts-with(@class,'quote soda sodavote')]/div[@class='sodatext'])"
        logger.info(xpathVariable)
        
        
    # use lxml xpath to get the list of seasons and URLs
    responseURLList = imdbResponseTree.xpath(xpathVariable)
    
    if len(responseURLList) > 0:
        if len(responseURLList) > 1 :
            indexNumber = random.randint(0,len(responseURLList)-1)
        else:
            indexNumber = 0

        if what != 'quotes':
            logger.info(f"{responseURLList}, {len(responseURLList)}")
            # Get a random URL in the list
            responseUrl = responseURLList[indexNumber]
            seasonURL = f"https://www.imdb.com{responseUrl}"
            logger.info(seasonURL)
        else:
            # generate an index to select all children (a & p) of div
            number = random.randint(1,len(responseURLList))
            xpathVariableQuotes = f"{xpathVariable}[{number}]/descendant::node()/text()"
            seasonURLRaw = imdbResponseTree.xpath(xpathVariableQuotes)
            # Replace \n in conversations
            seasonURLList=[]
            for quote in seasonURLRaw:
                quote = quote.replace('\n',' ')
                seasonURLList.append(quote)
            # List comprehension to make list into string with spaces
            seasonURL = ' '.join([str(element) for element in seasonURLList])
            logger.info(seasonURL)
    else:
        seasonURL = "No quotes found in the season I picked."
        
    return seasonURL

def orchestrate():
    logger.info("First Call")
    seasonsURL = f"{getQuote('','seasons')}"
    logger.info("Second Call")
    quotessURL = f"{getQuote(seasonsURL,'episodes')}trivia?tab=qt" # quotes URL is just episodes URL with trivia?tab=qt tacked on
    logger.info("Third Call")
    quotes = f"{getQuote(quotessURL,'quotes')}" 
    logger.info(f"{quotes}")
    
    return quotes

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        speak_output = f"{orchestrate()}. Would you like another one ?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class HelloWorldIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("HelloWorldIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = f"{orchestrate()}. Would you like another one ?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "NINE NINE !"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HelloWorldIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
