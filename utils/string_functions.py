
import re, random

def combine_piece(strings, start, end):
    selected_strings = strings[start:end+1]
    cleaned_list = list(filter(lambda line: line.strip(), selected_strings))
    return '\n'.join(cleaned_list)
def choose_piece(body, total):
    strings = body.splitlines()
    not_filled = True
    start_index = 0
    end_index = 0
    while not_filled:
        random_start = random.randint(0, len(strings) - 1)
        sum = 0
        start_index = random_start
        for i in range(random_start, len(strings)):
            if sum == 0 and len(strings[i]) < 3:
                start_index += 1
                continue
            sum += len(strings[i])
            if sum > total:
                end_index = i-1
                not_filled = False
                break  
            
    return combine_piece(strings, start_index, end_index)

def highlight_keywords(text, keyword_list):
    highlighted_text = text
    for keyword in keyword_list:
        highlighted_text = re.sub(r'\b' + re.escape(keyword) + r'\b', f'\033[91m{keyword}\033[0m', highlighted_text, flags=re.IGNORECASE)
    return  highlighted_text

def highlight_keywords_all(text, keyword_list):
    highlighted_text = text
    for keyword in keyword_list:
        highlighted_text = re.sub(keyword, f'\033[91m{keyword}\033[0m', highlighted_text, flags=re.IGNORECASE)
    return highlighted_text

def lowercase_end_of_words(text):
    pattern = re.compile(r'(\b[A-Za-z]*)([A-Z]+)\b')
    result = pattern.sub(lambda match: match.group(1) + match.group(2).lower(), text)
    return result