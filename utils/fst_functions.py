import numpy as np
import pywrapfst as fst

def fst_printout(in_fst):
	for state in in_fst.states():
		print(state)
		for arc in in_fst.arcs(state):
			print(state, arc.nextstate, arc.ilabel, arc.weight.to_string())

def normalize_fst(in_fst):
	if not in_fst.verify():		
		print("ERROR WRONG FST PASSED FOR NORMALIZATION")
		return in_fst
	else:
		out_fst = fst.Fst(in_fst.weight_type())
		for state in in_fst.states():
			n = out_fst.add_state()
			arcsum = 0.0
			for arc in in_fst.arcs(state):
				str_w = arc.weight.to_string()
				arcsum += np.exp(-1*float(str_w[:str_w.find(b' ')])) #fst.plus(arcsum,arc.weight)
			for arc in in_fst.arcs(state):
				str_w = arc.weight.to_string()
				new_weight = np.exp(-1*float(str_w[:str_w.find(b' ')])) / arcsum
				weight_log = -1*np.log(new_weight)
				st_t = int(str_w[str_w.find(b' ')+1:str_w.find(b' ',str_w.find(b' ')+1)])
				en_t = int(str_w[str_w.find(b' ',str_w.find(b' ')+1)+1:])
				out_fst.add_arc(state, fst.Arc(arc.ilabel, arc.olabel, fst.Weight(out_fst.weight_type(), str(weight_log) + ' ' + str(st_t) + ' ' + str(en_t)), arc.nextstate)) #fst.divide(arc.weight,arcsum), arc.nextstate))
		out_fst.set_start(0)
		out_fst.set_final(n, in_fst.final(n))
		if out_fst.verify():
			return out_fst
		else:
			print("NORM ERROR")
			fst_printout(out_fst)
			return in_fst	

