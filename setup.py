from setuptools import setup, find_packages

requires_list = [
  'SQLAlchemy==1.1.1',
  'argparse==1.4.0',
]

setup(name='sqlalchemy_fsm',
      version='0.0.2',
      platforms='any',
      description='FSM implementation for sqlalchemy',
      author='dagoof',
      url='https://github.com/PressLabs/sqlalchemy-fsm',
      packages = ['sqlalchemy_fsm'],
      include_package_data=True,
      install_requires=requires_list,
      classifiers = [
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
      ]
)
