#!/usr/bin/env python3
import json
import os
import subprocess

dependenciesout=set()

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
        dependenciesout.add(check)
    cmd=data["command"]
    if data["liborexe"]=="lib":
        #print("YEYYY")
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
        dependenciesout.add(check)
    cmd=data["command"]
    if data["liborexe"]=="lib":
        cmd+" -c"
    for dep in dependenciesout:
        cmd+=" "
        cmd+=dep
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

def main():
    path="./"
    process_module(path)

if __name__ == '__main__':
    main()
