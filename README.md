# OOV-recovery-in-hybrid-ASR-system
Out-of-vocabulary word recovery system makes use of a hybrid decoding network with both words and sub-word units. In the decoded lattices, candidates for OOV regions are identified as sub-graphs of sub-word units. To facilitate OOV word recovery, we search for recurring OOVs by clustering the detected candidate OOVs.

## What you need to run it:
- A hybrid decoder: https://github.com/kate-egorova/ASR-hybrid-decoding
- OpenFST tool updated to work with triple weight of costs, start times and end times. See README in pywrapfst-master for installation guide
- copy scripts from this repository to corresponding folders in your kaldi system build
- run run_OOV_extraction_and_clustering.sh script:
./run_OOV_extraction_and_clustering.sh [hybrid lang directory used for building decoding HCLG.fst] [graph dir with hybrid HCLG.fst] [decoding beam] [lattice beam] [script stage]
example: ./run_OOV_extraction_and_clustering.sh data/lang_hybrid_PWIP_0_PLMSF_0.8_PC_-10 exp/nnet5a_clean_100_gpu/graph_hybrid_PWIP_0_PLMSF_0.8_PC_-10/ 15 8 4
