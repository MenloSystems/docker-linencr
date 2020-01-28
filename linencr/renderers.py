#-*- coding: UTF-8 -*-

import importlib

import openpyxl
import openpyxl.styles
import openpyxl.writer.excel


import csv

try:
    from StringIO import StringIO # python 2
except ImportError:
    from io import StringIO # python 3

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
			if isinstance(u, basestring):
				return u.encode('utf-8')#.replace(",", "_")
			else:
				return u
		request = system.get('request')
		if request is not None:
			response = request.response
			ct = response.content_type
			if ct == response.default_content_type:
				response.content_type = 'text/csv'

		fout = StringIO()
		# writer = csv.writer(fout, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

		# writer.writerow(value.get('header', []))
		# writer.writerows(value.get('rows', []))

		# print value.get('rows', [])
		dict_writer = csv.DictWriter(fout, value.get('header', []), dialect=csv.excel, quoting=csv.QUOTE_NONNUMERIC)
		dict_writer.writeheader()
		# dict_writer.writerows(value.get('rows', []))
		for row in value.get('rows', []):
			dict_writer.writerow({py2_unicode_to_str(k):py2_unicode_to_str(v) for k,v in row.items()})

		return fout.getvalue()

##################################################################################
		
class XLSXRenderer(object):
    XLSX_CONTENT_TYPE = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    def __init__(self, info):
        self.suffix = info.type
        self.templates_pkg = info.package.__name__ + ".xlsx"

    def __call__(self, value, system):
	
        def get_header(system, value):
        	# value is the dictionary returned from the view
        	# request = system["request"]
        	# context = system["context"]
        	return ["Row number", "A number", "A string"]

        def iterate_rows(system, value):
        	for row in range(100):
        		return [row, 100, "A string"]	
	
        templ_name = system["renderer_name"][:-len(self.suffix)]
        templ_module = importlib.import_module("." + templ_name, self.templates_pkg)
        wb = openpyxl.Workbook()
        ws = wb.active
        if "get_header" in dir(templ_module):
            ws.append(getattr(templ_module, "get_header")(system, value))
            ws.row_dimensions[1].font = openpyxl.styles.Font(bold=True)
        if "iterate_rows" in dir(templ_module):
            for row in getattr(templ_module, "iterate_rows")(system, value):
                ws.append(row)

        request = system.get('request')
        if not request is None:
            response = request.response
            ct = response.content_type
            if ct == response.default_content_type:
                response.content_type = XLSXRenderer.XLSX_CONTENT_TYPE
            response.content_disposition = 'attachment;filename=%s.xlsx' % templ_name

        return openpyxl.writer.excel.save_virtual_workbook(wb)		