# -*- coding: UTF-8 -*-

from pyramid.view import view_config
from redminelib import Redmine
import random
import collections
import colorhash
import colormap
import traceback
import datetime
import math

from dateutil.relativedelta import relativedelta

from pyramid.httpexceptions import (
    HTTPMovedPermanently,
    HTTPNotFound
)

from ..config import Config

project_id = Config['project_id']

MenRedmine = Redmine(
    Config['private_url'],
    username=Config['username'], password=Config['password'],
    requests={'verify': False}
)

custom_fields = []
for cf in MenRedmine.custom_field.all():
    if cf.customized_type == 'issue':

        pvs = []
        if hasattr(cf, 'possible_values'):
            pvs = cf['possible_values']

        custom_fields.append(
            {'id': cf['id'], 'name': cf['name'], 'possible_values': pvs}
        )


trackers = [
    {'id': t['id'], 'name': t['name']} for t in MenRedmine.tracker.all()
]

tracker_Doku = next(item for item in trackers if item["name"] == "Meldung")
tracker_Reparatur = next(item for item in trackers if item["name"] == "Reparatur")
Feld_MeldendeGruppe = next(item for item in custom_fields if item["name"] == "Meldende Gruppe")
Feld_Baugruppe = next(item for item in custom_fields if item["name"] == "Baugruppe")
Feld_Fehler = next(item for item in custom_fields if item["name"] == "Fehlerursache")
Feld_Projektbezug = next(item for item in custom_fields if item["name"] == "Projektbezug")
Feld_Bauteil = next(item for item in custom_fields if item["name"] == "Defektes Bauteil")
Feld_VerursachtDurch = next(item for item in custom_fields if item["name"] == "Verursacht durch")
Feld_Produktgruppe = next(item for item in custom_fields if item["name"] == "Produktgruppe")


#########################################################################################


def holeGrupen():
    print("holeGrupen...")

    lis = [
        {'name': b, 'id': a, 'nameOrig': ":".join([a, b])}
        for a, b in (x['value'].split(":") for x in MenRedmine.custom_field.get(4).possible_values)
    ]
    lis = sorted(lis, key=lambda i: int(i['id']))

    for h in range(len(lis)):
        lis[h]['SpektrumsFarbe'] = colormap.Color(hsv=(0.90 * h / len(lis), 1, 1)).hex
    return lis


#########################################################################################


def Quartale():
    d = datetime.date(datetime.date.today().year + 1, 1, 1)
    d_stop = datetime.date(2015, 1, 1)
    day = relativedelta(days=1)
    quarter = relativedelta(months=3)
    ret = []
    while d > d_stop:
        q_erster = d - quarter
        q_letzter = d - day
        ret.append(
            {
                "q_erster": q_erster,
                "q_erster_str": q_erster.strftime('%Y-%m-%d'),
                "q_StartJahr": q_erster.strftime('%Y'),
                "q_StartMonat": q_erster.strftime('%m'),
                "q_StartTag": q_erster.strftime('%d'),
                "q_StoppJahr": q_letzter.strftime('%Y'),
                "q_StoppMonat": q_letzter.strftime('%m'),
                "q_StoppTag": q_letzter.strftime('%d'),
                "q_letzter": q_letzter,
                "q_letzter_str": q_letzter.strftime('%Y-%m-%d'),
                #~ 'Quartal': int(math.ceil(q_erster.month / 3) + 1),
                'Quartal': int(math.ceil(q_erster.month / 3) + 0),
                'Jahr': q_erster.year
            }
        )
        d -= quarter
    return ret

#########################################################################################
#########################################################################################


kelly_colors = ['222222', 'F3C300', '875692', 'F38400', 'A1CAF1', 'BE0032', 'C2B280', '848482', '008856', 'E68FAC', '0067A5', 'F99379', '604E97', 'F6A600', 'B3446C', 'DCD300', '882D17', '8DB600', '654522', 'E25822', '2B3D26', 'F2F3F4']
FehlerursachenCodes = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "99"]
Fehlerursachenfarben = {code: farbe for code, farbe in zip(FehlerursachenCodes, kelly_colors)}
Gewichte = collections.defaultdict(lambda: 100)

