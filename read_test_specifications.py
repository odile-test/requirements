#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#        Copyright (c) IRAP CNRS
#        Odile Coeur-Joly, Toulouse, France
#
"""
1. Open it Test-Procedure.docx document and read the tables.
2. Convert from WORD to EXCEL ==> 0065-Requirements.xlsx file
3. convert from EXCEL to CSV ==> 0065-Requirements.csv file
4. convert from CSV to XML ==> 0065-Requirements.xml file
"""
from docx.api import Document
import os

docname = '0065-Requirements'
workdir = os.path.abspath(os.getcwd())
filename = os.path.join(workdir + os.sep + 'data' + os.sep + docname)

document = Document(filename + '.docx')

"""
1. Open .docx document and read the tables.
"""

reqTabs = []

# Select only the tables containing requirements
for tab in document.tables:
    for col in tab.columns:        
        for cell in col.cells:
                if cell.text.find("XIFU-DRE"):
                    continue
                else:
                    reqTabs.append(tab)

print("len=", len(reqTabs))

# Extract keys from first requirement Table (i=0) and first column (j=0)
# Extract values from second column of requirement Table (j=1)
# CAUTION : to be adapted to every doc template

data = []
content = []
# Select the 2 columns needed: first = keys, second = values
for i, tab in enumerate(reqTabs):
    for j, col in enumerate(tab.columns):        
        if i == 0 and j == 0:
            text = (cell.text for cell in col.cells)
            text = (cell.text.replace('Reference:', 'docid').replace('Title:', 'title').replace('Description:', 'description') for cell in col.cells)
            keys = tuple(text)
            data.append(list(keys))
            continue
        if j == 1:
            # for XML conversion: < and > are not allowed in text
            content = (cell.text.replace('<', 'inferior to').replace('>', 'superior to') for cell in col.cells)
            row_data = dict(zip(keys, content))
            data.append(list(row_data.values()))

"""
2. Convert to EXCEL
"""
# Write requirements in an Excel file
import xlsxwriter

workbook = xlsxwriter.Workbook(filename + '.xlsx')
worksheet1 = workbook.add_worksheet("All Data")
worksheet2 = workbook.add_worksheet("3 columns")

# First spreadsheet1: write all.
for row, row_data in enumerate(data):
    worksheet1.write_row(row, 0, row_data)

# Reorg data in spreadsheet2: suppress, add columns
import numpy as np

data2 = np.array(data)
data2 = data2[:,[1, 0, 2]]

for row, row_data in enumerate(data2):
    worksheet2.write_row(row, 0, row_data)

workbook.close()

"""
3. convert to CSV
"""
# Try the Pandas package
import pandas as pd
df = pd.DataFrame(data2)

read_file = pd.read_excel(filename + '.xlsx', sheet_name='3 columns')
read_file.to_csv(filename + '.csv', index = None, header=True)

"""
4. convert to XML
"""
# Convert from csv o XML
df = pd.read_csv(filename + '.csv')

def to_xml(df, filename=None, mode='w'):
    def row_to_xml(row):
        xml = ['<requirement>']
        for i, col_name in enumerate(row.index):
            xml.append('  <{0}>{1}</{0}>'.format(col_name, row.iloc[i]))
        xml.append('</requirement>')
        return '\n'.join(xml)
    
    res = '<requirements>' + '\n' + '\n'.join(df.apply(row_to_xml, axis=1)) + '\n' + '</requirements>'
     
    if filename is None:
        return res
    # do NOT use "with open"  otherwise encoding is impossible
    f = open(filename, 'w', encoding='utf-8')
    f.write(res)
    f.close()
 
pd.DataFrame.to_xml = to_xml
df.to_xml(filename + '.xml')
