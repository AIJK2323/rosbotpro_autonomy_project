from setuptools import setup

package_name = 'human_behavior'


setup(
    name=package_name,
    version='0.0.1',

    packages=[package_name],

    install_requires=[
        'setuptools',
    ],

    zip_safe=True,

    description='Human behavior decision node',

    license='Apache-2.0',


    entry_points={
        'console_scripts': [

            'human_behavior_node = human_behavior.human_behavior_node:main',

        ],
    },
)
