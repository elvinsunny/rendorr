from django.shortcuts import render
from dotenv import load_dotenv
import os
# Create your views here.
# views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request, 'ind.html')






from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count, Q, Sum  # Import Sum for aggregating time spent
from .models import UserProfile, Joke, JokeFeedback
from django.contrib.auth.models import User

# Custom decorator to restrict access to superusers only
def superuser_required(view_func):
    decorated_view_func = user_passes_test(lambda user: user.is_superuser)(view_func)
    return decorated_view_func

@superuser_required
def admin_dashboard(request):
    # Fetch necessary statistics for the dashboard
    total_users = User.objects.count()
    total_jokes = Joke.objects.count()
    total_feedbacks = JokeFeedback.objects.count()

    # Aggregate total time spent by all users
    total_time_spent = UserProfile.objects.aggregate(total_time=Sum('total_time_spent'))['total_time']

    # User statistics
    users_with_most_feedback = User.objects.annotate(feedback_count=Count('jokefeedback')).order_by('-feedback_count')[:5]

    # Jokes statistics
    jokes_with_most_likes = Joke.objects.annotate(like_count=Count('jokefeedback', filter=Q(jokefeedback__feedback_type='like'))).order_by('-like_count')[:5]
    jokes_with_most_dislikes = Joke.objects.annotate(dislike_count=Count('jokefeedback', filter=Q(jokefeedback__feedback_type='dislike'))).order_by('-dislike_count')[:5]

    # User profiles with their total time spent
    users_with_time_spent = UserProfile.objects.select_related('user').order_by('-total_time_spent')[:5]

    # Pass all the statistics to the template context
    context = {
        'total_users': total_users,
        'total_jokes': total_jokes,
        'total_feedbacks': total_feedbacks,
        'total_time_spent': total_time_spent,  # Total time spent by all users
        'users_with_most_feedback': users_with_most_feedback,
        'jokes_with_most_likes': jokes_with_most_likes,
        'jokes_with_most_dislikes': jokes_with_most_dislikes,
        'users_with_time_spent': users_with_time_spent,  # Top users by time spent
    }

    return render(request, 'admin_dashboard.html', context)





from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


from django.shortcuts import render
from django.contrib.auth.models import User
from .models import UserProfile

def user_list(request):
    users = User.objects.all()
    user_profiles = UserProfile.objects.select_related('user')
    
    # Pass users and their time spent to the template
    context = {
        'users': user_profiles,
    }
    return render(request, 'user_list.html', context)


from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate

# Custom login view for handling superuser redirection
def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_superuser:
                    return redirect('admin_dashboard')  # Redirect superuser to the user list page
                else:
                    return redirect('home')  # Regular user goes to the home page
    else:
        form = AuthenticationForm()
    
    return render(request, 'login.html', {'form': form})



# import os
# from django.shortcuts import render
# import google.generativeai as genai

# # Hardcoding the API key for quick testing (not recommended for production)
# api_key = "AIzaSyCI4NREOv01U6o__ipo0d9x2UWC23OawlA"
# genai.configure(api_key=api_key)  # Configure the Google AI SDK

# generation_config = {
#     "temperature": 1,
#     "top_p": 0.95,
#     "top_k": 64,
#     "max_output_tokens": 8192,
#     "response_mime_type": "text/plain",
# }

# aimodel = genai.GenerativeModel(
#     model_name="gemini-1.5-flash",
#     generation_config=generation_config,
#     system_instruction=("What you have to do is user will input a joke "
#                         "and you have to say which category that joke belongs to. "
#                         "Give only one single category, don't give multiple categories. "
#                         "If the entered one is not even a joke, also say that. "
#                         "If you cannot classify under it any category, say it is not a joke. "
#                         "Say the joke category only, don't say anything else.\n"),
# )

