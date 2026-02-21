from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('full/', views.chat_full_screen, name='full_screen'),
    path('send/', views.process_chat, name='send_message'),
]
