#!/usr/bin/env python3
import json
import os
import subprocess
import sys

#dependenciesout=set()

def clone_dep(name):
    user=""
    for l in name:
        if l=="_":
            break
        user+=l
    repo_url = "https://github.com/"+user+"/"+name+".git"
    target_directory = './dependencies/'+name
    command = ['git', 'clone', repo_url, target_directory]
    try:
        result = subprocess.run(command, check=True)
        print("Repo cloned:", target_directory)
    except subprocess.CalledProcessError as e:
        print("Error:", e)


def process_dep(name):
    path="./dependencies/"+name
    if not os.path.isdir(path):
        clone_dep(name)
    file=path+"/cmodconfig.json"
    with open(file,'r') as f:
        data=json.load(f)
    #dependenciesout.append(data["output"])
    for dep in data["dependencies"]:
        check="./build/"+dep+".o"
        if not os.path.exists(check):
            process_dep(dep)
        #dependenciesout.add(check)
    cmd=data["command"]
    if data["liborexe"]=="lib":
        cmd+=" -c"
    #cmd+=" "
    for srcfile in data["srcfiles"]:
        cmd+=" "
        cmd+=path+"/"+srcfile
    #cmd+=path+"/"+data["srcfiles"]
    cmd+=" -o "+data["output"]
    try:
        result = subprocess.run(cmd, shell=True,check=True)
        print(result)
    except subprocess.CalledProcessError as e:
        print("Error:", e)
        

def process_module(path):
    build=path+"build"
    if not os.path.isdir(build):
        try:
            result = subprocess.run("mkdir build", shell=True, check=True)
            print(result)
        except subprocess.CalledProcessError as e:
            print("Error:", e)
    deps=path+"dependencies"
    if not os.path.isdir(deps):
        try:
            result = subprocess.run("mkdir dependencies", shell=True, check=True)
            print(result)
        except subprocess.CalledProcessError as e:
            print("Error:", e)
    file=path+"cmodconfig.json"
    with open(file, 'r') as f:
        data = json.load(f)
    objfiles=""
    for dep in data["dependencies"]:
        check="./build/"+dep+".o"
        if not os.path.exists(check):
            process_dep(dep)
        #dependenciesout.add(check)
    cmd=data["command"]
    if data["liborexe"]=="lib":
        cmd+" -c"
    """
    for dep in dependenciesout:
        cmd+=" "
        cmd+=dep
    """
    cmd+=" ./build/*.o "
    #cmd+=" "
    #cmd+=objfiles
    for srcfile in data["srcfiles"]:
        cmd+=" "
        cmd+=srcfile
    #cmd+=" "
    #cmd+=data["srcfiles"]
    try:
        result = subprocess.run(cmd, shell=True,check=True)
        print(result)
    except subprocess.CalledProcessError as e:
        print("Error:", e)

def build():
    path="./"
    if len(sys.argv)>=3 and sys.argv[2]=="-nocache":
        try:
            result = subprocess.run("rm -rf dependencies build", shell=True, check=True)
            print(result)
        except subprocess.CalledProcessError as e:
            print("Error:", e)
    process_module(path)
    
def addsrc():
    path="./"
    file=path+"cmodconfig.json"
    with open(file, 'r') as f:
        data = json.load(f)
    data["srcfiles"].append(sys.argv[2])
    with open(file,'w') as f:
        json.dump(data, f, indent=4)
    print(data)
    
def addep():
    path="./"
    file=path+"cmodconfig.json"
    with open(file, 'r') as f:
        data = json.load(f)
    data["dependencies"].append(sys.argv[2])
    with open(file,'w') as f:
        json.dump(data, f, indent=4)
    print(data)
    
def init():
    path="./"
    file=path+"cmodconfig.json"
    default={}
    default["output"]="a.out"
    default["command"]="g++ -fmodules-ts"
    default["dependencies"]=[]
    default["liborexe"]="exe"
    default["srcfiles"]=["*.cpp"]
    with open(file,'w') as f:
        json.dump(default, f, indent=4)
    
def usage():
    """This is what is shown on the terminal in case of incorrect usage"""
    print("Usage scenario 1:python cmod.py build [-nocache]")
    print("Usage scenario 2:python cmod.py addsrc main.cpp")
    print("Usage scenario 3:python cmod.py addep AntohiRobert_counter")
    print("Usage scenario 4:python cmod.py init")
    

def main():
    if sys.argv[1] == "build":
        build()
    elif sys.argv[1] == "addsrc":
        addsrc()
    elif sys.argv[1] == "addep":
        addep()
    elif sys.argv[1] == "init":
        init()
    else:
        usage()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage()
    else:
        main()