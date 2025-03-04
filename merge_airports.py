import json

# Read the current airports-data.js
with open('static/js/modules/airports-data.js', 'r') as f:
    js_content = f.read()
    # Extract the array content between [ and ]
    start = js_content.find('[')
    end = js_content.rfind(']') + 1
    airports_js = json.loads(js_content[start:end])

# Read the airports from populate_airports.py
with open('populate_airports.py', 'r') as f:
    content = f.read()
    # Extract the array content between airports_data = [ and ]
    start = content.find('airports_data = [')
    start = content.find('[', start)
    end = content.find(']', start) + 1
    airports_py = eval(content[start:end])

# Create a set of existing airport codes to check for duplicates
existing_codes = set()
merged_airports = []

# Helper function to format airport entry
def format_airport(airport):
    return {
        'code': airport['code'],
        'name': airport['name'],
        'city': airport['city']
    }

# Process all airports, checking for duplicates
for airport in airports_js + airports_py:
    code = airport['code']
    if code not in existing_codes:
        existing_codes.add(code)
        merged_airports.append(format_airport(airport))

# Sort airports by code
merged_airports.sort(key=lambda x: x['code'])

# Generate the new JavaScript file content
js_output = """/**
 * Airport Data Module
 * Contains airport data for autocomplete functionality
 * List of major international airports
 */
const airports = %s;

// Export the module
window.airports = airports;
""" % json.dumps(merged_airports, indent=2)

# Write the new content
with open('static/js/modules/airports-data.js', 'w') as f:
    f.write(js_output)

print(f"Merged {len(merged_airports)} unique airports into airports-data.js")
