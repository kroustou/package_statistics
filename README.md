# Package statistics

## Installation
It would be a good idea to create a virtualenv:

`python3 -m venv ~/.virtualenvs/canonical`

Install all requirements
`pip install -r requirements.txt`

## Usage
`./package_statistics.py amd64 mips --repository http://ftp.uk.debian.org/debian/dists/stable/main/` 

tests can be run with
`./test_package_statistics.py` 
