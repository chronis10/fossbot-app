from setuptools import setup, find_packages

# Read the content of your README file to include in the long description
# with open("README.md", "r") as fh:
#     long_description = fh.read()

setup(
    name='fossbot_app',
    version='1.1.9',
    packages=find_packages(),  # Automatically find and include all packages in your directory
    include_package_data=True,
    install_requires=[  # Core dependencies for your application
        'Flask',
        'Flask-Cors',
        'Flask-SocketIO',
        'Flask-Babel',
        'Flask-SQLAlchemy',
        'eventlet',
        'Pillow',
        'pystray',
        'pygame',
        'fossbot-lib',  # Replace with the source URL if not on PyPI
        'pyzmq==20.0.0',
        'coppeliasim-zmqremoteapi-client',
        'fossbot-lib-real>=0.0.0',  # Replace with the source URL if not on PyPI
        'mpu6050-raspberrypi',
        'smbus',
        'Adafruit-GPIO',
        'Adafruit-MCP3008',
	'sqlalchemy_serializer'
    ],
    extras_require={
        'dev': [
            'pytest',
            'flake8',
        ],
    },
    entry_points={  # Entry point for the CLI script
        'console_scripts': [
            'fossbot_app=blockly_server.run:main',  # Points to the `main()` function in `run.py`
        ],
    },
    author="Christos Chronis",
    author_email="chronis@hua.gr",
    description="FossBot Physical application",
    # long_description=long_description,
    # long_description_content_type="text/markdown",
    url="https://github.com/ellak/fossbot",  # Replace with your project URL
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',  # Define the minimum required Python version
)
