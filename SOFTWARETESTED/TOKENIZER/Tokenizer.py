import os
import re
from nltk.tokenize import sent_tokenize


# Function to identify and retain complete sentences
def retain_sentences(text):
    # Tokenize the text into sentences using NLTK
    potential_sentences = sent_tokenize(text)
    print(f'Found {len(potential_sentences)} potential sentences.')

    # Define a regex pattern for a complete sentence (any sentence ending with a terminal punctuation)
    sentence_pattern = re.compile(r".*[.!?]")

    # Filter out fragments that don't match the complete sentence pattern
    complete_sentences = [sentence.strip() for sentence in potential_sentences if sentence_pattern.match(sentence)]

    print(f'Retained {len(complete_sentences)} complete sentences.')
    return ' '.join(complete_sentences)


# Directory containing the text files (current working directory)
directory = '.'

# Iterate through all files in the directory
for filename in os.listdir(directory):
    # Check if the file is a text file
    if filename.endswith('.txt'):
        file_path = os.path.join(directory, filename)
        print(f'Processing file: {file_path}')

        # Read the content of the file
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()

        # Retain only complete sentences
        cleaned_content = retain_sentences(file_content)

        # Check if there is any cleaned content to write back
        if cleaned_content:
            # Overwrite the file with the cleaned content
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(cleaned_content)
                print(f'Successfully wrote cleaned content to {filename}')
        else:
            print(f'No sentences retained for {filename}, skipping overwrite.')

print('Processing completed.')
