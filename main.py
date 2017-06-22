# -*- coding: utf-8 -*-

import random
import OSParams
from PrimaryMemory import PrimaryMemory
from Process import Process
import sys
import json

process_file = 'Processes2.json'

def print_memory(actual_memory):
    print "======================================="
    for i in xrange(0, len(actual_memory)):
        try:
            print actual_memory[i].owners_pid, " [" + str(actual_memory[i].page_id) + "], ", actual_memory[i].last_used
        except:
            print -1
    print "======================================="

# Lê arquivo de entrada json e gera a lista de processos
def create_proc_list(file_name, current_cycle = 0):
    proc_list = []
    proc_to_be_created_list = []
    with open(file_name) as proc_file:
        proc_file_data = json.load(proc_file)

    for i in xrange(0, len(proc_file_data["procs"])):
        current_proc = proc_file_data["procs"][i]
        if current_proc["arrival_time"] == current_cycle:
            proc_list.append(Process(i + 1, current_proc["num_pages"] * OSParams.page_size, current_proc["arrival_time"], current_proc["page_exec_order"]))
        else:
            proc_to_be_created_list.append(Process(i + 1, current_proc["num_pages"], current_proc["arrival_time"], current_proc["page_exec_order"]))

    return proc_list, proc_to_be_created_list

# Usa o algorítimo FIFO para a troca de páginas na memória
def run(scheduling_policy):
    primaryMemory = PrimaryMemory(OSParams.installed_memory, OSParams.page_size)
    proc_list = [] # Lista de processos em execução
    proc_to_be_created_list = [] # Processos que vão entrar na CPU em ciclos futuros
    proc_dict = {}
    current_cycle = 0

    proc_list = create_proc_list(process_file)[0]
    proc_to_be_created_list = create_proc_list(process_file)[1]

    # print "Numero de frames = ", len(primaryMemory.actual_memory)

    while proc_list:
        if scheduling_policy.lower() == 'fifo':
            primaryMemory.proc_to_memory_fifo(proc_list[0], proc_list, current_cycle)
        elif scheduling_policy.lower() == 'lru':
            primaryMemory.proc_to_memory_lru(proc_list[0], proc_list, current_cycle)
        elif scheduling_policy.lower() == 'opt':
            primaryMemory.proc_to_memory_opt(proc_list[0], proc_list, current_cycle)

        """print "Cycle: ", current_cycle
        print "Free frames: ", primaryMemory.free_frames
        print "Proc list: ", [proc_list[i].pid for i in xrange(0, len(proc_list))]
        print proc_list[i].page_exec_order[proc_list[i].next_to_be_executed:]
        print_memory(primaryMemory.actual_memory)"""

        # Exclui processo da memória caso a execução tenha terminado
        if proc_list[0].next_to_be_executed == len(proc_list[0].page_exec_order):
            proc_dict[proc_list[0].pid] = current_cycle - proc_list[0].arrival_time
            for page_addr in proc_list[0].page_table:
                if page_addr != -1:
                    primaryMemory.actual_memory[page_addr] = -1
                    primaryMemory.free_frames.append(page_addr)
        else:
            proc_list.append(proc_list[0])
        proc_list.pop(0)
        current_cycle += OSParams.pages_per_cycle

        """ 
            Confere se existe algum processo para ser criado no novo ciclo. Caso exista, este processo(s) é(são) 
            adicionados ao fim da lista de processos prontos para execução
        """
        for i in xrange(0, len(proc_to_be_created_list)):
            current_proc = proc_to_be_created_list[i]
            if current_proc.arrival_time == current_cycle:
                proc_list.append(current_proc)

    # print proc_dict
    print "Page faults - " + scheduling_policy.upper() + ": " + str(primaryMemory.page_faults) + ", Page hits: " + str(primaryMemory.page_hits)

if __name__ == '__main__':
    run('fifo')
    run('lru')
    run('opt')