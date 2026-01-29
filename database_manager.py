import sqlite3
from datetime import datetime
from typing import List, Dict
from models import Stop, Bus

class DatabaseManager:
    def __init__(self, db_path: str = "metro_simulation.db"):
        self.db_path = db_path
        self.init_database()
        self.populate_all_routes_data()
    
    def init_database(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create stops table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS stops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            route_id TEXT NOT NULL
        )
        ''')
        
        # Create routes table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS routes (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            source TEXT NOT NULL,
            destination TEXT NOT NULL,
            total_distance REAL DEFAULT 0.0
        )
        ''')
        
        # Create buses table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS buses (
            id TEXT PRIMARY KEY,
            route_id TEXT NOT NULL,
            current_lat REAL NOT NULL,
            current_lng REAL NOT NULL,
            speed REAL NOT NULL,
            status TEXT NOT NULL,
            next_stop_index INTEGER NOT NULL,
            last_update TEXT NOT NULL,
            direction TEXT DEFAULT 'forward',
            FOREIGN KEY (route_id) REFERENCES routes (id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def populate_all_routes_data(self):
        """Populate database with all feeder routes data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM routes")
        if cursor.fetchone()[0] > 0:
            conn.close()
            return
        
        # Route definitions with source and destination
        routes_info = {
            'FR-01': {
                'name': 'Metro FR-01',
                'source': 'Khanna Pul Stop',
                'destination': 'NUST/G-12 Metro Station'
            },
            'FR-02': {
                'name': 'Metro FR-02',
                'source': 'Sohan',
                'destination': 'AOU'
            },
            'FR-03A': {
                'name': 'Metro FR-03A',
                'source': 'PIMS Hospital',
                'destination': 'Faisal Masjid'
            },
            'FR-03B': {
                'name': 'Metro FR-03B',
                'source': 'PIMS Hospital',
                'destination': 'National Library'
            },
            'FR-04': {
                'name': 'Metro FR-04',
                'source': 'PIMS Hospital',
                'destination': 'Bari Imam Stop'
            },
            'FR-04A': {
                'name': 'Metro FR-04A',
                'source': 'Bari Imam Stop',
                'destination': 'Quaid-e-Azam University Stop'
            },
            'FR-05': {
                'name': 'Metro FR-05',
                'source': 'Golara Morh',
                'destination': 'Taxilla Highway Stop'
            },
            'FR-06': {
                'name': 'Metro FR-06',
                'source': 'PIMS Hospital',
                'destination': 'Golara Shareef'
            },
            'FR-07': {
                'name': 'Metro FR-07',
                'source': 'PIMS Hospital',
                'destination': 'Police Foundation Metro Station'
            },
            'FR-08A': {
                'name': 'Metro FR-08A',
                'source': 'Capt. Naeem T. Shaheed Chowk',
                'destination': 'PIMS Hospital'
            },
            'FR-08B': {
                'name': 'Metro FR-08B',
                'source': 'Khanna Pul Stop',
                'destination': 'Nilore'
            },
            'FR-08C': {
                'name': 'Metro FR-08C',
                'source': 'Capt. Naeem T. Shaheed Chowk',
                'destination': 'PIMS Hospital'
            },
            'FR-09': {
                'name': 'Metro FR-09',
                'source': 'Golara Morh',
                'destination': 'Khanna Pul Stop'
            },
            'FR-10': {
                'name': 'Metro FR-10',
                'source': 'Golara Morh',
                'destination': 'Taxilla Highway Stop'
            },
            'FR-11': {
                'name': 'Metro FR-11',
                'source': 'Golara Morh',
                'destination': 'Noon I-16 Stop'
            },
            'FR-12': {
                'name': 'Metro FR-12',
                'source': 'Taxilla Highway Stop',
                'destination': 'Hassan Abdal'
            },
            'FR-13': {
                'name': 'Metro FR-13',
                'source': 'Golara Morh',
                'destination': 'Fateh Jang Stop'
            },
            'FR-14': {
                'name': 'Metro FR-14',
                'source': 'Bara Kahu',
                'destination': 'Mandi Morh'
            },
            'FR-14A': {
                'name': 'Metro FR-14A',
                'source': 'Bara Kahu',
                'destination': 'Satra Meel Stop'
            },
            'FR-15': {
                'name': 'Metro FR-15',
                'source': 'Gulber Green',
                'destination': 'T Chowk'
            }
        }
        
# All routes stops data
        all_routes_stops = {
            'FR-01': [
                ("Khanna Pul Stop", 33.62925827, 73.11352419),
                ("Zia masjid", 33.63673447, 73.1076464),
                ("Kuri Road", 33.64226592, 73.10347458),
                ("Iqbal Town", 33.64587248, 73.10087402),
                ("Dhoke Kala Khan", 33.64980447, 73.09776893),
                ("Sohan", 33.65968816, 73.09081386),
                ("Faizabad", 33.66214676, 73.08304602),
                ("IJP", 33.65603214, 73.07197937),
                ("Potohar", 33.66061322, 73.06454244),
                ("MCI School", 33.65943948, 73.06055447),
                ("CDA Complaint Center", 33.65749922, 73.05689877),
                ("OGTI", 33.65537697, 73.05275726),
                ("SUI Gas", 33.65315702, 73.04858977),
                ("PTCL I-10", 33.64923647, 73.04125419),
                ("IESCO I-10", 33.64759881, 73.03812801),
                ("Korang Road", 33.64389472, 73.03097094),
                ("Mandi Morh", 33.63488067, 73.03179802),
                ("Sabzi Mandi", 33.63722481, 73.02496389),
                ("Metro CNC", 33.63982626, 73.02409564),
                ("Islamabad Medical Complex", 33.64831062, 73.01736156),
                ("PAEC General Hospital", 33.65134388, 73.0150703),
                ("FAST University", 33.65729305, 73.01580215),
                ("Islamic University", 33.65823121, 73.01770362),
                ("National Police Academy", 33.65524607, 73.01069052),
                ("Police Foundation Metro Station", 33.66253963, 73.0072021),
                ("NUST/G-12 Metro Station", 33.65575324, 72.9935215)
            ],
            'FR-02': [
                ("Sohan", 33.65974195, 73.09081492),
                ("Faizabad", 33.66214676, 73.08304602),
                ("IJP", 33.65603214, 73.07197937),
                ("Potohar", 33.66061322, 73.06454244),
                ("I-8 Markaz", 33.66592737, 73.07447978),
                ("Federal Board", 33.67766026, 73.07310334),
                ("Shifa Hospital", 33.67462817, 73.06604196),
                ("H-8 Graveyard", 33.68236722, 73.06472591),
                ("Faiz Ahmed Faiz stop", 33.67608567, 73.05502537),
                ("AOU", 33.68229563, 73.05047891)
            ],
            'FR-03A': [
                ("PIMS Hospital", 33.70610123, 73.05205307),
                ("F-8 Katchery", 33.70871050, 73.03943033),
                ("F-8 Markaz", 33.71180577, 73.03711692),
                ("F-9 Park stop", 33.71047408, 73.02796912),
                ("Shaheen Chowk", 33.71246838, 73.02649274),
                ("Bahria University", 33.71542235, 73.03081936),
                ("Faisal Masjid", 33.72792852, 73.03953618)
            ],
            'FR-03B': [
                ("PIMS Hospital", 33.70610123, 73.05205307),
                ("F-8 Katchery", 33.70871050, 73.03943033),
                ("F-8 Markaz", 33.71180577, 73.03711692),
                ("F-9 Park stop", 33.71047408, 73.02796912),
                ("Shaheen Chowk", 33.71246838, 73.02649274),
                ("Bahria University", 33.71542235, 73.03081936),
                ("Naval Complex", 33.71893889, 73.03754319),
                ("Faisal Masjid", 33.72817746, 73.03959029),
                ("Kohsar Road", 33.72691664, 73.05271291),
                ("Daman e Koh", 33.73206411, 73.06258692),
                ("Saidpur Village", 33.74006761, 73.06718139),
                ("Hill road Park", 33.73602090, 73.0701455),
                ("Trail 3", 33.74222404, 73.08244713),
                ("Trail 5", 33.74435262, 73.08804845),
                ("Pak Secretariat", 33.73515670, 73.09242124),
                ("National Library", 33.72650537, 73.10169211)
            ],
            'FR-04': [
                ("PIMS Hospital", 33.70610123, 73.05205307),
                ("Children Hospital", 33.70506834, 73.05576938),
                ("Rescue 15", 33.69970392, 73.05985857),
                ("Bank Colony", 33.70032013, 73.06177842),
                ("Salai Centre", 33.70275393, 73.06640748),
                ("Sitara Market", 33.70629577, 73.06664485),
                ("Pully Stop", 33.70687548, 73.07054872),
                ("Iqbal Hall", 33.70917682, 73.07469392),
                ("G-6/1,2", 33.71276445, 73.08046056),
                ("Melody Market", 33.71494856, 73.08483353),
                ("Abpara Market", 33.70986141, 73.08866181),
                ("Youth Hostel", 33.70967826, 73.09199797),
                ("MCI", 33.71600619, 73.08735624),
                ("ICB G-6", 33.71801711, 73.09031558),
                ("NADRA Chowk", 33.72024229, 73.0952684),
                ("Lodges Park", 33.71588960, 73.09853111),
                ("Sukh Chayn Park", 33.71357503, 73.10030901),
                ("Ministry of Foreign Affairs", 33.71851383, 73.10362161),
                ("Radio Pakistan", 33.72271479, 73.1004729),
                ("National Library", 33.72460894, 73.10266456),
                ("Secretariate Police Station", 33.72722443, 73.10766925),
                ("Diplomatic Enclave Gate 4", 33.73050436, 73.11091096),
                ("Aiwan e Sadar Colony", 33.73327532, 73.10881378),
                ("Muslim Colony", 33.73810539, 73.10824318),
                ("Ranger's Gate", 33.74382355, 73.10956117),
                ("Bari Imam Stop", 33.74361181, 73.10952378)
            ],
            'FR-04A': [
                ("Bari Imam Stop", 33.74361181, 73.10952378),
                ("Muhallah Noori Bagh", 33.74436884, 73.11287774),
                ("Community Health Centre", 33.74464995, 73.11791722),
                ("D-Type Quaid-e-Azam Colony", 33.74474801, 73.12033869),
                ("C-Type Quaid-e-Azam Colony", 33.74485647, 73.12486356),
                ("Babul Quaid", 33.74504884, 73.13291714),
                ("Quaid-e-Azam University Stop", 33.74496451, 73.13294015)
            ],
            'FR-05': [
                ("Golara Morh", 33.70969129, 72.95523741),
                ("G-13", 33.65003572, 72.98148247),
                ("A.K Brohi road", 33.66288637, 73.00197477),
                ("G-11 Markaz", 33.67046274, 72.99957315),
                ("FG. College of Home Economics & Management Sciences", 33.67983175, 72.99536182),
                ("F-11 Markaz", 33.68255274, 72.98927255),
                ("OFP Girls College", 33.68633252, 72.98412992),
                ("Golra shareef", 33.68937674, 72.98189155),
                ("NPF Housing society", 33.70035638, 72.98633788),
                ("Multy stop", 33.70421846, 72.98301699),
                ("II Hospital", 33.70087787, 72.96454423),
                ("D-12 service road", 33.70065077, 72.96114005),
                ("IESCO D-12", 33.69711276, 72.95347811),
                ("D-12 Markaz", 33.70191169, 72.94985811),
                ("Sha Allah Ditta", 33.70506804, 72.9278628),
                ("Sangjani", 33.67488851, 72.85405182),
                ("B-17 gate no.1", 33.68666653, 72.84060894),
                ("B-17 gate no.2", 33.69412776, 72.83535973),
                ("Maragalla stop", 33.70512560, 72.82297501),
                ("Taxilla Bypass", 33.71124468, 72.81387052),
                ("Wahdat colony", 33.72331749, 72.80543381),
                ("Timber market", 33.73101712, 72.8044268),
                ("Taxilla Highway Stop", 33.73377947, 72.80364548)
            ],
            'FR-06': [
                ("PIMS Hospital", 33.70610123, 73.05205307),
                ("Tipu Market", 33.70106787, 73.04297818),
                ("Ibn-e-Sina Metro Station", 33.69688866, 73.03932051),
                ("Taqwa Market", 33.69040447, 73.039605),
                ("G-9/4 Park", 33.68904171, 73.03703059),
                ("Karachi Company", 33.68879045, 73.0345056),
                ("G-9 Markaz", 33.69008523, 73.03019634),
                ("Ibn-e-Sina Road G-9 Stop", 33.69773161, 73.03622983),
                ("F-9 Park Ravi Gate", 33.70910485, 73.02904596),
                ("Fazaia Housing scheme", 33.71025647, 73.02140474),
                ("PAF Hospital", 33.70750016, 73.01625058),
                ("Pakistan Gate DCI", 33.70382478, 73.00932253),
                ("Maroof International Hospital", 33.69806105, 73.01232877),
                ("F-10 Markaz", 33.69425202, 73.01263533),
                ("IMCB F-10/4", 33.69094464, 73.00630788),
                ("IMCB F-10/2", 33.68930676, 73.00309715),
                ("F-10/ F-11 Chowk", 33.68683615, 72.99681032),
                ("Major Road", 33.68447856, 72.99181828),
                ("F-11 Markaz", 33.68261309, 72.98896953),
                ("OFP Girls College", 33.68596694, 72.98440587),
                ("Golara Shareef", 33.68727569, 72.97627367)
            ],
            'FR-07': [
                ("PIMS Hospital", 33.70610123, 73.05205307),
                ("Children Hospital", 33.70506834, 73.05576938),
                ("NORI Hospital", 33.69852301, 73.05389354),
                ("Dental Hospital", 33.69958529, 73.04863819),
                ("G-8 Markaz", 33.69886171, 73.04723183),
                ("Development Park", 33.69517927, 73.04728551),
                ("Chaman Metro Station", 33.69081554, 73.04399415),
                ("G-9/4 Park", 33.68904171, 73.03703059),
                ("Karachi Company", 33.68879045, 73.0345056),
                ("G-9 Markaz", 33.69008523, 73.03019634),
                ("Police Flats", 33.68436520, 73.02521412),
                ("College Morh", 33.68120422, 73.01913397),
                ("G-10 Markaz", 33.67686331, 73.01504379),
                ("PHA Flats", 33.67554548, 73.0126642),
                ("Tanki Stop", 33.67398803, 73.00965796),
                ("Greenbelt G-10/G-11", 33.67283931, 73.00737152),
                ("Pakistan Institute of Modern Studies", 33.67178923, 73.00273937),
                ("G-11 Markaz", 33.66993389, 72.99857845),
                ("Mehrabad", 33.66635165, 72.98973679),
                ("Suzuki Stop", 33.66262717, 72.99187917),
                ("Ittefaq Stop", 33.66053424, 72.99347255),
                ("A.k Brohi road", 33.66024412, 72.99890001),
                ("Police Foundation", 33.66308254, 73.00474383)
            ],
            'FR-08A': [
                ("Capt. Naeem T. Shaheed Chowk", 33.64451547, 73.16440754),
                ("Tamma Stop", 33.64851111, 73.16203748),
                ("COMSATS University", 33.65295187, 73.15765696),
                ("Hostel City", 33.65695919, 73.15353668),
                ("Gulshan Alhuda", 33.66110241, 73.15336435),
                ("Chatta Bakahtawar", 33.66550481, 73.15173418),
                ("Green Avenue", 33.66773393, 73.14971672),
                ("Park View city", 33.67427622, 73.14418612),
                ("Shahzad Town", 33.67618671, 73.1423078),
                ("NIH Allergy Center", 33.68542012, 73.13472496),
                ("NARC Colony", 33.68724354, 73.13117702),
                ("Rawal Dam Colony", 33.68792768, 73.12138409),
                ("School Board", 33.68873807, 73.11644481),
                ("Rawal Town", 33.68891172, 73.11286209),
                ("Rawal Chowk", 33.69303417, 73.11013669),
                ("Kashmir Chowk", 33.70679023, 73.10608374),
                ("Foreign Office", 33.71248087, 73.10118121),
                ("Aabpara", 33.70709368, 73.09075807),
                ("CDA Stop", 33.70048151, 73.0781614),
                ("Zero Point", 33.69575431, 73.06921432),
                ("TNT", 33.69738605, 73.06157455),
                ("Children Hospital", 33.70567919, 73.0553135),
                ("PIMS Hospital", 33.70610123, 73.05205307)
            ],
            'FR-08B': [
                ("Khanna Pul Stop", 33.62925827, 73.11352419),
                ("Madina Town", 33.63267156, 73.12723917),
                ("Burma Town", 33.63369667, 73.13263942),
                ("Paracha Chowk", 33.63686935, 73.14161393),
                ("Post Office", 33.63954684, 73.14918262),
                ("School stop", 33.64142717, 73.15692337),
                ("Capt. Naeem T. Shaheed Chowk", 33.64447297, 73.16459641),
                ("HBS General Hospital", 33.64518159, 73.17235748),
                ("Ali Pur bank", 33.64536397, 73.18075933),
                ("Sultana foundation", 33.64307541, 73.20273654),
                ("Hafta bazar", 33.64581211, 73.21419902),
                ("Thanda pani", 33.64771108, 73.22025404),
                ("Nilore", 33.65349968, 73.24168997)
            ],
            'FR-08C': [
                ("Capt. Naeem T. Shaheed Chowk", 33.64451547, 73.16440754),
                ("Tamma Stop", 33.64851111, 73.16203748),
                ("COMSATS University", 33.65295187, 73.15765696),
                ("Hostel City", 33.65695919, 73.15353668),
                ("Gulshan Alhuda", 33.66110241, 73.15336435),
                ("Chatta Bakhtawar", 33.66550481, 73.15173418),
                ("Green Avenue", 33.66773393, 73.14971672),
                ("Park View city", 33.67427622, 73.14418612),
                ("Shahzad Town", 33.67618671, 73.1423078),
                ("NIH Allergy Center", 33.68542012, 73.13472496),
                ("NARC Colony", 33.68724354, 73.13117702),
                ("Rawal Dam Colony", 33.68792768, 73.12138409),
                ("School Board", 33.68873807, 73.11644481),
                ("Rawal Town", 33.68891172, 73.11286209),
                ("Garden Avenue", 33.68501927, 73.10656667),
                ("Margalla Town", 33.68149119, 73.10223211),
                ("ITP Centre", 33.67198119, 73.09326567),
                ("Sohan", 33.65651928, 73.09325521),
                ("Faizabad Interchange", 33.66691557, 73.08505201),
                ("I-8", 33.67342597, 73.08046914),
                ("Shakarparia", 33.68413203, 73.072542),
                ("TNT", 33.69725938, 73.06159648),
                ("PIMS Hospital", 33.70610123, 73.05205307)
            ],
            'FR-09': [
                ("Golara Morh", 33.70969129, 72.95523741),
                ("Home of Military Transport", 33.63233223, 72.96767205),
                ("Golra Morh Chowk", 33.62512929, 72.97071203),
                ("Kohinoor Mill", 33.61897282, 72.98136724),
                ("Kohinoor Mill Colony", 33.61642293, 72.98798578),
                ("Pir Wadhai Morh", 33.61594427, 72.99444521),
                ("British Homes", 33.61832812, 72.99956167),
                ("Social Security Hospital", 33.61991148, 73.00271892),
                ("CTTI Stop", 33.62543088, 73.01322),
                ("Westridge", 33.62665833, 73.01572592),
                ("Carriage Factory", 33.63030086, 73.02290935),
                ("Fauji Colony", 33.63309632, 73.02794045),
                ("Mandi Morh", 33.63466751, 73.03085576),
                ("Pully Stop I-10", 33.63784861, 73.03701505),
                ("CDA Stop", 33.64138065, 73.04357755),
                ("Katarian Pull", 33.64679147, 73.05347302),
                ("Katarian Chungi", 33.64881098, 73.05787084),
                ("Pindora Chungi", 33.65207237, 73.06405691),
                ("IJP", 33.65653201, 73.07204862),
                ("Faizabad", 33.66318257, 73.08522824),
                ("Sohan", 33.65947023, 73.09052323),
                ("Dhoke Kala Khan", 33.64980447, 73.09776893),
                ("Iqbal Town", 33.64587248, 73.10087402),
                ("Kuri road", 33.64226592, 73.10347458),
                ("Zia masjid", 33.63673447, 73.1076464),
                ("Khanna Pul Stop", 33.62925827, 73.11352419)
            ],
            'FR-10': [
                ("Golara Morh", 33.70969129, 72.95523741),
                ("26 no. Chungi", 33.63215158, 72.94468033),
                ("G-15/F-15", 33.63872635, 72.9268283),
                ("Tarnol", 33.65156055, 72.90896539),
                ("Safia road", 33.65838544, 72.90122733),
                ("Sara e kharbooza. Doke Paracha", 33.66141555, 72.89466027),
                ("D-17", 33.66938939, 72.8641333),
                ("Sangjani", 33.67488851, 72.85405182),
                ("B-17 gate no.1", 33.68666653, 72.84060894),
                ("B-17 gate no.2", 33.69412776, 72.83535973),
                ("Maragalla stop", 33.70512560, 72.82297501),
                ("Taxilla Bypass", 33.71124468, 72.81387052),
                ("Wahdat colony", 33.72331749, 72.80543381),
                ("Timber market", 33.73101712, 72.8044268),
                ("Taxilla Highway Stop", 33.73377947, 72.80364548)
            ],
            'FR-11': [
                ("Golara Morh", 33.70969129, 72.95523741),
                ("N5", 33.63228472, 72.94453106),
                ("Motorway chowk", 33.62860569, 72.9435493),
                ("NUST EME", 33.62412248, 72.95468772),
                ("Golra morh chowk", 33.62486132, 72.97143871),
                ("IMCG I-14/4", 33.62145687, 72.97081127),
                ("Riphah International University", 33.61685715, 72.96980987),
                ("I-14 Markaz", 33.61130963, 72.9694252),
                ("I-14/1 Park", 33.60879981, 72.96318263),
                ("Rafiullah Shaheed chowk", 33.60664292, 72.96056988),
                ("I-16 Markaz", 33.59756719, 72.93960192),
                ("PHA Apartments", 33.59416284, 72.93295265),
                ("Police Station Noon", 33.59177662, 72.92870443),
                ("Noon I-16 Stop", 33.59008334, 72.92539296)
            ],
            'FR-12': [
                ("Taxilla Highway Stop", 33.73377947, 72.80364548),
                ("Hassan Abdal", 33.82100597, 72.68010271)
            ],
            'FR-13': [
                ("Golara Morh", 33.70969129, 72.95523741),
                ("Fateh Jang Stop", 33.57108253, 72.64704862)
            ],
            'FR-14': [
                ("Bara Kahu", 33.73556201, 73.16539543),
                ("Malpur", 33.72977236, 73.14538823),
                ("Lakeview Park", 33.72333337, 73.13627209),
                ("Dhokri", 33.71155371, 73.1068884),
                ("Kashmir Chowk", 33.70679023, 73.10608374),
                ("Rawal Chowk", 33.69303417, 73.11013669),
                ("Garden Avenue", 33.68501927, 73.10656667),
                ("Margalla Town", 33.68149119, 73.10223211),
                ("ITP Centre", 33.67198119, 73.09326567),
                ("Sohan", 33.65651928, 73.09325521),
                ("Faizabad Metro Station", 33.66691557, 73.08505201),
                ("IJP", 33.65603214, 73.07197937),
                ("Pindora Chungi", 33.65207237, 73.06405691),
                ("Katarian Chungi", 33.64881098, 73.05787084),
                ("Katarian Pull", 33.64679147, 73.05347302),
                ("CDA Stop", 33.64138065, 73.04357755),
                ("Pully Stop I-10", 33.63784861, 73.03701505),
                ("Mandi Morh", 33.63466751, 73.03085576)
            ],
            'FR-14A': [
                ("Bara Kahu", 33.73556201, 73.16539543),
                ("Satra Meel Stop", 33.76365793, 73.21934328)
            ],
            'FR-15': [
                ("Gulberg Green", 33.59653227, 73.13815014),
                ("Fazaia stop", 33.62070188, 73.12009182),
                ("Gangal", 33.61303533, 73.12590285),
                ("Koral town", 33.60613877, 73.13103194),
                ("Gulber Green", 33.59633629, 73.13833649),
                ("Pagh Chowk", 33.58631715, 73.14589759),
                ("PWD", 33.57598452, 73.15376293),
                ("Soan garden E block", 33.56737549, 73.15999536),
                ("Soan garden G block", 33.56038778, 73.1651674),
                ("Soan garden H block", 33.55702451, 73.16766374),
                ("River Garden", 33.55192953, 73.17149045),
                ("Kaak Pul", 33.54283505, 73.17823205),
                ("DHA Gate 8", 33.53649327, 73.18125157),
                ("DHA Gate 7", 33.53239391, 73.18110209),
                ("Suparco", 33.51823887, 73.17926098),
                ("T Chowk", 33.51513917, 73.17880826)
            ]
        }
        
        # Merge all routes data
        #all_routes_stops.update(remaining_routes_stops)
        
        # Insert routes
        for route_id, route_info in routes_info.items():
            cursor.execute('''
            INSERT INTO routes (id, name, source, destination)
            VALUES (?, ?, ?, ?)
            ''', (route_id, route_info['name'], route_info['source'], route_info['destination']))
        
        # Insert stops for each route
        for route_id, stops_data in all_routes_stops.items():
            for name, lat, lng in stops_data:
                cursor.execute('''
                INSERT INTO stops (name, latitude, longitude, route_id)
                VALUES (?, ?, ?, ?)
                ''', (name, lat, lng, route_id))
        
        conn.commit()
        conn.close()
        print(f"✅ Populated database with {len(routes_info)} routes")
    
    def get_all_routes(self) -> List[Dict]:
        """Get all available routes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, name, source, destination, total_distance FROM routes')
        routes = []
        
        for row in cursor.fetchall():
            routes.append({
                'route_id': row[0],
                'name': row[1],
                'source': row[2],
                'destination': row[3],
                'total_distance': row[4]
            })
        
        conn.close()
        return routes
    
    def get_route_stops(self, route_id: str) -> List[Stop]:
        """Get all stops for a route"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, name, latitude, longitude
        FROM stops
        WHERE route_id = ?
        ORDER BY id
        ''', (route_id,))
        
        stops = []
        for row in cursor.fetchall():
            stops.append(Stop(
                stop_id=row[0],
                name=row[1],
                latitude=row[2],
                longitude=row[3]
            ))
        
        conn.close()
        return stops
    
    def save_bus(self, bus: Bus):
        """Save bus state to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT OR REPLACE INTO buses 
        (id, route_id, current_lat, current_lng, speed, status, next_stop_index, last_update, direction)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            bus.bus_id, bus.route_id, bus.current_lat, bus.current_lng,
            bus.speed, bus.status, bus.next_stop_index, 
            bus.last_update.isoformat(), bus.direction
        ))
        
        conn.commit()   
        conn.close()
    
    def delete_bus(self, bus_id: str):
        """Delete a bus from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM buses WHERE id = ?', (bus_id,))
        
        conn.commit()
        conn.close()
    
    def get_all_buses(self) -> List[Bus]:
        """Get all buses from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM buses')
        buses = []
        
        for row in cursor.fetchall():
            buses.append(Bus(
                bus_id=row[0],
                route_id=row[1],
                current_lat=row[2],
                current_lng=row[3],
                speed=row[4],
                status=row[5],
                next_stop_index=row[6],
                last_update=datetime.fromisoformat(row[7]),
                direction=row[8] if len(row) > 8 else 'forward'
            ))
        
        conn.close()
        return buses