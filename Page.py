# -*- coding: utf-8 -*-

class Page(object):
    """docstring for Page"""

    owners_pid = None
    last_used = None # Guarda em qual ciclo a pagina entrou na memória

    def __init__(self, owners_pid):
        super(Page, self).__init__()
        self.owners_pid = owners_pid
        