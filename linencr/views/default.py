#-*- coding: UTF-8 -*-

from pyramid.view import view_config
from redminelib import Redmine
import random
import collections 
import colorhash  
# import colorsys  
import colormap  
import sys  
import traceback  
import datetime  
import math  
# import csv  

from dateutil.relativedelta import relativedelta

from pyramid.httpexceptions import (
    HTTPMovedPermanently,
    HTTPNotFound
    )
	
project_id='ZyTest'

MenRedmine = Redmine('<redacted>', username='<redacted>', password='<redacted>')

custom_fields = []
for cf in MenRedmine.custom_field.all():	
	if cf.customized_type ==  u'issue':

		# print "------------"
		# print cf['id'], cf.name
		# print cf.__dict__
		pvs = []
		if  hasattr(cf,u'possible_values'):
			pvs = cf[u'possible_values']
			
		# print 
		# print 
		# print 
		custom_fields.append({'id':cf['id'], 'name':cf['name'], 'possible_values':pvs} )
# sys.exit()	
	

trackers =  [{'id':t['id'], 'name':t['name']} for t in MenRedmine.tracker.all()	]
# print trackers
tracker_Doku = next(item for item in trackers if item["name"] == u"Problem bereits gelöst")
tracker_Reparatur = next(item for item in trackers if item["name"] == u"Problemlösung erforderlich")
Feld_MeldendeGruppe = next(item for item in custom_fields if item["name"] == u"Meldende Gruppe")
Feld_Baugruppe = next(item for item in custom_fields if item["name"] == u"Baugruppe")
Feld_Fehler = next(item for item in custom_fields if item["name"] == u"Fehlerursache")
Feld_Projektbezug = next(item for item in custom_fields if item["name"] == u"Projektbezug")
Feld_Bauteil = next(item for item in custom_fields if item["name"] == u"Defektes Bauteil")
Feld_VerursachtDurch = next(item for item in custom_fields if item["name"] == u"Verursacht durch")
Feld_Produktgruppe = next(item for item in custom_fields if item["name"] == u"Produktgruppe")
# print tracker_Doku, tracker_Reparatur
# print Feld_MeldendeGruppe
# print Feld_Baugruppe
# sys.exit()
#########################################################################################
def holeGrupen():
	print "holeGrupen..."
	# return [{'name':b, 'id':a, 'nameOrig':":".join([a,b])} for a,b in (x['value'].split(":") for x in MenRedmine.custom_field.get(4).possible_values)]
	
	lis = [{'name':b, 'id':a, 'nameOrig':":".join([a,b])} for a,b in (x['value'].split(":") for x in MenRedmine.custom_field.get(4).possible_values)]
	lis = sorted(lis, key = lambda i: int(i['id']))
	print 
	for h in range(len(lis)):
		lis[h]['SpektrumsFarbe'] = colormap.Color(hsv=(0.90*h/len(lis),1,1)).hex
	return lis
	
#########################################################################################
def Quartale():
	d = datetime.date( datetime.date.today().year+1,1,1)
	d_stop = datetime.date( 2015,1,1)
	day = relativedelta(days=1)
	quarter = relativedelta(months=3)
	ret	= []
	while d>d_stop:
		q_erster = d - quarter
		q_letzter = d - day
		# print q_erster,q_letzter,int(math.ceil(q_erster.month/3)+1)
		# ret.insert(0,
		ret.append(
		{"q_erster":q_erster,"q_erster_str":q_erster.strftime('%Y-%m-%d'),
					"q_letzter":q_letzter,"q_letzter_str":q_letzter.strftime('%Y-%m-%d'),
					'Quartal':int(math.ceil(q_erster.month/3)+1),
					'Jahr':q_erster.year})
		d -= quarter
	return ret

#########################################################################################
#########################################################################################

# Gruppen = holeGrupen()
# gruppe = next(item for item in Gruppen if item["id"] == request.matchdict['Linie'])
# gruppe = next(item for item in Gruppen if item["id"] == 1)
# sys.exit()
	
