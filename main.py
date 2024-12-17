from create_data_base import create_database_and_tables
from data_parser import parse_from_csv_to_db


'''
def run_notebook():
    os.system("pip install jupyter")
    os.system("jupyter nbconvert --to notebook --execute analytics.ipynb")
'''

if __name__ == '__main__':
    create_database_and_tables()
    parse_from_csv_to_db()
    #run_notebook()
