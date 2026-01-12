
def read_sales_data(filename):
    encodings = ['utf-8', 'latin-1', 'cp1252']
    for enc in encodings:
        try:
            with open(filename, 'r', encoding=enc) as f:
                lines = f.readlines()
                return [line.strip() for line in lines if line.strip()][1:]
        except UnicodeDecodeError:
            continue
    raise FileNotFoundError(f"Unable to read file: {filename}")
