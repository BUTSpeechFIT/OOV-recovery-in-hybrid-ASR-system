#!/bin/bash
#
#$ -S /bin/bash
#$ -q long.q
#$ -l ram_free=4G,mem_free=4G,gpu=1

# Example usage of this script:
#$decode_long_cmd --num-threads 1 JOB=1:40 oov_logs_sge_frame_tol_${frame_tol}/out_cut_oovs_ttt_weight_JOB.txt oov-extraction-qsub-wrapper.sh ./data/kws_train_360/utter_id $hybrid_lang/words.txt exp/nnet5a_clean_100_gpu/decode_train_clean_360_${postfix}_$beams/kws_index.JOB.txt $frame_tol 0 data/OOVs_train_360/${postfix}_$beams/

unset PYTHONPATH
export PATH=/homes/kazi/iegorova/miniconda3/bin:$PATH
unset PYTHONHOME
source activate py35 # activate anaconda environment for Python 3.5

cand_list=$1 # list of utterance labels
cand_dir=$2 # words.txt in hybrid lang folder, containing PHN_ words
models_dir=$3 # path to kws_index.JOB.txt files that are outputs of make_index_output.sh script
model_sizes_file=$4 # if start and end tomes of the two candidates differ less than this number of frames, candidates are merged together
alpha=$5
batchnum=$6 # where OOv candidates are put

cd /mnt/matylda6/iegorova/LibriSPEECH_clean_new/s5 

#weight=0
#echo $output_path
#mkdir -p ${output_path}
python utils/OOV_clustering_sample_assign.py $cand_list $cand_dir $models_dir $model_sizes_file $alpha $batchnum 
#python utils/OOV_cut_from_index_per_file_ttt_weight.py $utt_file $words_file $kws_file $frame_tol $output_path
