from Cython.Build import cythonize
from distutils.core import setup, Extension
import numpy as np
import os
import sys

exts = cythonize(
    Extension('pywrapfst',
        sources=['src/registring_shit.cc', 'src/info-impl.cc', 'src/weight-class.cc', 'src/pywrapfst.pyx'],
        language='c++',
        extra_compile_args=['-std=c++11'],
        libraries=['fst', 'fstscript', 'fstfar', 'fstfarscript'],
        include_dirs=[os.path.join(sys.prefix, 'include'), np.get_include(), "/homes/kazi/iegorova/TOOLS/Openfst-1.6.3/include"]
    ),
    include_path=['src'],
)

setup(
    name='pywrapfst',
    version='1.0',
    description='python OpenFst wrapper',
    ext_modules=exts
)

