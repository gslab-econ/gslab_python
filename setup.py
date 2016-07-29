from setuptools import setup

setup(name='gslab',
      version='0.7',
      description='python package for GSLab',
      url='git@github.com:gslab-econ/GSLab.git',
      author='Frank',
      author_email='yangf2@carleton.edu',
      license='MIT',
      packages=['gslab_make', 'gslab_make.py','gslab_misc', 'gslab_misc.py', 'gslab_cmd', 'gslab_cmd.py_module',
      'extract_data', 'extract_data.py', 'ebt_records', 'ebt_records.py', 'eatthepie', 'eatthepie.py_module',
      'political_speech', 'political_speech.code', 'mental_coupons', 'mental_coupons.py', 'externals_search', 
      'externals_search.py', 'google_ngram_retriever', 'google_ngram_retriever.py'      ],
      zip_safe=False)