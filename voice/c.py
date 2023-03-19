import os
import pyaudio
import wave
import keyboard
import time

from voicevox import Client
import asyncio
import requests
import json
import sys
import base64


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


sys.stdout.reconfigure(encoding='utf-8')
input_text = sys.argv[1]

utf8Text = base64.b64decode(input_text).decode('utf-8')
print("utf8Text: " + utf8Text)

answer = get_answer(utf8Text)
print("Câu trả lời: " + answer)

speaker = 4
asyncio.run(speak(answer, speaker))

print("Done")
