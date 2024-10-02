from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.signals import user_logged_in, user_logged_out  # Correct imports

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_time_spent = models.DurationField(default=timedelta())  # Use an instance of timedelta
    last_login_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.user.username

# Create or update the user profile when a User instance is created or saved
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

# Update last login time when a user logs in
@receiver(user_logged_in)
def update_last_login(sender, request, user, **kwargs):
    user_profile = user.userprofile  # Access the user profile
    user_profile.last_login_time = timezone.now()  # Set the current time
    user_profile.save()  # Save the profile

# Update total time spent when a user logs out
@receiver(user_logged_out)
def update_total_time_spent(sender, request, user, **kwargs):
    user_profile = user.userprofile
    if user_profile.last_login_time:
        time_spent = timezone.now() - user_profile.last_login_time  # Calculate time spent since last login
        user_profile.total_time_spent += time_spent  # Update the total time spent
        user_profile.save()  # Save the profile


from django.db import models
from django.contrib.auth.models import User

class Joke(models.Model):
    joke_text = models.TextField()
    categories = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.joke_text


class JokeFeedback(models.Model):
    FEEDBACK_CHOICES = (
        ('like', 'Like'),
        ('dislike', 'Dislike'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joke = models.ForeignKey(Joke, on_delete=models.CASCADE)
    feedback_type = models.CharField(max_length=10, choices=FEEDBACK_CHOICES)

    class Meta:
        unique_together = ('user', 'joke')

    def __str__(self):
        return f"{self.user.username} - {self.joke.joke_text} - {self.feedback_type}"


