import random
from googleapiclient.discovery import build

# Your API key to access the YouTube Data API
api_key = "AIzaSyCXgaeWeZAER3C3bEaQVp-rZzbJ9SqDfuk"

def get_random_song(emotion, api_key):
    """
    This function takes an emotion (e.g., "Happy", "Sad") and an API key, 
    searches for songs on YouTube that match the emotion, and returns a 
    YouTube link to a random song from the search results.
    """
    
    # Create random descriptors (like "songs" or "playlist") and contexts (like "for coping with")
    # to generate a unique and dynamic search query.
    descriptors = ["songs", "music", "playlist", "tunes", "tracks"]
    contexts = ["for coping with", "to feel", "when feeling", "related to", "about"]
    random_desc = random.choice(descriptors)  # Pick a random descriptor
    random_context = random.choice(contexts)  # Pick a random context
    
    # Combine the descriptor, context, and emotion to form a search query
    query = f"{random_desc} {random_context} {emotion}"
    
    # Initialize the YouTube Data API client using the provided API key
    youtube = build("youtube", "v3", developerKey=api_key)
    
    # Define the maximum number of results to fetch (50 is the YouTube API limit)
    max_results = 50
    
    # Perform a YouTube search with the generated query
    # This will look for videos with the given query
    search_response = youtube.search().list(
        q=query,  # The search query string
        part="snippet",  # Retrieve the snippet information (e.g., title, description, thumbnails)
        type="video",  # Only search for videos (not channels or playlists)
        maxResults=max_results  # Fetch up to 50 results
    ).execute()
    
    # Extract video IDs from the search response
    videos = []
    for item in search_response.get("items", []):  # Loop through the search results
        video_id = item["id"]["videoId"]  # Extract the unique video ID
        videos.append(video_id)  # Add the video ID to the list of videos
    
    # If no videos are found, try a simpler fallback query (e.g., just "<emotion> songs")
    if not videos:
        fallback_query = f"{emotion} songs"  # A simpler query
        fallback_response = youtube.search().list(
            q=fallback_query,  # Simpler query string
            part="snippet",  # Retrieve the snippet information
            type="video",  # Only search for videos
            maxResults=max_results  # Fetch up to 50 results
        ).execute()
        
        # Extract video IDs from the fallback search response
        for item in fallback_response.get("items", []):
            video_id = item["id"]["videoId"]
            videos.append(video_id)
    
    # If still no videos are found after the fallback query, return an error message
    if not videos:
        return "No songs found for this emotion."
    
    # Randomly pick one video ID from the list of video IDs
    chosen_video_id = random.choice(videos)
    
    # Construct the YouTube link using the selected video ID
    youtube_link = f"https://www.youtube.com/watch?v={chosen_video_id}"
    return youtube_link


# Example usage here
# Define the API key and an emotion to search for
api_key = "AIzaSyCXgaeWeZAER3C3bEaQVp-rZzbJ9SqDfuk"
emotion = "Fear"

# Call the function and print the resulting YouTube link
youtube_link = get_random_song(emotion, api_key)
print(f"For emotion '{emotion}', check out: {youtube_link}")
