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
    page_faults = None
    page_hits = None

    def __init__(self, installed_memory, page_size):
        super(PrimaryMemory, self).__init__()
        self.start_addr = hex(0)
        self.end_addr = hex(OSParams.installed_memory)
        self.page_size = page_size
        self.actual_memory = []
        self.free_frames = []
        self.page_faults = 0
        self.page_hits = 0
        for i in xrange(0, int(self.end_addr, 16) / page_size):
            self.actual_memory.append(-1)
            self.free_frames.append(i)

    # Dado um PID, esta função retorna o indice do processo na lista de processos
    def get_process_index(self, pid, proc_list):
        for index, item in enumerate(proc_list):
                if item.pid == pid:
                    break
        return index

    # Checa se uma dada página está na memória principal
    def page_in_memory(self, page):
        for i in xrange(0, len(self.actual_memory)):
            if self.actual_memory[i] != -1:
                if self.actual_memory[i].page_id == page.page_id:
                    return True
        return False


    # Passa um processo da memória secundária para a memória principal usando o algorítimo FIFO
    def proc_to_memory_fifo(self, process, proc_list, current_cycle):
        # Retorna a página mais antiga na memória
        def get_oldest_page():
            copied_to_memory_on_aux = sys.maxint
            for page in self.actual_memory:
                if page != -1 and page.copied_to_memory_on < copied_to_memory_on_aux:
                    copied_to_memory_on_aux = page.copied_to_memory_on
                    page_aux = page
            return page_aux

        for i in xrange(process.next_to_be_executed, process.next_to_be_executed + OSParams.pages_per_cycle):
            try:
                index = process.page_exec_order[i]
                if not self.page_in_memory(process.pages[index]) and len(self.free_frames) >= OSParams.pages_per_cycle:
                    self.page_faults += 1
                    self.actual_memory[self.free_frames[0]] = process.pages[index]
                    process.pages[index].copied_to_memory_on = current_cycle
                    process.pages[index].last_used = current_cycle
                    process.page_table[index] = self.free_frames[0]
                    self.free_frames.pop(0)
                if self.page_in_memory(process.pages[index]):
                    self.page_hits += 1
                    process.pages[index].last_used = current_cycle
                    process.next_to_be_executed += 1
                    break
                if not self.page_in_memory(process.pages[index]) and len(self.free_frames) < OSParams.pages_per_cycle:
                    oldest_page = get_oldest_page()
                    j = self.get_process_index(oldest_page.owners_pid, proc_list)

                    while len(self.free_frames) < OSParams.pages_per_cycle:
                        current_proc = proc_list[j]
                        for i in xrange(0, len(current_proc.page_table)):
                            # Retira as páginas mais antigas da memória
                            if current_proc.page_table[i] != -1 and self.actual_memory[current_proc.page_table[i]].copied_to_memory_on == oldest_page.copied_to_memory_on:
                                frame = current_proc.page_table[i]
                                self.actual_memory[frame] = -1
                                self.free_frames.append(frame)
                                current_proc.page_table[i] = -1
                        oldest_page = get_oldest_page()
                        j = self.get_process_index(oldest_page.owners_pid, proc_list)
                    self.proc_to_memory_fifo(process, proc_list, current_cycle)      
            except:
                # Chegou ao fim da lista de páginas
                process.next_to_be_executed = len(process.page_exec_order)
                break

    # Passa um processo da memória secundária para a memória principal usando o algorítimo LRU
    def proc_to_memory_lru(self, process, proc_list, current_cycle):
        
        # Retorna a página usada menos recentememente na memória
        def get_oldest_page():
            last_used_aux = sys.maxint
            for page in self.actual_memory:
                if page != -1 and page.last_used < last_used_aux:
                    last_used_aux = page.last_used
                    page_aux = page
            return page_aux

        for i in xrange(process.next_to_be_executed, process.next_to_be_executed + OSParams.pages_per_cycle):
            try:
                index = process.page_exec_order[i]
                if not self.page_in_memory(process.pages[index]) and len(self.free_frames) >= OSParams.pages_per_cycle:
                    self.page_faults += 1
                    self.actual_memory[self.free_frames[0]] = process.pages[index]
                    process.pages[index].copied_to_memory_on = current_cycle
                    process.pages[index].last_used = current_cycle
                    process.page_table[index] = self.free_frames[0]
                    self.free_frames.pop(0)
                if self.page_in_memory(process.pages[index]):
                    self.page_hits += 1
                    process.pages[index].last_used = current_cycle
                    process.next_to_be_executed += 1
                    break
                if not self.page_in_memory(process.pages[index]) and len(self.free_frames) < OSParams.pages_per_cycle:
                    oldest_page = get_oldest_page()
                    j = self.get_process_index(oldest_page.owners_pid, proc_list)

                    while len(self.free_frames) < OSParams.pages_per_cycle:
                        current_proc = proc_list[j]
                        for i in xrange(0, len(current_proc.page_table)):
                            # Retira as páginas mais antigas da memória
                            if current_proc.page_table[i] != -1 and self.actual_memory[current_proc.page_table[i]].last_used == oldest_page.last_used:
                                frame = current_proc.page_table[i]
                                self.actual_memory[frame] = -1
                                self.free_frames.append(frame)
                                current_proc.page_table[i] = -1
                        oldest_page = get_oldest_page()
                        j = self.get_process_index(oldest_page.owners_pid, proc_list)
                    self.proc_to_memory_lru(process, proc_list, current_cycle)
            except:
                # Chegou ao fim da lista de páginas
                process.next_to_be_executed = len(process.page_exec_order)
                break

    def proc_to_memory_opt(self, process, proc_list, current_cycle):

        # Encontra a página ótima para ser retirada da memória
        def get_optmal_page(proc_list):
            optimal = -1
            for page in self.actual_memory:
                # Se o frame estiver vazio, pulamos para o próximo
                if page == -1:
                    continue
                for proc in proc_list:
                    """ 
                        Se o pid do proc atual não bater com o do frame, pulamos
                        para o próximo proc
                    """
                    if proc.pid != page.owners_pid:
                        continue
                    """ 
                        Iteramos pelas páginas do processo atual (que tem o mesmo PID do processo do frame)
                        e verificamos se alguma página deste processo está na memória e caso sim,
                        nós verificamos se esta página será chamada futuramente. Caso seja, calculamos
                        um novo valor de optimal e setamos ela como a página a ser retornada pela função
                    """
                    to_be_executed = proc.page_exec_order[process.next_to_be_executed:process.next_to_be_executed + (OSParams.installed_memory / OSParams.page_size)]
                    # to_be_executed = proc.page_exec_order[process.next_to_be_executed:]
                    proc_index = self.get_process_index(proc.pid, proc_list)
                    for current_page_id in to_be_executed:
                        """
                            Verificamos se a página atual está na memória, caso não estja, pulamos para a
                            próxima iteração
                        """
                        if self.page_in_memory(page):
                            """ 
                                Verifica se a página encontrada na memória será executada futuramente.
                                Caso não seja, retornamos a própria uma vez que ela está na memória e
                                nunca mais será usada
                            """
                            if current_page_id not in to_be_executed:
                                return page
                            # Caso a página seja executada novamente em iterações futuras
                            else:
                                # Indice da página atual na sequencia de páginas a serem executadas
                                page_exec_order_index = to_be_executed.index(current_page_id)
                                """ 
                                    Calculamos quando o processo precisará da página na memória e caso
                                    este valor seja maior do que o valor ótimo, substituimos a página
                                    ótima pela página atual
                                """
                                if proc_index + page_exec_order_index > optimal:
                                    optimal_page = page
                                    optimal = proc_index + page_exec_order_index
                        else:
                            continue
            return optimal_page

        for i in xrange(process.next_to_be_executed, process.next_to_be_executed + OSParams.pages_per_cycle):
            try:
                index = process.page_exec_order[i]
                if not self.page_in_memory(process.pages[index]) and len(self.free_frames) >= OSParams.pages_per_cycle:
                    self.page_faults += 1
                    self.actual_memory[self.free_frames[0]] = process.pages[index]
                    process.pages[index].copied_to_memory_on = current_cycle
                    process.pages[index].last_used = current_cycle
                    process.page_table[index] = self.free_frames[0]
                    self.free_frames.pop(0)
                if self.page_in_memory(process.pages[index]):
                    self.page_hits += 1
                    process.pages[index].last_used = current_cycle
                    process.next_to_be_executed += 1
                    break
                if not self.page_in_memory(process.pages[index]) and len(self.free_frames) < OSParams.pages_per_cycle:
                    oldest_page = get_optmal_page(proc_list)
                    j = self.get_process_index(oldest_page.owners_pid, proc_list)

                    while len(self.free_frames) < OSParams.pages_per_cycle:
                        current_proc = proc_list[j]
                        for i in xrange(0, len(current_proc.page_table)):
                            # Retira as páginas mais antigas da memória
                            # if current_proc.page_table[i] != -1 and self.actual_memory[current_proc.page_table[i]].last_used == oldest_page.last_used:
                            if current_proc.page_table[i] != -1 and self.actual_memory[current_proc.page_table[i]].page_id == oldest_page.page_id:
                                frame = current_proc.page_table[i]
                                self.actual_memory[frame] = -1
                                self.free_frames.append(frame)
                                current_proc.page_table[i] = -1
                        oldest_page = get_optmal_page(proc_list)
                        j = self.get_process_index(oldest_page.owners_pid, proc_list)
                    self.proc_to_memory_opt(process, proc_list, current_cycle)
            except:
                # Chegou ao fim da lista de páginas
                process.next_to_be_executed = len(process.page_exec_order)
                break
