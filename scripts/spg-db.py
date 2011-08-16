#!/usr/bin/python

import cmd

import spg.utils as utils
from spg.parameter import EnsembleBuilder, ParameterEnsemble
from spg.pool import MasterDB

from spg import VAR_PATH, RUN_DIR

import sqlite3 as sql
import sys, optparse
import os, os.path





class DBCommandParser(cmd.Cmd):
    """DB command handler"""

 
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = "( spg-db ) "
        self.possible_keys = ['weight', 'repeat', 'executable' , 'sql_retries']
        self.values = {'repeat': 1, 'sql_retries': 1, 'timeout' : 60, 'weight': 1}

        self.doc_header = "default values: %s"%(self.values )
        self.current_param_db = None 
        self.master_db =  MasterDB()


    def __translate_name( self,st):
        """translates the parameters filename and the  database name 
           into the other and viceversa (returns a duple: param_name, db_name)"""
        full_name = st
        if not os.path.exists(full_name):
            full_name = os.path.expanduser( "%s/%s"%(RUN_DIR,st) )
        if not os.path.exists(full_name):
            utils.newline_msg("ERR","database '%s' does not exist"%st)
            sys.exit(2)
        #  print ">", full_name
        path, st = os.path.split(full_name)
#        if path:
#            os.chdir(path)
        if ".sqlite" in st:
            par_name = st.replace("results","").replace(".sqlite","")
            par_name = "parameters%s.dat"%par_name
            return "%s/%s"%(path,par_name), "%s/%s"%(path,st)
        else:
            db_name = st.replace("parameters","").replace(".dat","")
            db_name = "results%s.sqlite"%db_name
            return "%s/%s"%(path,st),"%s/%s"%(path,db_name)
            
 
    def __update_active_result_db(self, c):
        c = c.strip()
        if not c: return 

        param_name, db_name = self.__translate_name(c)
        if os.path.exists( db_name ):
           self.current_param_db = ParameterEnsemble( db_name )
           self.values["weight"] = self.current_param_db.weight 
        if os.path.exists( param_name ) and not os.path.exists( db_name ):
           self.current_param_db = ParameterEnsemble( db_name , db_init = False)
           self.current_param_db.weight = self.values["weight"]
        
        db_id = self.master_db.execute_query_fetchone( "SELECT id FROM dbs WHERE full_name = '%s' "%full_name).fetchone()
        if db_id is not None:
            (self.current_param_db,) = db_id

        return   
        

        
    def do_build(self, c):
        """build PARAMETERS_NAME|DB_NAME [VAR1=VALUE1[:VAR2=VALUE2]]
        Generates a new database out of a parameters.dat"""
        c = c.split()
        i_arg = c[0]
        if len(c) >1: self.do_set( ":".join( c[1:] ) )

        i_arg, db_name = self.__translate_name(i_arg)
        parser = EnsembleBuilder( stream = open(i_arg), db_name=db_name , timeout = self.values['timeout'] )
        if 'executable' in self.values.keys():
            parser.command = self.values['executable']
        parser.init_db(retry = self.values['sql_retries'])
        parser.fill_status(repeat = int(self.values['repeat']) )
        
        
        

    def do_clean(self, c):
        """clean PARAMETERS_NAME|DB_NAME
        cleans the database. It accepts several of them"""
        for i_arg in c.split():
            i_arg, db_name = self.__translate_name(i_arg)
            parser = EnsembleBuilder( stream = open(i_arg), db_name=db_name , timeout = self.values['timeout'] )
            parser.clean_status()


    def do_clean_all(self, c):
        """clean_all PARAMETERS_NAME|DB_NAME
        cleans completely the database. It accepts several of them"""
        for i_arg in c.split():
            i_arg, db_name = self.__translate_name(i_arg)
            parser = EnsembleBuilder( stream = open(i_arg), db_name=db_name , timeout = self.values['timeout'] )
            parser.clean_all_status()

    def do_add(self, c):
        """add PARAMETERS_NAME|DB_NAME
        adds the database to the registered ones"""
#        for i_arg in c.split():
        pass

    def do_ls(self, c):
        """lists the databases already in the database"""
        ret = [ self.master_db.result_dbs[i] for i in  self.master_db.result_dbs]
        
        
        
        for i in sorted( ret , key = lambda x: x.full_name ):
            #print "%5d: %s"%(i_id, i_name)
            print "%5d: %s"%(i.id, os.path.relpath(i.full_name,RUN_DIR))
        
    def do_status(self, c):
        """gives the status of the results database """
        self.master_db.update_results_stat( self.current_param_db.full_name )
         = -1
        self.current_param_db.stat_processes_not_run = -1
        self.current_param_db.stat_processes_running = -1
        self.current_param_db.stat_processes_error = -1
        self.current_param_db.stat_values_set_with_rep = -1
        self.current_param_db.stat_values_set = -1

        print "%5d: %s"%( self.current_param_db.id, os.path.relpath(self.current_param_db.full_name,RUN_DIR) )
        frac_done =  float(self.current_param_db.stat_processes_done) / float(self.current_param_db.stat_values_set)
        print "[%s] TOT: %d - D: %d (%.5f) - R: %d -- E: %d "%
             (status, self.current_param_db.stat_values_set, self.current_param_db.stat_processes_done, frac_done, running, frac_running, error, frac_error) 
#


    def do_remove(self, c):
        """remove PARAMETERS_NAME|DB_NAME
        removes the database from the registered ones. It accepts many dbs"""
        for i_arg in c.split():
            i_arg, db_name = self.__translate_name(i_arg)
            connection = sql.connect("%s/spg_pool.sqlite"%VAR_PATH)
            cursor = connection.cursor()
            cursor.execute( "DELETE FROM dbs WHERE full_name = ?",(os.path.realpath(db_name),) )

            connection.commit()
    
    def do_set(self, c):
        """sets a VAR1=VALUE1[:VAR2=VALUE2]
        removes the database to the registered ones"""
        ret = utils.parse_to_dict(c, allowed_keys=self.possible_keys)
        for k in ret:
            self.values[k] = ret[k]
            print "%s = %s" %(k,ret[k])
        if self.current_param_db:
            self.current_param_db.weight = self.values["weight"]
            
        self.doc_header = "default values: %s"%(self.values )
                
    def default(self, line):
        return True        
    
    def do_EOF(self, line):
        return True

#    def do_EOF(self, line):
#        return True
    



if __name__ == '__main__':
    cmd_line = DBCommandParser()
    if len(sys.argv) == 1:
        cmd_line.cmdloop()
    else:
        cmd_line.onecmd(" ".join(sys.argv[1:]))
        
#       "usage: %prog [options] CMD VERB NAME {params}\n"
#       "commands NAME {params}: \n"
#       "   init PARAMETERS_NAME|DB_NAME \n"
#       "        params :: executable=EXE_NAME , repeat=REPEAT, sql_retries=1\n"
#       "   clean-all PARAMETERS_NAME|DB_NAME \n"
#       "   clean PARAMETERS_NAME|DB_NAME \n"
#       "   remove PARAMETERS_NAME|DB_NAME \n"

