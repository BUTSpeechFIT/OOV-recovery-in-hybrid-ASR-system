#$decode_cmd --num-threads 1 JOB=1:10 oov_logs_sge_frame_tol_30/out_cut_oovs_ttt_weight_JOB.txt oov-extraction-qsub-wrapper.sh ./data/kws_train/utter_id ./data/test_hybrid/PWIP_-1.5_PLMSF_1.1_PC_-10_3gram/words.txt ./exp/sgmm2_5b_mmi_b0.1_z/decode_eval_hybrid/PWIP_-1.5_PLMSF_1.1_PC_-10_3gram/kws_index.JOB.txt 30 data/OOVs_eval_combined/PWIP_-1.5_PLMSF_1.1_PC_-10_3gram_ttt_weight_sge_frame_tol_30

import sys
import os
import pywrapfst as fst
import codecs

utt_file = open(sys.argv[1], "r")
words_file = codecs.open(sys.argv[2], "r", encoding="utf-8")
kws_file = open(sys.argv[3], "r")
frame_tolerance = int(sys.argv[4])
print("frame tol " + str(frame_tolerance))
#pruneweight = sys.argv[5]
#print("prune " + str(pruneweight))
output_path = sys.argv[5]
print(output_path)

try:
	os.stat(output_path)
except:
	os.mkdir(output_path)

def find_all(a_str, sub):
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1: return
        yield start
        start += len(sub)

print("Processing lattices from " + sys.argv[3])

utt_names = []
for line in utt_file:
	utt_names.append(line.split()[0])
endlabel = 0

## compile phoneme mask to extract phoneme sublattices ##
phonemes = []
phoneme_mask = fst.Fst(arc_type=b'TripleTropicalWeight')
phoneme_mask.add_state()
phoneme_mask.add_state()
phoneme_mask.add_state()
phoneme_mask.add_state()
for line in words_file:
	if line[0:4] == 'PHN_' or line.split()[0] == '<UNK>' or line.split()[0] == '<PHNSILSP>' or line.split()[0] == 'PSI1':
		phonemes.append(int(line.split()[1]))
		if line.split()[0] == '<UNK>':
			phoneme_mask.add_arc(0, fst.Arc(int(line.split()[1]),int(line.split()[1]),fst.Weight.One(phoneme_mask.weight_type()),1))
		elif line.split()[0] == '<PHNSILSP>':
			phoneme_mask.add_arc(1, fst.Arc(int(line.split()[1]),int(line.split()[1]),fst.Weight.One(phoneme_mask.weight_type()),2))
			endlabel = int(line.split()[1])
		else:
			phoneme_mask.add_arc(1, fst.Arc(int(line.split()[1]),int(line.split()[1]),fst.Weight.One(phoneme_mask.weight_type()),1))

for i in range(0,5000):
	phoneme_mask.add_arc(2, fst.Arc(i,i,fst.Weight.One(phoneme_mask.weight_type()),3))

phoneme_mask.set_start(0)
phoneme_mask.set_final(3, fst.Weight.One(phoneme_mask.weight_type()))

OOV_count = 0
for line in kws_file:
	if line.strip() and line.split()[0] in utt_names: #line with file name, start new lattice
		utt_name = line[:line.find(" ")]
		utt_index = fst.Fst(arc_type=b'TripleTropicalWeight')
		print("utt name " + utt_name)
	elif line.strip(): #line not empty
		if len(line.split())>1:
			if line.find(",") > -1:
				utt_index.add_state()
				delimeters = list(find_all(line.split()[4],","))
				weight_string = line.split()[4][:delimeters[0]] + " " + line.split()[4][delimeters[0]+1:delimeters[1]] + " " + line.split()[4][delimeters[1]+1:]
				utt_index.add_arc(int(line.split()[0]), fst.Arc(int(line.split()[2]),int(line.split()[3]),fst.Weight(utt_index.weight_type(),weight_string),int(line.split()[1])))
			else:
				utt_index.add_state()
				utt_index.add_arc(int(line.split()[0]), fst.Arc(int(line.split()[2]),int(line.split()[3]),fst.Weight.One(utt_index.weight_type()),int(line.split()[1])))
		else:
			utt_index.add_state()
			utt_index.set_final(int(line.split()[0]), fst.Weight.One(utt_index.weight_type()))
	else: #empty line, end of lattice, do search
		## masking lattice with phoneme mask ##
		utt_index.set_start(0)
		utt_index.verify()
		phoneme_mask.verify()

		oov = fst.compose(phoneme_mask.arcsort(sort_type="olabel"), utt_index.arcsort())
		print("Num.states: " + str(oov.num_states()))
		print("Printing OOV from " + utt_name)

		if oov.num_states() > 0 and oov.num_states() < 1000:
			oov_modified = fst.Fst(arc_type=b'TripleTropicalWeight')
			for i in range(0, oov.num_states()):
				i = oov_modified.add_state()
			for state in oov.states():
