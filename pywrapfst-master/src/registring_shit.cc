#include <fst/script/register.h>
#include <fst/generic-register.h>
#include <fst/script/weight-class.h>
#include <fst/arc.h>
#include <fst/script/arciterator-class.h>
#include <fst/script/stateiterator-class.h>
#include <fst/script/script-impl.h>
#include </homes/kazi/iegorova/TOOLS/pywrapfst-master/src/triple-tropical-weight.h>
#include </homes/kazi/iegorova/TOOLS/pywrapfst-master/src/tropical_max_weight.h>
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
/*
    StateIteratorClass::StateIteratorClass(const FstClass &fst) : impl_(nullptr) {
    InitStateIteratorClassArgs args(fst, this);
    Apply<Operation<InitStateIteratorClassArgs>>("InitStateIteratorClass",
                                               fst.ArcType(), &args);
    }

    ArcIteratorClass::ArcIteratorClass(const FstClass &fst, int64 s) : impl_(nullptr) {
    InitArcIteratorClassArgs args(fst, s, this);
    Apply<Operation<InitArcIteratorClassArgs>>("InitArcIteratorClass",
                                               fst.ArcType(), &args);
    }

    MutableArcIteratorClass::MutableArcIteratorClass(MutableFstClass *fst, int64 s) : impl_(nullptr) {
    InitMutableArcIteratorClassArgs args(fst, s, this);
    Apply<Operation<InitMutableArcIteratorClassArgs>>("InitMutableArcIteratorClass", fst->ArcType(), &args);
    }

    void PrintFst(const FstClass &fst, std::ostream &ostrm, const string &dest,
              const SymbolTable *isyms, const SymbolTable *osyms,
              const SymbolTable *ssyms, bool accept, bool show_weight_one,
              const string &missing_sym) {
    const auto sep = FLAGS_fst_field_separator.substr(0, 1);
    FstPrinterArgs args(fst, isyms, osyms, ssyms, accept, show_weight_one, &ostrm,
                        dest, sep, missing_sym);
    Apply<Operation<FstPrinterArgs>>("PrintFst", fst.ArcType(), &args);
    }

    void ArcSort(MutableFstClass *fst, ArcSortType sort_type) {
    ArcSortArgs args(fst, sort_type);
    Apply<Operation<ArcSortArgs>>("ArcSort", fst->ArcType(), &args);
    }

    void Determinize(const FstClass &ifst, MutableFstClass *ofst,
                 const DeterminizeOptions &opts) {
    if (!ArcTypesMatch(ifst, *ofst, "Determinize") ||
        !ofst->WeightTypesMatch(opts.weight_threshold, "Determinize")) {
      ofst->SetProperties(kError, kError);
      return;
    }
    DeterminizeArgs1 args(ifst, ofst, opts);
    Apply<Operation<DeterminizeArgs1>>("Determinize", ifst.ArcType(), &args);
    }

    void Determinize(const FstClass &ifst, MutableFstClass *ofst, float d,
                   int64 n, int64 l, DeterminizeType t, bool i) {
    if (!ArcTypesMatch(ifst, *ofst, "Determinize")) {
      ofst->SetProperties(kError, kError);
      return;
    }
    DeterminizeArgs2 args(ifst, ofst, d, n, l, t, i);
    Apply<Operation<DeterminizeArgs2>>("Determinize", ifst.ArcType(), &args);
    }

    void Union(MutableFstClass *fst1, const FstClass &fst2) {
      if (!ArcTypesMatch(*fst1, fst2, "Union")) {
        fst1->SetProperties(kError, kError);
        return;
      }
      UnionArgs args(fst1, fst2);
      Apply<Operation<UnionArgs>>("Union", fst1->ArcType(), &args);
    }
    
    void Compose(const FstClass &ifst1, const FstClass &ifst2,
               MutableFstClass *ofst, ComposeFilter compose_filter) {
    if (!ArcTypesMatch(ifst1, ifst2, "Compose") ||
        !ArcTypesMatch(*ofst, ifst1, "Compose")) {
      ofst->SetProperties(kError, kError);
      return;
    }
    ComposeArgs1 args(ifst1, ifst2, ofst, compose_filter);
    Apply<Operation<ComposeArgs1>>("Compose", ifst1.ArcType(), &args);
    }


    void Compose(const FstClass &ifst1, const FstClass &ifst2,
                MutableFstClass *ofst, const ComposeOptions &copts) {
    if (!ArcTypesMatch(ifst1, ifst2, "Compose") ||
        !ArcTypesMatch(*ofst, ifst1, "Compose")) {
      ofst->SetProperties(kError, kError);
      return;
    }
    ComposeArgs2 args(ifst1, ifst2, ofst, copts);
    Apply<Operation<ComposeArgs2>>("Compose", ifst1.ArcType(), &args);
    }

    REGISTER_FST_OPERATION(InitStateIteratorClass, IndexArc,
                       InitStateIteratorClassArgs);
    REGISTER_FST_OPERATION(InitArcIteratorClass, IndexArc, InitArcIteratorClassArgs);
    REGISTER_FST_OPERATION(InitMutableArcIteratorClass, IndexArc,
                       InitMutableArcIteratorClassArgs);
    REGISTER_FST_OPERATION(PrintFst, IndexArc, FstPrinterArgs);
    REGISTER_FST_OPERATION(ArcSort, IndexArc, ArcSortArgs);*/
//    REGISTER_FST_OPERATION(Determinize, IndexArc, DeterminizeArgs1);
//    REGISTER_FST_OPERATION(Determinize, IndexArc, DeterminizeArgs2);
//    REGISTER_FST_OPERATION(Union, IndexArc, UnionArgs);
//    REGISTER_FST_OPERATION(Compose, IndexArc, ComposeArgs1);
//    REGISTER_FST_OPERATION(Compose, IndexArc, ComposeArgs2);
//    REGISTER_FST_OPERATION()
//    REGISTER_FST_CLASSES(IndexArc);
//    REGISTER_FST_OPERATIONS(IndexArc);
  }
}

