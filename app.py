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
            max_tokens=12000
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
    debate_name=request.form["debate_name"]

    
    if not video_id:
        return jsonify({'output': 'No video ID provided'}), 400
    if not debate_name:
        return jsonify({'output': 'No debate name provided'}), 400
    transcript_text = get_transcript_text_only(video_id)
    
    if transcript_text is None:
        return jsonify({'output': f'Failed to fetch transcript for video ID: {video_id}'}), 500
    if debate_name is None:
        return jsonify({'output': f'Failed to fetch debate name: {debate_name}'}), 500
    
    # Instruction with addition of debate name from user
    instruction = ("Imagine you are a fact check for the " + debate_name + " Debate. Analyze the transcript provided completely and look for groups of sentences that form complete ideas. Using your knowledge, check if these complete ideas are true or false. If you determine that any statements are opinions or general statements, ignore them and don't return them. Only return the complete ideas that are true or false in this format: 'Speaker from " + debate_name + " - Sentences that make the complete idea (True or False with explanation)'.")
    

    prompt = f"{instruction}\n'{transcript_text}'"
    
    #Adding response to csv file
    chatgpt_response = get_chatgpt_response(prompt)
    with open('responses.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([video_id, chatgpt_response])

    
    return jsonify({'output': chatgpt_response})

if __name__ == '__main__':
    app.run(debug=True)
