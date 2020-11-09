import sys

def set_basepath(steps=1):
    path0 = sys.path[0]
    split_path = path0.split('/')[:-steps]
    
    basepath = ""
    for it in split_path[:-1]:
        basepath += it
        basepath += '/'
    basepath += split_path[-1]
    
    sys.path.insert(0,basepath)
    
    return basepath