#				print(state)
				for arc in oov.arcs(state):
#					print(state, arc.nextstate, arc.ilabel, arc.olabel, arc.weight.to_string())
					if arc.olabel != 0:
						oov_modified.add_arc(state, fst.Arc(arc.ilabel+5000,arc.olabel,arc.weight,arc.nextstate))
						oov_modified.set_final(arc.nextstate, fst.Weight.One(oov_modified.weight_type()))
					else:
						oov_modified.add_arc(state, fst.Arc(arc.ilabel,arc.olabel,arc.weight,arc.nextstate))
			oov = oov_modified
#			print("Finish")
#			print("Printing modified oov")
#			for state in oov_modified.states():	
#				print(state)
#				for arc in oov_modified.arcs(state):
#					print(state, arc.nextstate, arc.ilabel, arc.olabel, arc.weight.to_string())

		## extracting oovs with different endsymbols from the utterance ##
			oovs = []
			found_oov = fst.Fst(arc_type=b'TripleTropicalWeight')
			for i in range(0, oov.num_states()):
				i = found_oov.add_state()
			found_oov.set_start(0)
			fst_states = []
			traversed_arcs = []
			fst_states.insert(0,0)
			while len(fst_states) > 0: #and oov.num_states() > 0:
				state = fst_states.pop()
				for arc in oov.arcs(state):
					arc_string = str(state) + " " + str(arc.nextstate) + " " + str(arc.ilabel) + " " + str(arc.olabel) + " " + str(arc.weight.to_string())
					if arc_string not in traversed_arcs:
						traversed_arcs.append(arc_string)
						found_oov.add_arc(state, fst.Arc(arc.ilabel,arc.ilabel,arc.weight,arc.nextstate))
						if arc.ilabel == endlabel: 
						
							found_oov.set_final(arc.nextstate, fst.Weight.One(found_oov.weight_type()))
							found_oov = fst.determinize(found_oov).minimize()
							found_oov.verify()

							if found_oov.num_states() > 3:
								oovs.append(found_oov)
								print("NUM OOV CANDIDATES: " + str(len(oovs)))
							oov.delete_states(states=[arc.nextstate])
							found_oov = fst.Fst(arc_type=b'TripleTropicalWeight')
							for i in range(0, oov.num_states()):
								i = found_oov.add_state()
							found_oov.set_start(0)
							fst_states = []
							fst_states.insert(0,0)
							traversed_arcs = []
							break
						elif arc.nextstate not in fst_states:
							fst_states.insert(0,arc.nextstate)
	
			print("FINAL NUM OOV CANDIDATES: " + str(len(oovs)))
			#merge overlapping candidates
			comp_oov_i = 0
			while comp_oov_i < len(oovs):
				if_merged = 0		
				print(str(comp_oov_i))
				comp_oov_1 = oovs[comp_oov_i]
				comp_oov_1_start = 0
				comp_oov_1_end = 0
				comp_oov_1_shortest = fst.determinize(fst.shortestpath(comp_oov_1)).minimize().rmepsilon()
				for tmp_state in comp_oov_1_shortest.states():
					for tmp_arc in comp_oov_1_shortest.arcs(tmp_state):
						str_w = tmp_arc.weight.to_string()
						comp_oov_1_start = comp_oov_1_start + int(str_w[str_w.find(b' ')+1:str_w.find(b' ',str_w.find(b' ')+1)])
						comp_oov_1_end = comp_oov_1_end + int(str_w[str_w.find(b' ',str_w.find(b' ')+1)+1:])
				for comp_oov_j in range(comp_oov_i+1, len(oovs)):
