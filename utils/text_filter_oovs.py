import sys

text_file = open(sys.argv[1], "r")
words_file = open(sys.argv[2], "r")
output_file = open(sys.argv[3], "w")

lex_words = []

for line in words_file:
	split_line = line.split()
	lex_words.append(split_line[0].lower())

lines = 0
oovs_num = 0
total_words = 0

for line in text_file:
	lines = lines + 1
	split_line = line.split()
	output_file.write(split_line[0] + " ")
	for word in split_line[1:]:
		total_words = total_words + 1
		if word.lower() in lex_words:
			output_file.write(word + " ")
		else:
			output_file.write("<UNK> ")
			oovs_num = oovs_num + 1
	output_file.write("\n")

print(str(float(oovs_num)/(float(total_words))))#-lines))))
		
