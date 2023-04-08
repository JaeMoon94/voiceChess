import speech_recognition as sr
import time
import torch
from transformers import pipeline, Wav2Vec2ForCTC, AutoTokenizer, Wav2Vec2Processor


r = sr.Recognizer()
import pyttsx3
engine = pyttsx3.init()

model_name = "facebook/wav2vec2-large-960h-lv60-self"
model_whisper_large = "openai/whisper-large"
model_whisper_medium = "openai/whisper-medium"
model_whisper_small = "openai/whisper-small"
model_whisper_tiny = "openai/whisper-tiny.en"

# processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-large-960h-lv60-self")
model = Wav2Vec2ForCTC.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

classifier = pipeline("zero-shot-classification", model=model, tokenizer=tokenizer)
candidate_labels = ['Super Miro Video Game',
                    'Music Domain Composition']

res = classifier("Start a new composition in 4/4 time signature with a tempo of 120 BPM.", candidate_labels)

# start = time.perf_counter()
print(res)
# end = time.perf_counter() - start
# print('{:.6f}s for the calculation'.format(end))

# with sr.Microphone() as source:
#     print('Calibrating...')
#     #r.adjust_for_ambient_noise(source)
#     #r.energy_threshold = 150
#     print('Okay, go!')
#     audio = r.listen(source)
#     #audio = r.record(source,duration = 5)
#     text = r.recognize_google(audio)
#     print("You said " + text)
#     engine.say(text)
#     engine.runAndWait()



# Utterance of Super Mario video games:

# "Jump over the Goomba and collect the mushroom."
# "Use the fire flower to defeat Bowser."
# "Watch out for the Piranha Plant on the ceiling."
# "Swim through the underwater tunnel to reach the secret exit."
# "Grab the star to become invincible."
# "Avoid falling into the lava pit."
# "Wall jump up to the platform to reach the warp pipe."
# "Hit the question block to reveal a power-up."
# "Ground pound to break the blocks below."
# "Ride the green shell to take out multiple enemies at once."


# Utterance of music composition.

# "Start a new composition in 4/4 time signature with a tempo of 120 BPM."
# "Add a new piano track and set it to a soft, mellow sound."
# "Create a melody using the notes C, E, and G in a major key."
# "Quantize the drum track to the nearest eighth note."
# "Apply a reverb effect to the guitar track and adjust the decay time to 2 seconds."
# "Duplicate the bass track and transpose it up an octave."
# "Change the time signature to 6/8 and adjust the tempo to 90 BPM."
# "Add a new instrument track and choose a trumpet sound."
# "Create a chord progression using the chords G, D, Em, and C."
# "Mute the second half of the chorus section on the vocal track."