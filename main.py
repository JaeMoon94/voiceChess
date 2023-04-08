import speech_recognition as sr
import pyttsx3 # to create response
import spacy# package to extract the features
from transformers import pipeline

r = sr.Recognizer()
nlp = spacy.load("en_core_web_md")
# classifier = pipeline('text-classification', model='distilbert-base-uncased-finetuned-sst-2-english')
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
candidate_labels = ['Directive', 'Info Request', 'Conversational Inquiry', 'Approval', 'Disapproval']

engine = pyttsx3.init()
#
#
def detectIntent(text):
    # Your intent classification code goes here.
    #
    # (feel free to define and call as many
    #  subsidiary functions as you like.)

    sequence_to_classify = text

    classified = classifier(sequence_to_classify, candidate_labels, multi_label=True)

    return classified



def respond(text):
    detected_intent = detectIntent(text)

    # Code to customize your response based
    # on the detected intent goes here.

    response = detected_intent['labels'][0]
    print(response)

    return response


if __name__=='__main__':
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        r.energy_threshold = 150
        print('Okay, go!')
        audio = r.listen(source)
        audio = r.record(source, duration=5)
        text = r.recognize_google(audio)
        # text = "NO NO"

        response = respond(text)
        print(response)
        if "Directive" in response:
            engine.say("Yes Sir I'll do what you say")
        elif "Request" in response:
            engine.say("That is such a Interesting request sir, I'll look into it")
        elif "Conversational" in response:
            engine.say("Thanks for talking to me sir.. I would love to talk to you")
        elif "Approval" in response:
            engine.say("Thanks the pleasure is own mine")
        elif "Disapproval" in response:
            engine.say("Sorry to hear that sir is there anything I can do for you?")
        engine.runAndWait()

        intents = {
            "DIRECTIVE": [
                "Turn on the lights", "Open the door", "Go right at the intersection",
                "Buy some cupcakes while you're at the store",
                "Would you turn the lights down please", "Stop", "Stop right there", "Please don't do that again",
                "Turn up the volume", "Add milk to the shopping list, would you", "Eat your vegetables",
                "Don't knock over the vase", "Can you pour me a glass of milk please",
                "I want you to paint this wall blue"
            ],
            "INFO_REQUEST": [
                "How far away is the moon", "What is a mars rover", "Can you tell me where Colorado is",
                "How many legs does a spider have", "Tell me how to use a piano",
                "Do you know who Benjamin Franklin is", "Who was Marilyn Monroe",
                "Name the ten largest animals on earth",
                "Why are butterflies so colorful", "Give me the current Dow Jones index",
                "Tomorrow's weather, what will it be like", "Jim Henson was the voice of which famous frog puppet",
                "What should you do if your best friend is choking",
                "If I am traveling to New Hampshire which freeway should I take"
            ],
            "CONV_INQUIRY": [
                "What's your name", "Do you have a favorite movie", "Who is your favorite actor", "How's it going",
                "Are you a fan of Stephen King", "Will it snow tomorrow, do you think",
                "Tell me your thoughts on polymorphism",
                "What's your opinion on global warming", "Okay, but what's your spirit animal",
                "Have you ever watched Gone With the Wind",
                "What would you do if you had a million dollars", "Did you know that my favorite color is green",
                "Would you like to play chess"
            ],
            "APPROVAL": [
                "That's great", "Awesome", "I'm glad to hear it", "Hey cool",
                "Hahaha", "That's funny", "I like that"
            ],
            "DISAPPROVAL": [
                "That's wrong", "I am unhappy", "You suck", "Why won't you listen to me you stupid robot",
                "I'm sad now", "Stop, just stop", "no no no no no", "i hate this"]
        }
