import logging
import ask_sdk_core.utils as ask_utils
import openai

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from datetime import datetime
import locale

from epicstore_api import EpicGamesStoreAPI

from ask_sdk_model import Response


openai.api_key = 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

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        speak_output = "Bem vindo a skill dos jogos de graça. Diga o que você precisa."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class HelloWorldIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("HelloWorldIntent")(handler_input)

    def handle(self, handler_input):
        api = EpicGamesStoreAPI()
        promotions = api.get_free_games()
        
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        
        freeGames = []
        
        for game in promotions['data']['Catalog']['searchStore']['elements']:
            if game['promotions'] is not None:        
                if "promotionalOffers" in game['promotions']:
                    if game['promotions']['promotionalOffers']:
                        if(game['title'] != 'Mystery Game'):
                            freeGames.append(game['title'])
            
        if len(freeGames) > 1:
            speak_output = "O jogo que está de graça hoje é " + freeGames[0] + " e " + freeGames[1] + ". "
        else:
            speak_output = "O jogo que está de graça hoje é " + freeGames[0] + ". "
        
        
        gpt_response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=f"Quais são os jogos de graça hoje na Epic Games Store? {speak_output}",
            max_tokens=50
        )

        speak_output = gpt_response.choices[0].text  # A resposta gerada pelo GPT-3

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        speak_output = "Como posso te ajudar?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class CancelOrStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        speak_output = "Tudo bem, tchau!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class FallbackIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        logger.info("In FallbackIntentHandler")
        speech = "Hmm, eu não tenho certeza."
        reprompt = "Eu não entendi. Como posso te ajudar?"

        return handler_input.response_builder.speak(speech).ask(reprompt).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.response

class IntentReflectorHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "Você acionou a " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class CatchAllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        logger.error(exception, exc_info=True)

        speak_output = "Desculpe, eu tive um problema ao executar o que você pediu. Por favor, tente de novo."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HelloWorldIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler())

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
