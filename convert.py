import os
import csv
import re
import copy
import time
import argparse
from collections import defaultdict
import pandas as pd
import numpy as np


COLNAME2POS = {val: k for k, val in enumerate(['TOKENID', 'POSITION', 'TOKEN', 'CANONICAL', 'CATEGORY', 'DEF_ELEMENT', 'RELATION', 'REL_VERB_FRAME'])}

TERM_CAT_GEN_SENT_REL_file = 'TERM_CAT_GEN_SENT_REL.csv'
TERM_CATEGORY_file = 'TERM_CATEGORY.csv'
DEF_ELEMENTS_file = 'DEF_ELEMENTS.csv'
REL_REL_FRAME_file = 'REL_REL_FRAME.csv'


def read_sentences(fname):
    '''
    Reads Webanno csv and splits into smaller tables according to "sentence_index-token_index" column.
    Returns a list of DataFrame objects.
    '''
    table = pd.read_csv(fname, sep='\t', quoting=csv.QUOTE_NONE, comment='#', header=None, na_values='_', index_col=0, encoding='utf-8')
    table = table.replace('\xa0', ' ', regex=True)
    table.drop([colid for colid in table.columns if table[colid].isnull().all()], inplace=True, axis='columns')  # drop empty columns
    groups = [pd.DataFrame(data) for gid, data in table.groupby(by=lambda s: int(s.split('-')[0]))]
    return groups


def read_data(fname):
    '''
    Reads the data from Webanno csv and returns a list where every element is a dictionary representing one annotated sentence.
    '''
    groups = read_sentences(fname)

    # first, expand all cells with multiple values separated with "|" into new rows
    datalines = []
    new_groups = []
    for g in groups:
        new_rows = []
        for colid in g.columns[4:]:  # in first four columns this cannot happen
            ismulti = g[colid].str.contains('|', na=False, regex=False)
            multirows = g[ismulti]
            if not multirows.empty:
                for idx, row in multirows.iterrows():
                    values = [x.strip() for x in row[colid].split('|')]
                    g[colid].loc[idx] = values[0]
                    for i, val in enumerate(values[1:]):
                        # create a new row which only contains this column and row index (name), everything else is NaN
                        new = pd.Series(index=row.index, dtype=np.object, name=row.name + '-{}'.format(i+1))
                        new[colid] = val
                        new[COLNAME2POS['TOKEN']] = row[COLNAME2POS['TOKEN']]
                        new_rows.append(new)
        g = g.append(new_rows)
        # g = pd.concat(g, new_rows)
        new_groups.append(g)
    groups = new_groups

    for g in groups:
        for colid in g.columns[4:]:
            nonempty = g[~g[colid].isna()]
            for idx, row in nonempty.iterrows():
                # print(colid, idx, g[colid].loc[idx], type(g[colid].loc[idx]))
                if not g[colid].loc[idx].endswith(']'):
                    g[colid].loc[idx] += '[{}]'.format(str(time.time()).replace('.', ''))
                    # print(colid, idx, g[colid].loc[idx])

    for g in groups:
        linedata = defaultdict(list)
        # build sentence from tokens
        sentence = ' '.join([x.strip() for x in g[COLNAME2POS['TOKEN']].values.tolist()])
        sentence = re.sub('[ ]+[ ]+', ' ', sentence)
        for ch in ',.:;!?)]}':
            sentence = sentence.replace(' ' + ch, ch)
        for ch in '([{':
            sentence = sentence.replace(ch + ' ', ch)
        linedata['SENTENCE'] = [sentence]

        for colid in [COLNAME2POS[x] for x in ['DEF_ELEMENT', 'RELATION', 'REL_VERB_FRAME']]:
            for val in list(g[colid].value_counts().index):
                rows = g.loc[g[colid] == val]
                string = ' '.join([x.strip() for x in rows[COLNAME2POS['TOKEN']].values.tolist() if x.strip()])
                val = re.sub('\[[0-9]+\]$', '', val)  # strip ending number in brackets
                val = val.replace('\\', '')
                linedata[val].append(string)

        # category is separate because it yields two columns
        col = 'CATEGORY'
        colid = COLNAME2POS[col]
        for val in list(g[colid].value_counts().index):
            rows = g.loc[g[colid] == val]
            string = ' '.join([x.strip() for x in rows[COLNAME2POS['TOKEN']].values.tolist() if x.strip()])
            val = re.sub('\[[0-9]+\]$', '', val)  # strip ending number in brackets
            val = val.replace('\\', '')
            # linedata[col].append((val, string))
            linedata[col].append(val)
            linedata['CATEGORY_TEXT'].append(string)

        datalines.append(linedata)
    return datalines, new_groups