# print [{'name':b, 'id':int(a)} for a,b in (x['value'].split(":") for x in MenRedmine.custom_field.get(4).possible_values)]	
# redmine_Fehlerursachen = 
# @view_config(route_name='home', renderer='../templates/mytemplate.pt')
# def my_view(request):
    # return {'project': 'LineNCR'}

kelly_colors = ['222222', 'F3C300', '875692', 'F38400', 'A1CAF1', 'BE0032', 'C2B280', '848482', '008856', 'E68FAC', '0067A5', 'F99379', '604E97', 'F6A600', 'B3446C', 'DCD300', '882D17', '8DB600', '654522', 'E25822', '2B3D26','F2F3F4']
FehlerursachenCodes = ["01","02","03","04","05","06","07","08","09","10","11","99"]
Fehlerursachenfarben = {code:farbe for code,farbe in zip (FehlerursachenCodes,kelly_colors)}
Gewichte = collections.defaultdict(lambda:100)

Gewichte.update({'06.1':900, '01.2':600, '07.2':600, '07.3':400})
print Gewichte

#########################################################################################
# Startseite
@view_config(route_name='home', renderer='../templates/Start.pt')
def my_view(request):
	# Gruppen = []
	# users = []
	# for user in list(redmine_users.values()):
		# users.append(user['firstname'])
	# Fehlerursachen = [{'name':x[u"value"], 'farbe':Fehlerursachenfarben[x[u"value"][0:2]], 'gewicht':Gewichte[x[u"value"][0:4]]} for x in MenRedmine.custom_field.get(5).possible_values]
	Gruppen = holeGrupen()
	Qs = Quartale()

	return {'Gruppen': Gruppen,'Quartale': Qs}
