import csv
import fecfile
import json
import os
import pyopenfec
import random
import requests
import shutil

FILINGS_DIR = 'filings'

def download_filing(file_number):
    if not os.path.exists(FILINGS_DIR):
        os.makedirs(FILINGS_DIR)
    url = 'https://docquery.fec.gov/dcdev/posted/{}.fec'.format(file_number)
    location = '{}/{}.fec'.format(FILINGS_DIR, file_number)
    headers = {'User-Agent': 'Mozilla/5.0'}
    with requests.get(url, stream=True, headers=headers) as r:
        with open(location, 'wb') as f:
            shutil.copyfileobj(r.raw, f)


def cached_file_path(file_number):
    location = '{}/{}.fec'.format(FILINGS_DIR, file_number)
    if not os.path.exists(location):
        print('downloading {}'.format(file_number))
        download_filing(file_number)
    return location


def get_file_numbers(committee_id, cycle):
    comm = pyopenfec.Committee.fetch_one(committee_id=committee_id)
    print(comm.name)
    f3_filings = comm.select_reports(
        cycle=cycle,
        is_amended=False,
    )
    return [r.file_number for r in f3_filings]


def actblue_test():
    file_path = cached_file_path(1344765)
    options = {'filter_itemizations': ['SA'], "as_strings": True}
    num_sch_a = 14272298
    num_sch_all = 25725482
    randos = random.sample(range(num_sch_a), 20)
    i = 0
    r = 0
    for item in fecfile.iter_file(file_path, options=options):
        if item.data_type == 'itemization':
            if i in randos:
                print(json.dumps(item.data, sort_keys=True, indent=2, default=str))
                r += 1
                print(r)
            i += 1
    print(i)


def main():
    with open('candidates.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            filings = get_file_numbers(row['Committee ID'], '2020')
            for filing in filings:
                download_filing(filing)
        actblue_filings = get_file_numbers('C00401224', '2020')
        for filing in actblue_filings:
            download_filing(filing)


if __name__ == '__main__':
    # main()
    actblue_test()
