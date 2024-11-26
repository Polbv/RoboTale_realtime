import os
import azure.cognitiveservices.speech as speechsdk
""" from azure.ai.translation.text import TextTranslationClient, TranslatorCredential
from azure.ai.translation.text.models import InputTextItem """
from azure.core.exceptions import HttpResponseError 
import time

#This file contains functions interacting with Azure AI services. Speech recognition,Audio Synthesis and translation
speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))

def recognize_from_microphone(lang_in):
   
    speech_config.speech_recognition_language=lang_in["S2T"]
    #speech_config.speech_recognition_language="da-DK"

    # audio_config = speechsdk.audio.AudioConfig(device_name=Tale.devname)
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)
    speech_recognizer.recognizer_initial_silence_timeout = 10
    print("Speak into your microphone.")
    speech_recognition_result = speech_recognizer.recognize_once_async().get()

    if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Recognized: {}".format(speech_recognition_result.text))
    elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(speech_recognition_result.no_match_details))
    elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_recognition_result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
            print("Did you set the speech resource key and region values?")
    return(speech_recognition_result.text)

def audio_setup(lang_out):

    audio_config = speechsdk.audio.AudioOutputConfig(device_name="hw:CARD=ArrayUAC10,DEV=0")
    speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
    speech_config.speech_synthesis_voice_name=lang_out["T2S"]
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    return(speech_synthesizer)

def audio_sythesis(text,lang_out):
  
    #audio_config = speechsdk.audio.AudioOutputConfig(device_name="hw:CARD=ArrayUAC10,DEV=0")

    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

    
    speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
    speech_config.speech_synthesis_voice_name=lang_out["T2S"]
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)


    speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()
    #speech_synthesis_result =speech_synthesizer.speak_text(text)
    #speech_synthesis_result =speech_synthesizer
    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        #print("Speech synthesized for text [{}]".format(text))
        a=1

    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")
    return(speech_synthesis_result)

""" def translate_text(input_text,lang_in,lang_out):
    # set `<your-key>`, `<your-endpoint>`, and  `<region>` variables with the values from the Azure portal
    

    credential = TranslatorCredential(TRANSLATIONKEY, TRANSREGION)
    text_translator = TextTranslationClient(endpoint=TRANSENDPOINT, credential=credential)

    try:
        source_language = lang_in["translation"]
        target_languages = [lang_out["transalation"]]
        input_text_elements = [ InputTextItem(text = input_text) ]

        response = text_translator.translate(content = input_text_elements, to = target_languages, from_parameter = source_language)
        translation = response[0] if response else None

        if translation:
            for translated_text in translation.translations:
                translation_text=translated_text.text
                print(f"Text was translated to: '{translated_text.to}' and the result is: '{translated_text.text}'.")

    except HttpResponseError as exception:
        print(f"Error Code: {exception.error.code}")
        print(f"Message: {exception.error.message}")

    return translation_text """

def speech_recognize_keyword_from_microphone(lang_in):
    """performs keyword-triggered speech recognition with input microphone"""
    speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
    speech_config.speech_recognition_language=lang_in["S2T"]
    # Creates an instance of a keyword recognition model. Update this to
    # point to the location of your keyword recognition model.
    model = speechsdk.KeywordRecognitionModel("config/Keyword_models/Robot.table")

    # The phrase your keyword recognition model triggers on.
    keyword = "robot"

    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)
    text=""
    done = False

    def stop_cb(evt):
        """callback that signals to stop continuous recognition upon receiving an event `evt`"""
        print('CLOSING on {}'.format(evt))
        nonlocal done
        done = True
        

    def recognizing_cb(evt):
        """callback for recognizing event"""
        if evt.result.reason == speechsdk.ResultReason.RecognizingKeyword:
            print('RECOGNIZING KEYWORD: {}'.format(evt))
        elif evt.result.reason == speechsdk.ResultReason.RecognizingSpeech:
            print('RECOGNIZING: {}'.format(evt))

    def recognized_cb(evt):
        """callback for recognized event"""
        
        if evt.result.reason == speechsdk.ResultReason.RecognizedKeyword:
            print('RECOGNIZED KEYWORD: {}'.format(evt))
        elif evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print('RECOGNIZED: {}'.format(evt))
            nonlocal text
            text=evt
        elif evt.result.reason == speechsdk.ResultReason.NoMatch:
            print('NOMATCH: {}'.format(evt))
    # Connect callbacks to the events fired by the speech recognizer
    speech_recognizer.recognizing.connect(recognizing_cb)
    speech_recognizer.recognized.connect(recognized_cb)
    speech_recognizer.session_started.connect(lambda evt: print('SESSION STARTED: {}'.format(evt)))
    speech_recognizer.session_stopped.connect(lambda evt: print('SESSION STOPPED {}'.format(evt)))
    speech_recognizer.canceled.connect(lambda evt: print('CANCELED {}'.format(evt)))
    # stop continuous recognition on either session stopped or canceled events
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)

    # Start keyword recognition
    speech_recognizer.start_keyword_recognition(model)
    print('Say something starting with "{}" followed by whatever you want...'.format(keyword))
    while not done:
        time.sleep(.5)

    speech_recognizer.stop_keyword_recognition()
    return text.result.text

def streamtts(Tale,chat,lang_out):
    model=Tale.Llm
    # setup speech synthesizer
    # IMPORTANT: MUST use the websocket v2 endpoint
    speech_config = speechsdk.SpeechConfig(endpoint=f"wss://{os.getenv('SPEECH_REGION')}.tts.speech.microsoft.com/cognitiveservices/websocket/v2",
                                        subscription=os.getenv("SPEECH_KEY"))
    
    # set a voice name
    audio_config = speechsdk.audio.AudioOutputConfig(device_name=Tale.devname)
    #audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
    speech_config.speech_synthesis_voice_name = lang_out["T2S"] 
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config,audio_config=audio_config)

    speech_synthesizer.synthesizing.connect(lambda evt: print("[audio]", end=""))

    # set timeout value to bigger ones to avoid sdk cancel the request when GPT latency too high
    properties = dict()
    properties["SpeechSynthesis_FrameTimeoutInterval"]="60000"
    properties["SpeechSynthesis_RtfTimeoutThreshold"]="10"
    speech_config.set_properties_by_name(properties)
    #speech_config.set_property(speechsdk.PropertyId.SpeechServiceConnection_SynthLanguage, "da-DK")
    #speech_config.set_property(speechsdk.PropertyId.SpeechServiceConnection_SynthVoice, lang_out["T2S"])


    # create request with TextStream input type
    tts_request = speechsdk.SpeechSynthesisRequest(input_type = speechsdk.SpeechSynthesisRequestInputType.TextStream)
    tts_task = speech_synthesizer.speak_async(tts_request)     
    output_text=""
    sentence=""
    for chunk in model.stream(chat):
        if(lang_out["name"]=="English"):

            chunk_text = chunk.content
            if chunk_text:
                output_text=output_text+chunk_text
                print(chunk_text, end="")
                tts_request.input_stream.write(chunk_text)
        else:
            
            chunk_text = chunk.content
            sentence=sentence+chunk_text
            if chunk_text in [".","!","?",":"] :
                output_text=output_text+sentence
                print(sentence, end="|")
                tts_request.input_stream.write(sentence)
                sentence=""

    print("[GPT END]", end="")

    # close tts input stream when GPT finished
    tts_request.input_stream.close()

    # wait all tts audio bytes return
    result = tts_task.get()
    print("[TTS END]", end="")

    return(output_text)
