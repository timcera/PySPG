from spg import utils
from spg import TIMEOUT, ROOT_DIR

#import os.path, os, sys
import os, sys, os.path, time
from subprocess import Popen, PIPE
import sqlite3 as sql
import spg.utils as utils
import numpy as n
#import math as m


import csv 

#TIMEOUT = 120
#
#
#
#
#
# class ParameterEnsembleCSV:
#
#     def __init__(self, full_name = "", id=-1, weight=1., queue = '*', status = 'R', repeat = 1, init_db = False):
#         self.full_name = full_name
#         self.path, self.db_name = os.path.split(full_name)
#
#         self.values = {}
#         self.directory_vars = None
#
#
#
#     def __close_db(self):
#         self.connection.commit()
#         self.connection.close()
#         del self.cursor
#         del self.connection
#
#
#
#     def execute_query(self, query, *args):
#         self.__connect_db()
#         ret = [i for i in self.cursor.execute(query, args)]
#         self.__close_db()
#         return ret
#
#
#     def execute_query_fetchone(self, query, *args):
#         self.__connect_db()
#         ret = self.cursor.execute(query, args).fetchone()
#         self.__close_db()
#         return ret
#
#     # def parse_output_line(self,  output_line):
#     #     """ parses a line from output. Returns a tuple containing: table of output, column names of output,  output values to be inserted in table"""
#     #     output_columns = output_line.strip().split()
#     #     table_name = "results"
#     # #    print ">>%s<<"%output_columns
#     #     if output_columns[0][0] == "@":
#     #         table_name = output_columns[0][1:]
#     #         output_columns.pop(0)
#     #     try:
#     #         output_column_names = [ i[0] for i in self.execute_query("SELECT column FROM output_tables WHERE name = '%s'"%(table_name)) ]
#     #     except:
#     #         utils.newline_msg("ERR", "DB does not contain table named '%s'"%table_name)
#     #         sys.exit(1)
#     #
#     #  #  print table_name, output_column_names, output_columns
#     #
#     #     return table_name, output_column_names, output_columns
#
#     def init_db(self):
#
#   #      self.__connect_db()
#
#
#         #:::~ Table with the name of the executable
# #        (self.command, ) = self.cursor.execute( "SELECT name FROM executable " ).fetchone()
# #        (self.command, ) = self.execute_query_fetchone( "SELECT name FROM executable " )
#         #try:
#   ###      print ":::init_db"
#         (self.command, ) = self.execute_query_fetchone( "SELECT value FROM information WHERE key = 'command'" )
#         #except:
#         #    self.command = None
#
#
#         #:::~ get the names of the columns
#         sel = self.execute_query("SELECT name FROM entities ORDER BY id")
#         self.entities = [ i[0] for i in sel ]
#         #:::~ get the names of the columns
#         sel = self.execute_query("SELECT name FROM entities WHERE varies = 1 ORDER BY id")
#         self.variables = [ i[0] for i in sel ]
#         #:::~ get the names of the outputs
#
#         self.output_column = {}
#
#         table_names = [i[0] for i in self.execute_query("SELECT DISTINCT name from output_tables")]
#      ###   print table_names
#         for table in table_names:
#             fa = self.execute_query("SELECT column FROM output_tables WHERE name = '%s';"%table)
#
#             self.output_column[table] = [ i[0] for i in fa ]
#
# #        self.output_column = self.output_column[2:]
#         self.directory_vars = self.variables[:-1]
#   ###      print self.output_column
#    #     self.__close_db()
#
#
#
#     def __iter__(self):
#         return self
#
#
#     def reset(self):
#         self.execute_query( 'UPDATE run_status SET status ="N" WHERE id>0 '  )
#
#     def next(self):
#         query = "SELECT r.id, r.values_set_id, %s FROM run_status AS r, values_set AS v "% ", ".join( ["v.%s"%i for i in self.entities] )  +"WHERE r.status = 'N' AND v.id = r.values_set_id ORDER BY r.id LIMIT 1"
# #       print query
#         res = self.execute_query_fetchone(query)
# #        print res
#         if res == None:
#             # utils.newline_msg("WRN","db '%s' did not return any new data point"%self.full_name)
#             raise StopIteration
#
#         self.current_run_id  = res[0]
#         self.current_valuesset_id = res[1]
#         self.execute_query( 'UPDATE run_status SET status ="R" WHERE id = %d'%self.current_run_id  )
#
#         for i in range( len(self.entities) ):
#             self.values[ self.entities[i] ] = res[i+2]
#
#         return self.values
#
#     def create_trees(self):
# #        self.__connect_db()
#         if not self.directory_vars: return False
#         ret = self.execute_query_fetchone("SELECT * FROM entities WHERE name LIKE 'store_%'")
#
# #        self.__close_db()
#         return ret is not None
#
#
#     def generate_tree(self, dir_vars = None):
#
#         if type(dir_vars) == type(""):
#             self.directory_vars = dir_vars.split(",")
#         elif type(dir_vars) == type([]):
#             self.directory_vars = dir_vars
#         else:
#             self.directory_vars  = self.variables
#
#     def update_status(self):
#         #:::~    'N': not run yet
#         #:::~    'R': running
#         #:::~    'D': successfully run (done)
#         #:::~    'E': run but with non-zero error code
#
#         (self.stat_values_set_with_rep , ) = self.execute_query_fetchone("SELECT COUNT(*) FROM run_status ;")
#         (self.stat_values_set, ) = self.execute_query_fetchone("SELECT COUNT(*) FROM values_set ;")
#
#         ret = self.execute_query("SELECT status, COUNT(*) FROM run_status GROUP BY status")
# #        self.stat_done, self.stat_not_run, self.stat_running,self.stat_error = 0,0,0,0
#         for (k,v) in ret:
#             if k == "D":
#                 self.stat_processes_done = v
#             elif k == "N":
#                 self.stat_processes_not_run = v
#             elif k == "R":
#                 self.stat_processes_running = v
#             elif k == "E":
#                 self.stat_processes_error = v
#
 

