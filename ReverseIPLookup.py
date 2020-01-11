import ctypes
import os
import threading
import time
from queue import Queue

import colorama
import requests


colorama.init()






class IPReverse():
    def __init__(self):
        self.Threadcount = int(input("Threads?\n"))
        os.system("cls")
        self.ProxyLoc = input("Proxyfile?\n")
        os.system("cls")
        self.IPListLoc = input("IPList?\n")
        os.system("cls")
        choose = input("[1]HTTP/S\n[2]Socks4\n[3]Socks5\n")
        os.system("cls")
        if choose == 1:
            self.ProxyPre = ""
        elif choose == 2:
            self.Proxypre = "socks4://"
        else:
            self.Proxypre = "socks5://"
        
        
        try:
            IP = open("ips.txt","r").readlines()
        except:
            print("Invalid IPFile!")
            pass
        
        self.proxys = Queue()
        self.IPs = Queue()
        
        self.PrintList = []
        
        self.currentproxy = ""
        self.ProxyCount = 0
        
        self.Count = 0
        self.Checked = 0
        self.Hits = 0
        self.Invalid = 0
        self.Domains = 0
        self.WriteQueue = Queue()
        
        self.CPM = 0
        
        try:
            proxy = open("proxy.txt","r").readlines()
        except:
            print("Invalid Proxyfile!")
            pass
        
        for i in IP:
            self.IPs.put(i.strip())

        for i in proxy:
            self.proxys.put(self.Proxypre + i.strip())
        
        for i in range(0,self.Threadcount):
            threading.Thread(target=self.Thread).start()

        threading.Thread(target=self.CPMCounter).start()
        threading.Thread(target=self.Writer).start()
        threading.Thread(target=self.Printer).start()


    def CPMCounter(self):
        while True:
            old = self.Checked 
            time.sleep(1)
            new = self.Checked
            self.CPM = int(new - old)*60
            
            
    def Lookup(self,ip,proxy):
        try:
            resp = requests.get("https://api.hackertarget.com/reverseiplookup/?q=" + ip,proxies={"https":proxy},timeout=3)
        except:
            return False
        return resp.text

    def Writer(self):
        while True:
            try:
                curip = self.WriteQueue.get(timeout=1)
            except:
                continue
            open("Output.txt","a+").write(curip + "\n")
            
    def Printer(self):
        while True:
            ctypes.windll.kernel32.SetConsoleTitleW("Reverse IP Lookup | Made by Nezuko | Proxys remaining: " + str(self.proxys.qsize()) + " | IPs remaining: " + str(self.IPs.qsize()) + " | Hits: " + str(self.Hits) + " | Found Domains: " + str(self.Domains) + " | CPM: " + str(self.CPM))
            cur = ""
            for i in self.PrintList:
                cur += i + "\n"
            print(cur)
            if self.ProxyCount >= 10:
                self.currentproxy = self.proxys.get()
                self.ProxyCount = 0
            time.sleep(0.1)
            os.system("cls")

    def Thread(self):
        while True:
            try:
                curip = self.IPs.get(timeout=1)
            except:
                continue
            if self.ProxyCount != 10:
                self.ProxyCount += 1
                resp = self.Lookup(curip,self.currentproxy)
            else:
                time.sleep(0.3)
                self.ProxyCount += 1
                resp = self.Lookup(curip,self.currentproxy)
            self.Checked += 1
            if resp == False or "429 Too Many Requests" in resp:
                self.IPs.put(curip)
                continue
            elif "No DNS A records found for " in resp or resp == "error check your search parameter":
                self.Invalid += 1
                #print(resp.text)
            else:
                #print(resp.text)
                self.Checked += 1
                self.Hits += 1
                
                domains = resp.split("\n")
                domains.pop(0)
                for m in domains:
                    self.Domains += 1
                    self.WriteQueue.put(m.strip())
                self.PrintList.append(colorama.Fore.GREEN + "Found Domain for " + curip + "!" + colorama.Style.RESET_ALL)


a = IPReverse()
while True:
    time.sleep(1)