# def classify_joke(request):
#     joke_category = ""  # Initialize variable to hold joke category
#     if request.method == 'POST':
#         user_joke = request.POST.get('joke_input', '')
#         if not user_joke:
#             joke_category = 'No joke provided.'  # Handle empty input
#         else:
#             try:
#                 # Start a chat session with the AI model
#                 chat_session = aimodel.start_chat(
#                     history=[
#                         {"role": "user", "parts": [user_joke]},
#                     ]
#                 )
#                 response = chat_session.send_message(user_joke)

#                 # Set the response text as the joke category
#                 joke_category = response.text.strip()
                
#             except Exception as e:
#                 joke_category = 'Error processing the joke: {}'.format(str(e))

#     return render(request, 'joke_classifier.html', {'joke_category': joke_category})




from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .models import Joke
import google.generativeai as genai
load_dotenv()

# Set up your API key here
api_key = os.getenv('API_KEY1')
genai.configure(api_key=api_key)  # Replace with your actual API key

# Model configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Set up the model with system instruction for joke categorization
aimodel = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction="User will input a joke, and you must categorize it into a single category like 'pun', 'knock-knock', etc. If it cannot be categorized as a joke, say 'not a joke'. Respond with the category only.",
)

@login_required(login_url='login')  # Specify the URL to redirect to if not logged in
# View for categorizing jokes
@csrf_exempt
def categorize_joke(request):
    categorized_response = None
    joke_input = None
    joke = None

    if request.method == 'POST':
        joke_input = request.POST.get('joke_input', '')

        if joke_input:
            # Start a chat session
            chat_session = aimodel.start_chat(
                history=[
                    {"role": "user", "parts": ["hi\n"]},
                    {"role": "model", "parts": ["That's not a joke. 😊 \n"]},
                ]
            )
            
            # Send the joke input to the model
            response = chat_session.send_message(joke_input)
            categorized_response = response.text.strip()  # Get the categorized joke response

            # Create or get the joke object
            joke, created = Joke.objects.get_or_create(
                joke_text=joke_input,
                defaults={'categories': categorized_response}
            )

        return render(request, 'categorize_joke.html', {
            'joke_input': joke_input,
            'categorized_response': categorized_response,
            'joke': joke,  # Pass the joke object with id to the template
        })

    return render(request, 'categorize_joke.html', {'joke_input': joke_input})






from django.shortcuts import redirect, get_object_or_404
from .models import Joke, JokeFeedback
from django.contrib.auth.decorators import login_required





@login_required
def joke_feedbacks(request, joke_id, feedback_type):
    # Ensure the feedback type is valid
    if feedback_type not in ['like', 'dislike']:
        return redirect('categorize_joke')  # Invalid feedback type, redirect

    # Retrieve the joke by its ID
    joke = get_object_or_404(Joke, id=joke_id)

    # Check if the user has already provided feedback for this joke
    existing_feedback = JokeFeedback.objects.filter(user=request.user, joke=joke).first()

    if existing_feedback:
        # Update the feedback if it differs from the current one
        if existing_feedback.feedback_type != feedback_type:
            existing_feedback.feedback_type = feedback_type
            existing_feedback.save()
    else:
        # Create new feedback
        JokeFeedback.objects.create(user=request.user, joke=joke, feedback_type=feedback_type)

    return redirect('categorize_joke')





from django.shortcuts import render
from .models import JokeFeedback

from django.contrib.auth.decorators import login_required

@login_required(login_url='login')  # Specify the URL to redirect to if not logged in
def liked_jokes(request):
    # Query all jokes where the logged-in user has liked them
    liked_jokes = JokeFeedback.objects.filter(user=request.user, feedback_type='like').select_related('joke')

    # Pass the liked jokes to the template
    context = {
        'liked_jokes': liked_jokes,
    }

    return render(request, 'liked_jokes.html', context)





import matplotlib.pyplot as plt
from django.http import HttpResponse, JsonResponse
from io import BytesIO
from .models import Joke, JokeFeedback
from collections import defaultdict

