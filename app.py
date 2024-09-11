from flask import Flask, request, jsonify, render_template
from youtube_transcript_api import YouTubeTranscriptApi
import openai
import csv

app = Flask(__name__)

# Your OpenAI API key
openai.api_key = ""

def get_transcript_text_only(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text_only = [entry['text'] for entry in transcript]
        return "\n".join(text_only)
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        return None

def get_chatgpt_response(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10000
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error in OpenAI request: {e}")
        return f"Error: {e}"

@app.route('/')
def index():
    return render_template('index.html')  # Serves your HTML form

@app.route('/process', methods=['POST'])
def process_video_id():
    video_id = request.form["video_id"] 


    
    if not video_id:
        return jsonify({'output': 'No video ID provided'}), 400
    
    print(f"Received video ID: {video_id}")
    
    transcript_text = get_transcript_text_only(video_id)
    
    if transcript_text is None:
        return jsonify({'output': f'Failed to fetch transcript for video ID: {video_id}'}), 500
    
    # ChatGPT prompt
    instruction = ("Imagine you are a fact check for the 2024 Donald Trump vs Kamala Harris Debate. Analyze the transcript provided completely and look for groups of sentences that form complete ideas. Using your knowledge, check if these complete ideas are true or false. If you determine that any statements are opinions or general statements, ignore them and don't return them. Only return the complete ideas that are true or false in this format: 'Trump or Harris - Sentences that make the complete idea (True or False with explanation)'.")
    
    prompt = f"{instruction}\n'{transcript_text}'"
    
    chatgpt_response = get_chatgpt_response(prompt)
    with open('responses.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        
        # Write a row for each segment and its response
        writer.writerow([video_id, chatgpt_response])
    
    return jsonify({'output': chatgpt_response})

if __name__ == '__main__':
    app.run(debug=True)
