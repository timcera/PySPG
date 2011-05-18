#! /usr/bin/env python
# -*- coding: utf-8 -*-

###########################################################################
# :::~ Copyright (C) 2003-2010 by Claudio J. Tessone <tessonec@ethz.ch> 
# 
# Modified on: v2.9.1 30 May 2010
# Modified on: v2.9   15 Sep 2008
# Created  on: v0.1   09 Jan 2005
# 
# License: Distributed according to GNU/GPL Version 2 
#          (see http://www.gnu.org)
#
###########################################################################


version_number = '2.9.0'
release_date = 'Sep 17 2008'

import iterator 

from math import * 

import os.path 
import re



class Execute(iterator.Iterator):
  def __init__(self, cl):
    """ name: the label to be assigned to this iterator
      data: the set of values can be assigned to this iterator
    """
    self.name  = ""
    self.data  = []
    self.reset()

    self.command = cl
    

  def __call__(self):
    print "function being called"
    
  



class Parser(iterator.MultIterator):
    """
      a param iterator with functionality added
    """

    def __init__(self, stream = None):
        iterator.MultIterator.__init__(self)
        self.regexp = re.compile('\\w')
        
        if stream is not None:
          self.fetch(stream)


    def directory_path(self, var_list):
      """
      returns the directory path conducting to the current values of the parameter set.
      by default (limit=-1) the directory tree is extended to all the variables list
      except for the last variable.
      By setting limit to something else, you change the amount of variables kept left from
      the directory generation. (i.e. limit=-2, will leave out of the directory path the last two variables)
      """
      the_path = (os.path.curdir + os.path.sep)
      for i_key in var_list:
            the_path += (('%s-%s' % (i_key,
              self.current_values[i_key])) + os.path.sep)

      return the_path

    def output_file(self, var_list):
      """
      returns the directory path conducting to the current values of the parameter set.
      by default (limit=-1) the directory tree is extended to all the variables list
      except for the last variable.
      By setting limit to something else, you change the amount of variables kept left from
      the directory generation. (i.e. limit=-2, will leave out of the directory path the last two variables)
      """
      of = "-".join([ "%s-%s"%(k,self.current_values[k]) for k in var_list ] ) 

      return of+".dat"

    def output_conf(self):
      ret = ""
      for i in self.data:
        if i.__class__ == iterator.Iterator:
          if len(i.data) == 0:
            ret += ":%s  %s\n"%(i.name, " ".join(i.data))
          else:
            ret += ".%s  %s\n"%(i.name, " ".join(i.data))
        if i.__class__ == iterator.IterOperator:
          ret += "%s%s  %s  %s  %s\n"%(i.type, i.name, i.xmin, i.xmax, i.xstep)
      return ret


    def fetch(self, stream):
        for l in stream:
            linea = l.strip()

            symbol_end = self.regexp.search(linea).start()
            symbol = linea[:symbol_end].strip()
            rest = linea[symbol_end:].strip().split()

            if symbol is '#': continue #line is a comment

            if (symbol in ('!')): # reserved for the future
              continue

            if (symbol in ['+', '-', '*', '/', '**']):

              self.add( \
                iterator.IterOperator( rest[0], symbol, \
                       (eval(rest[1] ), eval( rest[2]), eval(rest[3]) ) ) )
            if (symbol == '.'):
              self.add( \
                 iterator.Iterator(rest[0], rest[1:]) )
            if (symbol == ':'):
              self.add( iterator.Iterator( name = "".join(rest) ) )




class ExtensibleParser(Parser):
    """
      a param iterator with functionality added
    """

    def __init__(self, stream = None):
        Parser.__init__(self, stream)
        self.add_ins = {}
        
        if stream is not None:
          self.fetch(stream)

    def add_plugin(self, rw, manip):
      self.add_ins[rw] = manip

    def parse_reserved_word(self, rest):
       if rest[0] in self.add_ins.keys():
           self.add( self.add_ins[ rest[0] ]( rest[1:] ) )


    def fetch(self, stream):
        for l in stream:
            linea = l.strip()

            symbol_end = self.regexp.search(linea).start()
            symbol = linea[:symbol_end].strip()
            rest = linea[symbol_end:].strip().split()

            if symbol is '#': continue #line is a comment

            if (symbol in ('!')): # reserved for the future
              continue

            if (symbol is '@' and rest[0]=="execute"):
              self.add( Execute( rest[1:]) )

            if (symbol in ['+', '-', '*', '/', '**']):
              self.add( \
                iterator.IterOperator( rest[0], symbol, \
                       (eval(rest[1] ), eval( rest[2]), eval(rest[3]) ) ) )

            if (symbol == '.'):
              self.add( \
                 iterator.Iterator(rest[0], rest[1:]) )

            if (symbol == ':'):
              self.add( iterator.Iterator( name = "".join(rest) ) )





if __name__ == '__main__':
    pp = Parser()
#    pp.fetch(['+D 0. 10 1',' *r 2 16 2','**e 2 32 2', ': HELLO', '.bar 6 4 3','# this is a comment'])
    pp.fetch(['+D 0. 10 1',' *r 2 16 8'])
    pp.output_conf()
    for i in pp:
      print i


