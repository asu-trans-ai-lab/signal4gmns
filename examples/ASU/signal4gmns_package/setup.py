import setuptools

with open("README.md","r") as fh:
    long_description=fh.read()

setuptools.setup(
    name="signal4gmns",
    version="0.0.1",
    author="Xuesong Zhou, mzlatkovic, Han(Harry) Zheng",
    author_email="xzhou74@asu.edu",
    license='Apache 2.0',
    packages=['signal4gmns'],
    url="https://github.com/asu-trans-ai-lab/vol2timing/tree/master/release",
    description=long_description,
    install_requires=["loguru",'pandas','numpy','pyyaml']#TODO:PyYAML?
)

# python setup.py check
# python setup.py sdist upload