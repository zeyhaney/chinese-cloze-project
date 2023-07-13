# -*- encoding: utf-8 -*- #

import csv
import jieba
from translate import translate
from pypinyin import lazy_pinyin, Style

VOCABULARY_FILE = 'vocabulary.csv'

def create_cloze_questions(sentences, word_to_remove, meaning):
    """
    Generates cloze questions from a list of sentences by replacing the first occurrence of a word with blanks.

    Args:
        sentences (list): A list of sentences.
        word_to_remove (str): The word to be replaced with blanks.
        meaning (str): The meaning of the word.

    Returns:
        list: A list of cloze questions as dictionaries.
    """
    cloze_questions = []
    seen_sentences = set()
    english_word = meaning

    for sentence in sentences:
        if sentence in seen_sentences:
            continue
        seen_sentences.add(sentence)

        cloze_sentence = sentence.replace(word_to_remove, '______')  # Replace only the first occurrence

        cloze_question = {
            'Cloze Question': cloze_sentence,
            'Cloze Question Pinyin': ' '.join(lazy_pinyin(cloze_sentence, style=Style.TONE)),
            'Full Sentence': sentence,
            'Full Sentence Pinyin': ' '.join(lazy_pinyin(sentence, style=Style.TONE)),
            'Answer': word_to_remove,
            'Answer Pinyin': ' '.join(lazy_pinyin(word_to_remove, style=Style.TONE)),
            'English Word': english_word
        }

        cloze_questions.append(cloze_question)

    return cloze_questions

def write_cloze_questions_to_csv(cloze_questions, output_file):
    """
    Write cloze questions to a CSV file.

    Args:
        cloze_questions (list): List of dictionaries representing cloze questions.
        output_file (str): Output file path.

    """
    # Define the field names for the CSV file
    fieldnames = ['Cloze Question', 'Cloze Question Pinyin', 'Full Sentence', 'Full Sentence Pinyin', 'Answer', 'Answer Pinyin', 'English Word']
    
    # Open the CSV file for writing
    with open(output_file, 'w', encoding='utf-8', newline='') as csvfile:
        # Create a CSV writer object
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write the header row
        writer.writeheader()
        
        # Write each cloze question as a row in the CSV file
        for cloze_question in cloze_questions:
            writer.writerow(cloze_question)

def read_sentences_from_file(input_file):
    """
    Reads sentences from a file and returns them as a list.

    Args:
        input_file (str): The path to the input file.

    Returns:
        list: A list of sentences read from the file.

    """
    # Open the file in read mode with UTF-8 encoding
    with open(input_file, 'r', encoding='utf-8') as f:
        # Read all lines from the file
        sentences = f.readlines()
        # Remove leading and trailing whitespace from each line
        sentences = [sentence.strip() for sentence in sentences]
    
    return sentences

def load_vocabulary():
    """
    Loads vocabulary from a CSV file and returns it as a dictionary.

    Returns:
        dict: A dictionary containing the vocabulary loaded from the file.
    """
    vocabulary = {}

    with open(VOCABULARY_FILE, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) >= 2:
                vocabulary[row[0]] = row[1]

    return vocabulary

def getPinyin(chinese_word):
    """
    Returns the pinyin representation of a Chinese word.

    Args:
        chinese_word (str): The Chinese word to convert to pinyin.

    Returns:
        str: The pinyin representation of the Chinese word.
    """
    return ' '.join(lazy_pinyin(chinese_word, style=Style.TONE3))

def write_cloze_questions():
    """
    Generates and writes cloze questions for vocabulary words.

    """
    vocabulary_dict = load_vocabulary()

    for vocab, meaning in vocabulary_dict.items():
        # Prepare the input file path based on the vocabulary word
        pinyin_vocab = getPinyin(vocab)
        input_file = f"sentences/{pinyin_vocab}_sentences.txt"

        # Read sentences from the input file
        sentences = read_sentences_from_file(input_file)

        # Create cloze questions for the vocabulary word
        cloze_questions = create_cloze_questions(sentences, vocab, meaning)

        # Prepare the output file path based on the vocabulary word
        output_file = f"cloze questions/{pinyin_vocab}_cloze.csv"

        # Write the cloze questions to the output file
        write_cloze_questions_to_csv(cloze_questions, output_file)

        print(f"Done writing cloze questions for {vocab}!")

def main():
    write_cloze_questions()

if __name__ == "__main__":
    main()