#include <fst/script/register.h>
#include <fst/generic-register.h>
#include <fst/script/weight-class.h>
#include <fst/arc.h>
#include <fst/script/arciterator-class.h>
#include <fst/script/stateiterator-class.h>
#include <fst/script/script-impl.h>
#include <src/triple-tropical-weight.h>
#include <src/tropical_max_weight.h>
#include <fst/vector-fst.h>
#include <fst/script/fstscript.h>
#include <fst/script/union.h>
#include <fst/script/fst-class.h>
#include <fst/vector-fst.h>
#include <fst/script/print.h>
#include <fst/script/compose.h>
#include <fst/script/arcsort.h>
#include <fst/script/verify.h>
#include <fst/script/determinize.h>

using namespace fst;

//using TripleTropicalWeight = TripleTropicalWeightTpl<float, int, int>;
using TripleTropicalWeight = TripleTropicalWeightTpl<LogWeightTpl<float>, TropicalWeightTpl<double>, TropicalMaxWeightTpl<double>>;
using IndexArc = ArcTpl<TripleTropicalWeight>;

namespace fst {
  namespace script {

    REGISTER_FST(VectorFst, IndexArc);
    REGISTER_FST_CLASSES(IndexArc);
    REGISTER_FST_OPERATIONS(IndexArc);


