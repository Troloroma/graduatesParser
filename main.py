import os


def run_notebook():
    os.system("pip install jupyter")
    os.system("jupyter nbconvert --to notebook --execute analytics.ipynb")


if __name__ == '__main__':
    #parse_from_csv_to_db()
    run_notebook()
