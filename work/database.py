import psycopg2
from configparser import ConfigParser

def get_db_config(filename='db_config.ini', section='database'):
    parser = ConfigParser()
    parser.read(filename)
    if parser.has_section(section):
        return {key: value for key, value in parser.items(section)}
    else:
        raise Exception(f"Section {section} not found in the {filename} file.")

def connect():
    params = get_db_config()
    return psycopg2.connect(**params)
