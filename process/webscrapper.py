import requests
from bs4 import BeautifulSoup
import docx
import os
import subprocess
import re
import connetion_DB
import tkinter as tk
from tkinter import simpledialog
from enum import Enum
import datetime



class webscrapper:
    def executar(url):
        print("Iniciando o webscrapper: " + url )
        response = requests.get(url)
        if response.status_code == 200:
        
                # Analisando o HTML com BeautifulSoup
                soup = BeautifulSoup(response.text, "html.parser")
                return soup
        else:
            return None