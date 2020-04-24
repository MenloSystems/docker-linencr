# -*- coding: UTF-8 -*-

import importlib

import openpyxl
import openpyxl.styles
import openpyxl.writer.excel


import csv
import sys

try:
	from StringIO import StringIO  # python 2
except ImportError:
	from io import StringIO  # python 3


class CSVRenderer(object):
	def __init__(self, info):
		pass

	def __call__(self, value, system):
		""" Returns a plain CSV-encoded string with content-type
		``text/csv``. The content-type may be overridden by
		setting ``request.response.content_type``."""

		def py2_unicode_to_str(u):
			# unicode is only exist in python2
			# assert isinstance(u, unicode)
			if (sys.version_info < (3, 0)) and isinstance(u, basestring):
				return u.encode('utf-8')
			else:
				return u

		request = system.get('request')
		if request is not None:
			response = request.response
			ct = response.content_type
			if ct == response.default_content_type:
				response.content_type = 'text/csv'

		fout = StringIO()

		dict_writer = csv.DictWriter(fout, value.get('header', []), dialect=csv.excel, quoting=csv.QUOTE_NONNUMERIC)
		dict_writer.writeheader()

		for row in value.get('rows', []):
			dict_writer.writerow({py2_unicode_to_str(k): py2_unicode_to_str(v) for k, v in row.items()})

		return fout.getvalue()

##################################################################################


class XLSXRenderer(object):
	XLSX_CONTENT_TYPE = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

	def __init__(self, info):
		self.suffix = info.type

	def __call__(self, value, system):

		wb = openpyxl.Workbook()
		ws = wb.active

		# Header
		ws.append(value.get('header', []))
		ws.row_dimensions[1].font = openpyxl.styles.Font(bold=True)

		# Data
		for raw in value.get('rows', []):
			row = [raw[key] for key in value.get('header', [])]
			ws.append(row)

		request = system.get('request')
		if request is not None:
			response = request.response
			ct = response.content_type
			if ct == response.default_content_type:
				response.content_type = XLSXRenderer.XLSX_CONTENT_TYPE
			response.content_disposition = u'attachment;filename={}.xlsx'.format(u"Störereignisse")

		return openpyxl.writer.excel.save_virtual_workbook(wb)
