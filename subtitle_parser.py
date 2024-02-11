import os
import re
from collections import Counter
import pandas as pd
from janome.tokenizer import Tokenizer

# Directory where your .srt and .ass files are stored
srt_directory = '/Users/jacobmeyer/Documents/subtitles/jojo'

# Initialize the tokenizer
tokenizer = Tokenizer()

# Function to clean text: removing timestamps, metadata, etc., and non-lexical characters
def clean_text(text, file_extension):
    if file_extension == '.srt':
        # SRT cleaning process
        text = re.sub(r'\n\d+\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n', '\n', text)
    elif file_extension == '.ass':
        # ASS cleaning process: extract dialogue lines and split off the actual dialogue text
        dialogue_lines = [line.split(',', 9)[-1] for line in text.splitlines() if line.startswith('Dialogue')]
        text = '\n'.join(dialogue_lines)
    # Common cleaning steps for both formats
    text = re.sub(r'<[^>]+>', '', text)  # Remove any HTML-like tags
    text = re.sub(r'[\n\t]+', ' ', text).strip()  # Remove non-lexical characters
    # Remove punctuation using a predefined pattern, avoiding direct insertion of the punctuation string
    text = re.sub(r'[、。！？｡･｢｣「」『』（）〔〕【】〈〉《》“”‘’､･:;.,<>[\]{}()!"#$%&\'()*+,-./:;<=>?@\^_`{|}~\s]', '', text)
    return text

# Function to tokenize Japanese text and filter out common particles, filler words, and single characters
def tokenize_japanese(text):
    exclude = {'の', 'は', 'に', 'で', 'を', 'と', 'が', 'た', 'だ', 'て', 'な', 'も', 'から', 'よ', 'し', 'あり', 'ない', 'ん'}
    # Use the base_form of each token to consolidate variations into their dictionary form
    tokens = [token.base_form for token in tokenizer.tokenize(text) if token.base_form not in exclude and len(token.base_form.strip()) > 1]
    return tokens

# Initialize a Counter object to count word frequencies
word_freq = Counter()

# Loop through each file in the directory
for filename in os.listdir(srt_directory):
    file_extension = os.path.splitext(filename)[1]
    if file_extension in ['.srt', '.ass']:
        filepath = os.path.join(srt_directory, filename)
        with open(filepath, 'r', encoding='utf-8') as file:
            text = file.read()
            # Clean the text based on file extension
            cleaned_text = clean_text(text, file_extension)
            # Tokenize the text into words
            words = tokenize_japanese(cleaned_text)
            # Update the Counter with the tokens
            word_freq.update(words)

# Convert the Counter object into a pandas DataFrame for easy handling
df = pd.DataFrame(word_freq.items(), columns=['Word', 'Frequency'])

# Sort the DataFrame by frequency in descending order
df_sorted = df.sort_values(by='Frequency', ascending=False)

# Select the top 2000 words, excluding empty strings or undesired tokens
top_words = df_sorted[df_sorted['Word'].str.strip().astype(bool)].head(2000)

top_words.to_csv('/Users/jacobmeyer/Documents/subtitles/jojo.csv', index=False)
