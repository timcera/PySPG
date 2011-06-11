#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  8 16:20:26 2011

@author: -
"""

# logica del programa
#   leer la cantidad de procesos a ejecutar de la DB central
#   si este numero es menor (para alguna cola) que el que esta corriendo. lanzar los que faltan
#   si este numero es mayor (para alguna cola) que el que esta corriendo. matar los que sobran
#   en este ultimo caso, limpiar la DB central
  #print cmd
  
import time

from spg.pool import ProcessPool

    

if __name__ == "__main__":
    parser = optparse.OptionParser(usage = "usage: %prog [options] project_id1 ")
    parser.add_option("--sleep", type="int", action='store', dest="sleep",
                            default = 1800 , help = "waiting time before refresh" )

    options, args = parser.parse_args()

    while True:
       pp = ProcessPool()
       pp.update_worker_info()
     
     
      
       for i_j in pp.queues:
         print i_j.normalise_processes()
     
       pp.update_dbs_info()
       
       time.sleep(options.sleep)
