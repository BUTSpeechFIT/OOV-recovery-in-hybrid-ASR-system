#PWIP=$1
#PLMSF=$2
#PC=$3

lang_dir=$1
graph_dir=$2
beam=$3
lattice_beam=$4
stage=$5

prefix="data/lang_hybrid_"
postfix=${lang_dir#"$prefix"}
#postfix=${_dir} #PWIP_${PWIP}_PLMSF_${PLMSF}_PC_${PC}
baseline_lang=lang_baseline_ngram_oovs
#hybrid_lang=data/lang_hybrid_$postfix

. ./cmd.sh
. ./path.sh

#stage=6

beams=beam_${beam}_lb_${lattice_beam}

if [ $stage -le 0 ]; then
  if [ ! -f exp/tri4b_ali_clean_360_ngram_oovs/trans.1 ]; then
    echo "generating transforms and alignments for train"
    cp exp/tri4b/* exp/
    python utils/text_filter_oovs.py data/train_clean_360/text data/$baseline_lang/words.txt data/train_clean_360/text_wo_oovs.txt
    mv data/train_clean_360/text data/train_clean_360/text_w_oovs.txt
    mv data/train_clean_360/text_wo_oovs.txt data/train_clean_360/text
    steps/align_fmllr_lats.sh --nj 40 --cmd "$decode_long_cmd" data/train_clean_360/ data/$baseline_lang/ exp/tri4b exp/tri4b_ali_clean_360_ngram_oovs/
  fi
  echo "generate lattices on train"
  steps/nnet2/decode.sh --nj 40 --cmd "$decode_long_cmd" --beam $beam --lattice_beam $lattice_beam --transform-dir exp/tri4b_ali_clean_360_ngram_oovs/ $graph_dir data/train_clean_360/ exp/nnet5a_clean_100_gpu/decode_train_clean_360_${postfix}_${beams}/
fi

#exit 0;

if [ $stage -le 1 ]; then
  echo "index creation"
  # data/kws_train_360/ dir must include file called utter_id with utterance labels in the first column and numbers from one in the second column
  steps/make_index_output.sh --cmd "$decode_long_cmd" data/kws_train_360/ $lang_dir exp/nnet5a_clean_100_gpu/decode_train_clean_360_${postfix}_$beams/ exp/nnet5a_clean_100_gpu/decode_train_clean_360_${postfix}_$beams/kws
fi
if [ $stage -le 2 ]; then
  echo "cutting out OOVs" # to folder data/OOVs_eval_combined/${postfix}_3gram_beam_18_latbeam10_ttt_weight_sge_frame_tol_30"
  frame_tol=30
  mkdir -p oov_logs_sge_frame_tol_${frame_tol} 
  mkdir -p data/OOVs_train_360
  $decode_long_cmd --num-threads 1 JOB=1:40 oov_logs_sge_frame_tol_${frame_tol}/out_cut_oovs_ttt_weight_JOB.txt oov-extraction-qsub-wrapper.sh ./data/kws_train_360/utter_id $lang_dir/words.txt exp/nnet5a_clean_100_gpu/decode_train_clean_360_${postfix}_$beams/kws_index.JOB.txt $frame_tol data/OOVs_train_360/${postfix}_$beams/
fi

if [ $stage -le 3 ]; then
  echo "oov_detection score calculation put to ./oov_detection_score_train_360_${postfix}_${beams}.txt"
  if [ ! -f cluster_scoring/ref_ctm_frames.txt ]; then
    if [ ! -f exp/tri4b_ali_clean_360_ngram_oovs/ctm.1 ]; then
      echo "steps/align_fmllr_lats.sh"
#      steps/align_fmllr_lats.sh --nj 40 --cmd "$decode_long_cmd" data/train_clean_360/ data/$baseline_lang/ exp/tri4b exp/tri4b_ali_clean_360_ngram_oovs/
       $decode_long_cmd --num-threads 1 JOB=1:40 exp/tri4b_ali_clean_360_ngram_oovs/log/log_al_words.JOB lattice-align-words data/$baseline_lang/phones/word_boundary.int exp/tri4b_ali_clean_360_ngram_oovs/final.mdl "ark:gunzip -c exp/tri4b_ali_clean_360_ngram_oovs/lat.JOB.gz|" ark,t:exp/tri4b_ali_clean_360_ngram_oovs/lat_al_words.txt #| lattice-to-ctm-conf ark:- exp/tri4b_ali_clean_360_ngram_oovs/JOB.ctm
       $decode_long_cmd --num-threads 1 JOB=1:40 exp/tri4b_ali_clean_360_ngram_oovs/log/log_ctm.JOB lattice-to-ctm-conf ark:exp/tri4b_ali_clean_360_ngram_oovs/lat_al_words.txt exp/tri4b_ali_clean_360_ngram_oovs/ctm.JOB
    fi
    mkdir -p cluster_scoring
    mkdir -p cluster_scoring/ref
#    $decode_long_cmd --num-threads 1 JOB=1:40 exp/tri4b_ali_clean_360_ngram_oovs/log/log_ctm.JOB lattice-align-words data/$baseline_lang/phones/word_boundary.int exp/tri4b_ali_clean_360_ngram_oovs/final.mdl "ark:gunzip -c exp/tri4b_ali_clean_360_ngram_oovs/lat.JOB.gz|" ark,t:- | lattice-to-ctm-conf ark:- exp/tri4b_ali_clean_360_ngram_oovs/ctm.JOB
    for JOB in {1..40}; do cat exp/tri4b_ali_clean_360_ngram_oovs/ctm.$JOB | awk '{print($1,$3,$4+$3,$5)}' > cluster_scoring/ref/clusters.ctm.$JOB; done
    for JOB in {1..40}; do cat ./cluster_scoring/ref/clusters.ctm.$JOB >> ./cluster_scoring/ref_ctm.txt; done
    cat ./cluster_scoring/ref_ctm.txt | awk '{print($1,$2*100,$3*100,$4)}' > ./cluster_scoring/ref_ctm_frames.txt
  fi
  python utils/oov_detection_score_all_paths_ttt.py $lang_dir/words.txt cluster_scoring/ref_ctm_frames.txt data/OOVs_train_360/${postfix}_$beams > ./oov_detection_score_train_360_${postfix}_${beams}.txt
fi

if [ $stage -le 4 ]; then
  echo "oov clustering"
  # set alpha for chinese restaurant process here
  alpha=0.05
  num_oovs=$(find data/OOVs_train_360/${postfix}_$beams -maxdepth 1 -type f|wc -l)
  let num_clust_iter=num_oovs*10

  if [ ! -f OOV_cand_list_${beams}_1.txt ]; then
    ls data/OOVs_train_360/${postfix}_${beams}/ > OOV_cand_list_${beams}.txt
    cand_split_lists=$(for n in `seq 10`; do echo OOV_cand_list_${beams}_${n}.txt; done)
    utils/split_scp.pl OOV_cand_list_${beams}.txt $cand_split_lists || exit 1
  fi

  mkdir -p data/OOVs_train_360/${postfix}_${beams}_models_it_0
  mkdir -p data/OOVs_train_360/${postfix}_${beams}_models_it_0/logs

#  mkdir -p data/OOVs_train_360/${postfix}_${beams}_clustered_chinese
#  mkdir -p data/OOVs_train_360/${postfix}_${beams}_clustered_chinese/logs
#  python utils/OOV_clustering_chinese_corr.py OOV_cand_list_${beams}.txt data/OOVs_train_360/${postfix}_${beams}/ $alpha $num_clust_iter data/OOVs_train_360/${postfix}_${beams}_clustered_chinese/ > data/OOVs_train_360/${postfix}_${beams}_clustered_chinese/logs/clustering_output.txt
  it=0
  while [ $it -lt $num_clust_iter ]; do 
#    mkdir -p data/OOVs_train_360/${postfix}_${beams}_models_it_${it}
#    mkdir -p data/OOVs_train_360/${postfix}_${beams}_models_it_${it}/logs
    $decode_long_cmd --num-threads 1 JOB=1:10 data/OOVs_train_360/${postfix}_${beams}_models_it_${it}/logs/samle_assign_iter_${it}.JOB oov-clust-run-sample-assign-qsub-wrapper.sh OOV_cand_list_${beams}_JOB.txt data/OOVs_train_360/${postfix}_${beams} data/OOVs_train_360/${postfix}_${beams}_models_it_${it} data/OOVs_train_360/${postfix}_${beams}_models_it_${it}/model_sizes.txt $alpha JOB || exit 1 
    python utils/OOV_clustering_collect_assign_update_models.py OOV_cand_list_${beams}.txt data/OOVs_train_360/${postfix}_${beams} data/OOVs_train_360/${postfix}_${beams}_models_it_${it} 10 data/OOVs_train_360/${postfix}_${beams}_models_it_${it+1} data/OOVs_train_360/${postfix}_${beams}_models_it_${it+1}/out_collect_assign.txt > out_${it}.txt || exit 1
    let it=it+1
  done
fi

