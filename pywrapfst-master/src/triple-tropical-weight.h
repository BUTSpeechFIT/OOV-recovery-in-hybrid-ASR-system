// See www.openfst.org for extensive documentation on this weighted
// finite-state transducer library.
//
// Cartesian power weight semiring operation definitions.

//#ifndef FST_POWER_WEIGHT_H_
//#define FST_POWER_WEIGHT_H_

#include <string>

#include <fst/weight.h>
#include <fst/fst.h>
#include <fst/fstlib.h>
#include <fst/script/fst-class.h>
#include <fst/arc.h>
#include <iosfwd>
#include <iostream>
#include <sstream>
#include <src/tropical_max_weight.h>

using namespace std;

namespace fst {

template <class W, class st_t, class en_t>
class TripleTropicalWeightTpl { 
 public:
  using ReverseWeight = TripleTropicalWeightTpl<typename W::ReverseWeight, typename st_t::ReverseWeight, typename en_t::ReverseWeight>;

  TripleTropicalWeightTpl() {}

  TripleTropicalWeightTpl(const W prob, const st_t start_t, const en_t end_t) { prob_weight_ = prob; start_time_ = start_t; end_time_ = end_t; }
  
  TripleTropicalWeightTpl(const TripleTropicalWeightTpl &other) { prob_weight_ = other.prob_weight_; start_time_ = other.start_time_; end_time_ = other.end_time_; }

 template <class Iterator>
  TripleTropicalWeightTpl(Iterator begin, Iterator end) {
     auto it = begin;
     prob_weight_ = *it;
     it++;
     start_time_ = *it;
     it++;
     end_time_ = *it; 
  }

  static const string &Type() {
    static string type = "TripleTropicalWeight";
    return type;
  }

  static constexpr uint64 Properties() {
//    return W::Properties() & st_t::Properties() & en_t::Properties() & 
    return kLeftSemiring | kRightSemiring | kPath | kIdempotent | kCommutative;
  }

  std::ostream &Write(std::ostream &strm) const {
    prob_weight_.Write(strm);
    start_time_.Write(strm);
    return end_time_.Write(strm);
  }
  
  std::istream &Read(std::istream &strm) {
    prob_weight_.Read(strm);
    start_time_.Read(strm);
    return end_time_.Read(strm);
  }

  bool Member() const { return prob_weight_.Member() && start_time_.Member() && end_time_.Member(); }

  static const TripleTropicalWeightTpl<W, st_t, en_t> &NoWeight() {
    static const TripleTropicalWeightTpl no_weight(W::NoWeight(), st_t::NoWeight(), en_t::NoWeight()); 
    return no_weight;
  }

  static const TripleTropicalWeightTpl<W, st_t, en_t> &Zero() {
    static TripleTropicalWeightTpl zero;
    zero.SetProbWeight(W::Zero());
    zero.SetStartTime(st_t::Zero());
    zero.SetEndTime(en_t::Zero());
    return zero;
  }

  static const TripleTropicalWeightTpl<W, st_t, en_t> &One() {
    static TripleTropicalWeightTpl one;
    one.SetProbWeight(W::One());
    one.SetStartTime(st_t::One()); 
    one.SetEndTime(en_t::One());
    return one;
  }

  size_t Hash() const {
    uint64 hash = 0;
    hash = 5 * hash + prob_weight_.Hash();
    hash = 5 * hash + start_time_.Hash();
    hash = 5 * hash + end_time_.Hash();
    return size_t(hash); 
  }

  TripleTropicalWeightTpl<W, st_t, en_t> Quantize(float delta = kDelta) const {
    return TripleTropicalWeightTpl<W, st_t, en_t>(prob_weight_.Quantize(delta), start_time_.Quantize(delta), end_time_.Quantize(delta));
  }

  ReverseWeight Reverse() const {
    return ReverseWeight(prob_weight_.Reverse(), start_time_.Reverse(), end_time_.Reverse());
  }

  const st_t &StartTime() const { return start_time_; }
  const en_t &EndTime() const { return end_time_; }
  const W &ProbWeight() const { return prob_weight_; }

  void SetStartTime(const st_t &weight) { start_time_ = weight; }
  void SetEndTime(const en_t &weight) { end_time_ = weight; }
  void SetProbWeight(const W &weight) { prob_weight_ = weight; }

