import sys
import json
import os
import random


def get_string_type(string):
    if string.isdigit():
        return 'digit'
    elif string.isalpha() or string[0] == '\'':
        return 'alpha'
    else:
        return 'symbol'


def tokenize(string):
    tokens = []

    if len(string) >= 1:
        tokens.append([string[0]])

        for character in string:
        	if get_string_type(character) == 'symbol':
        		if character in '.!?':
        			tokens.append([character])
        		else:
        			tokens.append(' ')
        	else:
        		if get_string_type(character) != get_string_type(tokens[-1][0]):
        			tokens.append([character])
        		else:
        			tokens[-1].append(character)

        for i in range(len(tokens)):
            tokens[i] = "".join(tokens[i])

	return [token.replace('\'', '') for token in tokens if not token.isspace() and token != '\'']


def read_data(path):
	result = []
	file_names = []
	for root, dirs, files in os.walk(path):
	    for file in files:
	    	file_names.append(os.path.join(root, file))

	for file in file_names:
		f = open(file, 'r')
		tokens = tokenize(f.read().strip())
		result.append(tokens)
		f.close()

	return result


def count_probabilities(data):
	probability = dict()

	for depth in xrange(0,3):
		for current_file in data:
			for start_pos in xrange(len(current_file) - depth):
				history = tuple(current_file[start_pos: start_pos + depth])
				token = current_file[start_pos + depth]

				if token.istitle() or depth:
					if history not in probability:
						probability[history] = dict()
					if token not in probability[history]:
						probability[history][token] = 0
					probability[history][token] += 1			
	    	
	for history in probability.keys():
		token_amount = 0

		for token in probability[history].keys():
			token_amount += probability[history][token]
		for token in probability[history].keys():
			probability[history][token] = probability[history][token] * 1.0 / token_amount

	return probability


def save_data(data, path):
	new_data = dict()
	for key in data.keys():
		new_data[' '.join(key)] = data[key]
	f = open(path, 'w')
	f.write(json.dumps(new_data))
	f.close()


def load_data(path):
	f = open(path, 'r')
	data = f.read()
	f.close()
	temp_data = json.loads(data)
	result = dict()
	for key in temp_data.keys():
		result[tuple(key.split(' '))] = temp_data[key]

	return result


def normalize_text(tokens):
    text = ['\n']
    new_sentence = True
    sentence_counter = 0
    paragraph_size = random.randrange(11) + 15
    new_paragraph = True
    for token in tokens:
    	if new_paragraph:
        	text.append('   ')
        	new_paragraph = False

        if get_string_type(token) != 'symbol' and text[-1] != '\n':
            text.append(' ')
        if new_sentence:
            text.append(token.title())
            new_sentence = False
        else:
            text.append(token)
        

        if token in '.!?':
            new_sentence = True
            sentence_counter += 1

        if sentence_counter == paragraph_size:
        	
        	text.append('\n')
        	sentence_counter = 0
        	paragraph_size = random.randrange(11) + 15
        	new_paragraph = True

    if text[-1] not in '.?!':
        if get_string_type(text[-1]) != 'symbol':
            text.append('.')
        else:
            text[-1] = '.'
    return ''.join(text[1:])


def generate_text(probabilities, text_size):
    history = tuple()
    tokens = []

    for i in xrange(text_size):
        border = random.uniform(0, 1)
        current_probability = 0

        if len(history) > 0 and history[-1] in '.!?':
        	history = (history[-1], )
        while history not in probabilities:
        	print history
        	history = history[1:]
        for token, probability in probabilities[history].items():
            if current_probability <= border <= current_probability + probability:
                tokens.append(token)
                history = history + (token, )
                history = history[-2:]
                break
            current_probability += probability
    return normalize_text(tokens)


if __name__ == '__main__':
	data = read_data(".\corpus")
	probability = count_probabilities(data)
	save_data(probability, "json_data.json")
	loaded_data = load_data("json_data.json")

	text = generate_text(loaded_data, 10010)

	f = open('result.txt', 'w')
	f.write(text)
	f.close()