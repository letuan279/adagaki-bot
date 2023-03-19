import pyaudio
import wave
import keyboard
import time

from voicevox import Client
import asyncio
import requests
import json

import os


async def speak(japanese_text, speaker_id=1):
    async with Client() as client:
        audio_query = await client.create_audio_query(
            japanese_text, speaker=speaker_id
        )
        with open("voice.wav", "wb") as f:
            f.write(await audio_query.synthesis(speaker=speaker_id))


def get_voice_text():
    url = "https://api.openai.com/v1/audio/translations"
    payload = {'model': 'whisper-1'}
    files = [
        ('file', ('recorded.wav', open(
            'recorded.wav', 'rb'), 'application/octet-stream'))
    ]
    headers = {
        'Authorization': 'Bearer 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'
    }
    response = requests.request(
        "POST", url, headers=headers, data=payload, files=files)
    # print("Voice text: " + response.text)
    res = json.loads(response.text)
    return res['text']


def translate_text(voice_text):
    url = "https://api.openai.com/v1/chat/completions"
    payload = json.dumps({
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant that translates any language to Japanese."
            },
            {
                "role": "user",
                "content": "Translate the following any language text to Japanese without Romaji and give me only one translation: 'How long will the summer in Vietnam last?'"
            },
            {
                "role": "assistant",
                "content": "「ベトナムの夏は何ヶ月続くのでしょうか？」"
            },
            {
                "role": "user",
                "content": "Translate the following any language text to Japanese without Romaji and give me only one translation: 'Tôi thích bạn'"
            },
            {
                "role": "assistant",
                "content": "「好きです」"
            },
            {
                "role": "user",
                "content": f"Translate the following any language text to Japanese without Romaji and give me only one translation: {voice_text}"
            }
        ]
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer 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'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    res = json.loads(response.text)
    return res['choices'][0]['message']['content']


def get_answer(question):
    url = "https://api.openai.com/v1/chat/completions"

    payload = json.dumps({
        "messages": [
            {
                "role": "system",
                "content": "You are nice Japanese girl that answer the any language question by response a short (< 150 character) Japanese answer"
            },
            {
                "role": "user",
                "content": "Xin chào bạn"
            },
            {
                "role": "assistant",
                "content": "こんにちは。"
            },
            {
                "role": "user",
                "content": "Hello"
            },
            {
                "role": "assistant",
                "content": "こんにちは。"
            },
            {
                "role": "user",
                "content": "私はサッカーが好き"
            },
            {
                "role": "assistant",
                "content": "素晴らしい！私もサッカーが好きです。"
            },
            {
                "role": "user",
                "content": "今何時"
            },
            {
                "role": "assistant",
                "content": "現在の時刻は、私がいる場所によって異なります。申し訳ありません。"
            },
            {
                "role": "user",
                "content": "あなたがいる場所は今何時"
            },
            {
                "role": "assistant",
                "content": "私は仮想的な存在であり、時間の概念がありません。ですから、常にどんな時間帯でもお話しできます。"
            },
            {
                "role": "user",
                "content": "Bạn có thích đá bóng không"
            },
            {
                "role": "assistant",
                "content": "はい、私もサッカーが好きです！"
            },
            {
                "role": "user",
                "content": f"{question}"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 256,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "model": "gpt-3.5-turbo"
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer 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'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    res = json.loads(response.text)
    return res['choices'][0]['message']['content']


def play_voice():
    wav_file = wave.open('voice.wav', 'rb')

    # Initialize PyAudio
    audio = pyaudio.PyAudio()

    # Open a stream and start playing the audio
    stream = audio.open(format=audio.get_format_from_width(wav_file.getsampwidth()),
                        channels=wav_file.getnchannels(),
                        rate=wav_file.getframerate(),
                        output=True)
    data = wav_file.readframes(1024)
    while data:
        stream.write(data)
        data = wav_file.readframes(1024)

    # Clean up resources
    stream.stop_stream()
    stream.close()
    audio.terminate()
    wav_file.close()


# define constants
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 5
SILENCE_SECONDS = 1

# initialize PyAudio

# start recording when F key is pressed
while True:
    if keyboard.is_pressed('f'):
        if os.path.exists('recorded.wav'):
            os.remove('recorded.wav')
        if os.path.exists('voice.wav'):
            os.remove('voice.wav')
        audio = pyaudio.PyAudio()
        stream = audio.open(format=FORMAT, channels=CHANNELS,
                            rate=RATE, input=True,
                            frames_per_buffer=CHUNK)
        print('Recording started')
        # open a new stream for recording
        frames = []
        start_time = time.time()

        # record audio for RECORD_SECONDS or until 2 seconds of silence
        while True:
            data = stream.read(CHUNK)
            frames.append(data)
            current_time = time.time()
            # check if there has been any input in the last 2 seconds
            if current_time - start_time > SILENCE_SECONDS and not any(frames[-int(RATE/CHUNK*SILENCE_SECONDS):]):
                print('Recording ended')
                break
            # check if recording time has exceeded RECORD_SECONDS
            elif current_time - start_time > RECORD_SECONDS:
                print('Recording ended')
                break

        # stop recording
        stream.stop_stream()
        stream.close()
        audio.terminate()

        # save recorded audio to a WAV file
        wf = wave.open('recorded.wav', 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

        voice_text = get_voice_text()

        print("Voice nói: " + voice_text)

        answer = get_answer(voice_text)
        print("Câu trả lời: " + answer)

        speaker = 5
        if(not isinstance(answer, str) or "I'm sorry" in answer or len(answer) > 150):
            asyncio.run(speak("答えがわかりません、すみません。", speaker))
            print("press f to continue...")
            continue

        asyncio.run(speak(answer, speaker))
        print("press f to continue...")
        # play_voice()
    if keyboard.is_pressed('k'):
        break