class ParameterEnsemble:
    
    def __init__(self, full_name = "", id=-1, weight=1., queue = '*',
                 status = 'R', repeat = 1, init_db = False):

        self.full_name, self.path, self.base_name, ext = utils.translate_name(full_name)

        self.db_name = "%s.spgql"%self.base_name
        self.full_name = "%s/%s.spgql"%(self.path,self.base_name)
        self.values = {}
        self.directory_vars = None

        
        self.stat_processes_done = 0
        self.stat_processes_not_run = 0
        self.stat_processes_running = 0
        self.stat_processes_error = 0
        self.stat_values_set_with_rep = 0
        self.stat_values_set = 0

        self.weight = weight
        self.current_run_id = 0
        self.queue = queue
        self.status = status
        self.repeat = repeat

#        print self.full_name, self.db_name

        self.__connect_db()
        if init_db  :
            self.init_db()

        # :::~ Before they were in __connect_db(self)
#        self.connection = sql.connect(self.db_name, timeout = TIMEOUT)
#        self.cursor = self.connection.cursor()

    def __connect_db(self):
       # pass
        self.connection = sql.connect(self.full_name, timeout = TIMEOUT)
        self.cursor = self.connection.cursor()
         


    def __close_db(self):

        self.cursor.close()
        del self.cursor
        self.connection.commit()
        self.connection.close()
        del self.connection
