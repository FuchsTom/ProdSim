from setuptools import setup, find_packages

setup(
    name='ProdSim',
    version='0.1.0',
    description='ProdSim is a process-based discrete event simulation for production environments based on the '
                'framework SimPy, for the generation of high resolution synthetic manufacturing data',
    long_description=open('README.md').read(),
    author='Tom Fuchs',
    author_email='tom.fuchs@rwth-aachen.de',
    install_requires=[
        'simpy>=4.0.1',
        'dash>=2.0.0',
        'dash-cytoscape>=0.3.0',
        'dash-bootstrap-components>=1.0.2',
        'numpy>=1.21.5',
        'h5py>=3.6.0',
        'dill>=0.3.4'
    ],
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS",
        "Operating System :: Microsoft :: Windows :: Windows 10"
    ],
    packages=find_packages("."),
    package_dir={"": "."},
    package_data={"": ["*.json"]},
    python_requires=">=3.8",
    license='MIT License',
    platforms=['MacOS', 'Windows 10']
)
