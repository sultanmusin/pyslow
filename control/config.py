#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Oleg Petukhov"
__copyright__ = "2020, INR RAS"
__license__ = "GPL"
__version__ = "0.5"
__email__ = "opetukhov@inr.ru"
__status__ = "Development"



import sys
from lxml import etree
from bs4 import BeautifulSoup

sys.path.append('.')
sys.path.append('lib/hvsys')

from hvsys import HVsys

def validate(xml_path: str, xsd_path: str) -> bool:

    xmlschema_doc = etree.parse(xsd_path)
    xmlschema = etree.XMLSchema(xmlschema_doc)

    xml_doc = etree.parse(xml_path)
    #result = xmlschema.validate(xml_doc)

    #TODO xmlschema.assertValid(xml_doc)

    return True


def load(xml_path: str, schema: str):
    validate(xml_path, schema)
    with open(xml_path, 'r') as f:
        soup = BeautifulSoup(f, 'xml')
        return Config(soup)



class Config: 
    def __init__(self, soup):
        self.soup = soup
        self.process_config()


    def process_config(self):
        self.systemModules = {}

        for sys_mod in self.soup.select("global connection hvsys"):
            id = sys_mod.attrs['id']
            self.systemModules[id] = SystemModuleConfig(sys_mod)

        xx = list(map(lambda tag: int(tag.text), self.soup.select("config module geometry x")))
        self.geom_min_x, self.geom_max_x = min(xx), max(xx)
        self.geom_width = self.geom_max_x - self.geom_min_x + 1

        yy = list(map(lambda tag: int(tag.text), self.soup.select("config module geometry y")))
        self.geom_min_y, self.geom_max_y = min(yy), max(yy)
        self.geom_height = self.geom_max_y - self.geom_min_y + 1

        self.modules = {}
        self.modulesOrderedByGeometry = [''] * self.geom_height * self.geom_width

        for mod in self.soup.select("config module"):
            id = mod.attrs['id']
            x = int(mod.find('x').text) - 1
            y = int(mod.find('y').text) - 1
            self.modulesOrderedByGeometry[x + y * self.geom_width] = id
            self.modules[id] = ModuleConfig(mod)

        #print(self.modulesOrderedByGeometry)

        #self.modulesOrderedByGeometry = [
        #    "",   "",   " 1", " 2", " 3", " 4", " 5", "",   "",
        #    "35", "36", " 6", " 7", " 8", " 9", "10", "45", "46",
        #    "37", "38", "11", "12", "13", "14", "15", "47", "48",
        #    "39", "40", "16", "17", "",   "18", "19", "49", "50",
        #    "41", "42", "20", "21", "22", "23", "24", "51", "52",
        #    "43", "44", "25", "26", "27", "28", "29", "53", "54",
        #    "",   "",   "30", "31", "32", "33", "34", "",   ""
        #    ]

        self.modulesOrderedById = list(self.modules.keys())
        self.modulesOrderedById.sort(key=int)
        #print(self.modulesOrderedById)

        for mod in self.soup.select("global flags onlineModules"):
            self.modules[mod.text.strip()].online = True





class ModuleConfig:
    possible_parts = list(HVsys.catalogus.keys())

    def __init__(self, soup):
        self.id = soup.attrs['id']
        self.parts = []
        self.addr = {}

        for part in ModuleConfig.possible_parts:
            partConfigNode = soup.find('connection').find(part)
            if partConfigNode is not None:
                self.parts.append(part)
                self.addr[part] = int(partConfigNode.find('id').text)

        connectionNode = soup.find('connection').find('hvsys')
        self.systemModuleId = connectionNode.attrs['id']

        hvConfigNode = soup.find('connection').find('hv')
        if self.has('hv'):
            self.hv = {}
            for chan in soup.select("settings hv channel"):
                self.hv[chan.attrs['id']] = float(chan.text)
            self.hvPedestal = float(soup.find('settings').find('hv').find('pedestal').text)

        ledConfigNode = soup.find('connection').find('led')
        if self.has('led'):
            self.ledAutoTune = int(soup.find('settings').find('led').find('autoTune').text)
            self.ledBrightness = int(soup.find('settings').find('led').find('brightness').text)
            self.ledFrequency = int(soup.find('settings').find('led').find('frequency').text)
            self.ledPinADCSet = int(soup.find('settings').find('led').find('pinADCSet').text)

        self.online = False
    

    def has(self, part : str):
        return part in self.parts

    def address(self, part: str):
        return self.addr[part]


class SystemModuleConfig:
    def __init__(self, soup):
        self.id = soup.attrs['id']
        self.port = soup.find("port").text