#

    def execute_query(self, query, *args):
        self.__connect_db()
        ret = [i for i in self.cursor.execute(query, args)]
        self.__close_db()
        return ret 


    def execute_query_fetchone(self, query, *args):
        self.__connect_db()
        ret = self.cursor.execute(query, args).fetchone()
        self.__close_db()
        return ret 

    def parse_output_line(self,  output_line):
        """ parses a line from output. Returns a tuple containing: table of output, column names of output,  output values to be inserted in table"""
        output_columns = output_line.strip().split()
        table_name = "results"

        if output_columns[0][0] == "@":
            table_name = output_columns[0][1:] 
            output_columns.pop(0)
        try:
            output_column_names = [ i[0] for i in self.execute_query("SELECT column FROM output_tables WHERE name = '%s'"%(table_name)) ]
        except:
            utils.newline_msg("ERR", "DB does not contain table named '%s'"%table_name)
            sys.exit(1)
        
        return table_name, output_column_names, output_columns 

    def __getitem__(self, item):
        if item in self.values:
            return self.values[item]
        if item == 'id':
            return self.current_run_id

    def init_db(self):

        (self.command, ) = self.execute_query_fetchone( "SELECT value FROM information WHERE key = 'command'" )
        
        #:::~ get the names of the columns
        sel = self.execute_query("SELECT name FROM entities ORDER BY id")
        self.entities = [ i[0] for i in sel ]
        #:::~ get the names of the columns
        sel = self.execute_query("SELECT name FROM entities WHERE varies = 1 ORDER BY id")
        self.variables = [ i[0] for i in sel ]
        #:::~ get the names of the outputs
        
        self.output_column = {}
        
        table_names = [i[0] for i in self.execute_query("SELECT DISTINCT name from output_tables")]
     ###   print table_names
        for table in table_names:
            fa = self.execute_query("SELECT column FROM output_tables WHERE name = '%s';"%table)
            
            self.output_column[table] = [ i[0] for i in fa ]

        self.directory_vars = self.variables[:-1]


    def query_set_run_status(self, status, id = None):
        if id is None:
            id = self.current_run_id

        self.execute_query( 'UPDATE run_status SET status ="%s" WHERE id = %d'% (status,id)  )

    def __iter__(self):
        return self

    #
    # def clean_status(self, type = "all"):
    #     if type == 'all':
    #         self.execute_query( 'UPDATE run_status SET status ="N" WHERE id>0 '  )
    #
    #     elif type == 'failed':
    #         self.execute_query('UPDATE run_status SET status ="N" WHERE status = "E" ')
    #
    #     elif type == 'not-done':
    #         self.execute_query('UPDATE run_status SET status ="N" WHERE status <> "D" ')

    def next(self):

        query = "SELECT r.id, r.values_set_id, %s FROM run_status AS r, values_set AS v "% ", ".join( ["v.%s"%i for i in self.entities] )  +"WHERE r.status = 'N' AND v.id = r.values_set_id ORDER BY r.id LIMIT 1"
        res = self.execute_query_fetchone(query)
        if res == None:
            raise StopIteration

        self.current_run_id  = res[0]

        self.current_valuesset_id = res[1]
        self.query_set_run_status("R")


        for i in range( len(self.entities) ):
            self.values[ self.entities[i] ] = res[i+2]

        return self.values


    def variable_values(self):
        ret = {}
        for v in self.variables:
            ret[ v ] = self.values[v]

        return ret

    def create_trees(self):
        if not self.directory_vars: return False
        ret = self.execute_query_fetchone("SELECT * FROM entities WHERE name LIKE 'store_%'")

        return ret is not None


    def update_status(self):
        #:::~    'N': not run yet
        #:::~    'R': running
        #:::~    'D': successfully run (done)
        #:::~    'E': run but with non-zero error code

        (self.stat_values_set_with_rep , ) = self.execute_query_fetchone("SELECT COUNT(*) FROM run_status ;")
        (self.stat_values_set, ) = self.execute_query_fetchone("SELECT COUNT(*) FROM values_set ;")
        
        ret = self.execute_query("SELECT status, COUNT(*) FROM run_status GROUP BY status")
#        self.stat_done, self.stat_not_run, self.stat_running,self.stat_error = 0,0,0,0
        for (k,v) in ret:
            if k == "D":
                self.stat_processes_done = v
            elif k == "N":
                self.stat_processes_not_run = v
            elif k == "R":
                self.stat_processes_running = v
            elif k == "E":
                self.stat_processes_error = v




################################################################################
################################################################################















################################################################################
################################################################################

class ParameterEnsembleExecutor(ParameterEnsemble):
    def __init__(self, full_name = "", id=-1, weight=1., queue = '*', status = 'R', repeat = 1, init_db = True):
        ParameterEnsemble.__init__(self, full_name , id, weight, queue , status , repeat , init_db )
