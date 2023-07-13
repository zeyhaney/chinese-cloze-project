import requests
import json
import csv
import os
import re
import jieba
import codecs
from pypinyin import lazy_pinyin, Style

# File names for vocabulary and allowed characters
VOCABULARY_FILE = 'vocabulary copy.csv'
CHARACTERS_FILE = 'allowed_characters.csv'

# Number of sentences to generate
NUMBER_OF_SENTENCES_TO_GENERATE = 3

def makeGPTRequest(prompt):
    """
    This function makes a request to the OpenAI GPT-3 model and returns the response content.
    
    Parameters:
    - prompt: A string that contains the prompt to be sent to the GPT-3 model.
    """
    print("Starting GPT Request!")
    
    # Add API KEY to use
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': ''
    }
    
    payload = json.dumps({
        "model": "gpt-3.5-turbo-0301",
        "messages": [{"role": "user", "content": f"{prompt}"}]
    })

    # Making the API request
    try:
        response = requests.post(url, headers=headers, data=payload)
        print("Retrieved API response!")
    except:
        pass # Here you may want to handle exceptions (e.g., log the error, exit the program)

    # Extracting response content
    try:
        response_data = json.loads(response.text)
        content = response_data["choices"][0]["message"]["content"]
        print("Retrieved content!")
        return content
    except:
        print("Failed to retrieve content!")
        # Handle the error gracefully or raise it again

def retrieve_allowed_characters():
    """
    This function retrieves allowed characters from the csv file.
    """
    with open(CHARACTERS_FILE, 'r', encoding='utf-8') as input_file:
        reader = csv.reader(input_file)
        
        cleaned_string = ''
        for row in reader:
            cleaned_row = ''.join(row)
            cleaned_string += cleaned_row
        print("Retrieved allowed characters!")
        return cleaned_string

def buildPrompt(number_of_sentences, vocabulary, vocabulary_meaning, allowed_characters):
    """
    This function builds the prompt for the GPT-3 request.
    
    Parameters:
    - number_of_sentences: The number of sentences to generate.
    - vocabulary: The target vocabulary word.
    - vocabulary_meaning: The meaning of the vocabulary word.
    - allowed_characters: The characters that are allowed to be used in the generated sentences.
    """
    prompt = f"""Please generate {number_of_sentences} sentences at HSK Level 1 using the word '{vocabulary}', which means '{vocabulary_meaning}'. You may only use the following characters: '{allowed_characters}'. ABSOLUTELY DO NOT USE ANY OTHER CHARACTERS! The sentences should demonstrate a variety of lengths, structures, and vocabulary, while remaining simple enough for HSK Level 1.

    Wrong Response:
    着 is NOT in 风很大，他的帽子一直在飞。!
    着 is NOT in 她在准备考试，必须认真学习。!
    
    Example Prompt: 在 meaning at;in
    Example Response:
    我的妹妹在做作业。
    他们在打篮球。
    爸爸在工作。(continued.)
    """
    print("Built Prompt!")
    return prompt

def loadVocabulary():
    """
    This function loads the vocabulary from the csv file and returns it as a dictionary.
    """
    result = {}
    with open(VOCABULARY_FILE, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) >= 2:
                result[row[0]] = row[1]
    print("Loaded all vocabulary!")
    return result

def get_sentences(input_string, filter_word, allowed_characters):
    """
    This function splits the input string into sentences, 
    and then filters these sentences based on the filter word and allowed characters.
    
    Parameters:
    - input_string: The string to split into sentences.
    - filter_word: The word to filter the sentences.
    - allowed_characters: The characters that are allowed to be used in the sentences.
    """
    # Split the input string into sentences
    sentences = input_string.split('\n')
    sentences = fix_string_list(sentences)
    print("Split sentences!")

    # Remove BOM from the filter_word
    filter_word = filter_word.replace('\ufeff', '')
    
    # Filter the sentences based on the filter_word and allowed characters
    filtered_sentences = [
        sentence for sentence in sentences
        if is_filter_word_present(sentence, filter_word) and is_valid_sentence(sentence, allowed_characters)
    ]
    print("Filtered sentences!")
    return filtered_sentences

def is_filter_word_present(sentence, filter_word):
    """
    This function checks if a filter word is present in a sentence.
    
    Parameters:
    - sentence: The sentence to check.
    - filter_word: The word to check for.
    """
    result = filter_word in sentence
    if result:
        print(f"{filter_word} is in {sentence}!")
    else:
        print(f"{filter_word} is NOT in {sentence}!")
    return result

