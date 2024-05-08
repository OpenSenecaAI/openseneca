from setuptools import setup, find_packages

# pip install -e .
# rm -rf dist/ && python setup.py sdist bdist_wheel
# twine upload --repository openseneca dist/*

VERSION = '0.1.0'
DESCRIPTION = 'OpenSeneca'
LONG_DESCRIPTION = 'The opensource library to orchestrate all LLMs around the world (and save money).'

def read_requirements():
    with open('openseneca/requirements.txt', 'r') as req:
        content = req.read()
        requirements = content.split('\n')

    return requirements

# Setting up
setup(
        name="openseneca",
        version=VERSION,
        author="Ottavio Fogliata",
        author_email="ottavio.fogliata@openseneca.ai",
        python_requires='>=3.8.13',
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=read_requirements(),
        package_data={
          'openseneca': ['weights.pk', 'config.yml'],
        },
        keywords=['python']
)