#        self.init_db()
        os.chdir(self.path)

        if os.path.exists("./%s" % self.command):
            self.bin_dir = "."
        elif os.path.exists("%s%/bin/%s" % (ROOT_DIR, self.command)):
            self.bin_dir = "%s%/bin" % (ROOT_DIR)
        else:
            utils.newline_msg("ERR", "Fatal, binary '%s' not found" % self.command)
            sys.exit(1)

    def launch_process(self):
         os.chdir(self.path)
         started_time = time.time()

         configuration_filename = "%s-%d.input" % (self.base_name, self.current_run_id)
         fconf = open(configuration_filename, "w")
         for k in self.values.keys():
                print >> fconf, k, utils.replace_values(self.values[k], self, skip_id=False)
         fconf.close()

         fname_stdout = "%s_%s.tmp_stdout"% (self.base_name, self.current_run_id)
         fname_stderr = "%s_%s.tmp_stderr"% (self.base_name, self.current_run_id)
         file_stdout = open(fname_stdout, "w")
         file_stderr = open(fname_stderr, "w")

         cmd = "%s/%s %s" % (self.bin_dir, self.command, configuration_filename)

         proc = Popen(cmd, shell=True, stdin=PIPE, stdout=file_stdout, stderr=file_stderr, cwd=self.path)
         self.return_code = proc.wait()

         file_stdout.close()
         file_stderr.close()
         finish_time = time.time()

         self.output = [i.strip() for i in open(fname_stdout, "r")]
         self.stderr = [i.strip() for i in open(fname_stderr, "r")]

         os.remove(configuration_filename)
         os.remove( fname_stdout )
         os.remove( fname_stderr )

         self.run_time = finish_time - started_time
#         self.dump_result()
         try:
            self.dump_result()
         except:
            self.query_set_run_status("E")


    def dump_result(self):
         """ loads the next parameter atom from a parameter ensemble"""
#         flog = open(self.full_db_name.replace("spgql", "log"), "aw")
#         flog_err = open(self.full_db_name.replace("spgql", "err"), "aw")


         #:::~ status can be either
         #:::~    'N': not run
         #:::~    'R': running
         #:::~    'D': successfully run (done)
         #:::~    'E': run but with non-zero error code

         if self.return_code != 0:
             self.query_set_run_status("E")
             return

         for line in self.output:
             table_name, output_column_names, output_columns = self.parse_output_line(line)

             output_columns.insert(0, self.current_run_id)  # WARNING: MZ FOUND THAT BEFORE WE HAVE BEEN SETTING current_run_id
             cc = 'INSERT INTO %s (%s) VALUES (%s) ' % (table_name, ", ".join(output_column_names),
                                                                   ", ".join(["'%s'" % str(i) for i in output_columns]))
                 # print cc
             try:
                 self.execute_query(cc)
                 self.query_set_run_status("D")
             except:
                 self.query_set_run_status("E")



#         inf_str = "{%s} %s: ret=%s -- %s,%s "  % (
#                    self.command, self.in_name, self.return_code, self.current_run_id, self.current_valuesset_id )
#         if hasattr(self, 'run_time'):
#             inf_str += " run_time=%s"%self.run_time
#         utils.newline_msg("INF", inf_str, stream=flog)

#         print >> flog, "     values: ", self.values
#         print >> flog, "OUT--  ", "       ".join(self.output)

#         try:
#             print >> flog_err, "     \n ".join(self.stderr)
#         except:
#             utils.newline_msg("WRN", "NO_STDERR", stream=flog_err)

#         flog.close()
#         flog_err.close()
#
# #FIXME Deprecated
# class ParameterEnsembleInputFilesGenerator(ParameterEnsemble):
#     def __init__(self, full_name = "", id=-1, weight=1., queue = '*', status = 'R', repeat = 1, init_db = False):
#         ParameterEnsemble.__init__(self, full_name , id, weight, queue , status , repeat  , init_db )
#         os.chdir(self.path)
#
#     def launch_process(self):
# #        pwd = os.path.abspath(".")
#    #     if self.directory_vars or self.create_trees():
#    #         dir = utils.generate_string(self.values,self.directory_vars, joining_string = "/")
#    #         if not os.path.exists(dir): os.makedirs(dir)
#     #        os.chdir(dir)
#         configuration_filename = "input_%.8d.dat"%(self.current_valuesset_id)
#         fconf = open(configuration_filename,"w")
#
#         for k in self.values.keys():
#             print >> fconf, k, utils.replace_values(self.values[k])
#         fconf.close()
#
#
#
#

################################################################################
################################################################################
################################################################################








################################################################################
################################################################################

