import unittest
import tests
from setuptools import setup,find_packages

def readme():
    with open('../README.rst') as f:
        return f.read()

def test_suite():
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(test_module)
    return suite		
		
setup(name='apx',
      version='0.1.2',
      description='A framework for sending AUTOSAR signal data to non-AUTOSAR applications',
      long_description=readme(),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
      ],
      url='http://github.com/cogu/apx/python3',
      author='Conny Gustafsson',
      author_email='congus8@gmail.com',
      license='MIT',
	  install_requires=[
		  'autosar>=0.3.0'
      ],
      packages=['apx'],
      py_modules=['remotefile','numheader'],
	  test_suite = 'tests',
	  dependency_links=['https://github.com/cogu/autosar/archive/v0.3.0.tar.gz#egg=autosar-0.3.0'],
	  zip_safe=False)
	  