def export_TERM_CAT_GEN_SENT_REL(datalines, outfile, incell_separator='|'):
    cols = set()
    for d in datalines:
        cols.update(d.keys())

    # order of columns
    first = ['DEFINIENDUM', 'CATEGORY', 'CATEGORY_TEXT', 'SENTENCE']
    cols = first + sorted(list(cols - set(first)))

    rows = []
    for row in datalines:
        if len(row['DEFINIENDUM']) < 1:
            continue
        if len(row['DEFINIENDUM']) > 1:
            for d in row['DEFINIENDUM']:
                new = copy.copy(row)
                new['DEFINIENDUM'] = [d]
                rows.append(new)
        else:
            rows.append(copy.copy(row))
    for row in rows:
        for key in row:
            row[key] = incell_separator.join(row[key])

    with open(outfile, 'w') as csvfile:
        fieldnames = cols
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def export_TERM_CATEGORY(datalines, outfile):
    with open(outfile, 'w') as csvfile:
        fieldnames = ['TERM', 'CATEGORY']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for line in datalines:
            for term, category in zip(line['CATEGORY_TEXT'], line['CATEGORY']):
                writer.writerow({'TERM': term, 'CATEGORY': category})


def export_DEF_ELEMENTS(datalines, outfile, incell_separator='|'):
    rows = []
    for row in datalines:
        if len(row['DEFINIENDUM']) < 1:
            # print('skipping:', row)
            # print(' ')
            continue
        if len(row['DEFINIENDUM']) > 1:
            for d in row['DEFINIENDUM']:
                new = copy.copy(row)
                new['DEFINIENDUM'] = [d]
                rows.append(new)
        else:
            rows.append(copy.copy(row))
    for row in rows:
        for key in row:
            row[key] = incell_separator.join(row[key])

    with open(outfile, 'w') as csvfile:
        fieldnames = ['DEFINIENDUM', 'DEFINITOR', 'GENUS', 'SPECIES', 'SENTENCE']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            out = {k: row[k] for k in fieldnames if k in row}
            writer.writerow(out)


def export_REL_REL_FRAME(datalines, groups, outfile):
    fieldnames = ['REL_LABEL', 'REL_TOK', 'REL_FRAME']
    rows = []
    RELCOL = COLNAME2POS['RELATION']
    for g in groups:
        relations = set(g[RELCOL][~g[RELCOL].isna()].values.tolist())
        for relation in relations:
            rowsel = g[RELCOL].str.contains(relation, na=False, regex=False)
            miniframe = g[rowsel]

            # collect frame tokens
            frames = set(miniframe[COLNAME2POS['REL_VERB_FRAME']].values) - {np.nan}
            frametokens = []
            for frame in frames:
                subrowsel = miniframe[COLNAME2POS['REL_VERB_FRAME']].str.contains(frame, na=False, regex=False)
                subminiframe = miniframe[subrowsel]
                frametokens.append(' '.join(subminiframe[COLNAME2POS['TOKEN']].values))

            row = {'REL_LABEL': re.sub('\[[0-9]+\]$', '', relation).replace('\\', ''),  # strip ending number in brackets and \
                   'REL_TOK': ' '.join(miniframe[COLNAME2POS['TOKEN']].values),
                   'REL_FRAME': '|'.join(frametokens)
                   }
            rows.append(row)

    with open(outfile, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            out = {k: row[k] for k in fieldnames if k in row}
            writer.writerow(out)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A converter from WebAnno tsv to csv (multiple values per cell may occur)',
                                     epilog="Note: this converter assumes at least 5 annotations per token:\
                                            'CANONICAL', 'CATEGORY', 'DEF_ELEMENT', 'RELATION', 'REL_VERB_FRAME'.\
                                            They are specific to the TermFrame project.\
                                            Currently, the converter produces 4 csv files containing different selections of columns.")

    parser.add_argument("tsv_file", help="WebAnno tsv file")
    args = parser.parse_args()
    path, fname = os.path.split(os.path.abspath(args.tsv_file))
    base, suffix = os.path.splitext(fname)

    datalines, groups = read_data(args.tsv_file)
    export_TERM_CAT_GEN_SENT_REL(datalines, os.path.join(path, '{}__{}'.format(base, TERM_CAT_GEN_SENT_REL_file)))
    export_TERM_CATEGORY(datalines, os.path.join(path, '{}__{}'.format(base, TERM_CATEGORY_file)))
    export_DEF_ELEMENTS(datalines, os.path.join(path, '{}__{}'.format(base, DEF_ELEMENTS_file)))
    export_REL_REL_FRAME(datalines, groups, os.path.join(path, '{}__{}'.format(base, REL_REL_FRAME_file)))