class ParameterEnsembleThreaded(ParameterEnsemble):
    def __init__(self, full_name="", id=-1, weight=1., queue='*', status='R', repeat=1, init_db=True):
        ParameterEnsemble.__init__(self, full_name, id, weight, queue, status, repeat, init_db)
        #        self.init_db()
        os.chdir(self.path)

        if os.path.exists("./%s" % self.command):
            self.bin_dir = "."
        elif os.path.exists("%s%/bin/%s" % (ROOT_DIR, self.command)):
            self.bin_dir = "%s%/bin" % (ROOT_DIR)
        else:
            utils.newline_msg("ERR", "Fatal, binary '%s' not found" % self.command)
            sys.exit(1)

    def get_current_information(self):
        return self.current_run_id, self.values

    def launch_process(self, current_run_id, values):
        os.chdir(self.path)
        started_time = time.time()

        configuration_filename = "%s-%d.input" % (self.base_name,current_run_id)
        fconf = open(configuration_filename, "w")
        for k in self.values.keys():
            print >> fconf, k, utils.replace_values(values[k], self, skip_id=False)
        fconf.close()

        fname_stdout = "%s_%s.tmp_stdout" % (self.base_name, current_run_id)
        fname_stderr = "%s_%s.tmp_stderr" % (self.base_name, current_run_id)
        file_stdout = open(fname_stdout, "w")
        file_stderr = open(fname_stderr, "w")

        cmd = "%s/%s -i %s" % (self.bin_dir, self.command, configuration_filename)

        proc = Popen(cmd, shell=True, stdin=PIPE, stdout=file_stdout, stderr=file_stderr, cwd=self.path)
        return_code = proc.wait()

        file_stdout.close()
        file_stderr.close()
        finish_time = time.time()

        output = [i.strip() for i in open(fname_stdout, "r")]
        stderr = [i.strip() for i in open(fname_stderr, "r")]

        os.remove(configuration_filename)
        os.remove(fname_stdout)
        os.remove(fname_stderr)

        run_time = finish_time - started_time
        # self.dump_result()
        #try:
        #    self.dump_result()
        #    self.execute_query('UPDATE run_status SET status ="D" WHERE id = %d' % self.current_run_id)
        #except:
        #    self.execute_query('UPDATE run_status SET status ="E" WHERE id = %d' % self.current_run_id)

        return current_run_id, output, stderr, run_time, return_code


    def dump_result(self, current_run_id, output, stderr, run_time, return_code ):
        """ loads the next parameter atom from a parameter ensemble"""
        #         flog = open(self.full_db_name.replace("spgql", "log"), "aw")
        #         flog_err = open(self.full_db_name.replace("spgql", "err"), "aw")

#        print current_run_id, return_code
        if return_code == 0:
            for line in output:
                table_name, output_column_names, output_columns = self.parse_output_line(line)

                output_columns.insert(0,current_run_id)
                cc = 'INSERT INTO %s (%s) VALUES (%s) ' % (table_name, ", ".join(output_column_names),
                                                           ", ".join(["'%s'" % str(i) for i in output_columns]))
                # print cc
                # try:
                #print current_run_id, return_code
                self.execute_query(cc)
                self.query_set_run_status("D",current_run_id)
                #except:
#                self.query_set_run_status("E",current_run_id)

        else:
            #:::~ status can be either
            #:::~    'N': not run
            #:::~    'R': running
            #:::~    'D': successfully run (done)
            #:::~    'E': run but with non-zero error code
            self.query_set_run_status("E", current_run_id)


# inf_str = "{%s} %s: ret=%s -- %s,%s "  % (
#                    self.command, self.in_name, self.return_code, self.current_run_id, self.current_valuesset_id )
#         if hasattr(self, 'run_time'):
#             inf_str += " run_time=%s"%self.run_time
#         utils.newline_msg("INF", inf_str, stream=flog)

#         print >> flog, "     values: ", self.values
#         print >> flog, "OUT--  ", "       ".join(self.output)

#         try:
#             print >> flog_err, "     \n ".join(self.stderr)
#         except:
#             utils.newline_msg("WRN", "NO_STDERR", stream=flog_err)

#         flog.close()
#         flog_err.close()


class ParameterEnsembleInputFilesGenerator(ParameterEnsemble):
    def __init__(self, full_name="", id=-1, weight=1., queue='*', status='R', repeat=1, init_db=False):
        ParameterEnsemble.__init__(self, full_name, id, weight, queue, status, repeat, init_db)
        os.chdir(self.path)

    def launch_process(self):
        #        pwd = os.path.abspath(".")
        #     if self.directory_vars or self.create_trees():
        #         dir = utils.generate_string(self.values,self.directory_vars, joining_string = "/")
        #         if not os.path.exists(dir): os.makedirs(dir)
        #        os.chdir(dir)
        configuration_filename = "input_%.8d.dat" % (self.current_valuesset_id)
        fconf = open(configuration_filename, "w")

        for k in self.values.keys():
            print >> fconf, k, utils.replace_values(self.values[k], skip_id=False)
        fconf.close()


