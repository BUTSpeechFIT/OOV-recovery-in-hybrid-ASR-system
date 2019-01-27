# OOV-recovery-in-hybrid-ASR-system
Out-of-vocabulary word recovery system makes use of a hybrid decoding network with both words and sub-word units.  In the decoded lattices, candidates for OOV regions are identified as sub-graphs of sub-word units. To facilitate OOV word recovery, we search for recurring OOVs by clustering the detected candidate OOVs. 

## What you need to run it:
- A hybrid decoder: https://github.com/kate-egorova/ASR-hybrid-decoding
- OpenFST tool updated to work with triple weight of costs, start times and end times
