# -*- coding: utf-8 -*-

import random
import OSParams
from PrimaryMemory import PrimaryMemory
from Process import Process
import sys
import json

def print_memory(actual_memory):
    print "======================================="
    for i in xrange(0, len(actual_memory)):
        try:
            print actual_memory[i].owners_pid
        except:
            print -1
    print "======================================="

# Usa o algorítimo FIFO para a troca de páginas na memória
def fifo():
    primaryMemory = PrimaryMemory(OSParams.installed_memory, OSParams.page_size)
    proc_list = [] # Lista de processos em execução
    proc_to_be_created_list = [] # Processos que vão entrar na CPU em ciclos futuros
    proc_dict = {}
    current_cycle = 0

    with open('Processes.json') as proc_file:
        proc_file_data = json.load(proc_file)

    for i in xrange(0, len(proc_file_data["procs"])):
        current_proc = proc_file_data["procs"][i]
        if current_proc["arrival_time"] == current_cycle:
            proc_list.append(Process(i + 1, current_proc["num_pages"] * OSParams.page_size, current_proc["arrival_time"]))
        else:
            proc_to_be_created_list.append(Process(i + 1, current_proc["num_pages"], current_proc["arrival_time"]))

    print "Numero de frames = ", len(primaryMemory.actual_memory)

    while proc_list:
        primaryMemory.proc_to_memory_fifo(proc_list[0], proc_list, current_cycle)
        print "Cycle: ", current_cycle
        print "Free frames: ", primaryMemory.free_frames
        print "Proc list: ", [proc_list[i].pid for i in xrange(0, len(proc_list))]

        print_memory(primaryMemory.actual_memory)

        # Exclui processo da memória caso a execução tenha terminado
        if proc_list[0].next_to_be_executed == len(proc_list[0].pages):
            proc_dict[proc_list[0].pid] = current_cycle - proc_list[0].arrival_time
            """for i in xrange(0, len(primaryMemory.actual_memory)):
                # Exclui processo da memória caso a execução tenha terminado
                if primaryMemory.actual_memory[i] != -1 and (primaryMemory.actual_memory[i].owners_pid == proc_list[0].pid):
                    primaryMemory.actual_memory[i] = -1
                    primaryMemory.free_frames.append(i)"""
            for page_addr in proc_list[0].page_table:
                if page_addr != -1:
                    primaryMemory.actual_memory[page_addr] = -1
                    primaryMemory.free_frames.append(page_addr)
        else:
            proc_list.append(proc_list[0])
        proc_list.pop(0)
        current_cycle += 1

        """ 
            Confere se existe algum processo para ser criado no novo ciclo. Caso exista, este processo(s) é(são) 
            adicionados ao fim da lista de processos prontos para execução
        """
        for i in xrange(0, len(proc_to_be_created_list)):
            current_proc = proc_to_be_created_list[i]
            if current_proc.arrival_time == current_cycle:
                proc_list.append(current_proc)

    print proc_dict

    def sjf_round_robin():
        pass

if __name__ == '__main__':
    fifo()