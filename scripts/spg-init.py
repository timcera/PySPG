#!/usr/bin/python


import spg
import spg.params as params
import spg.utils as utils

import sqlite3 as sql
import sys, optparse
import time

class DBBuilder(spg.MultIteratorParser):
    def __init__(self, stream=None, db_name = "results.sqlite", timeout = 5):
        spg.parser.MultIteratorParser.__init__(self, stream)
        if not params.check_consistency(self.command, self):
            utils.newline_msg("ERR","data not consistent.")
            sys.exit(1)
        self.stdout_contents = params.contents_in_output(self.command)
                
        self.connection =  sql.connect(db_name, timeout = timeout)
        self.cursor = self.connection.cursor()

    def init_db(self, retry=1):
        #:::~ Table with the name of the executable
        self.cursor.execute("CREATE TABLE IF NOT EXISTS executable "
                            "(id INTEGER PRIMARY KEY, name CHAR(64))"
                            )
        self.cursor.execute( "SELECT name FROM executable " )
        prev_val = self.cursor.fetchone()
        
        
        if prev_val :
            if prev_val[0] != self.command:
                utils.newline_msg("ERR","conflict in executable name (in db '%s', in param '%s')"%(prev_val, self.command))
        else:
            self.cursor.execute("INSERT INTO executable (name) VALUES ('%s')"%self.command)
            self.connection.commit()

        #:::~ Table with the constant values
        self.cursor.execute("CREATE TABLE IF NOT EXISTS constants "
                            "(id INTEGER PRIMARY KEY, name CHAR(64), value CHAR(64))"
                            )
        for k in self.constant_items():
            self.cursor.execute( "SELECT value FROM constants WHERE name = '%s'"%k)
            prev_val = self.cursor.fetchone()
            if prev_val is not None:
                if prev_val[0] != self[k]:
                    spg.utils.newline_msg("ERR", "conficting values for parameter '%s' (was %s, is %s)"%(k, self[k], prev_val[0]))
                    sys.exit(1)
            else:
                self.cursor.execute( "INSERT INTO constants (name, value) VALUES (?,?)",(k, self[k]) )
            
        self.connection.commit()
        vi = self.varying_items()
        elements = "CREATE TABLE IF NOT EXISTS variables (id INTEGER PRIMARY KEY,  %s )"%( ", ".join([ "%s CHAR(64)"%i for i in vi ] ) )
#        print elements
        self.cursor.execute(elements)
        
        elements = "INSERT INTO variables ( %s ) VALUES (%s)"%(   ", ".join([ "%s "%i for i in vi ] ), ", ".join( "?" for i in vi) )
        #query_elements = "SELECT COUNT(*) FROM variables WHERE "%(   "AND ".join([ "%s "%i for i in vi ] ) , ", ".join( "?" for i in vi) )
        #print query_elements
        self.possible_varying_ids = []
        i_try = 0
        commited = False
        while i_try < retry and not commited:
          try:   
            i_try += 1
            for i in self:
            
                self.cursor.execute( elements, [ self[i] for i in vi] )
                self.possible_varying_ids.append(self.cursor.lastrowid)
          
#        print self.possible_varying_ids
            self.connection.commit()
            commited = True
          except sql.OperationalError:  
              utils.newline_msg("DB", "database is locked (%d/%d)"%(i_try, retry))
              
        if not commited:
              utils.newline_msg("ERR", "database didn't unlock, exiting")
          
        self.number_of_columns = 0
        for ic, iv in self.stdout_contents:
            if iv["type"] == "xy":
                self.number_of_columns += 1
            if iv["type"] == "xydy":
                self.number_of_columns += 2


        results = "CREATE TABLE IF NOT EXISTS results (id INTEGER PRIMARY KEY, variables_id INTEGER,  %s , FOREIGN KEY(variables_id) REFERENCES variables(id))"%( ", ".join([ "%s CHAR(64)"%ic for ic, iv in self.stdout_contents ] ) )
#        print results
        self.cursor.execute(results)
        self.connection.commit()
        
        
        self.cursor.execute("CREATE TABLE IF NOT EXISTS run_status (id INTEGER PRIMARY KEY, variables_id INTEGER, status CHAR(1), "
                            "FOREIGN KEY (variables_id ) REFERENCES variables(id) )")
                            
        self.connection.commit()


    def fill_status(self, repeat = 1):


       for i_repeat in range(repeat):

           for i_id in self.possible_varying_ids:
                #:::~ status can be either 
                #:::~    'N': not run
                #:::~    'R': running
                #:::~    'D': successfully run (done)
                #:::~    'E': run but with non-zero error code
                self.cursor.execute( "INSERT INTO run_status ( variables_id, status ) VALUES (%s,'N')"%(i_id) )

       self.connection.commit()


    def clean_status(self):
       self.cursor.execute('UPDATE run_status SET status = "N" WHERE status ="R"')
       self.connection.commit()

    def clean_all_status(self):
       self.cursor.execute('UPDATE run_status SET status = "N"')
       self.connection.commit()

#===============================================================================
#     cursor.execute("CREATE TABLE IF NOT EXISTS revision_history "
#                "( id INTEGER PRIMARY KEY, revision INTEGER, author CHAR(64), date CHAR(64), "
#                "  size INTEGER, number_of_files INTEGER, modified_files INTEGER, "
#                "  affected_lines_previous INTEGER , affected_lines_next INTEGER, "
#                "  removed_lines INTEGER, added_lines INTEGER, "
#                "  affected_bytes_previous INTEGER, affected_bytes_next INTEGER"
#                "   )"
#                )
# 
# 
#     cursor.execute("CREATE TABLE IF NOT EXISTS modified_files "
#                "( id INTEGER PRIMARY KEY, revision INTEGER, file_name CHAR(256))"
#                )
# 
# 
#===============================================================================








if __name__ == "__main__":
  


    
    parser = optparse.OptionParser(usage = "usage: %prog [options] project_id1 project_id2 project_id3... ")
    
    parser.add_option("--exe", type="string", action='store', dest="executable",
                            default = None, help = "The program to be run" )
    
    parser.add_option("-r","--repeat", type="int", action='store', dest="repeat",
                            default = 1 , help = "how many times the simulation is to be run" )
    
    parser.add_option("--sql-retries", type="int", action='store', dest="sql_retries",
                            default = 1 , help = "how many retries should attempt while writting to the database" )
    
    parser.add_option("--timeout", type="int", action='store', dest="timeout",
                            default = 5 , help = "timeout for database connection" )
    
    parser.add_option("--clean", action='store_true', dest = "clean",
                          help = 'cleans the running status in the database of the running processes')
    
    parser.add_option("--clean-all", action='store_true', dest = "clean_all",
                          help = 'clean the all the running status information')
    
    options, args = parser.parse_args()
    
    if len(args) == 0:
        args = ["parameters.dat"]
    
    for i_arg in args:
      db_name = i_arg.replace("parameters","").replace(".dat","")
      db_name = "results%s.sqlite"%db_name
#      print db_name
      parser = DBBuilder( stream = open(i_arg), db_name=db_name , timeout = options.timeout )
      if options.executable is not None:
          parser.command = options.executable
      if options.clean_all:
          parser.clean_all_status()
      elif options.clean:
          parser.clean_status()
      else:
          parser.init_db(retry = options.sql_retries)
          parser.fill_status(repeat = options.repeat )
