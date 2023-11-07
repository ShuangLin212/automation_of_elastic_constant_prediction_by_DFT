
import os
import shutil
import numpy as np
import sys

def step1_cij():
    shutil.copyfile(os.path.join('..', 'CONTCAR'), 'CONTCAR')
    with open('CONTCAR', 'r') as contcar, open('temp.rr0', 'w') as temp_rr0:
        lines = contcar.readlines()
        temp_rr0.writelines(lines[2:5])

def step2_cij(xx):
    rr = np.loadtxt('temp.rr0')
    dfm = xx
    dfALL = np.array([[dfm if i == j else 0 for j in range(6)] for i in range(6)])
    for N in range(6):
        ee = dfALL[N, :]
        ddff = np.array([[1+ee[i] if i == j else ee[5-i]/2 for j in range(3)] for i in range(3)])
        rrnew = np.dot(rr, ddff)
        filename = f'temp.df{N+1}'
        np.savetxt(filename, rrnew, fmt='%f')

def step3_cij():
    with open('CONTCAR', 'r') as contcar:
        lines = contcar.readlines()
    with open('temp.head', 'w') as temp_head:
        temp_head.writelines(lines[:2])
    with open('temp.tail', 'w') as temp_tail:
        temp_tail.writelines(lines[5:])
    
    for i in range(1, 7):
        os.makedirs(f's{i}', exist_ok=True)
        with open(f'temp.s{i}', 'w') as temp_s, open(f'temp.df{i}', 'r') as temp_df:
            temp_s.writelines(lines[:2])
            temp_s.writelines(temp_df.readlines())
            temp_s.writelines(lines[5:])
        
        shutil.copy('INCAR', f's{i}')
        shutil.copy('KPOINTS', f's{i}')
        shutil.copy('POTCAR', f's{i}')
        shutil.move(f'temp.s{i}', os.path.join(f's{i}', 'POSCAR'))
    
    for temp_file in ['temp.head', 'temp.tail', 'CONTCAR']:
        os.remove(temp_file)
    for i in range(1, 7):
        os.remove(f'temp.df{i}')

def cij_first(x):
    step1_cij()
    step2_cij(x)
    step3_cij()

def setup_environment_and_run_cij(directory):
    os.chdir(directory)
    os.makedirs('cij', exist_ok=True)
    shutil.copy('KPOINTS', 'KPOINTS.cij')
    if not os.path.isfile('INCAR.rx'):
        shutil.copy('INCAR', 'INCAR.rx')
    else:
        print('*** INCAR.rx in the Folder ***')
    
    with open('INCAR.rx', 'r') as incar_rx, open('INCAR.cij', 'w') as incar_cij:
        for line in incar_rx:
            if 'NSW' not in line and 'ISIF' not in line:
                incar_cij.write(line)
        incar_cij.write('ISIF = 2\n')
        incar_cij.write('NSW = 59\n')
    
    os.chdir('cij')
    shutil.copy('../INCAR.cij', 'INCAR')
    shutil.copy('../KPOINTS.cij', 'KPOINTS')
    shutil.copy('../CONTCAR', '.')
    shutil.copy('../POTCAR', '.')
    with open('../OUTCAR', 'r') as outcar, open('OUTCAR', 'w') as outcar_cij:
        lines = outcar.readlines()
        outcar_cij.writelines(lines[-1000:])
    
    for dir_name in ['m001', 'p001']:
        os.makedirs(dir_name, exist_ok=True)
        os.chdir(dir_name)
        cij_first(-0.01 if dir_name == 'm001' else 0.01)
        os.chdir('..')

# Check if a directory path was provided as a command-line argument
if len(sys.argv) > 1:
    directory_path = sys.argv[1]
    setup_environment_and_run_cij(directory_path)
else:
    print("Please provide the directory path as a command-line argument.")