Gewichte.update({'06.1': 900, '01.2': 600, '07.2': 600, '07.3': 400})
print(Gewichte)

#########################################################################################
# Startseite


@view_config(route_name='home', renderer='../templates/Start.pt')
def my_view(request):
    Gruppen = holeGrupen()
    Qs = Quartale()

    return {'Gruppen': Gruppen, 'Quartale': Qs}


#########################################################################################
# # Produktiionslinie Meldung Fertig


@view_config(route_name='MenLineMeldungFertig', renderer='../templates/MenLineMeldungFertig.pt')
def my_view_testpage2(request):
    Gruppen = holeGrupen()
    try:
        gruppe = next(item for item in Gruppen if item["id"] == request.matchdict['Linie'])
    except:
        return HTTPNotFound("Die Gruppen-ID '{}' ist ungültig.".format(request.matchdict['Linie']))

    # in Redmine Ticket anlegen:

    Projektbezug_Gattung = request.params['Projektbezug_Gattung']
    Projektbezug_AU = request.params['Projektbezug_AU']
    Projektbezug_PA = request.params['Projektbezug_PA']
    Projektbezug_Projekt = request.params['Projektbezug_Projekt']
    pData = {'KanBan': Projektbezug_PA, 'AU': Projektbezug_AU, 'Projekt': Projektbezug_Projekt}
    pTemp = {'KanBan': "{KanBan}", 'AU': "{AU}", 'Projekt': "{Projekt}", 'NA': "-"}
    Projektbezug = pTemp[Projektbezug_Gattung].format(**pData)
    Baugruppe_Gattung = request.params['Baugruppe_Gattung']
    Baugruppe_Baugruppe = request.params['Baugruppe_Baugruppe']
    bData = {'Baugruppe': Baugruppe_Baugruppe}
    bTemp = {'Baugruppe': "{Baugruppe}", 'unbekannt': "-"}
    Baugruppen = bTemp[Baugruppe_Gattung].format(**bData)
    FehlerGruppe = request.params['FehlerGruppe']
    Fehler = request.params[FehlerGruppe]
    Thema = request.params['Thema']
    Beschreibung = request.params['Beschreibung']
    if Beschreibung == "":
        Beschreibung = "Auf die Beschreibung wurde verzichtet."
    Bauteil = request.params['Bauteil']
    if Bauteil == "-":
        Bauteil = ""
    Zeit = float(request.params['Zeit'])
    Reparaturauftrag = 'Reparaturauftrag' in request.params
    Sonderfreigabe = 'Sonderfreigabe' in request.params
    Verursacht_Gattung = request.params['Verursacht_Gattung']
    if "Verursacht_Gruppe" in request.params:
        Verursacht_Gruppe = request.params['Verursacht_Gruppe']
    else:
        Verursacht_Gruppe = None
    Verursacht_Kreditor = request.params['Verursacht_Kreditor']
    Verursacht_Hersteller = request.params['Verursacht_Hersteller']

    vData = {'Gruppe': Verursacht_Gruppe, 'Kreditor': Verursacht_Kreditor, 'Hersteller': Verursacht_Hersteller}
    vTemp = {'Gruppe': "Gruppe:{Gruppe}", 'Kreditor': "Kreditor:{Kreditor}", 'Hersteller': "Hersteller:{Hersteller}", 'unbekannt': "unbekannt"}
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

    try:
        if True:

            issue = MenRedmine.issue.new()
            issue.project_id = Config['project_id']
            issue.tracker_id = tracker_id
            issue.subject = Thema
            issue.description = Beschreibung
            issue.custom_fields = custom_fields
            if Sonderfreigabe:
                issue.status_id = 8

            issue.save()
            ncrid = issue['id']

            if Sonderfreigabe:
                MenRedmine.issue.update(ncrid, notes='Um Sonderfreigabe wird gebeten.\n\nZur Bewilligung das Feld *Status* von "Ungelöst" -> "Erledigt" setzen.')

            time_entry = MenRedmine.time_entry.new()
            time_entry.activity_id = 24  # "Lösung"
            time_entry.issue_id = ncrid
            time_entry.spent_on = datetime.date.today()
            time_entry.hours = Zeit
            time_entry.comments = 'aus Formular'
            time_entry.save()
        else:
            ncrid = None
    except:
        print((traceback.format_exc()))
        ncrid = None

    # Antwortseite:
    gruppe.update({'farbe': colorhash.ColorHash(gruppe['name'], lightness=(0.85, 0.9, 0.95), saturation=(0.25, 0.35, 0.5, 0.65, 0.75)).hex})

    return {'Gruppe': gruppe, 'NCRID': ncrid, 'RedmineBaseURL': Config['private_url']}


