import sys

def modify_species_names(line):
    prefixes = ['s__', 'g__', 'f__', 'o__', 'c__', 'p__']
    for prefix in prefixes:
        if line.startswith(prefix):
            # Remove the prefix and replace underscores with spaces
            return line[len(prefix):].replace('_', ' ')
    return line

def process_files(source_file, destination_file):
    # Read the first line from the source file and modify it
    with open(source_file, 'r') as file:
        first_line_source = file.readline()
    modified_first_line = '\t'.join(word.replace('.txt', '') for word in first_line_source.split())

    # Read all content from the destination file and modify species names
    with open(destination_file, 'r') as file:
        lines = file.readlines()
    modified_lines = [modify_species_names(line.strip()) for line in lines]

    # Combine the modified first line with the modified content of the destination file
    updated_content = modified_first_line + '\n' + '\n'.join(modified_lines)

    # Write the updated content back to the destination file
    with open(destination_file, 'w') as file:
        file.write(updated_content)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: ./processing_script.py <source_file_path> <destination_file_path>")
        sys.exit(1)

    source_file_path = sys.argv[1]
    destination_file_path = sys.argv[2]
    process_files(source_file_path, destination_file_path)
