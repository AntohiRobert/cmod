#!/usr/bin/env python3
import json
import os
import subprocess
import shutil
import sys
import glob

#dependenciesout=set()

def get_compiler():
    gcc_path = shutil.which("g++-12")

    if not gcc_path:
        # Homebrew fallback paths (Apple Silicon + Intel)
        candidates = [
            "/opt/homebrew/opt/gcc@12/bin/g++-12",
            "/usr/local/opt/gcc@12/bin/g++-12"
        ]

        for c in candidates:
            if os.path.exists(c):
                gcc_path = c
                break

    if not gcc_path:
        raise RuntimeError("Homebrew GCC 12 not found")

    return gcc_path

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
    
    print("ENTER PROCESS DEP")
    path = "./dependencies/" + name

    if not os.path.isdir(path):
        clone_dep(name)

    file = path + "/cmodconfig.json"
    with open(file, "r") as f:
        data = json.load(f)

    for dep in data["dependencies"]:
        check = "./build/" + dep + ".o"
        if not os.path.exists(check):
            process_dep(dep)

    compiler = get_compiler()   # ✅ FIXED
    print(compiler)

    cmd = [compiler, "-fmodules-ts"]

    if data["liborexe"] == "lib":
        cmd.append("-c")

    for srcfile in data["srcfiles"]:
        files=glob.glob(os.path.join(path, srcfile))
        cmd.extend(files)
        #cmd.append(path + "/" + srcfile)

    cmd.extend (["-o", data["output"]]);
    print(cmd)

    try:
        result = subprocess.run(cmd, check=True)
        print(result)
    except subprocess.CalledProcessError as e:
        print("Error:", e)
        

def process_module(path):
    print(">>> ENTER PROCESS MODULE")
    build = path + "build"
    if not os.path.isdir(build):
        os.makedirs(build, exist_ok=True)

    deps = path + "dependencies"
    if not os.path.isdir(deps):
        os.makedirs(deps, exist_ok=True)

    file = path + "cmodconfig.json"
    with open(file, "r") as f:
        data = json.load(f)

    for dep in data["dependencies"]:
        check = "./build/" + dep + ".o"
        if not os.path.exists(check):
            process_dep(dep)

    compiler = get_compiler()   # ✅ FIXED

    cmd = [compiler, "-fmodules-ts"]

    if data["liborexe"] == "lib":
        cmd.append("-c")

    # ❌ replace wildcard with deterministic list
    for f in sorted(os.listdir("./build")):
        if f.endswith(".o"):
            cmd.append("./build/" + f)

    for srcfile in data["srcfiles"]:
        files=glob.glob(os.path.join(path,srcfile))
        cmd.extend(files)
        #cmd.append(srcfile)

    cmd.extend( ["-o", data["output"]])
    print(cmd)

    try:
        result = subprocess.run(cmd, check=True)
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
    #gcc = os.getenv("CMOD_CXX") or shutil.which("g++-11") or "g++"
    gcc=get_compiler()
    default["command"]=gcc+ " -fmodules-ts"
    default["dependencies"]=[]
    default["liborexe"]="exe"
    default["srcfiles"]=["*.cpp"]
    with open(file,'w') as f:
        json.dump(default, f, indent=4)
    
def usage():
    """This is what is shown on the terminal in case of incorrect usage"""
    print("Usage scenario 1:python cmod.py init")
    print("Usage scenario 2:python cmod.py addsrc main.cpp")
    print("Usage scenario 3:python cmod.py addep AntohiRobert_counter")
    print("Usage scenario 4:python cmod.py build [-nocache]")
    

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