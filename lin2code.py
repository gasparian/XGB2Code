import re

def linear_model_dump(model, train, f_names, key,
                      sc_mean, sc_std, path, Clike=True, canalNo=1, print_only=True, model_weight=1.0):

    #sv.linear_model_dump(lr, train, f_names, 'poly',
    #                       sc_mean, sc_std, path, canalNo='BGT-5_c2', print_only='both')
    
    def edit_string(string):
        string = re.split('\^', string)
        if len(string) != 1:
            string = (int(string[1]) * ('*' + string[0]))[1:]
        else:
            string = '*'.join(re.split('\s+', string[0]))
        return string
    
    def print_():
        print('float model_weight_' + key + ': ' + str(model_weight) + ';\n')
        print('Regress. coefs:\n')
        print('volatile float w_%s' % key + '[%s]={' % len(train.columns) + (',').join([str(coef) for coef in coefs]) + '};')
        print('\nCorrection model:\n')
        print(feat + ';\n')
        print('currentGcorr_grs=currentG_grs-(' + norm + ');')
    
    def to_txt():
        f.write('float model_weight_' + key + '=' + str(model_weight) + ';\n' + 'volatile float w_%s' % key + '[%s]={' % len(f_names) + (',').join([str(coef) for coef in coefs]) + '};\n\n' + 
                        feat + ';\n\n' + 'currentGcorr_grs=currentG_grs-(' + norm + ');')
    
    try:
        coefs = model.coef_
    except:
        coefs = model
    if Clike:
        feat = ';\n'.join(map(lambda i: 'volatile float ' + f_names[i] + '=' + 
                    f_names[i] + '*' + str(1 / sc_std[i]) +
                        '-' + '(' + str(sc_mean[i] / sc_std[i]) + ')', range(len(f_names))))
        
        norm = '+'.join(map(lambda i: edit_string(train.columns[i]) + '*' + 'w_%s[' % key + str(i) + ']', range(len(train.columns))))
    else:
        out = '/*\ model weight: %s\n\nnf_scale_1, f_scale_2,E_scale_1,E_scale_2,Q_scale_1,Q_scale_2,der_scale_1(const),der_scale_2(const)\n--> regress coefs\nScale form: X * X_scale_1 + X_scale_2\nRegress: sum(w[i] * X[i]) for i in range(len(w))\n*/\n\n' % str(model_weight)
        #out = '/*\nf_scale_1, f_scale_2,Q_scale_1,Q_scale_2,der_scale_1(const),der_scale_2(const)\n--> regress coefs\nScale form: X * X_scale_1 + X_scale_2\nRegress: sum(w[i] * X[i]) for i in range(len(w))\n*/\n\n'
        for i,j in zip(sc_mean, sc_std):
            out += str(1/j) + '\n'
            out += str(i/j) + '\n'
        for coef in coefs:
            out += str(coef) + '\n'
    if print_only == True:
        print_()
    elif print_only == 'both':
        print_()
        with open(path + '/linear_model_dump_' + canalNo +'.txt', 'w') as f:
            if Clike:
                to_txt()
            else:
                f.write(out)
    else:
        with open(path + '/linear_model_dump_' + canalNo +'.txt', 'w') as f:
            if Clike:
                to_txt()
            else:
                f.write(out)