################################################################################
################################################################################
################################################################################
















################################################################################
################################################################################
################################################################################
################################################################################

class ResultsDBQuery(ParameterEnsemble):
    def __init__(self, full_name = "", id=-1, weight=1., queue = '*', status = 'R', repeat = 1, init_db = True):

        ParameterEnsemble.__init__(self, full_name , id, weight, queue , status , repeat  , init_db )
        self.separated_vars = self.variables[:-2]
        self.coalesced_vars = self.variables[-2:-1]
        self.in_table_vars =  self.variables[-1:]


    def setup_vars_in_table(self, conf):
        """which are the variables that are inside of the output file, orphaned variables are sent into the coalesced ones"""
        if conf.strip() != "" :
            in_table_vars = conf.split(",")
        else:
            in_table_vars = []
        if set(in_table_vars).issubset( set(self.variables) ):
            self.in_table_vars = in_table_vars
            self.coalesced_vars = [ i for i in self.coalesced_vars if ( i not in self.in_table_vars ) ]
            self.separated_vars = [ i for i in self.separated_vars if ( i not in self.in_table_vars ) ]
            
            orphaned = set(self.variables) - set(self.separated_vars) - set( self.in_table_vars ) - set( self.coalesced_vars )
            if len(orphaned) > 0:
                utils.newline_msg("VAR", "orphaned variables '%s' added to separated variables"%orphaned, indent=4)
                for i in orphaned: self.coalesced_vars.append(i)
            print "    structure = %s - %s - %s "%(self.separated_vars, self.coalesced_vars, self.in_table_vars)
        else:
        #    print in_table_vars, conf
            utils.newline_msg("VAR", "the variables '%s' are not recognised"%set(in_table_vars)-set(self.variables) )
        
                
    def setup_vars_separated(self, conf):
        """Which variables are separated in different directories, orphaned variables are sent into the coalesced ones"""
        if conf.strip() != "" :
            separated = conf.split(",")
        else:
            separated = []
        if set(separated).issubset( set(self.variables) ):
            self.separated_vars = separated
            self.coalesced_vars = [ i for i in self.coalesced_vars if ( i not in self.separated_vars )  ]
            self.in_table_vars = [ i for i in self.in_table_vars if ( i not in self.separated_vars )  ]
            orphaned = set(self.variables) - set(self.separated_vars) - set( self.in_table_vars ) - set( self.coalesced_vars )
            if len(orphaned) > 0:
                utils.newline_msg("VAR", "orphaned variables '%s' added to separated variables"%orphaned, indent=4)
                for i in orphaned: self.coalesced_vars.append(i)
            print "    structure = %s - %s - %s "%(self.separated_vars, self.coalesced_vars, self.in_table_vars)
        else:
            utils.newline_msg("VAR", "the variables '%s' are not recognised"%set(separated)-set(self.variables) )

    def setup_vars_coalesced(self, conf):
        """Which variables are coalesced into the same files, orphaned variables are sent into the separated ones"""
        if conf.strip() != "" :
            coalesced = conf.split(",")
        else:
            coalesced = []
        if set(coalesced).issubset( set(self.variables) ):
            self.coalesced_vars = coalesced
            self.separated_vars = [ i for i in self.separated_vars if ( i not in self.coalesced_vars ) ]
            self.in_table_vars = [ i for i in self.in_table_vars if ( i not in self.coalesced_vars ) ]
            orphaned = set(self.variables) - set(self.separated_vars) - set( self.in_table_vars ) - set( self.coalesced_vars )
            if len(orphaned) > 0:
                utils.newline_msg("VAR", "orphaned variables '%s' added to separated variables"%orphaned, indent=4)
                for i in orphaned: self.separated_vars.append(i)
            print "    structure = %s - %s - %s "%(self.separated_vars, self.coalesced_vars, self.in_table_vars)
        else:
            utils.newline_msg("VAR", "the variables '%s' are not recognised"%set(coalesced)-set(self.variables) )



    def clean_dict(self,dict_to_clean):
        """ adds quotes to strings """
        for i in dict_to_clean:  
            try:
                float( dict_to_clean[i] ) 
            except:
                dict_to_clean[ i ] = "'%s'"%( dict_to_clean[i ].replace("'","").replace('"',"") )

    
    def table_from_query(self, query):
        """ print query """
