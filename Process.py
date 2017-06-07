# -*- coding: utf-8 -*-

import OSParams
from Page import Page

class Process(object):
    """docstring for Process"""

    pid = None
    size = None # In bytes
    pages = None # Vetor de páginas do processo
    page_table = None # Page table do processo. Guarda o frame em que cada página de um processo está
    next_to_be_executed = None
    arrival_time = None # Ciclo em que o processo foi criado

    def __init__(self, pid, size, arrival_time):
        super(Process, self).__init__()
        self.pid = pid
        self.size = size
        self.pages = []
        self.page_table = []
        self.next_to_be_executed = 0
        self.arrival_time = arrival_time
        if self.size % OSParams.page_size != 0:
            page_count = (self.size / OSParams.page_size) + 1
        else:
            page_count = (self.size / OSParams.page_size)
        for i in xrange(0, page_count):
            self.pages.append(Page(self.pid))
            self.page_table.append(-1)
        