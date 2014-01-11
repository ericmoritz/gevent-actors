from setuptools import setup


setup(
    name="gevent-actors",
    version="0.1",
    description="basic actors using gevent and kombu for communication",
    modules=['actors'],
    install_requires=[
        "kombu",
        "gevent",
    ]
)
