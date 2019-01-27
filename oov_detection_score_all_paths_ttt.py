import sys
import numpy as np
import os

#oov_symbol_file = sys.argv[1]
words_file = sys.argv[1]
ref_ctm = sys.argv[2]
OOV_cand_folder = sys.argv[3]
#num_jobs = int(sys.argv[4])+1
#print(str(num_jobs))

phoneme_indices = []

def find_all(a_str, sub):
	start = 0
	while True:
		start = a_str.find(sub, start)
		if start == -1: return
		yield start
		start += len(sub)

#for line in open(oov_symbol_file, "r"):
#	oov_symbol = line.split()[0]
#	print("OOV SYMBOL: " + oov_symbol)

for line in open(words_file, "r"):
	if line[0:4] == 'PHN_':
		phoneme_indices.append(line.split()[1])
	if line.split()[0] == "<UNK>":
		oov_symbol = line.split()[1]
	if line.split()[0] == "<PHNSILSP>":
		phnsilsp_symbol = line.split()[1]
print("phoneme indices: ") 
print(phoneme_indices)
print("OOV and phnsilsp symbols:")
print(oov_symbol + " " + phnsilsp_symbol)

ref_start = 1
#ref_oov = []

#for i in range(1, num_jobs):
#	print ref_ctm_path
ref_ctm_file = open(ref_ctm, "r")
for line in ref_ctm_file:
	spl = line.split()
#		print(spl[4])
	if spl[3] == oov_symbol: #unk found in reference
		if ref_start == 1:
			ref_oov = np.array([spl[0], spl[1], spl[2], 0])
			ref_start = 0
		else:
			ref_oov = np.vstack((ref_oov, [spl[0], spl[1], spl[2], 0]))
#			print(ref_oov)
print("REF OOVS: " + str(len(ref_oov)))
#print(ref_oov)

in_unk = 0
total_score = 0
total_unks = 0
usek_ready = 0
pred = ''
#total_phone_string_duration = 0

#for i in range(1, num_jobs):
for candidate in os.listdir(OOV_cand_folder):
	total_unks = total_unks + 1
#	hyp_ctm_file = open(hyp_ctm_path + "/ctm." + str(i), "r")
	print(candidate)
	underscores = list(find_all(candidate,"_"))
#	for line in hyp_ctm_file:
#		print(line)
#		spl = line.split()
#		print(spl[4])
#		if spl[4] == oov_symbol:
#			if pred == oov_symbol or pred == phnsilsp_symbol:
#				print("USEK READY CALCULATION SCORE")
#				all_ref_unks = ref_oov[ref_oov[:,0] == filename]
#				print(all_ref_unks)
#				biggest_intersection = 0
#			usek_ready = 0
#			print(line)
	filename = candidate[underscores[0]+1:underscores[1]]
	time_start = int(candidate[underscores[2]+1:underscores[3]])
	time_end = int(candidate[underscores[3]+1:candidate.index(".")])
	print(filename + " " + str(time_start) + " " + str(time_end))
#			print("USEK READY CALCULATION SCORE")
#			usek_ready = 0
#			in_unk = 0
	all_ref_unks = ref_oov[ref_oov[:,0] == filename]
	print(all_ref_unks)
	biggest_intersection = 0
	for i in range(0, len(all_ref_unks)):
		print("hyp time: " + str(time_start) + " " + str(time_end))
		ref_start_time = int(all_ref_unks[i,1])
		ref_end_time = int(all_ref_unks[i,2]) #ref_start_time + int(all_ref_unks[i,2])
		print("ref time: " + str(ref_start_time) + " " + str(ref_end_time))
		intersection_start = max(time_start, ref_start_time)
		intersection_end = min(time_end, ref_end_time)
		intersection_duration = intersection_end - intersection_start
		if (intersection_duration > biggest_intersection): 
			recall = intersection_duration / (ref_end_time - ref_start_time)
			precision = intersection_duration / (time_end - time_start)
			f_score = (2 * precision * recall) / (precision + recall)
			biggest_intersection = intersection_duration
			print("Biggest intersection: " + str(biggest_intersection))
			biggest_int_index = i
	if biggest_intersection > 0:
		ref_oov[np.where(np.all(ref_oov==all_ref_unks[biggest_int_index,:],axis=1)),3] = '1'
	else:
		f_score = 0
	total_score = total_score + f_score
#	total_phone_string_duration = total_phone_string_duration + phone_string_duration - 1
#pred = spl[4]

zeros_unks = ref_oov[ref_oov[:,3] == '0']
num_unfound = len(zeros_unks)
print("UNFOUND OOVS: " + str(num_unfound))
#print(zeros_unks)
print("UNKS IN HYPOTHESIS: " + str(total_unks))
#print("AVERAGE PHONEME STRING DURATION: " + str(float(total_phone_string_duration)/float(total_unks)))
if total_unks == 0:
	av_score = 0
else:
	av_score = float(total_score)/(float(total_unks)+float(num_unfound))
#	print("AVERAGE PHONEME STRING DURATION: " + str(float(total_phone_string_duration)/float(total_unks)))
#
print("average f_score: " + str(av_score))
