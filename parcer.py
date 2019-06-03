"""
Date > 01.05.2018
Certificate No =  G2S 097364 0007 Rev. 00
Company name = Kingstar Medical (Xianning) Co., LTD
Example link: https://sce.tuv-sud.com/sce?id=7ka10
"""

import datetime
import json
import re
import time

import requests
from bs4 import BeautifulSoup


class TUVSUD:
    def __init__(self):
        with open('companydata.json', 'r') as f:
            self.data = json.load(f)

    def find(self, company_name):
        """
        Find id of the company.
        :param company_name: name of the company.
        :return:
        """
        counter = 1
        skips = 0
        found = False
        for id_generated in self.id_generator():
            # Skip 6 if found if last one was a find.
            if skips == 6:
                found = False
                skips = 0

            if found:
                skips += 1
                print(f'Skip #{skips}. Skipping {id_generated}.')
                continue
                        
            # Try to go for the latest id.
            if list(reversed(sorted(self.data.keys())))[0] >= id_generated:
                continue
            
            # Get the page
            response = requests.get(f'https://sce.tuv-sud.com/sce?id={id_generated}')
            soup = BeautifulSoup(response.text, "lxml")

            # If the server is unreachable, save and quit
            if response.status_code == 500:
                print(f'Server unreachable. Exiting.')
                break

            # Check if the id has a company related to it.
            if soup.text.find('The scanned code did not return any valid certificate') != -1:
                print(f'#{counter} - Entry not found, id = {id_generated}')
                self.data[id_generated] = 'empty'
            else:
                found = True
                # If yes, get company name, date of issue, certificate number
                # Company name
                end = str(soup.find_all('li')[2].find_all('p')[1])[17:].find('<br/>')
                company_found = str(soup.find_all('li')[2].find_all('p')[1])[17:17 + end]
                # Certificate number
                cert_number = str(soup.find_all('li')[0].find_all('p')[1])[17:][:-4]
                # Date
                date = sorted(re.findall("[\d]{4}-[\d]{2}-[\d]{2}", str(soup.body)))[0]

                # Print full info
                print(f'#{counter} - Entry found, id = {id_generated}, company name = {company_found}, '
                      f'date of issue = {date}, certificate number = {cert_number}')

                # Clean up the unneeded, old empty ones, as the latest now is the company.
                for idNumber in list(self.data):
                    if self.data[idNumber] == 'empty':
                        self.data.pop(idNumber)

                # Output the company data into a dictionary
                self.data[id_generated] = {
                    'company_name': company_found,
                    'certificate_number': cert_number,
                    'date': date
                    }

                # If the right company, print bingo.
                if company_name == company_found:
                    print(f'#{counter} - Bingo!')
                    self.data[id_generated]['bingo'] = True

            # Flush at the end.
            self.write_to_file()

            # Wait to not timeout
            time.sleep(10)
            counter += 1

    def id_generator(self):
        """
        Generate query for the id format is 7LLNN, where L is letter, N is number.
        :return: query id
        """
        for q1 in 'klmnopqrstuvwxyz0123456789':
            for q2 in 'abcdefghijklmnopqrstuvwxyz':
                for q3 in 'abcdefghijklmnopqrstuvwxyz':
                    for q4 in '0123456789abcdefghijklmnopqrstuvwxyz':
                        yield f"7{q1}{q2}{q3}{q4}"

    def write_to_file(self):
        """
        Write to file, write to backup if to file fails.
        :return:
        """
        try:
            # Write to original file
            with open('companydata.json', 'w') as file:
                json.dump(self.data, file, indent=4)
                file.flush()
        except:
            # Write to backup
            print('Error occured. Writing to a different file backupfile.json.')
            with open('backupfile.json', 'w') as backupfile:
                json.dump(self.data, backupfile, indent=4)
                backupfile.flush()


while True:
    TUVSUD().find('Kingstar Medical (Xianning) Co., LTD')
    # Wait if a problem with connection arises
    print(
        f'Retrying at {str((datetime.datetime.now() + datetime.timedelta(minutes=35)))[11:19]} when the server is up.')
    time.sleep(2100)
