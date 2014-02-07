#!/usr/bin/python
import re
import nltk
import sys
import getopt

# defines the ngram size
NGRAM_LEVEL = 3 

# tolerance of accepting unappeared ngram ( 0.8 means if 80% of ngrams in the sentence are not in the LM, the sentence is identified as an unknown language)
FOREIGN_THRESHOLD = 0.8 

# if ngrams are padded with SSS
IS_PAD = True


def build_LM(in_file):
    
    print 'building language models...'

    def process_file(in_file):
        f = file(in_file)
        lang = {'malaysian': [], 'indonesian':[], 'tamil':[]}
        for line in f:
            for key in lang:
                if line.startswith(key):
                    line = line.replace(key+' ', '')
                    lang[key].append(line)
        return lang

    def build_ngram(source):
        ngram_set = {}
        for key, value in source.items():
            ngram = []
            for line in value:
                if IS_PAD:
                    ngram.extend(nltk.ngrams(line.strip(), NGRAM_LEVEL, pad_left=True, pad_right=True, pad_symbol='SSS'))
                else:
                    ngram.extend(nltk.ngrams(line.strip(), NGRAM_LEVEL))
            ngram_set[key] = ngram
        return ngram_set

    def build_model(ngram_set):
        def build_list_of_units(ngram_set):
            ngram_unit = []
            for key, value in ngram_set.items():
                ngram_unit = list(set(value)|set(ngram_unit))
            return ngram_unit
        def build_empty_frequency_model(ngram_unit):
            models = {'malaysian': {}, 'indonesian':{}, 'tamil':{}}
            for key in models:
                models[key] = { unit:1 for unit in ngram_unit }
            return models
        def build_probability_model(ngram_set, empty_model):
            for key in ngram_set:
                ngram = ngram_set[key] # [(a, b, c, d) , (d, e, f, g)...]
                model = empty_model[key]
                #print ngram[1]
                for unit in ngram:
                    model[unit] = model[unit] + 1     
                total_freq = sum(model.values())
                for k in model:
                    model[k] = float(model[k]) / float(total_freq) * float(10000)
                sum_freq = float(0)
                for k, v in model.items():
                    sum_freq = sum_freq + v
                empty_model[key] = model
            return empty_model
        ngram_unit = build_list_of_units(ngram_set)
        empty_model = build_empty_frequency_model(ngram_unit)
        models = build_probability_model(ngram_set, empty_model)
        return models

    source = process_file(in_file)
    ngram_set = build_ngram(source)
    LM = build_model(ngram_set)
    return LM

    # This is an empty method
    # Pls implement your code in below
    
def test_LM(in_file, out_file, LM):
    """
    test the language models on new URLs
    each line of in_file contains an URL
    you should print the most probable label for each URL into out_file
    """
    print "testing language models..."


    def break_line(line):
        units = nltk.ngrams(line, NGRAM_LEVEL)
        return units

    def init_results():
        results = {'malaysian': float(1.0), 'indonesian':float(1.0), 'tamil':float(1.0)}
        return results

    def calculate_results(units, LM, results, out_file, line):
        for key in results:
            foreign = 0
            for u in units:
                if u in LM[key]:
                    results[key] = results[key] * LM[key][u]
                else:
                    foreign = foreign + 1
            foreign_index = float(foreign) / (float(len(units)))
            if foreign_index > FOREIGN_THRESHOLD:
                results[key] = -1

        if max(results.values()) is -1:
            language = 'other'
        else:
            language = max(results, key=results.get)

        # wirte into file
        output_line = language + " " + line
        o = file(out_file, 'a')
        o.write(output_line)
        o.close()
    
    f = file(in_file)
    for line in f:
        units = break_line(line)
        #print units
        results = init_results()
        calculate_results(units, LM, results, out_file, line)

    print "test completed."
    
def usage():
    print "usage: " + sys.argv[0] + " -b input-file-for-building-LM -t input-file-for-testing-LM -o output-file"

input_file_b = input_file_t = output_file = None
try:
    opts, args = getopt.getopt(sys.argv[1:], 'b:t:o:')
except getopt.GetoptError, err:
    usage()
    sys.exit(2)
for o, a in opts:
    if o == '-b':
        input_file_b = a
    elif o == '-t':
        input_file_t = a
    elif o == '-o':
        output_file = a
    else:
        assert False, "unhandled option"
if input_file_b == None or input_file_t == None or output_file == None:
    usage()
    sys.exit(2)

LM = build_LM(input_file_b)
test_LM(input_file_t, output_file, LM)
