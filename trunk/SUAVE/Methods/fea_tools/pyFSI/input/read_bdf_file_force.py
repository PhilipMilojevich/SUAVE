#
# Created:  Oct 2015, Anil Variyar
# Modified: May 2016, Anil Variyar
#
#Write a nastran file

#--imports---
import re
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy


from SUAVE.Methods.fea_tools.pyFSI.class_str.grid.class_structure import grid
from SUAVE.Methods.fea_tools.pyFSI.class_str.elements.class_structure import CTRIA3
from SUAVE.Methods.fea_tools.pyFSI.class_str.material.class_structure import PSHELL
from SUAVE.Methods.fea_tools.pyFSI.class_str.material.class_structure import PBARL
from SUAVE.Methods.fea_tools.pyFSI.class_str.material.class_structure import MAT1
from SUAVE.Methods.fea_tools.pyFSI.class_str.load_disp_bc.class_structure import FORCE
from SUAVE.Methods.fea_tools.pyFSI.class_str.load_disp_bc.class_structure import PLOAD
from SUAVE.Methods.fea_tools.pyFSI.class_str.load_disp_bc.class_structure import SPC
from SUAVE.Methods.fea_tools.pyFSI.class_str.io.class_structure import SU2_import

from SUAVE.Methods.fea_tools.pyFSI.class_str.io.nastran_datatype_write_formats import float_form
from SUAVE.Methods.fea_tools.pyFSI.class_str.io.nastran_datatype_write_formats import int_form
from SUAVE.Methods.fea_tools.pyFSI.class_str.io.nastran_datatype_write_formats import str_form

from SUAVE.Methods.fea_tools.pyFSI.class_str.io.nastran_datatype_write_formats import float_forms
from SUAVE.Methods.fea_tools.pyFSI.class_str.io.nastran_datatype_write_formats import int_forms
from SUAVE.Methods.fea_tools.pyFSI.utility_functions.pressure_interpolation import pressure_interpolation


from SUAVE.Methods.fea_tools.pyFSI.class_str.optimization.constraints.class_structure import DCONSTR
from SUAVE.Methods.fea_tools.pyFSI.class_str.optimization.constraints.class_structure import DCONADD
from SUAVE.Methods.fea_tools.pyFSI.class_str.optimization.constraints.class_structure import DRESP
from SUAVE.Methods.fea_tools.pyFSI.class_str.optimization.constraints.class_structure import DRESP1
from SUAVE.Methods.fea_tools.pyFSI.class_str.optimization.constraints.class_structure import DRESP2
from SUAVE.Methods.fea_tools.pyFSI.class_str.optimization.constraints.class_structure import DDVAL
from SUAVE.Methods.fea_tools.pyFSI.class_str.optimization.constraints.class_structure import DEQUATN
from SUAVE.Methods.fea_tools.pyFSI.class_str.optimization.constraints.class_structure import DESVAR
from SUAVE.Methods.fea_tools.pyFSI.class_str.optimization.constraints.class_structure import DVPREL1
from SUAVE.Methods.fea_tools.pyFSI.class_str.optimization.constraints.class_structure import DVCREL1
from SUAVE.Methods.fea_tools.pyFSI.class_str.optimization.constraints.class_structure import DVGRID
from SUAVE.Methods.fea_tools.pyFSI.class_str.optimization.constraints.class_structure import DLINK
from SUAVE.Methods.fea_tools.pyFSI.class_str.optimization.constraints.class_structure import DOPTPRM

from SUAVE.Methods.fea_tools.pyFSI.utility_functions.print_equation import print_equation


from SUAVE.Methods.fea_tools.pyFSI.input.read_nas_file import read_nas_file
from SUAVE.Methods.fea_tools.pyFSI.utility_functions.interpolate_grid import interpolate_grid
from SUAVE.Methods.fea_tools.pyFSI.output.write_tecplot_file import write_tecplot_file
from SUAVE.Methods.fea_tools.pyFSI.input.read_beam_numbers import read_beam_numbers
from SUAVE.Methods.fea_tools.pyFSI.input.read_constraints import read_constraints

