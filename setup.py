from setuptools import setup, find_packages

setup(
    name="boss",
    version="0.1pre",
    packages=find_packages(),
    install_requires=['PyYAML'],

    package_data={
        '': ['*.yaml'],
    },

    author="Joshua Forman",
    author_email="josh@yoshrote.com",
    description="A dynamic job scheduler",
    long_description=open('README.md').read(),
    license="MIT",
    url="http://github.com/yoshrote/boss",

    entry_points={
        'console_scripts': [
            'boss = boss.__main__:main',
        ],
        'boss_task_finder': [
            'hardcoded = boss.task_finder:MemoryTaskFinder',
            'sqlite = boss.task_finder:SQLTaskFinder',
        ],
        'boss_scope_finder': [
            'hardcoded = boss.scope_finder:MemoryScopeFinder',
            'sqlite = boss.scope_finder:SQLScopeFinder',
        ],
        'boss_registry': [
            'memory = boss.registry:MemoryRegistry',
            'sqlite = boss.registry:SQLRegistry',
        ],

    }
)
