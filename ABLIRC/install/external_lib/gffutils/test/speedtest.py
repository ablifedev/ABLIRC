import gffutils
def create_test():
    gffutils.create_db(
        gffutils.example_filename(
            'dmel-all-no-analysis-r5.49_50k_lines.gff'),
        'a.db', merge_strategy='merge', force=True)

def split_test():
    for line in open(gffutils.example_filename('dmel-all-no-analysis-r5.49_50k_lines.gff')):
        gffutils.parser._split_keyvals(line.strip().split('\t')[-1])


split_test()