from SUAVE.Methods.fea_tools.pyFSI.input.read_beam import read_beam
from SUAVE.Methods.fea_tools.pyFSI.input.read_beam_numbers import read_beam_numbers
from SUAVE.Methods.fea_tools.pyFSI.input.read_opt_f06_file import read_opt_f06_file
from SUAVE.Methods.fea_tools.pyFSI.input.read_opt_f06_file_stress import read_opt_f06_file_stress
from SUAVE.Methods.fea_tools.pyFSI.utility_functions.check_mesh_quality import check_mesh_quality


def read_bdf_file_force(mesh_filename,scaling_factor):
    
    
    max_glob_point=0;
    file = open(mesh_filename, 'r')
    element_count=0
    element_pres =0
    count=0
    pcount=0
    no_of_elements = 0
    no_of_points=0
    elemlist =[]
    


    #----------each zone has a separate material-----

    no_of_materials = 0
    no_of_shell_elements = 0
    no_of_points = 0
    no_of_elements = 0
    no_of_constraint_points = 0
    no_of_force = 0

        
    for line in file:
        
        
        if (line[0:8]=='$CDSCRPT') or (line[0:6]=='PSHELL'):
            no_of_shell_elements = no_of_shell_elements +1
#            start = line.find(' ')
#            end = line.find('\n')
#            no_of_elements= int(line[start:end])
#            #print no_of_elements
#            element_pres = 1
#            elemlist = [ CTRIA3() for i in range(no_of_elements)]


        if (line[0:5]=='GRID*'):
            no_of_points = no_of_points +1
            
            
        if (line[0:6]=='CTRIA3')or(line[0:6]=='CQUAD4'):
            no_of_elements = no_of_elements +1

        if (line[0:3]=='SPC'):
            no_of_constraint_points = no_of_constraint_points +1

        if (line[0:4]=='MAT1'):
            no_of_materials = no_of_materials +1

        if (line[0:5]=='FORCE'):
            no_of_force = no_of_force +1

    
    
    file.close()



    if(no_of_materials==0):
        no_of_materials = 1;


#    no_of_loc_materials = no_of_materials/10
#    rem_no =  no_of_materials % 10
#    if (rem_no != 0 ):
#        no_of_loc_materials = no_of_loc_materials+1
#    
#    no_of_materials = no_of_loc_materials



    
    pointlist = [ grid() for i in range(no_of_points)]
    elemlist = [ CTRIA3() for i in range(no_of_elements)]
    material_list = [ MAT1() for i in range(no_of_materials)]
    shell_element_list = [ PSHELL() for i in range(no_of_shell_elements)]
    constrained_grid_point_list = [ SPC() for i in range(no_of_constraint_points)]
    force_list = [ FORCE() for i in range(no_of_force)]
    

    global_to_local_array = [ int for i in range(no_of_points)]
    max_glob_point = 0
    
    file = open(mesh_filename, 'r')
    point_count = 0
    element_count=0
    material_count=0
    shell_count =0
    constraint_count=0
    force_count = 0
    
    
    for line in file:

        
        
#        if (line[0:6]=='PSHELL'):
#            no_of_materials = no_of_materials +1
#        #            start = line.find(' ')
#        #            end = line.find('\n')
#        #            no_of_elements= int(line[start:end])
#        #            #print no_of_elements
#        #            element_pres = 1
#        #            elemlist = [ CTRIA3() for i in range(no_of_elements)]

        
        if (line[0:5]=='GRID*'):

            point_1 = float(line[40:56])
            point_2 = float(line[56:72])
            global_to_local_id  = int(line[8:24])

#            point_1 = line[41:56]
#            point_2 = line[57:72]

            for line in file:
                point_3 = float(line[8:24])
