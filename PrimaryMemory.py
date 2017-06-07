# -*- coding: utf-8 -*-

import OSParams
import sys
from Page import Page

class PrimaryMemory(object):
    """docstring for PrimaryMemory"""
    start_addr = None
    end_addr = None
    page_size = None
    actual_memory = None # Vetor representando a memória. Cada índice é uma página
    free_frames = None # Vetor contendo o índice dos frames desocupados da memória principal

    def __init__(self, installed_memory, page_size):
        super(PrimaryMemory, self).__init__()
        self.start_addr = hex(0)
        self.end_addr = hex(OSParams.installed_memory)
        self.page_size = page_size
        self.actual_memory = []
        self.free_frames = []
        for i in xrange(0, int(self.end_addr, 16) / page_size):
            self.actual_memory.append(-1)
            self.free_frames.append(i)

    # Dado um PID, esta função retorna o indice do processo na lista de processos
    def get_process_index(self, pid, proc_list):
        for index, item in enumerate(proc_list):
                if item.pid == pid:
                    break
        return index

    # Passa um processo da memória secundária para a memória principal usando o algorítimo FIFO
    def proc_to_memory_fifo(self, process, proc_list, current_cycle):

        # Retorna a página mais antiga na memória
        def get_oldest_page():
            last_used_aux = sys.maxint
            for page in self.actual_memory:
                if page != -1 and page.last_used < last_used_aux:
                    last_used_aux = page.last_used
                    page_aux = page
            return page_aux

        if len(self.free_frames) >= OSParams.pages_per_cycle:
            for i in xrange(process.next_to_be_executed, process.next_to_be_executed + OSParams.pages_per_cycle):
                try:
                    self.actual_memory[self.free_frames[0]] = process.pages[i]
                    process.pages[i].last_used = current_cycle
                    process.page_table[i] = self.free_frames[0]
                    self.free_frames.pop(0)
                    process.next_to_be_executed += 1
                except:
                    # Chegou ao fim da lista de páginas
                    process.next_to_be_executed = len(process.pages)
                    break
        else:
            oldest_page = get_oldest_page()
            j = self.get_process_index(oldest_page.owners_pid, proc_list)
            print "Last used process: ", proc_list[j].pid

            while len(self.free_frames) < OSParams.pages_per_cycle and j >= 0:
                current_proc = proc_list[j]
                for i in xrange(0, len(current_proc.page_table)):
                    # Retira as páginas mais antigas da memória
                    if current_proc.page_table[i] != -1 and self.actual_memory[current_proc.page_table[i]].last_used == oldest_page.last_used:
                        frame = current_proc.page_table[i]
                        self.actual_memory[frame] = -1
                        self.free_frames.append(frame)
                        current_proc.page_table[i] = -1
                # j -= 1
                oldest_page = get_oldest_page()
                j = self.get_process_index(oldest_page.owners_pid, proc_list)
            self.proc_to_memory_fifo(process, proc_list, current_cycle)

