from django.contrib import admin
from .models import UserProfile,Joke, JokeFeedback  # Import your models here

# Register your models here
admin.site.register(UserProfile)

admin.site.register(Joke)
admin.site.register(JokeFeedback)