#					if_merged = 0
					comp_oov_2 = oovs[comp_oov_j] 
					comp_oov_2_start = 0
					comp_oov_2_end = 0
					comp_oov_2_shortest = fst.determinize(fst.shortestpath(comp_oov_2)).minimize().rmepsilon()
					for tmp_state in comp_oov_2_shortest.states():
						for tmp_arc in comp_oov_2_shortest.arcs(tmp_state):
							str_w = tmp_arc.weight.to_string()
							comp_oov_2_start = comp_oov_2_start + int(str_w[str_w.find(b' ')+1:str_w.find(b' ',str_w.find(b' ')+1)])
							comp_oov_2_end = comp_oov_2_end + int(str_w[str_w.find(b' ',str_w.find(b' ')+1)+1:])
					if abs(comp_oov_1_start - comp_oov_2_start) < frame_tolerance and abs(comp_oov_1_end - comp_oov_2_end) < frame_tolerance:
						print("merging " + str(comp_oov_i) + " and " + str(comp_oov_j))
						comp_oov_1.union(comp_oov_2)
						oovs[comp_oov_i] = fst.determinize(comp_oov_1).minimize()
						oovs.pop(comp_oov_j)
						if_merged = 1
						print("NUM OOV CANDIDATES: " + str(len(oovs)))
						comp_oov_i = 0
						break
				if not if_merged:
					comp_oov_i = comp_oov_i + 1
						
	
			## output discovered oovs in this utterance ##r
			i = 1
			for oov in oovs:
				print("Printing OOV candidate " + str(i))
#				print(oov.num_states())
#				for tmp_fin_state in oov.states():
#					print(tmp_fin_state)
#					for tmp_fin_arc in oov.arcs(tmp_fin_state):
#						print(tmp_fin_state, tmp_fin_arc.nextstate, tmp_fin_arc.ilabel, tmp_fin_arc.olabel, tmp_fin_arc.weight.to_string())
#				final_oov = fst.determinize(oov).minimize()#fst.prune(oov)).minimize()
#				final_oov = fst.prune(fst.determinize(oov).minimize())
				final_oov = fst.determinize(oov).minimize()
#				fst.prune(oov, delta=0.000000000001)
#				print("After mindet")
#				print(final_oov.num_states())
#				for tmp_fin_state in final_oov.states():
#					print(tmp_fin_state)
#					for tmp_fin_arc in final_oov.arcs(tmp_fin_state):
#						print(tmp_fin_state, tmp_fin_arc.nextstate, tmp_fin_arc.ilabel, tmp_fin_arc.olabel, tmp_fin_arc.weight.to_string())
#				final_oov = fst.determinize(oov).minimize()
#				print("PRUNE WITH WEIGHT " + str(pruneweight))
#				final_oov.prune(weight=fst.Weight(final_oov.weight_type(), pruneweight + " 0 0"))#weight=20.0) #fst.Weight(final_oov.weight_type(), "0.000001 0 0"))
#				final_oov.prune()
#				print("After pruning")
#				print(final_oov.num_states())
				final_oov.verify()
#				for tmp_fin_state in final_oov.states():
#					print(tmp_fin_state)
#					for tmp_fin_arc in final_oov.arcs(tmp_fin_state):
#						print(tmp_fin_state, tmp_fin_arc.nextstate, tmp_fin_arc.ilabel, tmp_fin_arc.olabel, tmp_fin_arc.weight.to_string())

				if final_oov.num_states() == 0: 
					break
				final_oov_start = 0
				final_oov_end = 0
				final_oov_shortest = fst.determinize(fst.shortestpath(final_oov)).minimize().rmepsilon()
#				final_oov_shortest = 
				for tmp_state in final_oov_shortest.states():
					for tmp_arc in final_oov_shortest.arcs(tmp_state):
						str_w = tmp_arc.weight.to_string()
						final_oov_start = final_oov_start + int(str_w[str_w.find(b' ')+1:str_w.find(b' ',str_w.find(b' ')+1)])
						final_oov_end = final_oov_end + int(str_w[str_w.find(b' ',str_w.find(b' ')+1)+1:])
#					break
#				for state in final_oov.states():
#					print(state)
#					for arc in final_oov.arcs(state):
#						print(state, arc.nextstate, arc.ilabel, arc.olabel, arc.weight.to_string())
				print("output num states " + str(final_oov.num_states()))
#				print("OUTPUT TO " + output_path + "_" + pruneweight + "/OOV_" + utt_name + "_" + str(i) + "_" + str(final_oov_start) + "_" + str(final_oov_end) + ".fst")
				final_oov.write(output_path + "/OOV_" + utt_name + "_" + str(i) + "_" + str(final_oov_start) + "_" + str(final_oov_end) + ".fst")
#				final_oov.write(output_path + "_" + pruneweight + "/OOV_" + utt_name + "_" + str(i) + "_" + str(final_oov_start) + "_" + str(final_oov_end) + ".fst")
#		test_oov = fst.Fst.read(output_path + "/OOV_" + utt_name + "_" + str(i) + ".fst")
#				final_oov.draw(output_path + "/OOV_" + utt_name + "_" + str(i) + "_" + str(found_oov_start) + "_" + str(found_oov_end) + ".dot")
				i=i+1

