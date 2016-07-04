#!/usr/bin/python


import random as rnd
import threading, time
import spg.utils as utils


from spg.master import SPGMasterDB
from spg.simulation import ParameterEnsembleExecutor, ParameterEnsembleThreaded

class SPGRunningAtom(threading.Thread):
    n_threads = 0
    def __init__(self, ensemble, lock, master_db ):

        SPGRunningAtom.n_threads += 1
        threading.Thread.__init__(self)
        self.thread_id = SPGRunningAtom.n_threads
        self.ensemble = ensemble
        self.lock = lock
        self.master_db = master_db


    def run(self):
        self.lock.acquire()
        self.ensemble.next()
        current_run_id, values = self.ensemble.get_current_information()
        print "-S- [%4d]- ----- %s / %d" % (self.thread_id, self.ensemble.full_name, current_run_id)
        self.lock.release()

        try:
            current_run_id, output, stderr, run_time , return_code  = self.ensemble.launch_process(current_run_id, values )
        except:
            self.master_db.query_master_db("")

        self.lock.acquire()
        self.ensemble.dump_result( current_run_id, output, stderr, run_time , return_code  )
        if return_code == 0:
            self.ensemble.query_set_run_status("D")
        elif return_code == -2:
            self.ensemble.query_set_run_status("N")
        else:
            self.ensemble.query_set_run_status("E")
        print "-X- [%4d]- ----- %s / %d -> %d" % (self.thread_id, self.ensemble.full_name, current_run_id, return_code)
        self.lock.release()








class SPGRunningPool():
    def __init__(self):
        self.master_db = SPGMasterDB( EnsembleConstructor = ParameterEnsembleThreaded )
        self.lock = threading.Lock()
        self.db_locks = {}

    def get_lock(self, i_db):
        if not self.db_locks.has_key( i_db.full_name ):
            self.db_locks[ i_db.full_name  ] = threading.Lock()
        return self.db_locks[ i_db.full_name  ]

    def launch_workers(self):
        target_jobs, = self.master_db.query_master_fetchone('SELECT max_jobs FROM queues WHERE name = "default"')

        current_count = self.active_threads()
        to_launch = target_jobs - current_count
        if to_launch >= 0:
           utils.newline_msg( "STATUS", "[n_jobs=%d] run=%d ::: new=%d" % (target_jobs,current_count, to_launch ) )
        else:
            utils.newline_msg("STATUS", "[n_jobs=%d] run=%d :!: exceed" % (target_jobs,current_count))

        self.master_db.update_list_ensemble_dbs()
        for i_t in range(to_launch):
            self.lock.acquire()
            pick = self.master_db.pick_ensemble()
            self.lock.release()

            nt = SPGRunningAtom(pick, self.lock, self.master_db)
            # nt = SPGRunningAtom(pick, lock=self.get_lock( pick ) )

            nt.start()

    def active_threads(self):
        return threading.active_count() - 1











#rp = SPGRunningPool(50, 2)
#rp.run()