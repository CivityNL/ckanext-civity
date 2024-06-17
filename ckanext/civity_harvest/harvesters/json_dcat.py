from ckanext.dcat.harvesters import DCATJSONHarvester
import ckan.plugins.toolkit as toolkit

from urlparse import urlparse, parse_qsl, urlunparse
from urllib import urlencode

import logging

log = logging.getLogger(__name__)


class CivityDCATJSONHarvester(DCATJSONHarvester):

    def modify_package_dict(self, package_dict, dcat_dict, harvest_object):
        '''
            Allows custom harvesters to modify the package dict before
            creating or updating the actual package.
        '''
        package_dict = self.dcat_to_harmonized(package_dict, dcat_dict, harvest_object)
        return package_dict

    def dcat_to_harmonized(self, package_dict, dcat_dict, harvest_object):
        pkg_dict = {}

        # Fields from dcat_dict ignored so far:
        # accrualPeriodicity -> ignored (should be update_frequency)
        accrualPeriodicity_to_map = ["10annually",
                                     "5annually",
                                     "annually",
                                     "asNeeded",
                                     "biannually",
                                     "continual",
                                     "daily",
                                     "irregular",
                                     "monthly",
                                     "notPlanned",
                                     "unknown",
                                     None]
        # identifier -> put as extra
        # landingspage -> ignored for now.
        # theme -> mappings not made
        themes_mapping = {
            'AARDKUNDIG WAARDEVOLLE GEBIEDEN': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'AARDKUNDIGE WAARDEN': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'ADMINISTRATIEVE GRENZEN': 'http://standaarden.overheid.nl/owms/terms/Bestuur',
            'ADRESSEN': 'http://standaarden.overheid.nl/owms/terms/Ruimte_en_infrastructuur',
            'AGRARISCH NATUURBEHEER': 'http://standaarden.overheid.nl/owms/terms/Landbouw_(thema)',
            'AMMONIAK': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'ARBEID': 'http://standaarden.overheid.nl/owms/terms/Werk_(thema)',
            'ARBEIDSMOBILITEIT': 'http://standaarden.overheid.nl/owms/terms/Werk_(thema)',
            'BEBOUWDE KOM': 'http://standaarden.overheid.nl/owms/terms/Ruimte_en_infrastructuur',
            'BEDRIJFSLOCATIES': 'http://standaarden.overheid.nl/owms/terms/Ruimte_en_infrastructuur',
            'BEDRIJVENTERREINEN': 'http://standaarden.overheid.nl/owms/terms/Ruimte_en_infrastructuur',
            'Beleid van anderen': 'http://standaarden.overheid.nl/owms/terms/Bestuur',
            'BELEIDSEVALUATIE': 'http://standaarden.overheid.nl/owms/terms/Bestuur',
            'BELEIDSONTWIKKELING': 'http://standaarden.overheid.nl/owms/terms/Bestuur',
            'BELEIDSUITVOERING': 'http://standaarden.overheid.nl/owms/terms/Bestuur',
            'BERMEN': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'BEROEPSBEVOLKING': 'http://standaarden.overheid.nl/owms/terms/Werk_(thema)',
            'BIODIVERSITEIT': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'BODEM': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'BODEMBESCHERMING': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'BODEMKAARTEN': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'BODEMKUNDE': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'BODEMKWALITEIT': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'BODEMONDERZOEK': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'BODEMSANERING': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'BODEMTYPEN': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'BODEMTYPEN': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'BODEMVERONTREINIGING': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'BOMEN': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'BOSSEN': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'BUSHALTES': 'http://standaarden.overheid.nl/owms/terms/Verkeer_(thema)',
            'BUSHALTES': 'http://standaarden.overheid.nl/owms/terms/Verkeer_(thema)',
            'BUSLIJNEN': 'http://standaarden.overheid.nl/owms/terms/Verkeer_(thema)',
            'BUSLIJNEN': 'http://standaarden.overheid.nl/owms/terms/Verkeer_(thema)',
            'BUSVERVOER': 'http://standaarden.overheid.nl/owms/terms/Verkeer_(thema)',
            'CULTUUR': 'http://standaarden.overheid.nl/owms/terms/Cultuur_en_recreatie',
            'CULTUURBEHOUD': 'http://standaarden.overheid.nl/owms/terms/Cultuur_en_recreatie',
            'CULTUURBELEID': 'http://standaarden.overheid.nl/owms/terms/Cultuur_en_recreatie',
            'CULTUURHISTORIE': 'http://standaarden.overheid.nl/owms/terms/Cultuur_en_recreatie',
            'CULTUURHISTORISCHE WAARDENKAARTEN': 'http://standaarden.overheid.nl/owms/terms/Cultuur_en_recreatie',
            'DAGRECREATIE': 'http://standaarden.overheid.nl/owms/terms/Cultuur_en_recreatie',
            'DELFSTOFFENWINNING': 'http://standaarden.overheid.nl/owms/terms/Economie',
            'DETAILHANDEL': 'http://standaarden.overheid.nl/owms/terms/Economie',
            'DIJKEN': 'http://standaarden.overheid.nl/owms/terms/Ruimte_en_infrastructuur',
            'DIJKEN': 'http://standaarden.overheid.nl/owms/terms/Ruimte_en_infrastructuur',
            'DROOGTE': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'DUURZAAM BOUWEN': 'http://standaarden.overheid.nl/owms/terms/Ruimte_en_infrastructuur',
            'DUURZAAMHEID': 'http://standaarden.overheid.nl/owms/terms/Huisvesting_(thema)',
            'DUURZAME ENERGIE': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'ECOLOGIE': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'ECOLOGISCHE HOOFDSTRUCTUUR': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'ECOLOGISCHE VERBINDINGSZONES': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'ECONOMIE': 'http://standaarden.overheid.nl/owms/terms/Economie',
            'ECONOMISCHE ONTWIKKELING': 'http://standaarden.overheid.nl/owms/terms/Economie',
            'EDUCATIE': 'http://standaarden.overheid.nl/owms/terms/Onderwijs_en_wetenschap',
            'ELEKTRICITEITSVOORZIENING': 'http://standaarden.overheid.nl/owms/terms/Economie',
            'ENERGIEBESPARING': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'ENERGIEBRONNEN': 'http://standaarden.overheid.nl/owms/terms/Economie',
            'ENERGIEBRONNEN': 'http://standaarden.overheid.nl/owms/terms/Economie',
            'ENERGIEVOORZIENING': 'http://standaarden.overheid.nl/owms/terms/Economie',
            'ENERGIEVOORZIENING': 'http://standaarden.overheid.nl/owms/terms/Economie',
            'EVACUATIE': 'http://standaarden.overheid.nl/owms/terms/Openbare_orde_en_veiligheid-orde-en-veiligheid',
            'EXTERNE VEILIGHEID': 'http://standaarden.overheid.nl/owms/terms/Openbare_orde_en_veiligheid-orde-en-veiligheid',
            'FAUNA': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'FAUNABEHEER': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'FAUNABEHEEREENHEDEN': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'FAUNAVOORZIENINGEN': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'FIETSPADEN': 'http://standaarden.overheid.nl/owms/terms/Verkeer_(thema)',
            'FIETSROUTES': 'http://standaarden.overheid.nl/owms/terms/Verkeer_(thema)',
            'FLORA': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'FLORA- EN FAUNAWET': 'http://standaarden.overheid.nl/owms/terms/Recht_(thema)',
            'GANZEN': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'GEBIEDSGERICHT WERKEN': 'http://standaarden.overheid.nl/owms/terms/Ruimte_en_infrastructuur',
            'GELUID': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'GELUIDHINDER': 'http://standaarden.overheid.nl/owms/terms/Zorg_en_gezondheid',
            'GELUIDSISOLATIE': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'GELUIDSSCHERMEN': 'http://standaarden.overheid.nl/owms/terms/Ruimte_en_infrastructuur',
            'GELUIDSZONES': 'http://standaarden.overheid.nl/owms/terms/Recht_(thema)',
            'GELUIDSZONES': 'http://standaarden.overheid.nl/owms/terms/Recht_(thema)',
            'GEMEENTEWEGEN': 'http://standaarden.overheid.nl/owms/terms/Ruimte_en_infrastructuur',
            'GEUROVERLAST': 'http://standaarden.overheid.nl/owms/terms/Zorg_en_gezondheid',
            'GEVAARLIJKE STOFFEN': 'http://standaarden.overheid.nl/owms/terms/Zorg_en_gezondheid',
            'GLADHEIDSBESTRIJDING': 'http://standaarden.overheid.nl/owms/terms/Ruimte_en_infrastructuur',
            'GRENZEN': 'http://standaarden.overheid.nl/owms/terms/Bestuur',
            'GROENVOORZIENINGEN': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'GRONDWATER': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'GRONDWATER': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'GRONDWATERBESCHERMING': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'GRONDWATERBESCHERMING': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'GRONDWATERBESCHERMINGSGEBIEDEN': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'GRONDWATERKAARTEN': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'GRONDWATERONTTREKKINGEN': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'GRONDWATERSANERING': 'http://standaarden.overheid.nl/owms/terms/Zorg_en_gezondheid',
            'GRONDWATERSTAND': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'GRONDWATERSTAND': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'GRONDWATERWET': 'http://standaarden.overheid.nl/owms/terms/Recht_(thema)',
            'HABITATRICHTLIJN': 'http://standaarden.overheid.nl/owms/terms/Recht_(thema)',
            'Habitats en biotopen': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'HISTORISCHE KAARTEN': 'http://standaarden.overheid.nl/owms/terms/Cultuur_en_recreatie',
            'HOOGSPANNINGSKABELS': 'http://standaarden.overheid.nl/owms/terms/Ruimte_en_infrastructuur',
            'INFILTRATIE': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'Informatief': 'http://standaarden.overheid.nl/owms/terms/Onderwijs_en_wetenschap',
            'INFRASTRUCTUUR': 'http://standaarden.overheid.nl/owms/terms/Ruimte_en_infrastructuur',
            'JACHT': 'http://standaarden.overheid.nl/owms/terms/Landbouw_(thema)',
            'KABELS EN LEIDINGEN': 'http://standaarden.overheid.nl/owms/terms/Ruimte_en_infrastructuur',
            'KABELS EN LEIDINGEN': 'http://standaarden.overheid.nl/owms/terms/Ruimte_en_infrastructuur',
            'KABELS': 'http://standaarden.overheid.nl/owms/terms/Ruimte_en_infrastructuur',
            'Kaderstellend': 'http://standaarden.overheid.nl/owms/terms/Recht_(thema)',
            'KANALEN': 'http://standaarden.overheid.nl/owms/terms/Ruimte_en_infrastructuur',
            'KANTOORGEBOUWEN': 'http://standaarden.overheid.nl/owms/terms/Economie',
            'KANTOORLOCATIES': 'http://standaarden.overheid.nl/owms/terms/Economie',
            'KILOMETRERING': 'http://standaarden.overheid.nl/owms/terms/Verkeer_(thema)',
            'LANDBOUW': 'http://standaarden.overheid.nl/owms/terms/Landbouw_(thema)',
            'LANDGOEDEREN': 'http://standaarden.overheid.nl/owms/terms/Cultuur_en_recreatie',
            'LANDSCHAPSBEHEER': 'http://standaarden.overheid.nl/owms/terms/Cultuur_en_recreatie',
            'LANDSCHAPSONTWIKKELING': 'http://standaarden.overheid.nl/owms/terms/Cultuur_en_recreatie',
            'LANDSCHAPSVERORDENINGEN': 'http://standaarden.overheid.nl/owms/terms/Recht_(thema)',
            'LEIDINGEN': 'http://standaarden.overheid.nl/owms/terms/Ruimte_en_infrastructuur',
            'LOGISTIEK': 'http://standaarden.overheid.nl/owms/terms/Economie',
            'LUCHTKWALITEIT': 'http://standaarden.overheid.nl/owms/terms/Zorg_en_gezondheid',
            'LUCHTVAART': 'http://standaarden.overheid.nl/owms/terms/Economie',
            'MILIEU': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'MILIEUKWALITEIT': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'MILITAIRE TERREINEN': 'http://standaarden.overheid.nl/owms/terms/Openbare_orde_en_veiligheid-orde-en-veiligheid',
            'MONUMENTEN': 'http://standaarden.overheid.nl/owms/terms/Cultuur_en_recreatie',
            'NATIONALE PARKEN': 'http://standaarden.overheid.nl/owms/terms/Cultuur_en_recreatie',
            'NATUUR EN LANDSCHAP': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'NATUUR': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'NATUUR- EN LANDSCHAPSBELEID': 'http://standaarden.overheid.nl/owms/terms/Bestuur',
            'NATUURBEHEER': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'NATUURBESCHERMING': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'NATUURBESCHERMINGSWET': 'http://standaarden.overheid.nl/owms/terms/Recht_(thema)',
            'NATUURGEBIEDEN': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'NATUURMONUMENTEN': 'http://standaarden.overheid.nl/owms/terms/Cultuur_en_recreatie',
            'NATUURONTWIKKELING': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'NATUURPARELS': 'http://standaarden.overheid.nl/owms/terms/Cultuur_en_recreatie',
            'NATUURSCHOONWET 1928': 'http://standaarden.overheid.nl/owms/terms/Recht_(thema)',
            'NATUURWAARDEN': 'http://standaarden.overheid.nl/owms/terms/Cultuur_en_recreatie',
            'NATUURWAARDEN': 'http://standaarden.overheid.nl/owms/terms/Cultuur_en_recreatie',
            'NATUURWETGEVING': 'http://standaarden.overheid.nl/owms/terms/Recht_(thema)',
            'ONDERHOUD': 'http://standaarden.overheid.nl/owms/terms/Ruimte_en_infrastructuur',
            'ONDERWIJS': 'http://standaarden.overheid.nl/owms/terms/Onderwijs_en_wetenschap',
            'ONTHEFFINGEN': 'http://standaarden.overheid.nl/owms/terms/Recht_(thema)',
            'ONTSLUITINGSWEGEN': 'http://standaarden.overheid.nl/owms/terms/Ruimte_en_infrastructuur',
            'OPENBAAR VERVOER': 'http://standaarden.overheid.nl/owms/terms/Verkeer_(thema)',
            'OPENBAAR VERVOER': 'http://standaarden.overheid.nl/owms/terms/Verkeer_(thema)',
            'OPENLUCHTRECREATIE': 'http://standaarden.overheid.nl/owms/terms/Cultuur_en_recreatie',
            'OVERSTROMINGEN': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'Provinciaal beleid': 'http://standaarden.overheid.nl/owms/terms/Bestuur',
            'PROVINCIALE VERORDENINGEN': 'http://standaarden.overheid.nl/owms/terms/Recht_(thema)',
            'PROVINCIALE WEGEN': 'http://standaarden.overheid.nl/owms/terms/Ruimte_en_infrastructuur',
            'PROVINCIALE WEGEN': 'http://standaarden.overheid.nl/owms/terms/Ruimte_en_infrastructuur',
            'PROVINCIEGRENZEN': 'http://standaarden.overheid.nl/owms/terms/Bestuur',
            'RAMPEN': 'http://standaarden.overheid.nl/owms/terms/Openbare_orde_en_veiligheid-orde-en-veiligheid',
            'RAMPENBESTRIJDING': 'http://standaarden.overheid.nl/owms/terms/Openbare_orde_en_veiligheid-orde-en-veiligheid',
            'RECREATIE': 'http://standaarden.overheid.nl/owms/terms/Cultuur_en_recreatie',
            'RECREATIEGEBIEDEN': 'http://standaarden.overheid.nl/owms/terms/Cultuur_en_recreatie',
            'REGIONALE ECONOMIE': 'http://standaarden.overheid.nl/owms/terms/Economie',
            'RIJKSMONUMENTEN': 'http://standaarden.overheid.nl/owms/terms/Cultuur_en_recreatie',
            'RIJKSWEGEN': 'http://standaarden.overheid.nl/owms/terms/Ruimte_en_infrastructuur',
            'RISICOKAART': 'http://standaarden.overheid.nl/owms/terms/Openbare_orde_en_veiligheid-orde-en-veiligheid',
            'RIVIEREN': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'ROTONDES': 'http://standaarden.overheid.nl/owms/terms/Ruimte_en_infrastructuur',
            'SLOTEN': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'SPOORLIJNEN': 'http://standaarden.overheid.nl/owms/terms/Ruimte_en_infrastructuur',
            'SPOORWEGVAKKEN': 'http://standaarden.overheid.nl/owms/terms/Ruimte_en_infrastructuur',
            'Spreiding van soorten': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'STANKOVERLAST': 'http://standaarden.overheid.nl/owms/terms/Zorg_en_gezondheid',
            'STATIONS': 'http://standaarden.overheid.nl/owms/terms/Ruimte_en_infrastructuur',
            'STIKSTOF': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'STILTEGEBIEDEN': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'STRUCTUURPLANNEN': 'http://standaarden.overheid.nl/owms/terms/Recht_(thema)',
            'SUBSIDIES': 'http://standaarden.overheid.nl/owms/terms/Bestuur',
            'TOERISME': 'http://standaarden.overheid.nl/owms/terms/Cultuur_en_recreatie',
            'TOERISTISCHE ROUTES': 'http://standaarden.overheid.nl/owms/terms/Cultuur_en_recreatie',
            'TOETSING': 'http://standaarden.overheid.nl/owms/terms/Recht_(thema)',
            'UITBESTEDING': 'http://standaarden.overheid.nl/owms/terms/Bestuur',
            'UITWERKINGSPLANNEN': 'http://standaarden.overheid.nl/owms/terms/Bestuur',
            'VAARRECREATIE': 'http://standaarden.overheid.nl/owms/terms/Cultuur_en_recreatie',
            'VEEHOUDERIJBEDRIJVEN': 'http://standaarden.overheid.nl/owms/terms/Landbouw_(thema)',
            'VEEN': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'VEEN': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'VEGETATIE': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'VEGETATIE': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'VEILIGHEID': 'http://standaarden.overheid.nl/owms/terms/Openbare_orde_en_veiligheid-orde-en-veiligheid',
            'VEILIGHEIDSEISEN': 'http://standaarden.overheid.nl/owms/terms/Openbare_orde_en_veiligheid-orde-en-veiligheid',
            'VERBINDINGSWEGEN': 'http://standaarden.overheid.nl/owms/terms/Ruimte_en_infrastructuur',
            'VERBLIJFSRECREATIE': 'http://standaarden.overheid.nl/owms/terms/Cultuur_en_recreatie',
            'VERDROGING': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'VERDROGING': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'VERGUNNINGEN': 'http://standaarden.overheid.nl/owms/terms/Recht_(thema)',
            'VERKEER EN VERVOER': 'http://standaarden.overheid.nl/owms/terms/Verkeer_(thema)',
            'VERKEER EN VERVOER': 'http://standaarden.overheid.nl/owms/terms/Verkeer_(thema)',
            'VERKEERS- EN VERVOERSWETGEVING': 'http://standaarden.overheid.nl/owms/terms/Recht_(thema)',
            'VERKEERSINFORMATIE': 'http://standaarden.overheid.nl/owms/terms/Verkeer_(thema)',
            'VERKEERSINTENSITEITEN': 'http://standaarden.overheid.nl/owms/terms/Verkeer_(thema)',
            'VERKEERSLAWAAI': 'http://standaarden.overheid.nl/owms/terms/Zorg_en_gezondheid',
            'VERKEERSMOBILITEIT': 'http://standaarden.overheid.nl/owms/terms/Verkeer_(thema)',
            'VERKEERSMOBILITEIT': 'http://standaarden.overheid.nl/owms/terms/Verkeer_(thema)',
            'VERKEERSTEKENS': 'http://standaarden.overheid.nl/owms/terms/Verkeer_(thema)',
            'VERKEERSTEKENS': 'http://standaarden.overheid.nl/owms/terms/Verkeer_(thema)',
            'VERMESTING': 'http://standaarden.overheid.nl/owms/terms/Landbouw_(thema)',
            'VERVOERMANAGEMENT': 'http://standaarden.overheid.nl/owms/terms/Verkeer_(thema)',
            'VERZURING': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'VOGELRICHTLIJN': 'http://standaarden.overheid.nl/owms/terms/Recht_(thema)',
            'VOLKSGEZONDHEID': 'http://standaarden.overheid.nl/owms/terms/Zorg_en_gezondheid',
            'VOORTGEZET ONDERWIJS': 'http://standaarden.overheid.nl/owms/terms/Onderwijs_en_wetenschap',
            'WANDELROUTES': 'http://standaarden.overheid.nl/owms/terms/Cultuur_en_recreatie',
            'WATER': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'WATERBELEID': 'http://standaarden.overheid.nl/owms/terms/Bestuur',
            'WATERBELEID': 'http://standaarden.overheid.nl/owms/terms/Bestuur',
            'WATERCONSERVERING': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'WATERHUISHOUDING': 'http://standaarden.overheid.nl/owms/terms/Ruimte_en_infrastructuur',
            'WATERHUISHOUDING': 'http://standaarden.overheid.nl/owms/terms/Ruimte_en_infrastructuur',
            'WATERKERINGEN': 'http://standaarden.overheid.nl/owms/terms/Ruimte_en_infrastructuur',
            'WATERLOPEN': 'http://standaarden.overheid.nl/owms/terms/Ruimte_en_infrastructuur',
            'WATERNATUUR': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'WATERPEIL': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'WATERRECREATIE': 'http://standaarden.overheid.nl/owms/terms/Cultuur_en_recreatie',
            'WATERSCHAPPEN': 'http://standaarden.overheid.nl/owms/terms/Bestuur',
            'WATERSTAAT': 'http://standaarden.overheid.nl/owms/terms/Bestuur',
            'WATERTOERISME': 'http://standaarden.overheid.nl/owms/terms/Cultuur_en_recreatie',
            'WATERWEGEN': 'http://standaarden.overheid.nl/owms/terms/Ruimte_en_infrastructuur',
            'WATERWINGEBIEDEN': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'WATERWINNING': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'WEGBEHEER': 'http://standaarden.overheid.nl/owms/terms/Ruimte_en_infrastructuur',
            'WEGEN': 'http://standaarden.overheid.nl/owms/terms/Ruimte_en_infrastructuur',
            'WEGEN': 'http://standaarden.overheid.nl/owms/terms/Ruimte_en_infrastructuur',
            'WEGENINFORMATIESYSTEMEN': 'http://standaarden.overheid.nl/owms/terms/Verkeer_(thema)',
            'WEGENONDERHOUD': 'http://standaarden.overheid.nl/owms/terms/Ruimte_en_infrastructuur',
            'WEGMEUBILAIR': 'http://standaarden.overheid.nl/owms/terms/Ruimte_en_infrastructuur',
            'WEGVERKEER': 'http://standaarden.overheid.nl/owms/terms/Verkeer_(thema)',
            'WEGVERKEER': 'http://standaarden.overheid.nl/owms/terms/Verkeer_(thema)',
            'WEGVERLICHTING': 'http://standaarden.overheid.nl/owms/terms/Ruimte_en_infrastructuur',
            'WERKGELEGENHEID': 'http://standaarden.overheid.nl/owms/terms/Werk_(thema)',
            'WERKNEMERS': 'http://standaarden.overheid.nl/owms/terms/Werk_(thema)',
            'WET GELUIDHINDER': 'http://standaarden.overheid.nl/owms/terms/Recht_(thema)',
            'WETGEVING RUIMTELIJKE ORDENING EN VOLKSHUISVESTING': 'http://standaarden.overheid.nl/owms/terms/Recht_(thema)',
            'WILDBEHEEREENHEDEN': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'WOONSCHEPEN': 'http://standaarden.overheid.nl/owms/terms/Ruimte_en_infrastructuur',
            'ZONNE-ENERGIE': 'http://standaarden.overheid.nl/owms/terms/Natuur_en_milieu',
            'ZWEMWATER': 'http://standaarden.overheid.nl/owms/terms/Cultuur_en_recreatie'
        }

        pkg_dict['name'] = package_dict.get('name')
        pkg_dict['title'] = dcat_dict.get('title')
        pkg_dict['notes'] = dcat_dict.get('description', "")
        pkg_dict['private'] = False if dcat_dict.get('accessLevel', 'public') == 'public' else True
        pkg_dict['license_id'] = 'CC0-1.0'
        pkg_dict['language'] = 'http://publications.europa.eu/resource/authority/language/NLD'
        pkg_dict['metadata_language'] = 'http://publications.europa.eu/resource/authority/language/NLD'
        pkg_dict['contact_point_type'] = 'organization'
        contact_point_name = dcat_dict.get('contactPoint', {}).get('fn', None)
        pkg_dict['contact_point_name'] = contact_point_name if contact_point_name else "Provincie Utrecht"
        contact_point_email = dcat_dict.get('contactPoint', {}).get('fn', None)
        pkg_dict['contact_point_email'] = contact_point_email if contact_point_email else "GIS@provincie-utrecht.nl"
        pkg_dict['issued'] = dcat_dict.get('issued', "")
        pkg_dict['publisher'] = 'http://standaarden.overheid.nl/owms/terms/Utrecht_(provincie)'
        pkg_dict['authority'] = 'http://standaarden.overheid.nl/owms/terms/Utrecht_(provincie)'
        pkg_dict['access_rights'] = 'http://publications.europa.eu/resource/authority/access-right/PUBLIC'
        pkg_dict['bounding_box'] = dcat_dict.get('spatial', '')
        pkg_dict['update_frequency'] = 'onbekend'
        pkg_dict['geonetwork_link_enabled'] = 'False'
        pkg_dict['geoserver_link_enabled'] = 'True'
        pkg_dict['donl_link_enabled'] = 'False'

        pkg_dict['theme'] = 'geen-thema'
        dcat_theme = dcat_dict.get('theme', [])
        log.info('CivityDCATJSONHarvester :: [dcat_to_harmonized] dcat_theme = {}'.format(dcat_theme))
        log.info('CivityDCATJSONHarvester :: [dcat_to_harmonized] TYPE dcat_theme = {}'.format(type(dcat_theme)))
        for theme in dcat_theme:
            if theme in themes_mapping:
                pkg_dict['theme'] = themes_mapping[theme]
                # dcat_dict['theme'] might have multiple values, we take the first valid match
                break

        pkg_dict['tags'] = []
        for keyword in dcat_dict.get('keyword', []):
            pkg_dict['tags'].append({'name': keyword})

        # pkg_dict['extras'] = []
        # pkg_dict['extras'].append({'key': 'guid', 'value': dcat_dict.get('identifier')})

        pkg_dict['resources'] = []
        for distribution in dcat_dict.get('distribution', []):
            resource = {
                'name': distribution.get('title'),
                'description': distribution.get('description', distribution.get('title', "[AUTO-FILL] NO_DESCRIPTION")),
                'url': distribution.get('downloadURL') or distribution.get('accessURL'),
                'format': distribution.get('format')
            }

            if '/geoserver/' in resource.get('url', ''):
                self.update_url_for_geoserver(resource, 4326)

            if distribution.get('byteSize'):
                try:
                    resource['size'] = int(distribution.get('byteSize'))
                except ValueError:
                    pass
            pkg_dict['resources'].append(resource)

        return pkg_dict

    def update_url_for_geoserver(self, resource, srid=4326):
        log.info('CivityDCATJSONHarvester :: [update_url_for_geoserver]')
        url = resource.get('url')
        serviceKey = 'service'
        serviceValue = 'wfs'
        hasSrsNameKey = False
        srsNameKey = 'srsName'
        srsNameValue = 'EPSG:{}'.format(srid)

        parsed_url = list(urlparse(url))
        query_parameters = dict(parse_qsl(parsed_url[4]))

        for key in query_parameters:
            if key.lower() == srsNameKey.lower():
                log.info('CivityDCATJSONHarvester :: [update_url_for_geoserver] query parameter "{}" exists'.format(
                    srsNameKey))
                value = query_parameters.get(key)
                if value is not None and value.startswith('EPSG:'):
                    log.info(
                        'CivityDCATJSONHarvester :: [update_url_for_geoserver] try to extract SRID from "{}"'.format(
                            value))
                    try:
                        srid = int(value.replace('EPSG:', ''))
                        hasSrsNameKey = True
                    except:
                        pass
            if key.lower() == serviceKey.lower():
                log.info('CivityDCATJSONHarvester :: [update_url_for_geoserver] query parameter "{}" exists'.format(
                    serviceKey))
                value = query_parameters.get(key)
                if value is not None and value.lower() != serviceValue.lower():
                    log.info(
                        'CivityDCATJSONHarvester :: [update_url_for_geoserver] value of "{}" not equal to "{}"'.format(
                            serviceKey, serviceValue))
                    return

        if not hasSrsNameKey:
            query_parameters[srsNameKey] = srsNameValue
            parsed_url[4] = urlencode(query_parameters)
            resource['url'] = urlunparse(parsed_url)

        resource['layer_srid'] = srid
        log.info('CivityDCATJSONHarvester :: [update_url_for_geoserver] result "{}"'.format(resource))