ncrid = 2222 # Debug
#########################################################################################
# # Produktiionslinie Meldung Fertig
@view_config(route_name='MenLineMeldungFertig', renderer='../templates/MenLineMeldungFertig.pt')
def my_view_testpage2(request):
	# global ncrid # Debug
	Gruppen = holeGrupen()
	try:
		gruppe = next(item for item in Gruppen if item["id"] == request.matchdict['Linie'])
	except:
		return HTTPNotFound(u"Die Gruppen-ID '{}' ist ungültig.".format(request.matchdict['Linie']))
	
	# in Redmine Ticket anlegen:
	
	# Projektbezug = request.params[u'Projektbezug']
	Projektbezug_Gattung = request.params[u'Projektbezug_Gattung']
	Projektbezug_AU = request.params[u'Projektbezug_AU']
	Projektbezug_PA = request.params[u'Projektbezug_PA']
	Projektbezug_Projekt = request.params[u'Projektbezug_Projekt']
	pData = {'KanBan':Projektbezug_PA,'AU':Projektbezug_AU,'Projekt':Projektbezug_Projekt}
	pTemp = {'KanBan':"{KanBan}",'AU':"{AU}",'Projekt':"{Projekt}",'NA':"-"}
	Projektbezug = pTemp[Projektbezug_Gattung].format(**pData)#
	# print Projektbezug
	
	
	Baugruppe_Gattung = request.params[u'Baugruppe_Gattung']
	Baugruppe_Baugruppe = request.params[u'Baugruppe_Baugruppe']
	bData = {'Baugruppe':Baugruppe_Baugruppe}
	bTemp = {'Baugruppe':"{Baugruppe}",'unbekannt':"-"}
	Baugruppen = bTemp[Baugruppe_Gattung].format(**bData)#
	# print Baugruppen
	
	FehlerGruppe = request.params[u'FehlerGruppe']
	# print FehlerGruppe, [x for x in request.params.keys() if x.startswith('FehlerGruppe_')]
	Fehler = request.params[FehlerGruppe]
	# print Fehler

	
	# Baugruppen = request.params[u'Baugruppe']
	Thema = request.params[u'Thema']
	Beschreibung = request.params[u'Beschreibung']
	# print "Projektbezug",Projektbezug
	# Fehler = request.params[u'Fehler']
	Bauteil = request.params[u'Bauteil']
	if Bauteil == "-":
		Bauteil = ""
	
	Zeit = float(request.params[u'Zeit'])
	Reparaturauftrag = u'Reparaturauftrag' in request.params
	Sonderfreigabe = u'Sonderfreigabe' in request.params
	
	Verursacht_Gattung = request.params[u'Verursacht_Gattung']
	if "Verursacht_Gruppe" in request.params:
		Verursacht_Gruppe = request.params[u'Verursacht_Gruppe']
	else:
		Verursacht_Gruppe = None
	Verursacht_Kreditor = request.params[u'Verursacht_Kreditor']
	Verursacht_Hersteller = request.params[u'Verursacht_Hersteller']
	vData = {'Gruppe':Verursacht_Gruppe,'Kreditor':Verursacht_Kreditor,'Hersteller':Verursacht_Hersteller}
	vTemp = {'Gruppe':"Gruppe:{Gruppe}",'Kreditor':"Kreditor:{Kreditor}",'Hersteller':"Hersteller:{Hersteller}",'unbekannt':"unbekannt"}
	VerursachtDurch = vTemp[Verursacht_Gattung].format(**vData)
	
	if Reparaturauftrag or Sonderfreigabe:
		tracker_id = tracker_Reparatur['id']
	else:
		tracker_id = tracker_Doku['id']

		
	custom_fields = [
					{'id': Feld_MeldendeGruppe['id'], 'value': gruppe['nameOrig']},
					{'id': Feld_Fehler['id'], 'value': Fehler},
					{'id': Feld_VerursachtDurch['id'], 'value': VerursachtDurch},
					{'id': Feld_Projektbezug['id'], 'value': Projektbezug},
					{'id': Feld_Baugruppe['id'], 'value': Baugruppen},
					{'id': Feld_Bauteil['id'], 'value': Bauteil},
					{'id': Feld_Produktgruppe['id'], 'value': "N/A"}
					]
	# print custom_fields
	
	try:
		if True:
			
			issue = MenRedmine.issue.new()
			issue.project_id = project_id
			issue.tracker_id = tracker_id
			issue.subject = Thema
			issue.description = Beschreibung
			issue.custom_fields = custom_fields
			if Sonderfreigabe:
				issue.status_id = 8
			# issue.watcher_user_ids=[14]
			issue.save()
			ncrid = issue['id']
			
			if Sonderfreigabe:
				MenRedmine.issue.update(ncrid, notes='Um Sonderfreigabe wird gebeten.\n\nZur Bewilligung das Feld *Status* von "Ungelöst" -> "Erledigt" setzen.')
			
			time_entry = MenRedmine.time_entry.new()
			time_entry.activity_id = 24 # "Lösung"
			time_entry.issue_id = ncrid
			time_entry.spent_on = datetime.date.today()
			time_entry.hours = Zeit
			time_entry.comments = 'aus Formular'
			time_entry.save()
		else:
			ncrid = None
	except:
		print traceback.format_exc()
		ncrid = None
		
	# Antwortseite:
	gruppe.update({'farbe':colorhash.ColorHash(gruppe['name'],lightness=(0.85,0.9,0.95), saturation=(0.25, 0.35, 0.5, 0.65, 0.75)).hex})
	# print gruppe
	# ncrid += 1 # Debug
	return {'Gruppe': gruppe, 'NCRID':ncrid}