def is_valid_sentence(sentence, allowed_characters):
    """
    This function checks if a sentence is valid based on allowed characters.
    
    Parameters:
    - sentence: The sentence to check.
    - allowed_characters: The characters that are allowed to be used in the sentence.
    """
    forbidden_characters = [char for char in sentence if char not in allowed_characters and char != ' ']
    if not forbidden_characters:
        print(f"Sentence uses only allowed characters. Sentence: {sentence}")
        return True
    else:
        print(f"Sentence uses FORBIDDEN characters. Forbidden characters: {', '.join(forbidden_characters)}. Sentence: {sentence}")
        return False

def fix_string_list(string_list):
    """
    This function fixes a list of strings by removing extra white spaces,
    leading and trailing white spaces, and dot and following characters if present.
    
    Parameters:
    - string_list: The list of strings to fix.
    """
    fixed_list = []
    for string in string_list:
        # Remove extra white spaces
        new_string = ' '.join(string.split())
        
        # Remove leading and trailing white spaces
        new_string = new_string.strip()
        
        # Remove dot and following characters if present
        new_string = new_string[new_string.index('.') + 2:] if '.' in new_string else new_string
        
        fixed_list.append(new_string)
    return fixed_list

def add_unique_sentences_to_file(sentences, filename):
    """
    This function checks if a file exists, if not it creates a new file. 
    Then it reads the current sentences in the file and appends any new unique sentences.

    Parameters:
    - sentences: The list of sentences to append to the file.
    - filename: The filename where sentences will be appended.
    """
    
    # Check if the file exists, if not create an empty file
    if not os.path.exists(filename):
        open(filename, 'w').close()
    print("File found/created!")

    # Read the current sentences in the file
    with open(filename, 'r', encoding='utf-8') as file:
        current_sentences = file.read().splitlines()
    print("File read!")

    # Add unique sentences to the file
    with open(filename, 'a', encoding='utf-8') as file:
        for sentence in sentences:
            if sentence not in current_sentences:
                file.write(sentence + '\n')
    print("Unique sentences added!")

def process_content(input_string, filter_word, filename, allowed_characters):
    """
    This function splits the input content into sentences, 
    filters these sentences based on the filter word and allowed characters, 
    and then writes these sentences to a file.

    Parameters:
    - input_string: The string to be processed.
    - filter_word: The word to be used for filtering the sentences.
    - filename: The filename where sentences will be written.
    - allowed_characters: The list of allowed characters in the sentences.
    """
    sentences = get_sentences(input_string, filter_word, allowed_characters)
    print(f"Created {len(sentences)} sentences!")
    if (len(sentences) > 0):
        add_unique_sentences_to_file(sentences, filename)

def getPinyin(chinese_word):
    """
    This function converts a Chinese word to Pinyin representation.

    Parameters:
    - chinese_word: The Chinese word to be converted.
    """
    chinese_word = chinese_word.replace('\ufeff', '')
    return ' '.join(lazy_pinyin(chinese_word, style=Style.TONE3))

def countLines(filename):
    """
    This function counts the number of lines in a file.

    Parameters:
    - filename: The filename to count lines.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            line_count = sum(1 for _ in file)
        return line_count
    except:
        return 0
    
def main():
    """
    The main function of the program. It iterates over the vocabulary, makes GPT-3 requests,
    processes the content received from the GPT-3 model, and writes the sentences to a file.
    """
    vocabulary_dict = loadVocabulary()
    allowed_characters = retrieve_allowed_characters()
    unsuccessful_words = []
    for vocab in vocabulary_dict.keys():
        
        vocabulary_pinyin = getPinyin(vocab)
        print(vocabulary_pinyin)
        filename = f'sentences/{vocabulary_pinyin}_sentences.txt'
        sentences = countLines(filename)
        print(sentences)
        tries = 0
        while (sentences < NUMBER_OF_SENTENCES_TO_GENERATE):
            prompt = buildPrompt(NUMBER_OF_SENTENCES_TO_GENERATE*2, vocab, vocabulary_dict[vocab], allowed_characters)
            GPTresponse = makeGPTRequest(prompt)
            process_content(GPTresponse, vocab, filename, allowed_characters)
            sentences = countLines(filename)
            tries = tries + 1
            if tries >= NUMBER_OF_SENTENCES_TO_GENERATE * 2:
                unsuccessful_words.append(vocab)
                break
        print("Done!")

    for unsuccessful_word in unsuccessful_words:
        print(f"Could not complete {unsuccessful_word}")

if __name__ == "__main__":
    main()