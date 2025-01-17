
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import asyncio
import threading
import os
import sys
import time
from transformers import TextClassificationPipeline, AutoModelForSequenceClassification, AutoTokenizer
import numpy as np
import soundfile as sf
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
import sounddevice as sd
import azureS2T as aS2T
import json
import socket
import rospy
from std_msgs.msg import String
#import tkinter as tk
#from PIL import Image, ImageTk
from rtclient import (
    InputTextContentPart,
    RTAudioContent,
    RTClient,
    RTFunctionCallItem,
    RTMessageItem,
    RTResponse,
    UserMessageItem,
)
start_time = time.time()

# Example audio parameters (change these according to your data)
sample_rate = 24000  # in Hz
channels = 1  # mono audio; use 2 for stereo
dtype = 'int16'  # example dtype, can be 'float32', 'int16', etc., depending on your data

# Convert the bytearray to a numpy array for playback


image_list={}
image_list["question"]="input/Questions.jpeg"
image_list["exclamation"]="input/surprise.jpeg"
image_list["joy"]="input/joy.jpeg"
image_list["love"]="input/love.png"
image_list["surprise"]="input/surprise.jpeg"
image_list["fear"]="input/fear.jpeg"
image_list["sadness"]="input/sadness.jpg"
# Create the main window
current_image_path = "input/joy.jpeg"

text_chunk_index=0




def log(*args):
    elapsed_time_ms = int((time.time() - start_time) * 1000)
    print(f"{elapsed_time_ms} [ms]: ", *args)


sentence_dict={}

