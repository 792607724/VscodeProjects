# coding = utf8
import os

import openpyxl

os.path.abspath(".")
"""
    @File:pdfExcelAnalysis.py
    @Author:Bruce
    @Date:2022/3/29
"""
# coding = utf8

import os

import pandas as pd

os.path.abspath(".")

import pdfplumber


def readPDF_text(pdf_file="./Mac os极简用法及设置.pdf"):
    page_content = []
    with pdfplumber.open(pdf_file) as pdf:
        pdf_pages = pdf.pages
        for i in range(0, len(pdf_pages)):
            cur_page = pdf_pages[i]
            cur_page_content = cur_page.extract_text().strip()
            print("==========当前页面【{}】的文字内容是：==========\n\n{}\n".format(str(i + 1), cur_page_content))
            page_content.append(cur_page_content)
    if page_content:
        return page_content
    else:
        return 0


def toTxt(result):
    with open("./Result.txt", "a+", encoding="utf-8") as f:
        f.write(result + "\n")


# 从excel中读取数据并返回(element)
def read_excel_for_page_element(form="./page_sheet.xlsx", sheet_name="calendar_page"):
    df = pd.read_excel(form, sheet_name=sheet_name, index_col="element_number", engine="openpyxl")
    data_list = []
    print(df.shape[0])
    for i in range(1, df.shape[0] + 1):
        original_data = df.loc[i, "element_data"]
        data_list.append([i, original_data])
    return data_list


def write_into_excel(form="./page_sheet.xlsx", sheet_name="calendar_page", row=1, column=5, value="PASS"):
    wb = openpyxl.load_workbook(form)
    ws = wb[sheet_name]
    ws.cell(row + 1, column).value = value
    wb.save(form)


if __name__ == '__main__':
    # pdf_file = "./AndroidTool_Guide.pdf"
    # pdf_contents = readPDF_text(pdf_file)
    # for pdfContent in pdf_contents:
    #     toTxt(pdfContent)
    print(read_excel_for_page_element())
    write_into_excel()
