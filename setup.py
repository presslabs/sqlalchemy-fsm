from setuptools import setup, find_packages

requires_list = [
  'SQLAlchemy==0.8.4',
  'argparse==1.2.1',
  'wsgiref==0.1.2',
]

setup(name='sqlalchemy_fsm',
      version='0.0.1',
      platforms='any',
      description='FSM implementation for sqlalchemy',
      author='dagoof',
      url='https://github.com/PressLabs/sqlalchemy-fsm',
      packages = ['sqlalchemy_fsm'],
      include_package_data=True,
      install_requires=requires_list,
      classifiers = [
        'Programming Language :: Python :: 2.7',
      ]
)