#########################################################################################
# Produktiionslinie Meldung


@view_config(route_name='MenLineMeldung', renderer='../templates/MenLineMeldung.pt')
def my_view_testpage(request):

    redmine_users = MenRedmine.user.all()
    users = []
    if False:
        for user in list(redmine_users.values()):
            users.append(user['firstname'])

    Fehlerursachen = [
        {'name': x["value"], 'farbe':Fehlerursachenfarben[x["value"][0:2]], 'gewicht': Gewichte[x["value"][0:4]]}
        for x in MenRedmine.custom_field.get(5).possible_values
    ]

    FehlerursachenGruppen = [
        {'txt': 'Information und Vorgehen', 'name': 'FehlerGruppe_Information_und_Vorgehen', 'Fehlerursachen': [x for x in Fehlerursachen if x["name"][0:2] in ['01', '02']]},
        {'txt': 'Herstellungsschritte und Lager', 'name': 'FehlerGruppe_Herstellungsschritte', 'Fehlerursachen': [x for x in Fehlerursachen if x["name"][0:2] in ['03', '05', '06', '07']]},
        {'txt': 'Defekte', 'name': 'FehlerGruppe_Defekte', 'Fehlerursachen': [x for x in Fehlerursachen if x["name"][0:2] in ['04']]},
        {'txt': 'Organisation und Sonstiges', 'name': 'FehlerGruppe_Organisation_und_Sonstiges', 'Fehlerursachen': [x for x in Fehlerursachen if x["name"][0:2] in ['08', '09', '99']]},
        {'txt': 'Alle', 'name': 'FehlerGruppe_Alle', 'Fehlerursachen': Fehlerursachen}
    ]

    Gruppen = holeGrupen()
    try:
        gruppe = next(item for item in Gruppen if item["id"] == request.matchdict['Linie'])
    except:
        return HTTPNotFound("Die Gruppen-ID '{}' ist ungültig.".format(request.matchdict['Linie']))
    gruppe.update({'farbe': colorhash.ColorHash(gruppe['name'], lightness=(0.85, 0.9, 0.95), saturation=(0.25, 0.35, 0.5, 0.65, 0.75)).hex})
    print(gruppe)
    return {'Gruppe': gruppe, 'Gruppen': Gruppen, 'Nutzer': users, 'Fehlerursachen': Fehlerursachen, 'FehlerursachenGruppen': FehlerursachenGruppen}


#########################################################################################
#########################################################################################
#########################################################################################
# Rohdaten csv


