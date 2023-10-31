from setuptools import setup, find_packages

VERSION = '0.0.1' 
DESCRIPTION = 'ImTk'
LONG_DESCRIPTION = 'An Immediate GUI implementation for Tkinter'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="imtk", 
        version=VERSION,
        author="Dominik Penk",
        author_email="<penk.dominik@gmail.com>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[],
        
        keywords=['python', 'gui', 'tkinter'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 3",
            "Operating System :: Microsoft :: Windows",
        ]
)