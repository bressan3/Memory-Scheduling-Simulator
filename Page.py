# -*- coding: utf-8 -*-

class Page(object):
    """docstring for Page"""

    owners_pid = None
    page_id = None
    last_used = None # Guarda qual o último ciclo que a página foi usada
    copied_to_memory_on = None # Guarda em qual ciclo a pagina entrou na memória

    def __init__(self, owners_pid, page_id):
        super(Page, self).__init__()
        self.owners_pid = owners_pid
        self.page_id = page_id
        