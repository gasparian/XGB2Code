import re

def xgb_get_code(model=None, spacer_base="    ", print_only=True, path=None, lang='C', packing_in_line=True):

	"""Trained ML model exporting.
    Parameters
    ----------
    model : model instance
        xgboost regressor model.
    spacer_base : str
        initial spaces to decorate code for readability
    print_only : bool/str, (True / False / 'both')
        Prints output code or dumps it to text file
    path : str
        path where code will be saved
    lang : str, default 'C', ('C' / 'Python')
        in which language to convert
    packing_in_line : bool
    	If True, each tree will be in one line.

    """
    
    def recurse_print(left, right, threshold, features, value, node, depth):
        if lang == 'C':
            spacer = spacer_base * depth
        elif lang == 'Py':
            spacer = spacer_base * (depth + 1)
        if (threshold[node] != -2):
            if lang == 'C':
                print(spacer + "if ( " + features[node] + " <= " + \
                      str(threshold[node]) + " ) {")
            elif lang == 'Py':
                print(spacer + "if " + features[node] + " <= " + \
                      str(threshold[node]) + ':')
            if left[node] != -1:
                    recurse_print(left, right, threshold, features, value,
                                  left[node], depth+1)
            if lang == 'C':
                print(spacer + "}\n" + spacer +"else {")
            elif lang == 'Py':
                print(spacer +"else:")
            if right[node] != -1:
                    recurse_print(left, right, threshold, features, value,
                                  right[node], depth+1)
            if lang == 'C':
                print(spacer + "}")
        else:
            target = value[node]
            if lang == 'C':
                print(spacer + 'leaf += ' + str(target) + ';')
            elif lang == 'Py':
                print(spacer + 'leaf += ' + str(target))

    def recurse_to_txt(left, right, threshold, features, value, node, depth):
        if lang == 'C':
            spacer = spacer_base * depth
        elif lang == 'Py':
            spacer = spacer_base * (depth + 1)
        if (threshold[node] != -2):
            if lang == 'C':
                if packing_in_line:
                    f.write("if ( " + features[node] + " <= " + \
                        str(threshold[node]) + " ) { ")
                else:
                    f.write(spacer + "if ( " + features[node] + " <= " + \
                      str(threshold[node]) + " ) {\n")
            elif lang == 'Py':
                f.write(spacer + "if " + features[node] + " <= " + \
                      str(threshold[node]) + ':\n')
            if left[node] != -1:
                    recurse_to_txt(left, right, threshold, features, value,
                                  left[node], depth+1)
            if lang == 'C':
                if packing_in_line:
                    f.write("} else { ")
                else:
                    f.write(spacer + "}\n" + spacer +"else {\n")
            elif lang == 'Py':
                f.write("else: ")
            if right[node] != -1:
                    recurse_to_txt(left, right, threshold, features, value,
                                  right[node], depth+1)
            if lang == 'C':
                if packing_in_line:
                    f.write("} ")
                else:
                    f.write(spacer + "}\n")
        else:
            target = value[node]
            if lang == 'C':
                if packing_in_line:
                    f.write('leaf += ' + str(target) + '; ')
                else:
                    f.write(spacer + 'leaf += ' + str(target) + ';\n')
            elif lang == 'Py':
                f.write(spacer + 'leaf += ' + str(target) + '\n')
                
    def parse_tree(tree_):
        tree_rows = re.split('\n', tree_)
        tree_split = []
        for row in tree_rows: 
            tree_split.append(re.split('\t|,|leaf|:|yes=|no=|missing=|\s+', row))
        tr = [[word for word in line if word] for line in tree_split if line != ['']]

        for i, line in enumerate(tr): 
            if line[1][0] == '[': tr[i] = line[:-1]

        n = len(tr)
        ids = {}
        thresholds, fnames, values, children_left, children_right = [[] for i in range(5)]

        for i, line in enumerate(tr):
            ids[int(line[0])] = i

        for i, line in enumerate(tr):
            if line[1][0] == '[':
                thresholds.append(float(re.split('<|>', line[1])[1][:-1]))
                fnames.append(re.split('<|>', line[1])[0][1:])
                values.append(None)
                children_left.append(ids[int(line[2])]) 
                children_right.append(ids[int(line[3])])
            else:
                thresholds.append(-2)
                fnames.append(-2)
                values.append(float(re.split('=', line[1])[1]))
                children_left.append(-1) 
                children_right.append(-1)

        thresholds = np.array(thresholds)
        values = np.array(values)
        children_left, children_right = np.array(children_left), np.array(children_right)  
        
        return children_left, children_right, thresholds, fnames, values
    
    def print_head(lang, features_names):
        if lang == 'C':
            print('float func(')
        elif lang == 'Py':
            print('def func(')
        if features_names:
            for name in features_names:
                print('\t' + '_'.join(re.split('\W+', name)) + ',')
        if lang == 'C':
            print('\t) {')
        elif lang == 'Py':
            print('\t):')
    
    def print_foot(lang):
        if lang == 'C':
            print('return leaf;\n}')
            print('float leaf = 0;\n')
        elif lang == 'Py':
            print('    return leaf\n')
            print('leaf = 0\n')
            
    def txt_head(lang, features_names):
        if lang == 'C':
            f.write('\nfloat func(\n')
            if features_names:
                for name in features_names:
                    f.write('   float ' + '_'.join(re.split('\W+', name)) + ',\n')
        elif lang == 'Py':
            f.write('def func(\n')
            if features_names:
                for name in features_names:
                    f.write('    ' + name + ',\n')
        f.write('\tleaf')
        if lang == 'C':
            f.write(') {\n')
        elif lang == 'Py':
            f.write('):\n')

    def txt_foot(lang):
        if lang == 'C':
            f.write('return leaf;\n}\n\n')
            f.write('float leaf = 0;\n\n')
            f.write('leaf = func(\n')
            if features_names:
                for name in features_names:
                    f.write('    ' + name + ',\n')
            f.write('\tleaf);\ncurrentGcorr_tree_grs=currentG_grs-leaf-0.5;\n')
        elif lang == 'Py':
            f.write('    return leaf\n\n')
            f.write('leaf = 0\n\n')
            
    forest = model.booster().get_dump()
        
    features_names = list(model.booster().get_fscore().keys())
          
    if print_only == True:
        print_head(lang, features_names)
        if type(forest) != str:
            for tree_ in forest:
                children_left, children_right, thresholds, fnames, values = parse_tree(tree_)
                recurse_print(children_left, children_right, thresholds, fnames, values, 0, 0)
                print('\n')
        else:
            children_left, children_right, thresholds, fnames, values = parse_tree(forest)
            recurse_print(children_left, children_right, thresholds, fnames, values, 0, 0)
            print('\n')
        print_foot(lang)
    elif print_only == 'both':
        print_head(lang, features_names)
        with open(path + '/xgb_dump.txt', 'w') as f:
            txt_head(lang, features_names)
            if type(forest) != str:
                for tree_ in forest:
                    children_left, children_right, thresholds, fnames, values = parse_tree(tree_)
                    recurse_print(children_left, children_right, thresholds, fnames, values, 0, 0)
                    recurse_to_txt(children_left, children_right, thresholds, fnames, values, 0, 0)
                    f.write('\n')
            else:
                children_left, children_right, thresholds, fnames, values = parse_tree(forest)
                recurse_print(children_left, children_right, thresholds, fnames, values, 0, 0)
                recurse_to_txt(children_left, children_right, thresholds, fnames, values, 0, 0)
                f.write('\n')
            print('\n')
            print_foot(lang)
            txt_foot(lang)
    else:
        with open(path + '/xgb_dump.txt', 'w') as f:
            txt_head(lang, features_names)
            if type(forest) != str:
                for tree_ in forest:
                    children_left, children_right, thresholds, fnames, values = parse_tree(tree_)
                    recurse_to_txt(children_left, children_right, thresholds, fnames, values, 0, 0)
                    f.write('\n')
            else:
                children_left, children_right, thresholds, fnames, values = parse_tree(forest)
                recurse_to_txt(children_left, children_right, thresholds, fnames, values, 0, 0)
                f.write('\n')
            txt_foot(lang)