def pie_chart(request):
    # Aggregating the data for joke categories and their feedback counts
    category_likes = defaultdict(int)
    category_dislikes = defaultdict(int)

    jokes = Joke.objects.all()

    for joke in jokes:
        likes = JokeFeedback.objects.filter(joke=joke, feedback_type='like').count()
        dislikes = JokeFeedback.objects.filter(joke=joke, feedback_type='dislike').count()
        
        category_likes[joke.categories] += likes
        category_dislikes[joke.categories] += dislikes

    # Preparing data for the pie chart
    labels = []
    sizes_likes = []
    sizes_dislikes = []
    
    for category in category_likes.keys():
        labels.append(category)
        sizes_likes.append(category_likes[category])
        sizes_dislikes.append(category_dislikes[category])

    # Creating the pie chart for likes and dislikes
    fig, ax = plt.subplots(1, 2, figsize=(14, 7))  # Two subplots for likes and dislikes
    ax[0].pie(sizes_likes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax[0].set_title('Likes Distribution by Category')

    ax[1].pie(sizes_dislikes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax[1].set_title('Dislikes Distribution by Category')

    plt.tight_layout()

    # Output the pie chart to an HTTP response
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)

    return HttpResponse(buf.getvalue(), content_type='image/png')



import matplotlib.pyplot as plt
from django.http import HttpResponse
from io import BytesIO
from .models import UserProfile
import numpy as np

def user_time_spent_chart(request):
    # Fetch all user profiles and their total time spent
    user_profiles = UserProfile.objects.select_related('user').all()
    
    # Prepare data for the chart
    users = [profile.user.username for profile in user_profiles]
    time_spent = [profile.total_time_spent.total_seconds() / 3600 for profile in user_profiles]  # Convert to hours

    # Create the bar chart
    fig, ax = plt.subplots(figsize=(10, 6))
    
    y_pos = np.arange(len(users))
    ax.barh(y_pos, time_spent, align='center')
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(users)
    ax.invert_yaxis()  # Invert y-axis to have the largest bar on top
    ax.set_xlabel('Total Time Spent (hours)')
    ax.set_title('User Total Time Spent on Platform')

    # Output the bar chart to an HTTP response
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)

    return HttpResponse(buf.getvalue(), content_type='image/png')





from django.shortcuts import render
from .models import UserProfile

def user_time_spent_chart(request):
    # Fetch all user profiles and their total time spent
    user_profiles = UserProfile.objects.select_related('user').all()

    # Prepare data to be passed to the template
    users = [profile.user.username for profile in user_profiles]
    time_spent = [profile.total_time_spent.total_seconds() / 3600 for profile in user_profiles]  # Convert to hours

    context = {
        'users': users,
        'time_spent': time_spent
    }

    return render(request, 'user_time_spent_chart.html', context)

from django.shortcuts import render
from .models import JokeFeedback, Joke

def likes_dislikes_chart(request):
    # Get all jokes and their categories
    jokes = Joke.objects.all()

    # Initialize a dictionary to store likes and dislikes for each category
    category_likes = {}
    category_dislikes = {}

    # Iterate over each joke and count the likes and dislikes
    for joke in jokes:
        # Get the category for the joke
        category = joke.categories  # Use the existing 'categories' field

        # Initialize category in the dictionary if not already present
        if category not in category_likes:
            category_likes[category] = 0
            category_dislikes[category] = 0

        # Count likes
        likes_count = JokeFeedback.objects.filter(feedback_type='like', joke=joke).count()
        category_likes[category] += likes_count

        # Count dislikes
        dislikes_count = JokeFeedback.objects.filter(feedback_type='dislike', joke=joke).count()
        category_dislikes[category] += dislikes_count

    # Prepare data for rendering
    categories_labels = list(category_likes.keys())
    likes_data = list(category_likes.values())
    dislikes_data = list(category_dislikes.values())

    context = {
        'categories': categories_labels,
        'likes_data': likes_data,
        'dislikes_data': dislikes_data,
    }

    return render(request, 'likes_dislikes_chart.html', context)


from django.shortcuts import render

def visualization_selection(request):
    return render(request, 'visualization_selection.html')  # Create this template file




