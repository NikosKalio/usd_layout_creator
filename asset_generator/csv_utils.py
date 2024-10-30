import csv

def process_csv(input_file, output_file):
    type_counters = {}
    
    with open(input_file, 'r', newline='') as infile, open(output_file, 'w', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        
        # Write the header
        header = next(reader)
        new_header = ['Name'] + header[1:]
        writer.writerow(new_header)
        
        for row in reader:
            if row and len(row) > 1:
                item_type = row[1].lower().replace(' ', '_')
                type_counters[item_type] = type_counters.get(item_type, 0) + 1
                new_name = f"{item_type}_{type_counters[item_type]}"
                
                new_row = [new_name] + row[1:]
                writer.writerow(new_row)

# Usage
input_file = 'Lista Products - LIST.csv'
output_file = 'Lista Products - Enumerated.csv'
process_csv(input_file, output_file)