#        self.__connect_db()
        ret = self.execute_query(query)
        # ret = n.array( [ map(float,i) for i in self.execute_query(query) ] )
#        self.__close_db()
        return ret



    def values_set_table(self):
        query = "SELECT * FROM values_set"
        header = ["values_set_id"] + self.in_table_vars
        return header, self.table_from_query(query)

    def result_table(self, table = "results", restrict_to_values = {}, raw_data = False, restrict_by_val = False, output_column = []):

        self.clean_dict(restrict_to_values)

        if len(self.in_table_vars) == 0:
            var_cols = ""
        elif len(self.in_table_vars) == 1:
            var_cols = "v.%s, "%self.in_table_vars[0]
        elif len(self.in_table_vars) > 1:
            var_cols = "%s, "%",".join(["v.%s"%v for v in self.in_table_vars])
        if not output_column:
            output_column = self.output_column[table][:]
        if "values_set_id" in output_column: 
                output_column.remove("values_set_id")

        out_cols = ""
        if not raw_data :
            if len(output_column ) == 1:
                out_cols = "AVG(r.%s) "%output_column[0]
            elif len(output_column) > 1:
                out_cols = " %s"%",".join(["AVG(r.%s)"%v for v in output_column])
        else:
            if len(output_column ) == 1:
                out_cols = "r.%s "%output_column[0]
            elif len(output_column) > 1:
                out_cols = " %s"%",".join(["r.%s"%v for v in output_column])
          
        query = "SELECT %s %s FROM %s AS r, values_set AS v WHERE r.values_set_id = v.id "%(var_cols, out_cols, table)
        #:::~ This command was needed only because of a mistake in the id stores in the results table
        restrict_cols = ""
        if restrict_to_values:
            restrict_cols = " AND ".join(["v.%s = '%s'"%(v, restrict_to_values[v]) for v in restrict_to_values.keys()])
            if restrict_cols :
                restrict_cols = "AND %s"%restrict_cols 
        query = "%s  %s "%(query, restrict_cols)
        if not raw_data :
            if restrict_by_val:
                query = "%s  GROUP BY %s"%(query, var_cols.strip(", "))
            else:  
                query = "%s %s GROUP BY v.id"%(query, restrict_cols)
        query=query.replace("''", "'").replace("'\"", "'")

        return self.table_from_query(query)

    def result_id_table(self, table="results"):


        query = "SELECT %s FROM %s ORDER BY values_set_id " % (",".join(self.output_column[table]), table)

        return self.output_column[table], self.table_from_query(query)

    def table_header(self, table='results',output_column = []):
   
        var_cols = self.in_table_vars

        if not output_column:
            output_column = self.output_column[table][:]
        if "values_set_id" in output_column: 
            output_column.remove("values_set_id")
        return var_cols+output_column
          


    def __iter__(self):
        vars_to_separate = self.separated_vars[:]
        vars_to_separate.extend(self.coalesced_vars)

        if not vars_to_separate:
            yield {}
            return
        elif len(vars_to_separate) == 1:
            query = "SELECT DISTINCT %s FROM values_set "%( vars_to_separate[0] )
        elif len(vars_to_separate) > 1:
            query = "SELECT DISTINCT %s FROM values_set "%(",".join([v for v in vars_to_separate] ))

        pairs = self.execute_query(query)
        d = {}
        for i in pairs:
            d.clear()
            for j in range( len( vars_to_separate ) ):
                d[vars_to_separate[j] ] = i[j]
            yield d


    def update_results_from_data(self, table_file, table_name = "results", sep = "," ):
        table = csv.reader(open(table_file), delimiter=sep, lineterminator="\n")

        header = table.next()
        for row in table:
            cc = 'INSERT INTO %s (%s) VALUES (%s) ' % (table_name, ", ".join(header),
                                                   ", ".join(["'%s'" % str(i) for i in row]))

            self.execute_query(cc)


