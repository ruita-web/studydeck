from youtube_transcript_api import YouTubeTranscriptApi

video_id = "8S0FDjFBj8o" # Short TED talk

try:
    # 1. Create an instance of the API
    ytt_api = YouTubeTranscriptApi()
    
    # 2. Fetch the transcript using the new .fetch() method
    fetched_transcript = ytt_api.fetch(video_id)
    
    # 3. Extract the text from the transcript snippets
    full_text = " ".join([snippet.text for snippet in fetched_transcript])
    
    print(f"✅ Success! Got {len(full_text)} characters")
    print("\n--- First 500 chars ---\n")
    print(full_text[:500])
    
except Exception as e:
    print(f"❌ Error: {e}")