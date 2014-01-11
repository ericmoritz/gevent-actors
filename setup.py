from setuptools import setup


setup(
    name="gevent-actors",
    description="basic actors using gevent and kombu for communication",
    modules=['actors'],
    install_requires=[
        "kombu",
        "gevent",
    ]
)
