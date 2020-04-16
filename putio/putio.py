#!/usr/bin/env python
# coding: utf-8

import ftplib as ftp
import pandas as pd
from termcolor import colored
from imdb import IMDb
import re
from socket import _GLOBAL_DEFAULT_TIMEOUT
import os


class Identifiants:
    
    def __init__(self, host, user, passwd):
        self.host = host
        self.user = user
        self.passwd = passwd

    def __str__(self):
        return self.host + " | " + self.user


class Connexion(ftp.FTP):
    
    def __init__(self, identifiants, acct='', timeout=_GLOBAL_DEFAULT_TIMEOUT, source_address=None):
        self.source_address = source_address
        self.timeout = timeout
        if identifiants.host:
            self.connect(identifiants.host)
            if identifiants.user:
                self.login(identifiants.user, identifiants.passwd, acct)
    
    
    def is_dir(self, filename):
        try:
            self.cwd(filename)
        except:
            return False
        self.cwd("..")
        return True

    
    def liste_contenu(self, dossier):
        dir_list = self.nlst(dossier)
        return pd.DataFrame(dir_list, columns=["Dir"])

    
    def suppr_fichier(self, fichier):
        global flag
        global film_supprime
        x = fichier.split(".")
        self.sendcmd("TYPE i")
        try:
            size = self.size(fichier)
        except:
            print(colored("Fichier invalide :", 'red'), fichier)
        extension = x[-1]
        if extension in ["mkv", "mp4"]:
            titre = recuperer_titre_re(fichier)
            annee = recuperer_annee_re(fichier)
            if len(titre) < 35 and is_serie(fichier) == False:
                rating = info_film(titre, annee)
                if rating and rating >= 6.5:
                    couleur = "green"
                else:
                    couleur = "red"
                    try:
                        self.delete(fichier)
                        print(colored("Supprimé : {0} (note : {1})".format(fichier, rating), 'green'))
                        flag += 1
                        film_supprime = 1
                    except:
                        print(colored("Suppression du fichier impossible :", 'red'), fichier)
                #print(indent + titre + ": " + colored(str(rating), couleur))
        elif extension in ["jpg", "jpeg"]:
            try:
                self.delete(fichier)
                print(colored("Supprimé : {0} (jpeg)".format(fichier), 'green'))
                flag += 1
            except:
                print(colored("Suppression du fichier impossible.", 'red'), fichier)
        elif extension == "srt" and film_supprime == 1:
            try:
                self.delete(fichier)
                print(colored("Supprimé : {0} (film supprimé)".format(fichier), 'green'))
                flag += 1
            except:
                print(colored("Suppression du fichier impossible.", 'red'), fichier)
        elif size < 1000000 and extension != "srt":
            try:
                self.delete(fichier)
                print(colored("Supprimé : {0} (taille : {1})".format(fichier, size), 'green'))
                flag += 1
            except:
                print(colored("Suppression du fichier impossible.", 'red'), fichier)
        return flag

    
    def parcours_liste(self, liste):
        global flag
        global indent
        global film_supprime
        film_supprime= 0
        for contenu in liste["Dir"]:
            #print(indent, contenu)
            if self.is_dir(contenu):
                sous_contenu = self.liste_contenu(contenu)
                if sous_contenu.empty:
                    try:
                        self.rmd(contenu)
                        print(colored("Suppression du dossier :", 'green'), contenu)
                        flag += 1
                    except:
                        print(colored("Suppression du dossier impossible :", 'red'), contenu)
                    #print("")
                else:
                    indent = indent + "    "
                    try:
                        self.cwd(contenu)
                    except:
                        print(colored("Parcours du dossier impossible :", 'red'), contenu)
                    self.parcours_liste(sous_contenu)
                    self.cwd("..")
                    indent = indent[:len(indent)-4]
            else:
                flag = self.suppr_fichier(contenu)
        #print("")


def recuperer_titre(fichier):
    film = fichier.replace('2018', '2019')
    film = film.split("2019")
    titre = film[0].replace(".", " ")
    return titre


def recuperer_titre_re(fichier):
    p = re.compile(r"([\w\d \.]*).([\d]{4}).([\dp]{4,5})(.*)")
    m = p.search(fichier)
    if m:
        return m.group(1).replace(".", " ")
    else:
        return ""

    
def recuperer_annee_re(fichier):
    p = re.compile(r"([\w\d \.]*).([\d]{4}).([\dp]{4,5})(.*)")
    m = p.search(fichier)
    if m:
        return m.group(2)
    else:
        return ""

    
def recuperer_annee_imdb(fichier):
    p = re.compile(r"([\d]{4})")
    m = p.search(fichier)
    if m:
        return m.group(1)
    else:
        return ""


def is_serie(fichier):
    p = re.compile('[sS][0-9]+[eE][0-9]+')
    m = p.search(fichier)
    if m:
        return True
    else:
        return False


def info_film(titre, annee):
    s = i.search_movie(titre, results=5)
    for j in range(len(s)):
        m = i.get_movie(s[j].movieID)
        i.update(m, 'release dates')
        try:
            if recuperer_annee_imdb(m["release dates"][0]) == annee:
                try:
                    rating = m.get('rating')
                    return rating
                except:
                    print(indent, colored("Note introuvable :", 'red'), titre)
                    return 10
        except:
            continue


def main():

    HOST = os.getenv('HOST')
    USER = os.getenv('USER')
    PASSWORD = os.getenv('PASSWORD')

    print("---- Cleaning started ----")
    print("Host => " + HOST)
    print("User => " + USER)

    identifiants = Identifiants(HOST, USER, PASSWORD)
    print(colored(identifiants, 'blue'))
    
    connect = Connexion(identifiants)

    liste = connect.liste_contenu('/')
    connect.parcours_liste(liste)
    
    if flag == 0:
        print("Terminé : pas de fichier supprimé.")
    else:
        print("Terminé : {0} fichier(s) ou dossier(s) supprimé(s).".format(flag))


if __name__ == '__main__':
    indent = ""
    flag = 0
    i = IMDb()
    film_supprime = 0
    main()