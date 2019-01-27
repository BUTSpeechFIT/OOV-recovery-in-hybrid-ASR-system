import sys
import numpy as np
import pywrapfst as fst
import os
#from random import randrange
#from random import shuffle
#from numpy.random import choice
#from fst_functions import fst_printout
from fst_functions import normalize_fst
#import matplotlib.pyplot as plt
#import scipy
#from scipy.spatial import distance

OOV_list = sys.argv[1]
OOV_dir = sys.argv[2]
models_dir = sys.argv[3]
#assign_output = sys.argv[4]
batch_num = int(sys.argv[4])
new_models_dir = sys.argv[5]
#out_file = open(sys.argv[6], "w")

#model_sizes_file = open(new_models_dir + "/model_sizes.txt", "w")

#alpha = float(sys.argv[3])
#num_iters = int(sys.argv[4])
#out_dir = sys.argv[5]

if not os.path.exists(new_models_dir):
	os.mkdir(new_models_dir)
	os.mkdir(new_models_dir + "/logs/")

out_file = open(sys.argv[6], "w")

model_sizes_file = open(new_models_dir + "/model_sizes.txt", "w")

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

cluster_models = []
cluster_sizes = []
cluster_names = []

cluster_assign = np.zeros(num_candidates)-1

for i in range(batch_num):
	assign_file = open(models_dir + "/assign_output_" + str(i+1) + ".txt", "r")
	for line in assign_file:
		split_line = line.split()
		print("cand_name " + split_line[0] + "\n")
		print("model_name " + split_line[1] + "\n")
#	cluster_assig
#cluster_models = []
#cluster_sizes = []
#cluster_names = []
#	for i in range(0, num_candidates): #update models after all candidates are sampled
		cand_index = candidate_names.index(split_line[0])
		print("cand_index " + str(cand_index) + "\n")
		print(cluster_names)
		print(cluster_sizes)
		print(cluster_assign)
		if split_line[1] not in cluster_names: #cluster_assign[i] not in cluster_names:
			cluster_names.append(split_line[1])
			cluster_sizes.append(1.0)
			model = normalize_fst(fst.Fst.read(models_dir + "/" + split_line[1] + ".fst"))
			model.verify()
			cluster_models.append(model) #normalize_fst(fst.Fst.read(models_dir + "/" + split_line[1] + ".fst")))
			cluster_assign[cand_index] = len(cluster_models)-1
		else:
			existing_cl_ind = cluster_names.index(split_line[1])
#			cluster_sizes[existing_cl_ind] += 1.0
			updated_model = fst.determinize(fst.compose(candidates[cand_index].arcsort(sort_type="olabel"),cluster_models[existing_cl_ind].arcsort())).minimize()
			if updated_model.num_states() > 0:
				cluster_models[existing_cl_ind] = normalize_fst(updated_model)				
				cluster_sizes[existing_cl_ind] += 1.0
				cluster_assign[cand_index] = existing_cl_ind
			else:
				print("ERROR EMPTY INTERSECTION OF MODEL AND CANDIDATE") #remove candidate from cluster?

#	print("iter " + str(it))
#	if it % 100 == 0:	
#		out_file = open(out_dir + "/logs/iter_" + str(int(it)) + ".txt", "w")
print("CLUSTER OUTPUT")
for i in range(0,len(cluster_sizes)):
	print(str(i))
	model_sizes_file.write(str(i) + " " + str(int(cluster_sizes[i])) + "\n")
	cluster_models[i].write(new_models_dir + "/" + str(i) + ".fst")
	if cluster_sizes[i] > 2:
		out_file.write("cluster name " + str(cluster_names[i]) + " cluster size " + str(cluster_sizes[i]) + "\n")
		for state in cluster_models[i].states():
			for arc in cluster_models[i].arcs(state):
				out_file.write(str(state) + " " + str(arc.nextstate) + " " + str(arc.ilabel) + " " + str(arc.olabel) + " " + str(arc.weight.to_string()) + "\n")
		out_file.write("candidates clustered here:\n")
		for cand_ind in range(0,len(cluster_assign)):
			if cluster_assign[cand_ind] == i:
				out_file.write(str(candidate_names[cand_ind]) + "\n")

#	it=it+1

#out_file = open(out_dir + "/logs/final_" + str(num_iters) + "_iters.txt", "w")
#for i in range(0,`len(cluster_sizes)):
#	if cluster_sizes[i] > 2: 
#		out_file.write("cluster name " + str(i) + " cluster size " + str(cluster_sizes[i]) + "\n")
#		for state in cluster_models[i].states():
#			for arc in cluster_models[i].arcs(state):
#				out_file.write(str(state) + " " + str(arc.nextstate) + " " + str(arc.ilabel) + " " + str(arc.olabel) + " " + str(arc.weight.to_string()) + "\n") #state, arc.nextstate, arc.ilabel, arc.olabel, arc.weight.to_string())
#		out_file.write("candidates clustered here:\n")
#		for cand_ind in range(0,len(cluster_assign)):
#			if cluster_assign[cand_ind] == i:
#				out_file.write(str(candidate_names[cand_ind]) + "\n")
		




#print(cluster_sizes)
#print(len(cluster_models))
#for i in range(len(cluster_models)):
#	cluster_models[i].write(out_dir+"/OOV_"+str(i)+".fst")
