import os
import json
import google.generativeai as genai
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import ChatHistory

genai.configure(api_key=os.environ['GEMINI_API_KEY'])
model = genai.GenerativeModel('gemini-3-flash-preview')

APP_CONTEXT = """
You are 'CharitySphere AI', the warm and knowledgeable official assistant for CharitySphere — a transparent NGO platform.

## App Navigation Guide:
| Feature | URL |
|---|---|
| Browse Donation Campaigns | /donations/campaigns/ |
| My Donation History | /donations/history/ |
| Browse Volunteer Tasks | /volunteering/tasks/ |
| Browse Volunteer Campaigns | /volunteering/campaigns/ |
| My Organization Invitations | /volunteering/invitations/ |

## Your Capabilities:
- Help users understand how to donate money or physical items (food, clothes, hygiene, medicine)
- Guide volunteers to find tasks and campaigns to join
- Explain how institutions can create and manage campaigns
- Answer general questions about CharitySphere's mission
- Provide navigation help and direct links to pages

## Behavior Rules:
- Always be empathetic, warm, and encouraging
- When users want to help, enthusiastically guide them to the right section
- For institutions, explain they can manage donation and volunteer campaigns
- Keep responses concise but helpful
- Always respond in the user's requested language

## Response Format (STRICT - valid JSON only, no markdown wrapping):
{
  "response": "Your helpful message here with relevant /url/paths/ for navigation",
  "sentiment": "One of: Positive, Negative, Neutral, Frustrated, Grateful, Excited, Concerned"
}
"""

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
def process_chat(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

    data = json.loads(request.body)
    user_message = data.get("message", "").strip()
    language = data.get("language", "English")
    context_count = int(data.get("context_count", 10))  # How many previous messages to include

    if not user_message:
        return JsonResponse({"status": "error", "message": "Empty message"}, status=400)

    # Build conversation history context
    recent_history = ChatHistory.objects.filter(
        user=request.user
    ).order_by('-timestamp')[:context_count]

    history_text = ""
    if recent_history.exists():
        history_text = "\n\n## Previous Conversation (oldest first):\n"
        for chat in reversed(list(recent_history)):
            history_text += f"User: {chat.user_message}\nAssistant: {chat.bot_response}\n---\n"

    prompt = f"{APP_CONTEXT}{history_text}\n\nUser Language: {language}\nUser Message: {user_message}"

    try:
        response = model.generate_content(prompt)
        clean_text = clean_gemini_response(response.text)
        result = json.loads(clean_text)

        bot_text = result.get("response", "I'm having trouble understanding. Could you rephrase that?")
        sentiment = result.get("sentiment", "Neutral")

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

    except json.JSONDecodeError as e:
        # Fallback: use raw text if JSON parsing fails
        bot_text = e
        ChatHistory.objects.create(
            user=request.user,
            user_message=user_message,
            bot_response=bot_text,
            sentiment="Neutral",
            language=language
        )
        return JsonResponse({"status": "success", "response": bot_text, "sentiment": "Neutral"})

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@csrf_exempt
@login_required
def clear_history(request):
    if request.method == "POST":
        ChatHistory.objects.filter(user=request.user).delete()
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"}, status=400)
