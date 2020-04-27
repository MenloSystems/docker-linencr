from .config import Config

def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('MenLineMeldung', '/{Linie}/meldung')
    config.add_route('MenLineMeldungFertig', '/{Linie}/meldungfertig')
    config.add_route('Rohdaten', '/rohdaten/{StartJahr}-{StartMonat}-{StartTag}/{StoppJahr}-{StoppMonat}-{StoppTag}/csv')
    config.add_route('RohdatenExcel', '/rohdaten/{StartJahr}-{StartMonat}-{StartTag}/{StoppJahr}-{StoppMonat}-{StoppTag}/xlsx')
    config.add_route('Ticket', Config['public_url'] + '/issues/{NCRID}')
