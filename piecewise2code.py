import re

def piecewise_dump(coefs, extremes, train, f_names, sc_mean, sc_std, path):

    #sv.piecewise_dump(coefs, extremes, train_sc_poly, list(train.drop(['T_g_'+str(c)], axis=1).columns),
    #                   sc_mean, sc_std, path + '/' + key + '_' + str(c) + '_pw.txt')

    def edit_string(string):
        string = re.split('\^', string)
        if len(string) != 1:
            string = (int(string[1]) * ('*' + string[0]))[1:]
        else:
            string = '*'.join(re.split('\s+', string[0]))
        return string

    names_match = {
        'currentF': ['freq_1', 'freq_2', 'freq_3'],
        'currentE': ['Exc_1', 'Exc_2', 'Exc_3'],
        'currentQ': ['Q_1', 'Q_2', 'Q_3'],
        'df1s': ['None_11', 'None_12', 'None_13']
    }

    feat = ';\n'.join(map(lambda i: f_names[i] + '=' + 
                        f_names[i] + '*' + str(1 / sc_std[i]) +
                            '-' + '(' + str(sc_mean[i] / sc_std[i]) + ')', range(len(f_names))))

    normj = '+'.join(map(lambda i: edit_string(train.columns[i]) + '*' + 'w[j][' + str(i) + ']', range(len(train.columns))))
    normj1 = '+'.join(map(lambda i: edit_string(train.columns[i]) + '*' + 'w[j-1][' + str(i) + ']', range(len(train.columns))))
    norm1j = '+'.join(map(lambda i: edit_string(train.columns[i]) + '*' + 'w[j+1][' + str(i) + ']', range(len(train.columns))))

    with open(path, 'w') as f:
        f.write('float scale(float freq, float min, float max) {\n\treturn (freq - min) / (max - min);\n};\n\n')
        f.write('float correct(void) {\n')
        f.write('float freq = currentF;\n')
        f.write('volatile float extremes[%s][%s] = {\n' % (len(extremes), len(extremes[1])))
        try:
            for value in extremes.values():
                if value != list(extremes.values())[-1]:
                    f.write('\t{%s, %s},\n' % (value[0], value[1]))
                else:
                    f.write('\t{%s, %s}\n' % (value[0], value[1]))
        except:
            f.write('\t{%s, %s}\n' % (extremes[1][0], extremes[1][1]))
        f.write('};\n\n')

        f.write('volatile float w[%s][%s] = {\n' % (len(coefs)-4, len(coefs[1])))
        for key in list(coefs.keys())[:-4]:
            if key != list(coefs.keys())[:-4][-1]:
                f.write('\t{%s},' % (','.join(str(coefs[key])[1:-1].split())) + '\n')
            else:
                f.write('\t{%s}' % (','.join(str(coefs[key])[1:-1].split())) + '\n')
        f.write('};\n\n')

        _ = 'volatile float '
        names = list(names_match.keys())
        for name in names:
            for fname in f_names:
                if fname in names_match[name]:
                    if name != names[-1]:
                        _ += fname + '=' + name + ', '
                    else:
                        _ += fname + '=' + name + ';'

        f.write(_ + '\n')
        f.write(feat + ';\n\n')
        f.write('int j;\n\n')            

        if (len(coefs.keys()) - 4) > 2:
            f.write('for ( j = 0; j < %s; j++ ) {\n' % (len(coefs.keys()) - 4))

            f.write('if ( j == 0 ) {\n')
            f.write('if ( freq < %s ) {\n' % (coefs['min']+coefs['step']))
            f.write('if ( if (%s + %s - %s) <= freq ) {\n' % (coefs['min'], coefs['step'], coefs['step']/coefs['overlap']))
            f.write('return ((1 - scale(freq, extremes[j][0], extremes[j][1])) * (%s) + scale(freq, extremes[j][0], extremes[j][1]) * (%s));\n}\n' % (normj, norm1j))
            f.write('else {\n')
            f.write('return (%s);\n\t\t\t}\n\t\t}\n\t}\n' % (normj))

            f.write('else if ( j == %s ) {\n' % (len(coefs.keys()) - 5))
            f.write('if ( %s + %s * ( j-1 ) < freq ) {\n' % (coefs['min'], coefs['step']))
            f.write('if ( freq <= %s + %s * ( j-1 ) + %s ) {\n' % (coefs['min'], coefs['step'], coefs['step']/coefs['overlap']))
            f.write('return ((1 - scale(freq, extremes[j-1][0], extremes[j-1][1])) * (%s) + scale(freq, extremes[j-1][0], extremes[j-1][1]) * (%s));\n}\n' % (normj1, normj))
            f.write('else {\n')
            f.write('return (%s);\n\t\t\t}\n\t\t}\n\t}\n' % (normj))

            f.write('else {\n')
            f.write('if ( %s + %s * ( j-1 ) <= freq ) {\n' % (coefs['min'], coefs['step']))
            f.write('if ( freq <= %s + %s * ( j-1 ) + %s ) {\n' % (coefs['min'], coefs['step'], coefs['step']/coefs['overlap']))
            f.write('return ((1 - scale(freq, extremes[j-1][0], extremes[j-1][1])) * (%s) + scale(freq, extremes[j-1][0], extremes[j-1][1]) * (%s));\n}\n' % (normj1, normj))
            f.write('else if ( %s + %s * ( j-1 ) - %s <= freq ) {\n' % (coefs['min'], coefs['step'], coefs['step']/coefs['overlap']))
            f.write('return ((1 - scale(freq, extremes[j][0], extremes[j][1])) * (%s) + scale(freq, extremes[j][0], extremes[j][1]) * (%s));\n}\n' % (normj, norm1j))
            f.write('else {\n')
            f.write('return (%s);\n\t\t\t}\n\t\t}\n\t}\n\n' % (normj))
        else:
            f.write('for ( j = 0; j < %s; j++ ) {\n' % (len(coefs.keys()) - 4))

            f.write('if ( j == 0 ) {\n')
            f.write('if ( freq < %s ) {\n' % (coefs['min']+coefs['step']))
            f.write('return ((1 - scale(freq, extremes[j][0], extremes[j][1])) * (%s) + scale(freq, extremes[j][0], extremes[j][1]) * (%s));\n}\n' % (normj, norm1j))
            f.write('else {\n')
            f.write('return (%s);\n\t\t\t}\n\t\t}\n' % (normj))

            f.write('else  {\n')
            f.write('if ( %s < freq ) {\n' % (coefs['min']+coefs['step']))
            f.write('if ( freq <= %s ) {\n' % ((coefs['min']+coefs['step'])+coefs['step']/coefs['overlap']))
            f.write('return ((1 - scale(freq, extremes[j-1][0], extremes[j-1][1])) * (%s) + scale(freq, extremes[j-1][0], extremes[j-1][1]) * (%s));\n}\n' % (normj1, normj))
            f.write('else {\n')
            f.write('return (%s);\n\t\t\t}\n\t\t}\n\t}\n' % (normj))

        f.write('}\n\n')
        f.write('return (0);\n')
        f.write('};\n\n')

        f.write('currentGcorr_grs=currentG_grs-correct();\n')