async def receive_message_item(item: RTMessageItem, out_dir: str):
    global client_socket
    prefix = f"[response={item.response_id}][item={item.id}]"
    async for contentPart in item:
        if contentPart.type == "audio":

            async def collect_audio(audioContentPart: RTAudioContent):
                global timestart
                timestart=time.time()
                audio_data = bytearray()
                global sentence_dict
                global audio_id
                global text_chunk_index
                await asyncio.sleep(1.5)
                text_chunk_index=0
                def callback(outdata, frames, time, status):
                   
                    if status:
                        print(status)
                    chunk_size = frames * 2  # 2 bytes per frame for int16
                    chunk = audio_data[:chunk_size]
                    if len(chunk) < chunk_size:
                        # If the chunk is smaller than expected, pad with zeros
                        chunk = chunk + bytearray(chunk_size - len(chunk))
                    outdata[:] = np.frombuffer(chunk, dtype=np.int16).reshape(-1, 1)
                    del audio_data[:chunk_size]

                stream = sd.OutputStream(samplerate=sample_rate, channels=channels, dtype=dtype, callback=callback)
                stream.start()
                audio_id=0  
                start_audio=time.time()
                timestart=time.time()
                async for chunk in audioContentPart.audio_chunks():
                    
                    audio_id+=1
                    audio_data.extend(chunk)
                    audio_tstamp=time.time()-timestart
                    #l=sentence_dict[str(text_chunk_index)]["chunk_id"]
                    d=time.time()-start_audio
                    #print(sentence_dict[str(text_chunk_index)]["sentence_emotion"])

                    #print ("sentence_id", text_chunk_index,"sentence length: ",l, "time:",(d))

                    if(text_chunk_index<len(sentence_dict)-1):
                        if audio_tstamp>=(sentence_dict[str(text_chunk_index)]["sentence_timestamp"]*7+sentence_dict[str(text_chunk_index)]["length"]*0.01):
                            text_chunk_index+=1
                            print("audio timestamp",audio_tstamp,"sentence timestamp",sentence_dict[str(text_chunk_index-1)]["sentence_timestamp"]*7+sentence_dict[str(text_chunk_index-1)]["length"]*0.01)
                            print(sentence_dict[str(text_chunk_index-1)]["sentence"])
                            message=sentence_dict[str(text_chunk_index)]["sentence_emotion"]
                            client_socket.send(message.encode('utf-8'))
                            response=client_socket.recv(1024).decode('utf-8')
                            
                    """  if (time.time()-start_audio)>l*0.22:
                        if(text_chunk_index<len(sentence_dict)+1):s
                            start_audio=time.time()
                            text_chunk_index+=1
                            #message=sentence

                            
                             """
                        
        
    
                            
                    while len(audio_data) >= sample_rate * channels * 2:
                        await asyncio.sleep(0.5)  # Allow the callback to process the audio data
                
                while len(audio_data) > 0:
                    await asyncio.sleep(2)
                stream.stop()
                stream.close()
                stop_audio=time.time()
                print("speaking done")
                print("Count of audio ids",audio_id, "Speaking time: "  ,stop_audio-start_audio)

                return audio_data
           
            async def collect_transcript(audioContentPart: RTAudioContent):
                timestart=time.time()
                sentence_list=[]
                sentence=""
                audio_transcript: str = ""
                global chunk_id
                chunk_id=0
                k=0
                global sentence_dict
                
                async for chunk in audioContentPart.transcript_chunks():
                    chunk_id+=1
                    sentence+=chunk
                    
                    #print(chunk)
                    if chunk in [".", "?", "!",":"]:
                        text_tstamp=time.time()-timestart
                        #append dict with k, sentence,chunk id and predicted_label
                        # Perform text classification
                        predicted_label=""
                        if "?" in sentence:
                             predicted_label="question"
                        elif "!" in sentence:
                             predicted_label="exclamation"
                        else:
                            result = pipeline(sentence)
                            predicted_label = result[0]['label']
                        # Print the predicted label
                       
                        if k>0:
                            old_key = str(k-1)
                            l=chunk_id-sentence_dict[old_key]["chunk_id"]
                        else:
                            l=chunk_id
                        new_key = str(k)
                        
                        sentence_dict[new_key]={"sentence":sentence,"chunk_id":chunk_id,"sentence_emotion":predicted_label,"length":len(sentence),"sentence_timestamp":text_tstamp}
                        sentence=""
                        k+=1
                    audio_transcript += chunk
                
                #print("transcription done with chunk ids :", chunk_id)
                #print("Count of chunk ids",sentence_dict)
                #print(sentence_list)
                return audio_transcript

            audio_task = asyncio.create_task(collect_audio(contentPart))
            transcript_task = asyncio.create_task(collect_transcript(contentPart))
            audio_data, audio_transcript = await asyncio.gather(audio_task, transcript_task)
            #print(prefix, f"Audio received with length: {len(audio_data)}")
            #print(prefix, f"Audio Transcript: {audio_transcript}")
            print (sentence_dict)
            
            """  with open(os.path.join(out_dir, f"{item.id}_{contentPart.content_index}.wav"), "wb") as out:
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
                sf.write(out, audio_array, samplerate=24000) """
            with open(
                os.path.join(out_dir, f"{item.id}_{contentPart.content_index}.audio_transcript.txt"),
                "w",
                encoding="utf-8",
            ) as out:
                out.write(audio_transcript)
            
        elif contentPart.type == "text":
            text_data = ""
            async for chunk in contentPart.text_chunks():
                text_data += chunk
            print(prefix, f"Text: {text_data}")
            with open(
                os.path.join(out_dir, f"{item.id}_{contentPart.content_index}.text.txt"), "w", encoding="utf-8"
            ) as out:
                out.write(text_data)


async def receive_function_call_item(item: RTFunctionCallItem, out_dir: str):
    prefix = f"[function_call_item={item.id}]"
    await item
    print(prefix, f"Function call arguments: {item.arguments}")
    with open(os.path.join(out_dir, f"{item.id}.function_call.json"), "w", encoding="utf-8") as out:
        out.write(item.arguments)


async def receive_response(client: RTClient, response: RTResponse, out_dir: str):
    prefix = f"[response={response.id}]"
    async for item in response:
        print(prefix, f"Received item {item.id}")
        if item.type == "message":
            asyncio.create_task(receive_message_item(item, out_dir))
            await receive_message_item(item, out_dir)
        elif item.type == "function_call":
            asyncio.create_task(receive_function_call_item(item, out_dir))

    print(prefix, f"Response completed ({response.status})")
    #if response.status == "completed":
        #await client.close()


