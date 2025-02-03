/**
 * Airport Data Module
 * Contains airport data for autocomplete functionality
 * List of top 50 US airports by passenger traffic
 */
const airports = [
    // Top 10
    { code: 'ATL', name: 'Hartsfield-Jackson Atlanta International Airport', city: 'Atlanta' },
    { code: 'DFW', name: 'Dallas/Fort Worth International Airport', city: 'Dallas' },
    { code: 'DEN', name: 'Denver International Airport', city: 'Denver' },
    { code: 'ORD', name: "O'Hare International Airport", city: 'Chicago' },
    { code: 'LAX', name: 'Los Angeles International Airport', city: 'Los Angeles' },
    { code: 'CLT', name: 'Charlotte Douglas International Airport', city: 'Charlotte' },
    { code: 'MCO', name: 'Orlando International Airport', city: 'Orlando' },
    { code: 'LAS', name: 'Harry Reid International Airport', city: 'Las Vegas' },
    { code: 'PHX', name: 'Phoenix Sky Harbor International Airport', city: 'Phoenix' },
    { code: 'MIA', name: 'Miami International Airport', city: 'Miami' },
    
    // 11-20
    { code: 'SEA', name: 'Seattle-Tacoma International Airport', city: 'Seattle' },
    { code: 'IAH', name: 'George Bush Intercontinental Airport', city: 'Houston' },
    { code: 'JFK', name: 'John F. Kennedy International Airport', city: 'New York' },
    { code: 'EWR', name: 'Newark Liberty International Airport', city: 'Newark' },
    { code: 'FLL', name: 'Fort Lauderdale–Hollywood International Airport', city: 'Fort Lauderdale' },
    { code: 'MSP', name: 'Minneapolis−Saint Paul International Airport', city: 'Minneapolis' },
    { code: 'DTW', name: 'Detroit Metropolitan Airport', city: 'Detroit' },
    { code: 'BOS', name: 'Boston Logan International Airport', city: 'Boston' },
    { code: 'SLC', name: 'Salt Lake City International Airport', city: 'Salt Lake City' },
    { code: 'PHL', name: 'Philadelphia International Airport', city: 'Philadelphia' },
    
    // 21-30
    { code: 'LGA', name: 'LaGuardia Airport', city: 'New York' },
    { code: 'BWI', name: 'Baltimore/Washington International Airport', city: 'Baltimore' },
    { code: 'TPA', name: 'Tampa International Airport', city: 'Tampa' },
    { code: 'SAN', name: 'San Diego International Airport', city: 'San Diego' },
    { code: 'MDW', name: 'Chicago Midway International Airport', city: 'Chicago' },
    { code: 'BNA', name: 'Nashville International Airport', city: 'Nashville' },
    { code: 'IAD', name: 'Washington Dulles International Airport', city: 'Washington' },
    { code: 'DCA', name: 'Ronald Reagan Washington National Airport', city: 'Washington' },
    { code: 'AUS', name: 'Austin-Bergstrom International Airport', city: 'Austin' },
    { code: 'RDU', name: 'Raleigh-Durham International Airport', city: 'Raleigh' },
    
    // 31-40
    { code: 'SNA', name: 'John Wayne Airport', city: 'Santa Ana' },
    { code: 'HNL', name: 'Daniel K. Inouye International Airport', city: 'Honolulu' },
    { code: 'STL', name: 'St. Louis Lambert International Airport', city: 'St. Louis' },
    { code: 'PDX', name: 'Portland International Airport', city: 'Portland' },
    { code: 'MCI', name: 'Kansas City International Airport', city: 'Kansas City' },
    { code: 'SMF', name: 'Sacramento International Airport', city: 'Sacramento' },
    { code: 'DAL', name: 'Dallas Love Field', city: 'Dallas' },
    { code: 'RSW', name: 'Southwest Florida International Airport', city: 'Fort Myers' },
    { code: 'IND', name: 'Indianapolis International Airport', city: 'Indianapolis' },
    { code: 'CLE', name: 'Cleveland Hopkins International Airport', city: 'Cleveland' },
    
    // 41-50
    { code: 'MSY', name: 'Louis Armstrong New Orleans International Airport', city: 'New Orleans' },
    { code: 'PIT', name: 'Pittsburgh International Airport', city: 'Pittsburgh' },
    { code: 'SJC', name: 'Norman Y. Mineta San Jose International Airport', city: 'San Jose' },
    { code: 'CVG', name: 'Cincinnati/Northern Kentucky International Airport', city: 'Cincinnati' },
    { code: 'CMH', name: 'John Glenn Columbus International Airport', city: 'Columbus' },
    { code: 'OAK', name: 'Oakland International Airport', city: 'Oakland' },
    { code: 'SAT', name: 'San Antonio International Airport', city: 'San Antonio' },
    { code: 'MKE', name: 'Milwaukee Mitchell International Airport', city: 'Milwaukee' },
    { code: 'BUF', name: 'Buffalo Niagara International Airport', city: 'Buffalo' },
    { code: 'JAX', name: 'Jacksonville International Airport', city: 'Jacksonville' }
];

// Export the module
window.airports = airports;