#                point_3 = line[9:24]
                break
            

            pointlist[point_count].type = 'GRID'
            pointlist[point_count].id = point_count + 1
            pointlist[point_count].global_to_local = global_to_local_id
            global_to_local_array[point_count] = global_to_local_id
            if(global_to_local_id>max_glob_point):
                max_glob_point=global_to_local_id
#            pointlist[point_count].x1 = point_1*scaling_factor
#            pointlist[point_count].x2 = point_2*scaling_factor
#            pointlist[point_count].x3 = point_3*scaling_factor

            pointlist[point_count].x[0] = point_1*scaling_factor
            pointlist[point_count].x[1] = point_2*scaling_factor
            pointlist[point_count].x[2] = point_3*scaling_factor
            pointlist[point_count].t1 = 0.0
            pointlist[point_count].t2 = 0.0
            pointlist[point_count].t3 = 0.0
            pointlist[point_count].thickness =0.0
            pointlist[point_count].in_stress_von_mises = 0.0
            pointlist[point_count].fin_stress_von_mises = 0.0
            
#            if (pointlist[point_count].x1 <= 0.):#and(pointlist[point_count].x1 >= -0.5):
#                print pointlist[point_count].x1, pointlist[point_count].x2,pointlist[point_count].x3

            pointlist[point_count].cp = 0
            pointlist[point_count].cd = 0
            
            #print pointlist[point_count].x1,pointlist[point_count].x2,pointlist[point_count].x3
            
            
            
            
            point_count = point_count +1
                

        
        


        
        if (line[0:6]=='CTRIA3'):
            
            element_break= [int(s) for s in line.split() if s.isdigit()]
            
            elemlist[element_count].type='CTRIA3'
            elemlist[element_count].eid=element_count+1 #element_break[0] #element_count+1
#            elemlist[element_count].g1=element_break[2]
#            elemlist[element_count].g2=element_break[3]
#            elemlist[element_count].g3=element_break[4]

            elemlist[element_count].g[0]=element_break[2]
            elemlist[element_count].g[1]=element_break[3]
            elemlist[element_count].g[2]=element_break[4]
            
            elemlist[element_count].theta=0.0
            elemlist[element_count].pid=element_break[1]
            elemlist[element_count].thickness = 0.0
            
            element_count = element_count +1



        if (line[0:6]=='CQUAD4'):
    
            element_break= [int(s) for s in line.split() if s.isdigit()]
        
            elemlist[element_count].type='CQUAD4'
            elemlist[element_count].eid=element_count+1 #element_break[0]
#            elemlist[element_count].g1=element_break[2]
#            elemlist[element_count].g2=element_break[3]
#            elemlist[element_count].g3=element_break[4]
#            elemlist[element_count].g4=element_break[5]

            elemlist[element_count].g[0]=element_break[2]
            elemlist[element_count].g[1]=element_break[3]
            elemlist[element_count].g[2]=element_break[4]
            elemlist[element_count].g[3]=element_break[5]
            elemlist[element_count].theta=0.0
            elemlist[element_count].pid=element_break[1]
            elemlist[element_count].thickness = 0.0
            
            element_count = element_count +1



        if (line[0:4]=='MAT1'):
    
        
            material_list[material_count].type='MAT1'
            material_list[material_count].mid=material_count+1
            material_list[material_count].e=line[14:24]
            material_list[material_count].nu=element_break[31:40]
            material_list[material_count].rho=element_break[41:48]

            
            material_count = material_count +1


        if (line[0:8]=='$CDSCRPT') or (line[0:6]=='PSHELL'):
    
    
            shell_element_list[shell_count].type='PSHELL'
            shell_element_list[shell_count].pid=shell_count+1
            
            
            if(line[0:8]=='$CDSCRPT'):
                shell_element_name = line.split()
                shell_element_list[shell_count].name = shell_element_name[2]
            
            elif(line[0:6]=='PSHELL'):
                shell_element_list[shell_count].t = float(line[24:32])
            
            