async def run(client: RTClient, instructions_file_path: str, out_dir: str):
    global client_socket
    with open(instructions_file_path, encoding="utf-8") as instructions_file:
        instructions = instructions_file.read()

        log("Configuring Session...")
        await client.configure(instructions=instructions,voice='echo')
        client_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        HOST="192.168.120.240"
        PORT=12345
        client_socket.connect((HOST,PORT))
        log("Done")
    
        with open('languages.json', 'r') as json_file:
            lang_file = json.load(json_file)

        lang=lang_file["English"]
        while True:
            user_message=""
            while user_message=="":
                #user_message=aS2T.recognize_from_microphone(lang)
                user_message=input("type your message ")
            #user_message = input("Enter your message (type 'stop' to end): ")
            if "Stop." in user_message or "Goodbye." in user_message or "Bye." in user_message:
                break
            
           
            log("Sending User Message...")
            await client.send_item(UserMessageItem(content=[InputTextContentPart(text=user_message)]))

            log("Done")
            response = await client.generate_response()
            await receive_response(client, response, out_dir)

        log("Closing client...")
        await client.close()
        client_socket.close()
        log("Client closed")



def get_env_var(var_name: str) -> str:
    value = os.environ.get(var_name)
    if not value:
        raise OSError(f"Environment variable '{var_name}' is not set or is empty.")
    return value


async def with_azure_openai(instructions_file_path: str, out_dir: str):
    endpoint = get_env_var("AZURE_OPENAI_ENDPOINT")
    key = get_env_var("AZURE_OPENAI_API_KEY")
    deployment = get_env_var("AZURE_OPENAI_DEPLOYMENT")
    async with RTClient(url=endpoint, key_credential=AzureKeyCredential(key), azure_deployment=deployment) as client:
        await run(client, instructions_file_path, out_dir)


async def with_openai(instructions_file_path: str, user_message_file_path: str, out_dir: str):
    key = get_env_var("OPENAI_API_KEY")
    model = get_env_var("OPENAI_MODEL")
    async with RTClient(key_credential=AzureKeyCredential(key), model=model) as client:
        await run(client, instructions_file_path, user_message_file_path, out_dir)

# Load the fine-tuned model and tokenizer
model_name = "ahmettasdemir/distilbert-base-uncased-finetuned-emotion"
model = AutoModelForSequenceClassification.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Create the text classification pipeline
pipeline = TextClassificationPipeline(model=model, tokenizer=tokenizer)

def publisher():
        global text_chunk_index,sentence_dict
       
        last_tci=0
        pub = rospy.Publisher('chatter', String, queue_size=10)
        rospy.init_node('Emotion', anonymous=True)
        rate = rospy.Rate(10)  # 10 Hz
        while not rospy.is_shutdown():
            if (text_chunk_index>last_tci) :
                message=sentence_dict[str(text_chunk_index)]["sentence_emotion"]
            rospy.loginfo(message)
            pub.publish(message)
            rate.sleep()
            
        while True:
            try:
               
                    client_socket.send(message.encode('utf-8'))
                    response=client_socket.recv(1024).decode('utf-8')
                    #print(response)
                    last_tci=last_tci+1
            except(KeyboardInterrupt):
                break

                

def main():
    """Main function to run the image loop in a separate thread."""
    global current_image_path
    load_dotenv()
    instructions_file_path="instructionsenglish.text"
    out_dir="outputs"
    asyncio.run(with_azure_openai(instructions_file_path, out_dir))

if __name__ == "__main__":
    """ load_dotenv()
    if len(sys.argv) < 3:
        log(f"Usage: python {sys.argv[0]} <instructions_file> <message_file> <out_dir> [azure|openai]")
        log("If the last argument is not provided, it will default to azure")
        sys.exit(1)

    instructions_file_path = sys.argv[1]
    user_message_file_path = sys.argv[2]
    out_dir = sys.argv[3]
    provider = sys.argv[4] if len(sys.argv) == 4 else "azure"

    if not os.path.isfile(instructions_file_path):
        log(f"File {instructions_file_path} does not exist")
        sys.exit(1)

    if not os.path.isfile(user_message_file_path):
        log(f"File {user_message_file_path} does not exist")
        sys.exit(1)

    if not os.path.isdir(out_dir):
        log(f"Directory {out_dir} does not exist")
        sys.exit(1)

    if provider not in ["azure", "openai"]:
        log(f"Provider {provider} needs to be one of 'azure' or 'openai'")
        sys.exit(1)

    if provider == "azure":
        asyncio.run(with_azure_openai(instructions_file_path, out_dir))
    else:
        asyncio.run(with_openai(instructions_file_path, user_message_file_path, out_dir)) """
    main()