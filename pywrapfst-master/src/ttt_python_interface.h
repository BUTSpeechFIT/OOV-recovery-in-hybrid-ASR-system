// See www.openfst.org for extensive documentation on this weighted
// finite-state transducer library.
//
// Cartesian power weight semiring operation definitions.

#include <fst/arc.h>
#include <fst/float-weight.h>
#include <fst/weight.h>
#include <fst/script/fst-class.h>
#include </homes/kazi/iegorova/TOOLS/pywrapfst-master/src/tropical_max_weight.h>
#include </homes/kazi/iegorova/TOOLS/pywrapfst-master/src/triple-tropical-weight.h>
//#include <fst/string-weight.h>

using namespace fst;

using TripleTropicalWeight = TripleTropicalWeightTpl<LogWeightTpl<float>, TropicalWeightTpl<double>, TropicalMaxWeightTpl<double>>;
using IndexArc = ArcTpl<TripleTropicalWeight>;

using namespace fst::script;

VectorFstClass* CreateIndexFst() {
   const VectorFst<IndexArc> *fst = new VectorFst<IndexArc>();
   return new VectorFstClass(*fst);
}

WeightClass* IndexWeight(float prob, double start_t, double end_t) {

//   const TropicalWeightTpl<float> *probab = new TropicalWeightTpl<float>(prob);
//   const TropicalWeightTpl<double> *start_time = new TropicalWeightTpl<double>(start_t);
//   const TropicalWeightTpl<double> *end_time = new TropicalWeightTpl<double>(end_t);

   const TripleTropicalWeight *ttt_weight = new TripleTropicalWeight(LogWeightTpl<float>(prob), TropicalWeightTpl<double>(start_t), TropicalMaxWeightTpl<double>(end_t)); 

//*probab, *start_time, *end_time); //fst::TropicalWeightTpl<float>(prob), fst::TropicalWeightTpl<double>(start_t), fst::TropicalWeightTpl<double>(end_t));

   return new WeightClass(*ttt_weight);
}