@view_config(route_name='Rohdaten', renderer='csv')
def Rohdaten(request):
    project_id = Config['project_id']
    StartDatumStr = "{}-{}-{}".format(request.matchdict['StartJahr'], request.matchdict['StartMonat'], request.matchdict['StartTag'])
    StoppDatumStr = "{}-{}-{}".format(request.matchdict['StoppJahr'], request.matchdict['StoppMonat'], request.matchdict['StoppTag'])

    issues = MenRedmine.issue.filter(project_id=project_id, created_on='><{}|{}'.format(StartDatumStr, StoppDatumStr), status_id="*")
    x = ['author', 'created_on', 'description', 'id', 'project', 'status', 'subject', 'tracker', 'updated_on']
    x = ['author', 'created_on', 'id', 'status', 'subject', 'tracker', 'updated_on']

    rows = []
    for issue in issues:
        print((issue.url))
        d = {k: "{}".format(issue[k]) for k in x}
        if hasattr(issue, 'assigned_to'):
                d['assigned_to'] = issue.assigned_to.id
        if hasattr(issue, 'custom_fields'):
            for cf in issue['custom_fields']:
                d[cf.name] = "{}".format(cf.value)
        total_duration = 0
        #  Todo: Sobald eine neue Version vom RM verfügbar ist, issue."spent_hours" auswerten! Zusammenfassen mit excel (Q3.2020)
        if hasattr(issue, 'time_entries'):
            for time_entry in issue['time_entries']:
                total_duration += time_entry.hours
        d['total_duration'] = total_duration
        print((d['id']))
        print()

        if d['status'] != "Abgewiesen":
            rows.append(d)

    if rows:
        header = list(rows[0].keys())
    else:
        header = ['Info']
        rows = [{'Info': "keine Daten verfügbar."}]

    filename = 'NCR-Ereignisse_{}_{}.csv'.format(StartDatumStr, StoppDatumStr)
    request.response.content_disposition = 'attachment;filename=' + filename

    return {
        'header': header,
        'rows': rows,
    }

#########################################################################################
#########################################################################################
#########################################################################################
# Rohdaten Excel


@view_config(route_name='RohdatenExcel', renderer='xlsx')
def Rohdaten2(request):
    project_id = Config['project_id']
    StartDatumStr = "{}-{}-{}".format(request.matchdict['StartJahr'], request.matchdict['StartMonat'], request.matchdict['StartTag'])
    StoppDatumStr = "{}-{}-{}".format(request.matchdict['StoppJahr'], request.matchdict['StoppMonat'], request.matchdict['StoppTag'])

    issues = MenRedmine.issue.filter(project_id=project_id, created_on='><{}|{}'.format(StartDatumStr, StoppDatumStr), status_id="*")
    x = ['author', 'created_on', 'description', 'id', 'project', 'status', 'subject', 'tracker', 'updated_on']
    x = ['author', 'created_on', 'id', 'status', 'subject', 'tracker', 'updated_on']

    rows = []
    for issue in issues:
        print((issue.url))
        d = {k: "{}".format(issue[k]) for k in x}
        if hasattr(issue, 'assigned_to'):
                d['assigned_to'] = issue.assigned_to.id
        if hasattr(issue, 'custom_fields'):
            for cf in issue['custom_fields']:
                d[cf.name] = "{}".format(cf.value) if hasattr(cf, 'value') else ""
        total_duration = 0
        #  Todo: Sobald eine neue Version vom RM verfügbar ist, issue."spent_hours" auswerten! Zusammenfassen mit csv (Q3.2020)
        if hasattr(issue, 'time_entries'):
            for time_entry in issue['time_entries']:
                total_duration += time_entry.hours
        d['total_duration'] = total_duration
        print((d['id']))
        print()

        if d['status'] != "Abgewiesen":
            rows.append(d)

    if rows:
        header = list(rows[0].keys())
    else:
        header = ['Info']
        rows = [{'Info': "keine Daten verfügbar."}]

    filename = 'NCR-Ereignisse_{}_{}.csv'.format(StartDatumStr, StoppDatumStr)
    request.response.content_disposition = 'attachment;filename=' + filename

    return {
        'header': header,
        'rows': rows,
    }