 private:
  W prob_weight_;
  st_t start_time_;
  en_t end_time_;
};

// Semiring plus operation.
template <class W, class st_t, class en_t>
inline TripleTropicalWeightTpl<W, st_t, en_t> Plus(const TripleTropicalWeightTpl<W, st_t, en_t> &w1,
                              const TripleTropicalWeightTpl<W, st_t, en_t> &w2) {
  TripleTropicalWeightTpl<W, st_t, en_t> result;
    result.SetProbWeight(Plus(w1.ProbWeight(), w2.ProbWeight()));
    result.SetStartTime(Plus(w1.StartTime(), w2.StartTime()));
    result.SetEndTime(Plus(w1.EndTime(), w2.EndTime()));
  return result;
}

// Semiring times operation.
template <class W, class st_t, class en_t>
inline TripleTropicalWeightTpl<W, st_t, en_t> Times(const TripleTropicalWeightTpl<W, st_t, en_t> &w1,
                               const TripleTropicalWeightTpl<W, st_t, en_t> &w2) {
  TripleTropicalWeightTpl<W, st_t, en_t> result;
  result.SetProbWeight(Times(w1.ProbWeight(), w2.ProbWeight()));
  result.SetStartTime(Times(w1.StartTime(), w2.StartTime()));
  result.SetEndTime(Times(w1.EndTime(), w2.EndTime()));
  return result;
}

template <class W, class st_t, class en_t>
inline TripleTropicalWeightTpl<W, st_t, en_t> Divide(const TripleTropicalWeightTpl<W, st_t, en_t> &w,
                                          const TripleTropicalWeightTpl<W, st_t, en_t> &v, 
                                          DivideType typ = DIVIDE_ANY) {
  return TripleTropicalWeightTpl<W, st_t, en_t>(Divide(w.ProbWeight(), v.ProbWeight(), typ), 
						Divide(w.StartTime(), v.StartTime(), typ),
						Divide(w.EndTime(), v.EndTime(), typ));
}

template <class W, class st_t, class en_t>
inline std::ostream &operator<<(std::ostream &strm,
                                const TripleTropicalWeightTpl<W, st_t, en_t> &weight) {
  strm << weight.ProbWeight();
  strm << " ";
  strm << weight.StartTime();
  strm << " ";
  strm << weight.EndTime();
  return strm;
}

template <class W, class st_t, class en_t>
inline std::istream &operator>>(std::istream &strm,
                                TripleTropicalWeightTpl<W, st_t, en_t> &weight) {
  W prob_weight;
  st_t start_time;
  en_t end_time;
  strm >> prob_weight;
  strm >> start_time;
  strm >> end_time;
  weight.SetProbWeight(prob_weight);
  weight.SetStartTime(start_time);
  weight.SetEndTime(end_time);
  return strm;
}

template <class W, class st_t, class en_t>
inline bool operator==(const TripleTropicalWeightTpl<W, st_t, en_t> &w1,
                       const TripleTropicalWeightTpl<W, st_t, en_t> &w2) {
  return w1.ProbWeight() == w2.ProbWeight() && w1.StartTime() == w2.StartTime() && w1.EndTime() == w2.EndTime();
}

template <class W, class st_t, class en_t>
inline bool operator!=(const TripleTropicalWeightTpl<W, st_t, en_t> &w1,
                       const TripleTropicalWeightTpl<W, st_t, en_t> &w2) {
  return w1.ProbWeight() != w2.ProbWeight() || w1.StartTime() != w2.StartTime() || w1.EndTime() != w2.EndTime();
}

template <class W, class st_t, class en_t>
inline bool ApproxEqual(const TripleTropicalWeightTpl<W, st_t, en_t> &w1,
                        const TripleTropicalWeightTpl<W, st_t, en_t> &w2, float delta = kDelta) {
    if (!ApproxEqual(w1.ProbWeight(), w2.ProbWeight(), delta)) return false;
    if (!ApproxEqual(w1.StartTime(), w2.StartTime(), delta)) return false;
    if (!ApproxEqual(w1.EndTime(), w2.EndTime(), delta)) return false;
  return true;
}

using TripleTropicalWeight = TripleTropicalWeightTpl<LogWeightTpl<float>, TropicalWeightTpl<double>, TropicalMaxWeightTpl<double>>;
//using IndexArc = ArcTpl<TripleTropicalWeight>;

template<>
class NaturalLess<TripleTropicalWeight> { //(const TripleTropicalWeightTpl<W, st_t, en_t> &w1,
                //                                         const TripleTropicalWeightTpl<W, st_t, en_t> &w2) 
  public:
    using Weight = TripleTropicalWeight;
    bool operator()(const TripleTropicalWeight &t1, const TripleTropicalWeight &t2) const {
      NaturalLess<TropicalWeight> less;
//      WeightConvert<LogWeightTpl<float>, TropicalWeight> to_trop_weight;
//	exp(-to_log_weight_(aiter.Value().weight).Value())
//      return less(TropicalWeight(exp(-1*t1.ProbWeight().Value())), TropicalWeight(exp(-1*t2.ProbWeight().Value())));
	return less(TropicalWeight(t1.ProbWeight().Value()), TropicalWeight(t2.ProbWeight().Value()));
    }
};

template <class W1, class W2, class W3>
class Adder<TripleTropicalWeightTpl<W1, W2, W3>> {
public:
  using Weight = TripleTropicalWeightTpl<W1, W2, W3>;

  explicit Adder(Weight w = Weight::Zero())
      : sum_(w.ProbWeight()),
        min_(w.StartTime()), 
        max_(w.EndTime()) { }
  //      c_(0.0) { }

  Weight Add(const Weight &w) {
//    Adder<Weight> adder(w);
//    Adder<W1> adder_sum(sum_);
//    Adder<W2> adder_min(min_);
//    Adder<W3> adder_max(max_);
//    sum_ = adder_sum.Add(w.ProbWeight().Value());
//    min_ = adder_min.Add(w.StartTime().Value());
//    max_ = adder_max.Add(w.EndTime().Value());
//    const T f = w.Value();
    W1 prob_w = w.ProbWeight();
    W2 st_t = w.StartTime();
    W3 en_t = w.EndTime();
    sum_ = Plus(prob_w, sum_);
    min_ = Plus(st_t, min_);
    max_ = Plus(en_t, max_);
    return Sum();
//      sum_ = internal::KahanLogSum(f, sum_, &c_);
//    }
//    return Sum();
  }

  Weight Sum() { return Weight(sum_, min_, max_); }

  void Reset(Weight w = Weight::Zero()) {
    sum_ = w.ProbWeight();
    min_ = w.StartTime();
    max_ = w.EndTime();
//    c_ = 0.0;
  }

 private:
  W1 sum_;
  W2 min_;
  W3 max_;
//  double c_;   // Kahan compensation.
};


//template <>
//class ShortestDistance<IndexArc>(const Fst<IndexArc> &fst, float delta = kDelta) {
//  return 


};  // namespace fst