#########################################################################################
# Produktiionslinie Meldung
# @view_config(route_name='MenLineMeldungFertig', renderer='../templates/MenLineMeldungFertig.pt')
@view_config(route_name='MenLineMeldung', renderer='../templates/MenLineMeldung.pt')
def my_view_testpage(request):
		
	redmine_users = MenRedmine.user.all()
	users = []
	for user in list(redmine_users.values()):
		users.append(user['firstname'])
		
	Fehlerursachen = [{'name':x[u"value"], 'farbe':Fehlerursachenfarben[x[u"value"][0:2]], 'gewicht':Gewichte[x[u"value"][0:4]]} for x in MenRedmine.custom_field.get(5).possible_values]
	
	# for x in MenRedmine.custom_field.get(5).possible_values:
		# print x[u"value"][0:2], x[u"value"][0:4], x[u"value"]
		
	FehlerursachenGruppen = [
	{'txt':'Information und Vorgehen', 'name':'FehlerGruppe_Information_und_Vorgehen', 'Fehlerursachen':[x for x in Fehlerursachen if x[u"name"][0:2] in ['01', '02']]},
	{'txt':'Herstellungsschritte und Lager', 'name':'FehlerGruppe_Herstellungsschritte', 'Fehlerursachen':[x for x in Fehlerursachen if x[u"name"][0:2] in ['03', '05', '06', '07']]},
	{'txt':'Defekte', 'name':'FehlerGruppe_Defekte', 'Fehlerursachen':[x for x in Fehlerursachen if x[u"name"][0:2] in ['04']]},
	{'txt':'Organisation und Sonstiges', 'name':'FehlerGruppe_Organisation_und_Sonstiges', 'Fehlerursachen':[x for x in Fehlerursachen if x[u"name"][0:2] in ['08', '09', '99']]},
	{'txt':'Alle', 'name':'FehlerGruppe_Alle', 'Fehlerursachen':Fehlerursachen}
	]
		
	Gruppen = holeGrupen()
	try:
		gruppe = next(item for item in Gruppen if item["id"] == request.matchdict['Linie'])
	except:
		return HTTPNotFound(u"Die Gruppen-ID '{}' ist ungültig.".format(request.matchdict['Linie']))
	gruppe.update({'farbe':colorhash.ColorHash(gruppe['name'],lightness=(0.85,0.9,0.95), saturation=(0.25, 0.35, 0.5, 0.65, 0.75)).hex})
	print gruppe
	return {'Gruppe': gruppe, 'Gruppen': Gruppen, 'Nutzer': users, 'Fehlerursachen':Fehlerursachen, 'FehlerursachenGruppen':FehlerursachenGruppen}

	
#########################################################################################
#########################################################################################
#########################################################################################
#[u'attachments', u'author', u'changesets', u'children', u'created_on', u'custom_fields', u'description', u'done_ratio', u'id', u'journals', u'priority', u'project', u'relations', u'status', u'subject', u'time_entries', u'tracker', u'updated_on', u'watchers']

# Rohdaten
@view_config(route_name='Rohdaten', renderer='csv')
def Rohdaten(request):
	project_id='e-bu-ncr-tracker'
	project_id='ZyTest'
	StartDatumStr = "{}-{}-{}".format(request.matchdict['StartJahr'],request.matchdict['StartMonat'],request.matchdict['StartTag'])
	StoppDatumStr = "{}-{}-{}".format(request.matchdict['StoppJahr'],request.matchdict['StoppMonat'],request.matchdict['StoppTag'])
	
	issues = MenRedmine.issue.filter(project_id=project_id,created_on='><{}|{}'.format(StartDatumStr,StoppDatumStr), status_id = "*")
	# x = [u'author', u'changesets', u'created_on', u'custom_fields', u'description', u'id', u'project', u'status', u'subject', u'time_entries', u'tracker', u'updated_on']
	x = [u'author', u'created_on', u'description', u'id', u'project', u'status', u'subject', u'tracker', u'updated_on']
	x = [u'author', u'created_on', u'id', u'status', u'subject', u'tracker', u'updated_on']
	y = [u'custom_fields', u'time_entries']
	
	rows = []
	for issue in issues:
		print issue.url
		d = {k: u"{}".format(issue[k]) for k in x}
		# issue.export('pdf', savepath='/home/hschmitz/test/loeschen')
		if hasattr(issue, u'assigned_to'):
				d[u'assigned_to'] = issue.assigned_to.id
		if hasattr(issue, u'custom_fields'):
			for cf in issue[u'custom_fields']:
				d[cf.name] = u"{}".format(cf.value)
		total_duration = 0
		#Todo: Sobald eine neue Version vom RM verfügbar ist, issue."spent_hours" auswerten!
		if hasattr(issue, u'time_entries'):
			for time_entry in issue[u'time_entries']:
				total_duration += time_entry.hours
		d[u'total_duration'] = total_duration
		print d['id']
		print 
		# print 
		# keys = d[0].keys()
		if d['status'] != "Abgewiesen":
			rows.append(d) 
	# return HTTPNotFound(u"OK")
	if rows:
		header =  rows[0].keys()
	else:
		header = ['First Name', 'Last Name']
		# rows = [["A","b"]]
		rows = [{'First Name':"A",'Last Name':"b"},{'First Name':"C",'Last Name':"d"},{'First Name':"sfhkjsfd",'Last Name':"wetk."}]
	
	filename = u'NCR-Ereignisse_{}_{}.csv'.format(StartDatumStr,StoppDatumStr)
	request.response.content_disposition = 'attachment;filename=' + filename
	
	return {
		'header': header,
		'rows': rows,
		}