#            material_list[element_count].mid1=line[14:24]
#            material_list[element_count].t=element_break[31:40]
#            material_list[element_count].rho=element_break[41:48]

            
            shell_count = shell_count +1





        if (line[0:3]=='SPC'):
    
            constrained_grid_point_list[constraint_count].type='SPC1'
            constrained_grid_point_list[constraint_count].sid= int(line[8:16])  #int(line[9:16])
            constrained_grid_point_list[constraint_count].c1=int(line[16:24])  #int(line[17:24])
            constrained_grid_point_list[constraint_count].g1=int(line[24:32])  #int(line[25:32])
            #constrained_grid_point_list[constraint_count].d1=float(line[32:40])   #float(line[33:40])
            

            
            
            constraint_count = constraint_count +1


        if (line[0:5]=='FORCE'):
    
            if(line[0:6]=='FORCE*'):
                force_list[force_count].type='FORCE'
                force_list[force_count].sid=int(line[8:24])  #int(line[9:16])
                force_list[force_count].g=int(line[24:40])  #int(line[17:24])
                force_list[force_count].cid=int(line[40:56])  #int(line[25:32])
                force_list[force_count].f=float(line[56:72])   #float(line[33:40])
                
                for line in file:

                    force_list[force_count].n1=float(line[8:24])  #int(line[17:24])
                    force_list[force_count].n2=float(line[24:40])  #int(line[25:32])
                    force_list[force_count].n3=float(line[40:56])   #float(line[33:40])
                    break
                
                
                
                print
            else:
    
                force_list[force_count].type='FORCE'
                force_list[force_count].sid=int(line[8:16])  #int(line[9:16])
                force_list[force_count].g=int(line[16:24])  #int(line[17:24])
                force_list[force_count].cid=int(line[24:32])  #int(line[25:32])
                force_list[force_count].f=float(line[32:40])   #float(line[33:40])
                force_list[force_count].n1=float(line[40:48])  #int(line[17:24])
                force_list[force_count].n2=float(line[48:56])  #int(line[25:32])
                force_list[force_count].n3=float(line[56:64])   #float(line[33:40])
            
            
            
            
            force_count = force_count +1




    file.close()



    for i in range(0,len(force_list)):
        pointlist[force_list[i].g-1].f[0] = force_list[i].n1
        pointlist[force_list[i].g-1].f[1] = force_list[i].n2
        pointlist[force_list[i].g-1].f[2] = force_list[i].n3


#convert element  numbering to local numbering-----

    local_to_global_array = [ int for i in range(max_glob_point+1)]

    for i in range(0,no_of_points):

        local_to_global_array[global_to_local_array[i]]=i+1



    for i in range(0,no_of_elements):
        if(elemlist[i].type == 'CQUAD4'):

            for j in range(0,4):
                elemlist[i].g[j] = local_to_global_array[elemlist[i].g[j]]




        elif (elemlist[i].type == 'CTRIA3'):
            for j in range(0,3):
                elemlist[i].g[j] = local_to_global_array[elemlist[i].g[j]]







    for i in range(0,no_of_force):
        force_list[i].g=local_to_global_array[force_list[i].g]


    #check for mesh quality
    #elemlist_valid = check_mesh_quality(elemlist,pointlist)
    #no_of_elements = len(elemlist_valid)

    print 'no of points ' , no_of_points
    #print 'no of elements ' , no_of_elements, len(elemlist_valid)
    print 'no of materials ' , no_of_materials
    print 'no of shell elements ' , no_of_shell_elements
    print 'no of constraints ' , no_of_constraint_points


#return elemlist
    print "Done reading file"

#return elemlist,pointlist,no_of_points,no_of_elements,material_list,no_of_materials,shell_element_list,no_of_shell_elements,constrained_grid_point_list,no_of_constraint_points
    return elemlist,pointlist,no_of_points,no_of_elements,material_list,no_of_materials,shell_element_list,no_of_shell_elements,constrained_grid_point_list,no_of_constraint_points,force_list,no_of_force









