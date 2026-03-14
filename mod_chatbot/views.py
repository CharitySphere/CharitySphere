import os
import json
from google import genai
from google.genai import types
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import ChatHistory
from .utils import get_dynamic_system_prompt

client = genai.Client(api_key=os.environ.get('CS_API_KEY'))
MODEL_ID = 'gemini-3-flash-preview'

LANGUAGES = [
    "Afrikaans", "Albanian", "Amharic", "Arabic", "Armenian", "Assamese",
    "Azerbaijani", "Basque", "Belarusian", "Bengali", "Bosnian", "Bulgarian",
    "Catalan", "Chinese (Simplified)", "Chinese (Traditional)", "Croatian",
    "Czech", "Danish", "Dutch", "English", "Estonian", "Farsi", "Filipino",
    "Finnish", "French", "Galician", "Georgian", "German", "Greek", "Gujarati",
    "Hebrew", "Hindi", "Hungarian", "Icelandic", "Indonesian", "Italian",
    "Japanese", "Kannada", "Kazakh", "Khmer", "Korean", "Lao", "Latvian",
    "Lithuanian", "Macedonian", "Malay", "Malayalam", "Marathi", "Mongolian",
    "Nepali", "Norwegian", "Odia", "Polish", "Portuguese", "Punjabi",
    "Romanian", "Russian", "Serbian", "Slovak", "Slovenian", "Spanish",
    "Swahili", "Swedish", "Tamil", "Telugu", "Thai", "Turkish", "Ukrainian",
    "Urdu", "Uzbek", "Vietnamese", "Zulu"
]


def clean_gemini_response(text):
    """Strip markdown code fences from Gemini response."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first and last fence lines
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines).strip()
    return text


@login_required
def chat_full_screen(request):
    history = ChatHistory.objects.filter(user=request.user).order_by('timestamp')[:100]
    return render(request, 'chatbot/full_screen.html', {
        'history': history,
        'languages': LANGUAGES,
    })


@csrf_exempt
@login_required
@csrf_exempt
@login_required
def process_chat(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

    try:
        data = json.loads(request.body)
        user_message = data.get("message", "").strip()
        language = data.get("language", "English")
        context_count = int(data.get("context_count", 10))

        if not user_message:
            return JsonResponse({"status": "error", "message": "Empty message"}, status=400)

        # 1. Fetch Dynamic System Context based on Profile
        system_prompt = get_dynamic_system_prompt(request.user)

        # 2. Build conversation history
        recent_history = ChatHistory.objects.filter(
            user=request.user
        ).order_by('-timestamp')[:context_count]

        history_text = ""
        if recent_history.exists():
            history_text = "\n\n## Recent Conversation History:\n"
            for chat in reversed(list(recent_history)):
                history_text += f"User: {chat.user_message}\nAssistant: {chat.bot_response}\n---\n"

        final_prompt = f"{system_prompt}{history_text}\n\nUser Language: {language}\nUser Message: {user_message}"

        # 3. Call Gemini
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=final_prompt,
            config=types.GenerateContentConfig(
                response_mime_type='application/json',
                temperature=0.2,
            )
        )

        # 4. Parse Result
        result = json.loads(response.text or "{}")
        bot_text = result.get("response", "I'm here to help, but I had a technical glitch. Could you try again?")
        sentiment = result.get("sentiment", "Neutral")

        # 5. Save to History
        ChatHistory.objects.create(
            user=request.user,
            user_message=user_message,
            bot_response=bot_text,
            sentiment=sentiment,
            language=language
        )

        return JsonResponse({
            "status": "success",
            "response": bot_text,
            "sentiment": sentiment
        })

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@csrf_exempt
@login_required
def clear_history(request):
    if request.method == "POST":
        ChatHistory.objects.filter(user=request.user).delete()
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"}, status=400)
