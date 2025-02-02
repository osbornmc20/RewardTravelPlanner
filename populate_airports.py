from app import app, db
from models import Airport

# List of top 100 airports worldwide
airports_data = [
    # United States
    {"code": "ATL", "name": "Hartsfield-Jackson Atlanta International Airport", "city": "Atlanta", "country": "United States"},
    {"code": "DFW", "name": "Dallas/Fort Worth International Airport", "city": "Dallas", "country": "United States"},
    {"code": "DEN", "name": "Denver International Airport", "city": "Denver", "country": "United States"},
    {"code": "ORD", "name": "O'Hare International Airport", "city": "Chicago", "country": "United States"},
    {"code": "LAX", "name": "Los Angeles International Airport", "city": "Los Angeles", "country": "United States"},
    {"code": "CLT", "name": "Charlotte Douglas International Airport", "city": "Charlotte", "country": "United States"},
    {"code": "MCO", "name": "Orlando International Airport", "city": "Orlando", "country": "United States"},
    {"code": "LAS", "name": "Harry Reid International Airport", "city": "Las Vegas", "country": "United States"},
    {"code": "PHX", "name": "Phoenix Sky Harbor International Airport", "city": "Phoenix", "country": "United States"},
    {"code": "MIA", "name": "Miami International Airport", "city": "Miami", "country": "United States"},
    {"code": "SEA", "name": "Seattle-Tacoma International Airport", "city": "Seattle", "country": "United States"},
    {"code": "IAH", "name": "George Bush Intercontinental Airport", "city": "Houston", "country": "United States"},
    {"code": "JFK", "name": "John F. Kennedy International Airport", "city": "New York", "country": "United States"},
    {"code": "EWR", "name": "Newark Liberty International Airport", "city": "Newark", "country": "United States"},
    {"code": "SFO", "name": "San Francisco International Airport", "city": "San Francisco", "country": "United States"},
    {"code": "BOS", "name": "Boston Logan International Airport", "city": "Boston", "country": "United States"},
    {"code": "DTW", "name": "Detroit Metropolitan Airport", "city": "Detroit", "country": "United States"},
    {"code": "MSP", "name": "Minneapolis-Saint Paul International Airport", "city": "Minneapolis", "country": "United States"},
    {"code": "PHL", "name": "Philadelphia International Airport", "city": "Philadelphia", "country": "United States"},
    {"code": "LGA", "name": "LaGuardia Airport", "city": "New York", "country": "United States"},
    
    # Asia
    {"code": "HND", "name": "Tokyo Haneda Airport", "city": "Tokyo", "country": "Japan"},
    {"code": "PVG", "name": "Shanghai Pudong International Airport", "city": "Shanghai", "country": "China"},
    {"code": "CAN", "name": "Guangzhou Baiyun International Airport", "city": "Guangzhou", "country": "China"},
    {"code": "ICN", "name": "Seoul Incheon International Airport", "city": "Seoul", "country": "South Korea"},
    {"code": "HKG", "name": "Hong Kong International Airport", "city": "Hong Kong", "country": "China"},
    {"code": "BKK", "name": "Suvarnabhumi Airport", "city": "Bangkok", "country": "Thailand"},
    {"code": "SIN", "name": "Singapore Changi Airport", "city": "Singapore", "country": "Singapore"},
    {"code": "KUL", "name": "Kuala Lumpur International Airport", "city": "Kuala Lumpur", "country": "Malaysia"},
    {"code": "NRT", "name": "Tokyo Narita International Airport", "city": "Tokyo", "country": "Japan"},
    {"code": "DEL", "name": "Indira Gandhi International Airport", "city": "Delhi", "country": "India"},
    {"code": "BOM", "name": "Chhatrapati Shivaji International Airport", "city": "Mumbai", "country": "India"},
    {"code": "CGK", "name": "Soekarno-Hatta International Airport", "city": "Jakarta", "country": "Indonesia"},
    
    # Middle East
    {"code": "DXB", "name": "Dubai International Airport", "city": "Dubai", "country": "United Arab Emirates"},
    {"code": "DOH", "name": "Hamad International Airport", "city": "Doha", "country": "Qatar"},
    {"code": "AUH", "name": "Abu Dhabi International Airport", "city": "Abu Dhabi", "country": "United Arab Emirates"},
    {"code": "IST", "name": "Istanbul Airport", "city": "Istanbul", "country": "Turkey"},
    
    # Europe
    {"code": "LHR", "name": "London Heathrow Airport", "city": "London", "country": "United Kingdom"},
    {"code": "CDG", "name": "Charles de Gaulle Airport", "city": "Paris", "country": "France"},
    {"code": "AMS", "name": "Amsterdam Airport Schiphol", "city": "Amsterdam", "country": "Netherlands"},
    {"code": "FRA", "name": "Frankfurt Airport", "city": "Frankfurt", "country": "Germany"},
    {"code": "MAD", "name": "Adolfo Suárez Madrid–Barajas Airport", "city": "Madrid", "country": "Spain"},
    {"code": "BCN", "name": "Barcelona–El Prat Airport", "city": "Barcelona", "country": "Spain"},
    {"code": "FCO", "name": "Leonardo da Vinci International Airport", "city": "Rome", "country": "Italy"},
    {"code": "MUC", "name": "Munich Airport", "city": "Munich", "country": "Germany"},
    {"code": "ZRH", "name": "Zurich Airport", "city": "Zurich", "country": "Switzerland"},
    {"code": "CPH", "name": "Copenhagen Airport", "city": "Copenhagen", "country": "Denmark"},
    {"code": "DUB", "name": "Dublin Airport", "city": "Dublin", "country": "Ireland"},
    {"code": "LGW", "name": "London Gatwick Airport", "city": "London", "country": "United Kingdom"},
    {"code": "MXP", "name": "Milan Malpensa Airport", "city": "Milan", "country": "Italy"},
    {"code": "ARN", "name": "Stockholm Arlanda Airport", "city": "Stockholm", "country": "Sweden"},
    {"code": "VIE", "name": "Vienna International Airport", "city": "Vienna", "country": "Austria"},
    
    # Oceania
    {"code": "SYD", "name": "Sydney Airport", "city": "Sydney", "country": "Australia"},
    {"code": "MEL", "name": "Melbourne Airport", "city": "Melbourne", "country": "Australia"},
    {"code": "BNE", "name": "Brisbane Airport", "city": "Brisbane", "country": "Australia"},
    {"code": "AKL", "name": "Auckland Airport", "city": "Auckland", "country": "New Zealand"},
    
    # Canada
    {"code": "YYZ", "name": "Toronto Pearson International Airport", "city": "Toronto", "country": "Canada"},
    {"code": "YVR", "name": "Vancouver International Airport", "city": "Vancouver", "country": "Canada"},
    {"code": "YUL", "name": "Montréal-Pierre Elliott Trudeau International Airport", "city": "Montreal", "country": "Canada"},
    {"code": "YYC", "name": "Calgary International Airport", "city": "Calgary", "country": "Canada"},
    
    # Latin America
    {"code": "MEX", "name": "Mexico City International Airport", "city": "Mexico City", "country": "Mexico"},
    {"code": "GRU", "name": "São Paulo/Guarulhos International Airport", "city": "São Paulo", "country": "Brazil"},
    {"code": "BOG", "name": "El Dorado International Airport", "city": "Bogota", "country": "Colombia"},
    {"code": "SCL", "name": "Santiago International Airport", "city": "Santiago", "country": "Chile"},
    {"code": "LIM", "name": "Jorge Chávez International Airport", "city": "Lima", "country": "Peru"},
    {"code": "GIG", "name": "Rio de Janeiro/Galeão International Airport", "city": "Rio de Janeiro", "country": "Brazil"},
    {"code": "CUN", "name": "Cancún International Airport", "city": "Cancún", "country": "Mexico"},
    
    # Additional US Airports
    {"code": "BWI", "name": "Baltimore/Washington International Airport", "city": "Baltimore", "country": "United States"},
    {"code": "IAD", "name": "Washington Dulles International Airport", "city": "Washington", "country": "United States"},
    {"code": "DCA", "name": "Ronald Reagan Washington National Airport", "city": "Washington", "country": "United States"},
    {"code": "SAN", "name": "San Diego International Airport", "city": "San Diego", "country": "United States"},
    {"code": "MDW", "name": "Chicago Midway International Airport", "city": "Chicago", "country": "United States"},
    {"code": "TPA", "name": "Tampa International Airport", "city": "Tampa", "country": "United States"},
    {"code": "PDX", "name": "Portland International Airport", "city": "Portland", "country": "United States"},
    {"code": "SLC", "name": "Salt Lake City International Airport", "city": "Salt Lake City", "country": "United States"},
    
    # Additional European Airports
    {"code": "OSL", "name": "Oslo Airport", "city": "Oslo", "country": "Norway"},
    {"code": "HEL", "name": "Helsinki-Vantaa Airport", "city": "Helsinki", "country": "Finland"},
    {"code": "WAW", "name": "Warsaw Chopin Airport", "city": "Warsaw", "country": "Poland"},
    {"code": "PRG", "name": "Václav Havel Airport Prague", "city": "Prague", "country": "Czech Republic"},
    {"code": "BRU", "name": "Brussels Airport", "city": "Brussels", "country": "Belgium"},
    {"code": "ATH", "name": "Athens International Airport", "city": "Athens", "country": "Greece"},
    {"code": "LIS", "name": "Lisbon Airport", "city": "Lisbon", "country": "Portugal"},
    
    # Additional Asian Airports
    {"code": "TPE", "name": "Taiwan Taoyuan International Airport", "city": "Taipei", "country": "Taiwan"},
    {"code": "MNL", "name": "Ninoy Aquino International Airport", "city": "Manila", "country": "Philippines"},
    {"code": "HAN", "name": "Noi Bai International Airport", "city": "Hanoi", "country": "Vietnam"},
    {"code": "SGN", "name": "Tan Son Nhat International Airport", "city": "Ho Chi Minh City", "country": "Vietnam"},
    {"code": "KIX", "name": "Kansai International Airport", "city": "Osaka", "country": "Japan"},
    
    # Additional Middle Eastern Airports
    {"code": "RUH", "name": "King Khalid International Airport", "city": "Riyadh", "country": "Saudi Arabia"},
    {"code": "JED", "name": "King Abdulaziz International Airport", "city": "Jeddah", "country": "Saudi Arabia"},
    {"code": "TLV", "name": "Ben Gurion Airport", "city": "Tel Aviv", "country": "Israel"},
    
    # Additional Oceania Airports
    {"code": "PER", "name": "Perth Airport", "city": "Perth", "country": "Australia"},
    {"code": "ADL", "name": "Adelaide Airport", "city": "Adelaide", "country": "Australia"},
    {"code": "CHC", "name": "Christchurch International Airport", "city": "Christchurch", "country": "New Zealand"},
]

def populate_airports():
    with app.app_context():
        # Clear existing airports
        Airport.query.delete()
        
        # Add new airports
        for airport_data in airports_data:
            airport = Airport(**airport_data)
            db.session.add(airport)
        
        db.session.commit()
        print(f"Airports database populated successfully with {len(airports_data)} airports!")

if __name__ == "__main__":
    populate_airports()
