import os
import json
import google.generativeai as genai
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import ChatHistory

# Configure Gemini (Add your API Key to environment variables)
# genai.configure(api_key="YOUR_GEMINI_API_KEY")
genai.configure(api_key=os.environ['GEMINI_API_KEY'])
model = genai.GenerativeModel('gemini-3-flash-preview')

APP_CONTEXT = """
You are 'CharitySphere AI', the official assistant for CharitySphere NGO.
App Map:
- Donation Campaigns: /donations/campaigns/
- Donation History: /donations/history/
- Volunteer Tasks: /volunteering/tasks/
- Volunteer Campaigns: /volunteering/campaigns/
- Organization Invitations: /volunteering/invitations/

If a user wants to help or donate, guide them to these specific links.
Always respond in the requested language.
Crucially, you must return your response in a valid JSON format with two keys:
"response" (the text for the user) and "sentiment" (choose one: Positive, Negative, Neutral, Frustrated, Grateful).
"""

@login_required
def chat_full_screen(request):
    """Dedicated full-screen chat page"""
    history = ChatHistory.objects.filter(user=request.user).order_by('-timestamp')[:50]
    return render(request, 'chatbot/full_screen.html', {'history': reversed(list(history))})

@csrf_exempt
@login_required
def process_chat(request):
    """AJAX endpoint for chatbot processing"""
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("message")
        language = data.get("language", "English")

        # Prepare Prompt
        prompt = f"{APP_CONTEXT}\nUser Language: {language}\nUser Message: {user_message}"

        try:
            response = model.generate_content(prompt)
            # Clean response text as Gemini sometimes wraps JSON in markdown blocks
            clean_text = response.text.replace('```json', '').replace('```', '').strip()
            result = json.loads(clean_text)

            bot_text = result.get("response", "I'm having trouble connecting. Please try again.")
            sentiment = result.get("sentiment", "Neutral")

            # Save to Database
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

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)
