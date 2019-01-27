// See www.openfst.org for extensive documentation on this weighted
// finite-state transducer library.
//
// Float weight set and associated semiring operation definitions.

#ifndef FST_FLOAT_WEIGHT_H_
#define FST_FLOAT_WEIGHT_H_

#include <climits>
#include <cmath>
#include <cstdlib>
#include <cstring>

#include <algorithm>
#include <limits>
#include <sstream>
#include <string>

#include <fst/util.h>
#include <fst/weight.h>
#include <fst/float-weight.h>

namespace fst {

// Tropical max semiring: (max, +, -inf, 0).
template <class T>
class TropicalMaxWeightTpl : public FloatWeightTpl<T> {
 public:
  using typename FloatWeightTpl<T>::ValueType;
  using FloatWeightTpl<T>::Value;
  using ReverseWeight = TropicalMaxWeightTpl<T>;
  using Limits = FloatLimits<T>;

  constexpr TropicalMaxWeightTpl() : FloatWeightTpl<T>() {}

  constexpr TropicalMaxWeightTpl(T f) : FloatWeightTpl<T>(f) {}

  constexpr TropicalMaxWeightTpl(const TropicalMaxWeightTpl<T> &weight)
      : FloatWeightTpl<T>(weight) {}

  static const TropicalMaxWeightTpl<T> &Zero() {
    static const TropicalMaxWeightTpl zero(Limits::NegInfinity());
    return zero;
  }

  static const TropicalMaxWeightTpl<T> &One() {
    static const TropicalMaxWeightTpl one(0.0F);
    return one;
  }

  static const TropicalMaxWeightTpl<T> &NoWeight() {
    static const TropicalMaxWeightTpl no_weight(Limits::NumberBad());
    return no_weight;
  }

  static const string &Type() {
    static const string *const type =
        new string(string("tropical_max") +
                   FloatWeightTpl<T>::GetPrecisionString());
    return *type;
  }

  bool Member() const {
    // First part fails for IEEE NaN.
    return Value() == Value() && Value() != Limits::PosInfinity();
  }

  TropicalMaxWeightTpl<T> Quantize(float delta = kDelta) const {
    if (!Member() || Value() == Limits::NegInfinity()) {
      return *this;
    } else {
      return TropicalMaxWeightTpl<T>(floor(Value() / delta + 0.5F) * delta);
    }
  }

  TropicalMaxWeightTpl<T> Reverse() const { return *this; }

  static constexpr uint64 Properties() {
    return kLeftSemiring | kRightSemiring | kCommutative | kPath | kIdempotent;
  }
};

// Single precision tropical weight.
//using TropicalWeight = TropicalMaxWeightTpl<float>;

template <class T>
inline TropicalMaxWeightTpl<T> Plus(const TropicalMaxWeightTpl<T> &w1,
                                 const TropicalMaxWeightTpl<T> &w2) {
  if (!w1.Member() || !w2.Member()) return TropicalMaxWeightTpl<T>::NoWeight();
  return w1.Value() > w2.Value() ? w1 : w2;
}

// See comment at operator==(FloatWeightTpl<float>, FloatWeightTpl<float>)
// for why these overloads are present.
inline TropicalMaxWeightTpl<float> Plus(const TropicalMaxWeightTpl<float> &w1,
                                     const TropicalMaxWeightTpl<float> &w2) {
  return Plus<float>(w1, w2);
}

inline TropicalMaxWeightTpl<double> Plus(const TropicalMaxWeightTpl<double> &w1,
                                      const TropicalMaxWeightTpl<double> &w2) {
  return Plus<double>(w1, w2);
}

template <class T>
inline TropicalMaxWeightTpl<T> Times(const TropicalMaxWeightTpl<T> &w1,
                                  const TropicalMaxWeightTpl<T> &w2) {
  using Limits = FloatLimits<T>;
  if (!w1.Member() || !w2.Member()) return TropicalMaxWeightTpl<T>::NoWeight();
  const T f1 = w1.Value();
  const T f2 = w2.Value();
  if (f1 == Limits::NegInfinity()) {
    return w1;
  } else if (f2 == Limits::NegInfinity()) {
    return w2;
  } else {
    return TropicalMaxWeightTpl<T>(f1 + f2);
  }
}

inline TropicalMaxWeightTpl<float> Times(const TropicalMaxWeightTpl<float> &w1,
                                      const TropicalMaxWeightTpl<float> &w2) {
  return Times<float>(w1, w2);
}

inline TropicalMaxWeightTpl<double> Times(const TropicalMaxWeightTpl<double> &w1,
                                       const TropicalMaxWeightTpl<double> &w2) {
  return Times<double>(w1, w2);
}

template <class T>
inline TropicalMaxWeightTpl<T> Divide(const TropicalMaxWeightTpl<T> &w1,
                                   const TropicalMaxWeightTpl<T> &w2,
                                   DivideType typ = DIVIDE_ANY) {
  using Limits = FloatLimits<T>;
  if (!w1.Member() || !w2.Member()) return TropicalMaxWeightTpl<T>::NoWeight();
  const T f1 = w1.Value();
  const T f2 = w2.Value();
  if (f2 == Limits::NegInfinity()) {
    return Limits::NumberBad();
  } else if (f1 == Limits::NegInfinity()) {
    return Limits::NegInfinity();
  } else {
    return TropicalMaxWeightTpl<T>(f1 - f2);
  }
}

inline TropicalMaxWeightTpl<float> Divide(const TropicalMaxWeightTpl<float> &w1,
                                       const TropicalMaxWeightTpl<float> &w2,
                                       DivideType typ = DIVIDE_ANY) {
  return Divide<float>(w1, w2, typ);
}

inline TropicalMaxWeightTpl<double> Divide(const TropicalMaxWeightTpl<double> &w1,
                                        const TropicalMaxWeightTpl<double> &w2,
                                        DivideType typ = DIVIDE_ANY) {
  return Divide<double>(w1, w2, typ);
}

template <class T>
inline TropicalMaxWeightTpl<T> Power(const TropicalMaxWeightTpl<T> &weight,
                                  T scalar) {
  return TropicalMaxWeightTpl<T>(weight.Value() * scalar);
}


template <class T>
class WeightGenerate<TropicalMaxWeightTpl<T>>
    : public FloatWeightGenerate<TropicalMaxWeightTpl<T>> {
 public:
  using Weight = TropicalMaxWeightTpl<T>;
  using Generate = FloatWeightGenerate<Weight>;

  explicit WeightGenerate(bool allow_zero = true,
                          size_t num_random_weights = kNumRandomWeights)
      : Generate(allow_zero, num_random_weights) {}

  Weight operator()() const { return Weight(Generate::operator()()); }
};

}  // namespace fst

#endif  // FST_FLOAT_WEIGHT_H_
