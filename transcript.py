import io
import base64
from flask import Flask, request, jsonify, render_template
import matplotlib
from youtube_transcript_api import YouTubeTranscriptApi
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from textblob import TextBlob
import spacy
import matplotlib.pyplot as plt
from youtube_api import get_video_details

# Don't need the GUI so using the 'Agg' backend which doesn't require a display
matplotlib.use('agg')

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze-video', methods=['POST'])
def analyze_video():
    # Get video URL from the request
    data = request.get_json()
    video_url = data.get('video_url', '')

    # Get the transcript
    video_id = video_url.replace('https://www.youtube.com/watch?v=', '')
    transcript = YouTubeTranscriptApi.get_transcript(video_id)

    # Get video details
    video_details = get_video_details(video_id)

    # Combine all text in the transcript
    output = ' '.join([entry['text'] for entry in transcript])

    # Tokenize and remove punctuation
    tokens = word_tokenize(output.lower())
    words = [word for word in tokens if word.isalpha()]

    # Remove stop words
    stop_words = set(stopwords.words('english'))
    filtered_words = [word for word in words if word not in stop_words]

    # Lemmatization
    lemmatizer = WordNetLemmatizer()
    lemmatized_words = [lemmatizer.lemmatize(word) for word in filtered_words]

    # Sentiment Analysis using TextBlob
    sentiment_score = TextBlob(output).sentiment.polarity

    # Keyword Extraction using lemmatized and filtered words
    keywords = list(set(filtered_words))

    # Count word occurrences
    word_counts = {}
    for word in lemmatized_words:
        if word in word_counts:
            word_counts[word] += 1
        else:
            word_counts[word] = 1

    # Get top 10 words
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    top_words = sorted_words[:10]

    # Plot the graph
    plt.bar(*zip(*top_words))
    plt.xlabel('Words')
    plt.ylabel('Occurrences')
    plt.title('Top 10 Most Used Words')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Save the image to a BytesIO object
    image_stream = io.BytesIO()
    plt.savefig(image_stream, format='png')
    image_stream.seek(0)

    # Convert the image to base64
    base64_image = base64.b64encode(image_stream.read()).decode('utf-8')

    # Close the plot
    plt.close()

    # Return the base64 image, sentiment score, keywords, title, channel name, and thumbnail URL to the frontend
    return jsonify({
        'message': 'Analysis completed successfully',
        'image': base64_image,
        'sentiment': sentiment_score,
        'keywords': keywords,
        'title': video_details['title'],
        'channel': video_details['channel'],
        'thumbnail': video_details['thumbnail']
    })

if __name__ == '__main__':
    app.run(debug=True)