#########################################################################################
#########################################################################################
#########################################################################################
#[u'attachments', u'author', u'changesets', u'children', u'created_on', u'custom_fields', u'description', u'done_ratio', u'id', u'journals', u'priority', u'project', u'relations', u'status', u'subject', u'time_entries', u'tracker', u'updated_on', u'watchers']

# Rohdaten Excel
@view_config(route_name='RohdatenExcel', renderer='xlsx')
def Rohdaten2(request):
	project_id='e-bu-ncr-tracker'
	project_id='ZyTest'	
	StartDatumStr = "{}-{}-{}".format(request.matchdict['StartJahr'],request.matchdict['StartMonat'],request.matchdict['StartTag'])
	StoppDatumStr = "{}-{}-{}".format(request.matchdict['StoppJahr'],request.matchdict['StoppMonat'],request.matchdict['StoppTag'])
	
	issues = MenRedmine.issue.filter(project_id=project_id,created_on='><{}|{}'.format(StartDatumStr,StoppDatumStr), status_id = "*")
	# x = [u'author', u'changesets', u'created_on', u'custom_fields', u'description', u'id', u'project', u'status', u'subject', u'time_entries', u'tracker', u'updated_on']
	x = [u'author', u'created_on', u'description', u'id', u'project', u'status', u'subject', u'tracker', u'updated_on']
	x = [u'author', u'created_on', u'id', u'status', u'subject', u'tracker', u'updated_on']
	y = [u'custom_fields', u'time_entries']
	
	rows = []
	for issue in issues:
		print issue.url
		d = {k: u"{}".format(issue[k]) for k in x}
		# issue.export('pdf', savepath='/home/hschmitz/test/loeschen')
		if hasattr(issue, u'assigned_to'):
				d[u'assigned_to'] = issue.assigned_to.id
		if hasattr(issue, u'custom_fields'):
			for cf in issue[u'custom_fields']:
				d[cf.name] = u"{}".format(cf.value)
		total_duration = 0
		#Todo: Sobald eine neue Version vom RM verfügbar ist, issue."spent_hours" auswerten!
		if hasattr(issue, u'time_entries'):
			for time_entry in issue[u'time_entries']:
				total_duration += time_entry.hours
		d[u'total_duration'] = total_duration
		print d['id']
		print 
		# print 
		# keys = d[0].keys()
		if d['status'] != "Abgewiesen":
			rows.append(d) 
	# return HTTPNotFound(u"OK")
	if rows:
		header =  rows[0].keys()
	else:
		header = ['First Name', 'Last Name']
		# rows = [["A","b"]]
		rows = [{'First Name':"A",'Last Name':"b"},{'First Name':"C",'Last Name':"d"},{'First Name':"sfhkjsfd",'Last Name':"wetk."}]
	
	filename = u'NCR-Ereignisse_{}_{}.csv'.format(StartDatumStr,StoppDatumStr)
	request.response.content_disposition = 'attachment;filename=' + filename
	
	return {
		'header': header,
		'rows': rows,
		}		
