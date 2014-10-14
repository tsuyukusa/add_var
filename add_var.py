#!/usr/bin/env python
# -*- coding: utf-8 -*-

#########################
##  add_var.py
#########################
help="""
#### 使用シーン #########
##
## GAUSSIANの入力ファイルで，z-matrixの変数を変えながら大量に入力ファイルを作る
##
#### 使い方 ############
##
## $ add_var.py [var_file] init.com
##
## init.com : 初期構造。増減したい値にはマーカーとして
##            $var1= をつける
## <var_file> : 初期構造に対して足し算したい値を記録したファイル。
##              特に指定しない場合は add_var.txt を参照する。
##              内部的にはpythonのスクリプトとして直接読み込む。
##              変数はvar1,var2...と無数に指定できる。var1,var2...は
##              1つのセットとしてとして振る舞う（例:基準振動の変位ベクトル）
##
##              var1とvar2が独立して振る舞ってほしいなら，add_var.pyを2回にわけて実行する
##"""

import sys
import os
import re

########################################################
## ファイルの生成用関数の定義 ##########################
########################################################
def make_inputfile(s):
    init_filename = init_filenames[s]
    # init_fileより $var[0-9]* の初期値と変数名の組を得る
    init_file = open(init_filename).readlines()
    init_var_indexandlines = [ [init_file.index(x),x] for x in init_file if re.search("\$var[0-9]*=",x) ]
    init_varindex = [ x[0] for x in init_var_indexandlines ] # $var= を含む行番号
    init_varlines = [ x[1] for x in init_var_indexandlines ] # $var= を含む行の内容
    init_var = [ x.split("=")[-1][0:-1] for x in init_varlines ] # $var=以降の値
    init_varnames = [ re.search("\$var[0-9]*=",x).group()[1:-1] for x in init_varlines] # $var[0-9]の名前

    # var_fileより読み込んだ変数名がinit_fileに存在しないならエラー終了
    diffset = set(var_varnames) - set(init_varnames)
    if len(diffset) > 0:
        print "in " +var_filename+  ":\t" + " ".join(var_varnames)
        print "in " +init_filename+ ":\t" + " ".join(init_varnames) + '\n'
        print var_filename + " contains undefined variable(s)!"
        print "you must define " + " ".join([x for x in diffset ]) + " in " + init_filename
        exit(1)

    ### var_fileより読み込んだ変数名とinit_fileの変数名が一致しないなら，無視するか判断させる
    #if set(var_varnames) != set(init_varnames):
    #    symdiff = set(var_varnames) ^ set(init_varnames)
    #    print "in " +var_filename+ ":\t" + " ".join(var_varnames)
    #    print "in " +init_filename+ ":\t" + " ".join(init_varnames)
    #
    # # ignore_var_difference は常に同じ選択肢を使うためのvar_file内のオプション
    #    if "ignore_var_difference" in globals():
    #        if ignore_var_difference :
    #            key = "y"
    #        else :
    #            key = "n"
    #    else:
    #        key = ""
    #
    #    while not key in ["y","n","q"]:
    #        key = raw_input( "IGNORE " + " ".join(list(symdiff)) + " ?  (y/n/q) > " )
    #    exec(  {"y":'print 1', "n": 'print 2', "q": 'exit(1)'}[key]  )
    #    exit(1)

    # var_fileに無いがinit_fileにある変数は無視するために除外
    diffset = set(init_varnames) - set(var_varnames)
    if len(diffset) > 0:
        for  v in diffset:
            delindex = init_varnames.index(v)
            del init_varnames[delindex]
            del init_var[delindex]
            del init_varlines[delindex]
            del init_varindex[delindex]

    # 初期値と足し算する
    out_var = []
    for i in range(0,len(init_var)) : 
        out_var.append(  map( (lambda x: str(float(init_var[i])+x)), globals()[init_varnames[i]] ) )

    init_varbefore = [ x.split("$")[0] for x in init_varlines ] # $var=以前の文字列

    out_var2 = []
    for i in range(0,len(out_var[0])):
        varvalue = [ x[i] for x in out_var ]
        out_var2.append(map( (lambda x,y: x+y+'\n'), init_varbefore,varvalue))

    global suffix
    global prefix
    # 書き出し用ファイル名を作成
    if "suffix" not in globals():
        suffix = [""] *len(out_var2)
    if "prefix" not in globals():
        prefix = [""] *len(out_var2)

    out_filename = []
    for i in range(0,len(out_var2)):
        out_filename.append(prefix[i]+basename[s]+suffix[i]+extension)

    # 書き出し用文字列を作成し，ファイルに保存する
    for i in range(0,len(out_var2)):
        for j in range(0,len(init_varindex)):
            init_file[init_varindex[j]] = out_var2[i][j]
        f = open(out_filename[i],'w')
        f.writelines(init_file)
        f.close()

    print init_filename+ " Done!"

########################################################
###  ここから実行行
########################################################

########################################################
## 引数と変数の準備 ####################################
########################################################

# 引数の取得
argvs = sys.argv
argc = len(argvs)

# var_fileとinit_fileの判別
var_filename = "var_file.txt"
if argc == 2 :
    init_filenames = argvs[1:]
elif argc >= 3 :
    if 'add_var.py setting file' in open(argvs[1]).readline() :
        var_filename = argvs[1]
        init_filenames = argvs[2:]
    else:
        init_filenames = argvs[1:]
else:
    print "usage: $ add_var.py [var_file] init.com"
    print help
    exit(1)

# ファイルの存在確認
exist_var_file = os.path.exists(var_filename)
exist_init_files = [ os.path.exists(x) for x in init_filenames ]

# init_fileとvar_fileのどちらかが存在しないなら終了
error = False
if not exist_var_file:
    print "error: file  " +var_filename+ " is not exist"
    error = True
for i in range(0,len(init_filenames)):
    if not exist_init_files[i]: 
        print "error: file " +init_filenames[i]+ " is not exist"
        error = True
if error:
    exit(1)

# var_fileの読み込み
execfile(var_filename)

# init_fileが複数あるなら，basenameとしてはinit_filenameの拡張子を除いたものを使う
if len(init_filenames) > 1:
    basename = [ ".".join(x.split(".")[0:-1]) for x in init_filenames ]
elif isinstance(basename,str):
    basename = [basename]

# 使用されているvar[数字]を見つける
var_varnames = globals().keys()
var_varnames = [ x for x in var_varnames if re.search("var[0-9]", x) ]

# varの次元が異なるならエラー終了
lengths = [ len(globals()[x]) for x in  var_varnames ]
if len(lengths) > 2:
    for i in range(0,len(lengths)):
        if lengths[1] != lengths[i]:
            print "error! var* must same length"
            exit(1)
########################################################
## ファイルの生成 ######################################
########################################################

for s in range(0,len(init_filenames)):
    make_inputfile(s)

