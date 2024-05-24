import re, random, math

def combine_piece(strings, start, end):
    selected_strings = strings[start:end+1]
    cleaned_list = list(filter(lambda line: line.strip(), selected_strings))
    return '\n'.join(cleaned_list)
def choose_piece(body, total, start_line = -1):
    strings = body.splitlines()
    start_index = 0
    end_index = len(strings)
    sum = 0
    if start_line >= len(strings):
        print(f'start line {start_line} exceed limit {len(strings)}')
        return "", -1

    if start_line < 0:
        if len(body) > 10*total:
            start_index = random.randint(0, math.floor(len(strings)/2) - 1)
        else:
            print("cut from the start")
            start_index = 0
    else:
        start_index = start_line
    
    cut_index = start_index
    for i in range(start_index, len(strings)):
        # skip empty lines
        if sum == 0 and len(strings[i]) < 3:
            cut_index += 1
            continue
        sum += len(strings[i])
        if sum > total:
            end_index = i-1
            break
    print(f"cut from {cut_index} to {end_index}, total {len(strings)}")  
    return combine_piece(strings, start_index, end_index), end_index

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