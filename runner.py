from decimal import Decimal

import json
import sys
import time
import traceback

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import chromedriver_autoinstaller

import xlsxwriter

##
#
# This is the runner to automatically calculate spectral periods for a given set of input data.
#
##

#
# https://realpython.com/installing-python/#step-1-download-the-python-3-installer
#

BASE_URL = 'https://earthquake.usgs.gov/designmaps/rtgm/'

print('\nStarting...\n')

# init webdriver
chromedriver_autoinstaller.install()
driver = webdriver.Chrome()
driver.get(BASE_URL)
driver.maximize_window()

# open data file
with open('raw_data.json') as fp:
    data = json.load(fp)

# set up excel workbook and worksheet
workbook = xlsxwriter.Workbook('temp_site_specific_seismic.xlsx')
worksheet = workbook.add_worksheet()
row = 1
col = 'A'

spectral_periods = [0.0, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0, 2.0, 3.0, 4.0, 5.0]

print('Calculating values...\n')

for x in range(11):

    try:

        header = 'SPECTRAL PERIOD {}'.format(spectral_periods[x])
        print(header)

        worksheet.write('{}{}'.format(col, row), header)
        row += 1

        x_vals = [str(i) for i in data['response'][x]['metadata']['xvalues']]
        y_vals = [str(i) for i in data['response'][x]['data'][0]['yvalues']]
        assert (len(x_vals) == len(y_vals))

        # Note: this is checking for continuous entries of 0.0, but does not account for multiple of other numbers
        flag = 0
        for i in reversed(range(len(y_vals))):
            # we can break early once the value is greater than zero
            if Decimal(y_vals[i]) > Decimal('0'):
                break
            # set the flag on the first occurence of zero
            if Decimal(y_vals[i]) == Decimal('0') and flag == 0:
                flag += 1
                continue
            # handle the case where there are multiple entries of zero
            if Decimal(y_vals[i]) == Decimal('0') and flag >= 1:
                flag += 1
                # strikethrough
                y_vals[i + 1] = ''.join([u'\u0336{}'.format(c) for c in y_vals[i + 1]])
                x_vals[i + 1] = ''.join([u'\u0336{}'.format(c) for c in x_vals[i + 1]])

        if flag > 1:
            print('X VALUES: {} (modified) \nY VALUES: {} (modified)\n'.format(x_vals, y_vals))
        else:
            print('X VALUES: {}\nY VALUES: {}\n'.format(x_vals, y_vals))

        # curve title
        rtgm_title_inputElement = driver.find_element_by_id('rtgm-input-view-0-title')
        rtgm_title_inputElement.clear()
        rtgm_title_inputElement.send_keys('Spectral Period: {}'.format(spectral_periods[x]))

        end = len(x_vals) - (flag - 1)

        # spectral response acceleration values (x vals)
        rtgm_sa_vals_inputElement = driver.find_element_by_id('rtgm-input-view-0-sa')
        rtgm_sa_vals_inputElement.clear()
        rtgm_sa_vals_inputElement.send_keys(', '.join(x_vals[:end]))

        # annual frequency of exceedence values (y vals)
        rtgm_afe_vals_inputElement = driver.find_element_by_id('rtgm-input-view-0-afe')
        rtgm_afe_vals_inputElement.clear()
        rtgm_afe_vals_inputElement.send_keys(', '.join(y_vals[:end]))

        # compute button
        rtgm_compute_button = driver.find_element_by_id('rtgm-input-view-0-compute')
        rtgm_compute_button.click()

        # Note: need to go x + 2 for the index since it's not zero-based and the page starts with
        #       an existing entry
        vals = [
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                (By.XPATH, '/html/body/main/div/div/div[2]/ul/li[{}]/dl/dd[1]'.format(x + 2)))
            ).text,
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                (By.XPATH, '/html/body/main/div/div/div[2]/ul/li[{}]/dl/dd[2]'.format(x + 2)))
            ).text,
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                (By.XPATH, '/html/body/main/div/div/div[2]/ul/li[{}]/dl/dd[3]'.format(x + 2)))
            ).text
        ]

        # TODO: is this necessary?
        time.sleep(.5)

        # write data to workbook
        worksheet.write('{}{}'.format(col, row), 'x_vals: {}'.format(x_vals[:end]))
        row += 1
        worksheet.write('{}{}'.format(col, row), 'y_vals: {}'.format(y_vals[:end]))
        row += 1
        worksheet.write('{}{}'.format(col, row), 'UHGM: {}'.format(vals[0]))
        row += 1
        worksheet.write('{}{}'.format(col, row), 'RTGM: {}'.format(vals[1]))
        row += 1
        worksheet.write('{}{}'.format(col, row), 'RC: {}'.format(vals[2]))
        row += 2

    except Exception as ex:

        # print('Error... {}'.format(ex))
        try:
            exc_info = sys.exc_info()
        finally:
            traceback.print_exception(*exc_info)
            del exc_info
            sys.exit(1)

# not going to close the driver in case we want to keep the web page open to verify
# driver.close()
workbook.close()

print('Success...')
