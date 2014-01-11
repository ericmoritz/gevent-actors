from setuptools import setup


setup(
    name="gevent-actors",
    version="0.1.1",
    description="basic actors using gevent and kombu for communication",
    packages=['actor'],
    install_requires=[
        "kombu",
        "gevent",
    ]
)