# # views.py
# from django.shortcuts import render
# from django.views.decorators.csrf import csrf_exempt
# import google.generativeai as genai

# # Configure the API key (ensure it's correct)
# genai.configure(api_key="AIzaSyCi5rNWXoIXa2wWosI1cEWwCT4eGDPTz5w")

# # Create the model configuration
# generation_config = {
#     "temperature": 1,
#     "top_p": 0.95,
#     "top_k": 64,
#     "max_output_tokens": 8192,
#     "response_mime_type": "text/plain",
# }

# # Create the Generative Model
# model = genai.GenerativeModel(
#     model_name="gemini-1.5-flash",
#     generation_config=generation_config,
#     system_instruction="The user will input the joke details (language, joke type, and joke context). Generate a joke based on the provided language, prioritizing language first. If unable to generate based on the specific language, inform the user politely. Continue to generate jokes based on type and context where possible.",
# )

# # Joke Generator View
# @csrf_exempt
# def generate_joke(request):
#     joke_response = None

#     if request.method == 'POST':
#         language = request.POST.get('language')
#         joke_type = request.POST.get('joke_type')
#         joke_context = request.POST.get('joke_context')

#         if language and joke_type and joke_context:
#             # Start the chat session
#             chat_session = model.start_chat(
#                 history=[{
#                     "role": "user",
#                     "parts": [f"language:{language}\njoke type:{joke_type}\njoke context:{joke_context}\n"],
#                 }]
#             )

#             # Generate the response
#             response = chat_session.send_message("Generate a joke")
#             joke_response = response.text.strip()

#     return render(request, 'generate_joke.html', {
#         'joke_response': joke_response
#     })



from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .models import Joke, JokeFeedback
import google.generativeai as genai
from django.contrib.auth.decorators import login_required


# Configure the API key
genai.configure(api_key = os.getenv('API_KEY2')
)  # Replace with your actual API key

# Model configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction="The user will input the joke details (language, joke type, and joke context). Generate a joke based on the provided language.",
)

# View for generating a joke and saving the joke type
@csrf_exempt
@login_required(login_url='login')  # Specify the URL to redirect to if not logged in
def generate_joke(request):
    generated_joke = None
    joke_type = None
    joke_object = None

    if request.method == 'POST':
        # Retrieve form inputs
        language = request.POST.get('language')
        joke_type = request.POST.get('joke_type')
        joke_context = request.POST.get('joke_context')

        if language and joke_type and joke_context:
            # Start the chat session and generate the joke
            chat_session = model.start_chat(
                history=[
                    {
                        "role": "user",
                        "parts": [f"language:{language}\njoke type:{joke_type}\njoke context:{joke_context}\n"],
                    }
                ]
            )
            response = chat_session.send_message("Generate a joke")
            generated_joke = response.text.strip()

            # Save the joke and its type to the database
            joke_object, created = Joke.objects.get_or_create(
                joke_text=generated_joke,
                defaults={'categories': joke_type}
            )

    return render(request, 'generate_joke.html', {
        'generated_joke': generated_joke,
        'joke_type': joke_type,
        'joke_object': joke_object,  # Pass the joke object with ID
    })


# Like or Dislike Feedback
@login_required
def joke_feedback(request, joke_id, feedback_type):
    # Ensure the feedback type is valid
    if feedback_type not in ['like', 'dislike']:
        return redirect('generate_joke')

    # Retrieve the joke by its ID
    joke = get_object_or_404(Joke, id=joke_id)

    # Check if the user already gave feedback
    existing_feedback = JokeFeedback.objects.filter(user=request.user, joke=joke).first()

    if existing_feedback:
        if existing_feedback.feedback_type != feedback_type:
            existing_feedback.feedback_type = feedback_type
            existing_feedback.save()
    else:
        JokeFeedback.objects.create(user=request.user, joke=joke, feedback_type=feedback_type)

    return redirect('generate_joke')




from django.shortcuts import render

# Create a view for gg.html
def generate_jok(request):
    return render(request, 'gg.html')
