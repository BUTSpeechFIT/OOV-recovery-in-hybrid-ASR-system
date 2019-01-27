import sys
import numpy as np
import pywrapfst as fst
import os
#from random import randrange
from random import shuffle
from numpy.random import choice
#from fst_functions import fst_printout
from fst_functions import normalize_fst
#mport matplotlib.pyplot as plt
#import scipy
#from scipy.spatial import distance

#python utils/OOV_clustering_sample_assign.py OOV_cand_list_beam_15_lb_8_100.txt data/OOVs_train_360/PWIP_0_PLMSF_0.8_PC_-10_beam_15_lb_8 data/OOVs_train_360/PWIP_0_PLMSF_0.8_PC_-10_beam_15_lb_8_models data/OOVs_train_360/PWIP_0_PLMSF_0.8_PC_-10_beam_15_lb_8_models/model_sizes_iter_0.txt 0.01 data/OOVs_train_360/PWIP_0_PLMSF_0.8_PC_-10_beam_15_lb_8_models/assign_output_100.txt > out_cand_addign.txt

OOV_list = sys.argv[1]
OOV_dir = sys.argv[2]
models_dir = sys.argv[3]
model_sizes_file = sys.argv[4]
alpha = float(sys.argv[5])
batch_num = sys.argv[6]
#num_iters = int(sys.argv[4])
out_file = open(models_dir + "/assign_output_" + str(batch_num) + ".txt", "w")

#if not os.path.exists(out_dir):
#	os.mkdir(out_dir)
#os.mkdir(out_dir + "/logs/")


print("Reading OOVs from directory " + OOV_dir + " in order of the list in " + OOV_list)

num_candidates=0
candidate_names = []
candidates = []

for line in open(OOV_list, "r"):
	candidate_names.append(line[:line.find(".")])
	ltt_fst = fst.Fst.read(OOV_dir + "/" + line[:line.find("\n")])
	candidates.append(ltt_fst)
#       cluster_models.append(lff_fst)
	num_candidates+=1

print(candidate_names)

cluster_assign = np.zeros(num_candidates)-1

#it = 0.0
cluster_models = []
cluster_sizes = []
model_names = []

if os.path.isfile(model_sizes_file):
	print("Model sizes file discovered " + model_sizes_file)
	model_file = open(model_sizes_file, "r")
	for line in model_file:
		split_line = line.split()
		model_names.append(split_line[0])
		cluster_sizes.append(int(split_line[1]))
		cluster_models.append(fst.Fst.read(models_dir + "/" + split_line[0] + ".fst"))

print("Number of pre-existing models " + str(len(cluster_models)))

#while it < num_iters: #200000:
#	print("iter " + str(it))
#	print(cluster_assign)
#	cluster_assign = np.zeros(num_candidates)-1
#	if it > 1:
#		print("num clusters")
#		print(len(cluster_models))
#		print("cluster sizes max")
#		print(max(cluster_sizes))

shuffled_ind = [i for i in range(num_candidates)]
shuffle(shuffled_ind)
#print(shuffled_ind)
for sample_index in shuffled_ind:
#	print(sample_index)
	sample = candidates[sample_index]#OOV_array[cand_index]
	prob_new_table = alpha / (sum(cluster_sizes) + alpha)
	nonzero_tables = [-1]		
	table_probs = [prob_new_table]

	for cluster_model_ind in range(0, len(cluster_models)):
#		print("comparing with model " + str(cluster_model_ind))
		cluster_model = cluster_models[cluster_model_ind]
		cluster_size = cluster_sizes[cluster_model_ind]
		comp = fst.determinize(fst.compose(sample.arcsort(sort_type="olabel"), cluster_model.arcsort())).minimize()
		if comp.num_states() > 0:
#			print("nonzero composition")
			shortest_dis_list = fst.shortestdistance(comp)
			score = 0.0
			for state in comp.states():
				if comp.num_arcs(state) == 0:
					str_w = shortest_dis_list[state].to_string()
					score_float = float(str_w[:str_w.find(b' ')]) #float(str_w)
					score = score + np.exp(-1*score_float)
			prob_merge = cluster_size / (sum(cluster_sizes) + alpha) * score 
#			print(str(prob_merge))
			table_probs.append(prob_merge)
			nonzero_tables.append(cluster_model_ind)#cluster_names[cluster_model_ind])						

	sum_probs = sum(table_probs)
	table_probs_norm = [x / sum_probs for x in table_probs]#table_probs / sum(table_probs)

#	print(nonzero_tables)
#	print(table_probs_norm)

	chosen_table = int(choice(nonzero_tables, p=table_probs_norm))
#	print(chosen_table)
	if chosen_table == -1:
		new_model = normalize_fst(sample)
		cluster_models.append(new_model)
		model_names.append(str(batch_num) + "_" + str(len(cluster_models)-1))
		new_model.write(models_dir + "/" + str(batch_num) + "_" + str(len(cluster_models)-1) + ".fst")
		cluster_assign[sample_index] = len(cluster_models)-1
		cluster_sizes.append(1.0)
	else:
		cluster_sizes[chosen_table] = cluster_sizes[chosen_table] + 1.0 #+ table_probs_norm[nonzero_tables.index(chosen_table)]*100
		cluster_assign[sample_index] = chosen_table
#	print(cluster_assign)
	out_file.write(candidate_names[sample_index] + " " + model_names[int(cluster_assign[sample_index])] + "\n")
