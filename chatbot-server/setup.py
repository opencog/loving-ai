from distutils.core import setup

setup(
    version='0.1.1',
    name='chatbot',
    packages=['chatbot', 'chatbot.server'],
    package_dir={'': 'src'}
)
