# -*- coding: utf-8 -*-

from collections import Counter, defaultdict
from optparse import OptionParser
import codecs
import json
import os.path
import random
import re
import sys

RYMY_PLIK = os.path.join('data', 'rymy.json')
POPRZEDNIE_SLOWO_PLIK = os.path.join('data', 'beforewords.json')
NAZWY_WLASNE_PLIK = os.path.join('data', 'propernames.json')

ZNAKI_DO_USUNIECIA = ',-—–„”«»*/[]1234567890'
SEPARATORY_SENTENCJI = '.!?…;:()'

RZYMSKIE_WZOR_1 = re.compile('^[IVX]+$', re.MULTILINE)
RZYMSKIE_WZOR_2 = re.compile('^.* [IVX]+$', re.MULTILINE)


def UsuntTytulIInformacjeOAutorze(tekst):
    index = tekst.find('\n\n\n') + 3
    return tekst[index:]


def UsunPrzypis(tekst):
    index = tekst.rfind('\n\n\n\n')
    return tekst[:index]


def getText(sciezkaPliku):
    f = codecs.open(sciezkaPliku, 'r', 'utf-8')
    linie = f.readlines()
    tekst = "".join(linie)
    tekst = UsuntTytulIInformacjeOAutorze(tekst)
    tekst = UsunPrzypis(tekst)
    return tekst


def usunLinieZRzymskimiNumerami(tekst):
    while (re.search(RZYMSKIE_WZOR_1, tekst)):
        tekst = re.sub(RZYMSKIE_WZOR_1, '', tekst)
    while (re.search(RZYMSKIE_WZOR_2, tekst)):
        tekst = re.sub(RZYMSKIE_WZOR_2, '', tekst)
    return tekst


def usunZnak(s, znaki):
    rezultat = s
    for c in znaki:
        rezultat = rezultat.replace(c, '')
    return rezultat


def PodzielNaZdania(tekst):
    wzor = re.compile('[' + SEPARATORY_SENTENCJI + ']')
    return re.split(wzor, tekst)


def UaktualnijPrzedSlowami(slowoPrzed, tekst):
    tekstMaly = tekst.lower()
    zdania = PodzielNaZdania(tekstMaly)
    for zdanie in zdania:
        poprzednieSlowo = None
        for slowo in zdanie.split():
            if (poprzednieSlowo != None):
                slowoPrzed[slowo][poprzednieSlowo] += 1
            poprzednieSlowo = slowo


def RymDoSlowa(slowo1, slowo2):
    a = slowo1.replace('ó', 'u')
    a = a.replace('rz', 'ż')
    a = a.replace('ch', 'h')
    b = slowo2.replace('ó', 'u')
    b = b.replace('rz', 'ż')
    b = b.replace('ch', 'h')
    return a[-3:] == b[-3:]


def przechodniSymetrycznyDodaj(rymy, slowo1, slowo2):
    rymy1 = set(rymy[slowo1])
    rymy2 = set(rymy[slowo2])

    for slowo in rymy1:
        rymy[slowo].update(rymy2)
        rymy[slowo].add(slowo2)

    for slowo in rymy2:
        rymy[slowo].update(rymy1)
        rymy[slowo].add(slowo1)

    rymy[slowo1].update(rymy2)
    rymy[slowo1].add(slowo2)
    rymy[slowo2].update(rymy1)
    rymy[slowo2].add(slowo1)


def znajdzRymy(rymy, tekst):
    tekstZMalejLitery = tekst.lower()
    linie = tekstZMalejLitery.splitlines()
    slowaWLiniach = []
    for linia in linie:
        slowaWLini = linia.split()
        if (len(slowaWLini) != 0):
            slowaWLiniach.append(slowaWLini)
    ostatnieSlowa = [slowaWLini[-1] for slowaWLini in slowaWLiniach]
    for i in range(0, len(ostatnieSlowa) - 1):
        slowo1 = ostatnieSlowa[i]
        for j in range(i + 1, min(i + 4, len(ostatnieSlowa))):
            slowo2 = ostatnieSlowa[j]
            if not slowo1 == slowo2 and RymDoSlowa(slowo1, slowo2) and not slowo2 in rymy[slowo1]:
                przechodniSymetrycznyDodaj(rymy, slowo1, slowo2)


def ZnajdzOdpowiedniaNazwe(nazwyWlasne, zwykleSlowa, tekst):
    zdania = PodzielNaZdania(tekst)
    pierwszeSlowoWSentencji = set()
    for zdanie in zdania:
        slowa = zdanie.split()
        if slowa:
            pierwszeSlowoWSentencji.add(slowa[0])
    czyscTekst = usunZnak(tekst, SEPARATORY_SENTENCJI)
    linie = czyscTekst.splitlines()
    pierwszeSlowaWSentencji = set()
    for linia in linie:
        slowa = linia.split()
        if slowa:
            pierwszeSlowaWSentencji.add(slowa[0])
    slowa = czyscTekst.split()
    for slowo in slowa:
        if slowo[0].isupper() and not slowo in pierwszeSlowaWSentencji and not slowo in pierwszeSlowoWSentencji:
            nazwyWlasne.add(slowo)
        if slowo[0].islower():
            zwykleSlowa.add(slowo)


def liczbaSylabNaLiscie(l):
    return LiczbaSylab(" ".join(l))


def LiczbaSylab(tekst):
    count = tekst.count('a')
    count += tekst.count('ą')
    count += tekst.count('e')
    count += tekst.count('ę')
    count += tekst.count('i')
    count += tekst.count('o')
    count += tekst.count('ó')
    count += tekst.count('u')
    count += tekst.count('y')
    count -= tekst.count('au')
    count -= tekst.count('eu')
    count -= tekst.count('ia')
    count -= tekst.count('ie')
    count -= tekst.count('ią')
    count -= tekst.count('ię')
    return count


def stworzLinie(sylaby, slowoPrzed, linia):
    s = liczbaSylabNaLiscie(linia)
    if s == sylaby:
        linia[0] = linia[0].capitalize()
        return linia
    if s > sylaby: return None

    mozliweSlowo = slowoPrzed[linia[0]]
    if not mozliweSlowo: return None
    mozliweSlowoLewe = set(mozliweSlowo)
    slowo = random.choice(list(mozliweSlowoLewe))
    mozliweSlowoLewe.remove(slowo)
    nowaLinia = stworzLinie(sylaby, slowoPrzed, [slowo] + linia)
    while not nowaLinia and mozliweSlowoLewe:
        slowo = random.choice(list(mozliweSlowoLewe))
        mozliweSlowoLewe.remove(slowo)
        nowaLinia = stworzLinie(sylaby, slowoPrzed, [slowo] + linia)
    return nowaLinia


def stworzLinieZOstatnimSlowem(sylaby, slowoPrzed, ostatnieSlowo):
    return stworzLinie(sylaby, slowoPrzed, [ostatnieSlowo])


def stworzWerset(slowoPrzed, rymy, rymWzor, sylabWzor):
    linie = []

    for numerLini in range(0, len(rymWzor)):
        RymowyWzorSymbolu = rymWzor[numerLini]
        rymowaneSlowo = None
        for i in range(numerLini - 1, -1, -1):
            if rymWzor[i] == RymowyWzorSymbolu:
                rymowaneSlowo = linie[i][-1]
                break

        MozliweLinie = []
        if rymowaneSlowo:
            for ostatnieSlowo in rymy[rymowaneSlowo]:
                l = stworzLinieZOstatnimSlowem(sylabWzor[numerLini], slowoPrzed, ostatnieSlowo)
                if l: MozliweLinie.append(l)
        else:
            for ostatnieSlowo in random.sample(list(rymy.keys()), 10):
                l = stworzLinieZOstatnimSlowem(sylabWzor[numerLini], slowoPrzed, ostatnieSlowo)
                if l: MozliweLinie.append(l)

        linia = None
        if MozliweLinie:
            linia = random.choice(MozliweLinie)
        else:
            return stworzWerset(slowoPrzed, rymy, rymWzor, sylabWzor)

        linie.append(linia)

    tekst = ''
    for linia in linie:
        tekst += ' '.join(linia)
        tekst += '\n'

    return tekst


def stworzWierszPoeto(liczbaWersow, rymWzor, sylabWzor):
    wersy = []
    for _ in range(liczbaWersow):
        wersy.append(stworzWerset(slowoPrzed, rymy, rymWzor, sylabWzor))
    poem = '\n'.join(wersy)
    slowa = poem.split()
    for slowo in slowa:
        if slowo.capitalize() in nazwyWlasne:
            wzor = re.compile('\\b' + slowo + '\\b', re.MULTILINE)
            poem = re.sub(wzor, slowo.capitalize(), poem)
    return poem


def zapiszRymy(rymy):
    if not os.path.exists('data'):
        os.mkdir('data')
    f = open(RYMY_PLIK, 'w')
    prostyRym = dict()
    for slowo in rymy.keys():
        prostyRym[slowo] = list(sorted(rymy[slowo]))
    json.dump(prostyRym, f, indent=10)
    f.close()


def zaladujRymy():
    f = open(RYMY_PLIK, 'r')
    prostyRym = json.load(f)
    rymy = defaultdict(set)
    for slowo in prostyRym.keys():
        rymy[slowo] = set(prostyRym[slowo])
    f.close()
    return rymy


def zapiszPoprzednieSlowo(slowoPrzed):
    if not os.path.exists('data'):
        os.mkdir('data')
    f = open(POPRZEDNIE_SLOWO_PLIK, 'w')
    prostePoprzednieSlowo = dict()
    for slowo in slowoPrzed.keys():
        prostePoprzednieSlowo[slowo] = list(sorted(slowoPrzed[slowo]))
    json.dump(prostePoprzednieSlowo, f, indent=10)
    f.close()


def zaladujPoprzednieSlowo():
    f = open(POPRZEDNIE_SLOWO_PLIK, 'r')
    prostePoprzednieSlowo = json.load(f)
    slowoPrzed = defaultdict(Counter)
    for slowo in prostePoprzednieSlowo.keys():
        slowoPrzed[slowo] = set(prostePoprzednieSlowo[slowo])
    f.close()
    return slowoPrzed


def zapiszNazwyWlasne(nazwyWlasne):
    if not os.path.exists('data'):
        os.mkdir('data')
    f = open(NAZWY_WLASNE_PLIK, 'w')
    prosteNazwyWlasne = list(sorted(nazwyWlasne))
    json.dump(prosteNazwyWlasne, f, indent=10)
    f.close()


def zaladujNazwyWlasne():
    f = open(NAZWY_WLASNE_PLIK, 'r')
    prosteNazwyWlasne = json.load(f)
    nazwyWlasne = set(prosteNazwyWlasne)
    f.close()
    return nazwyWlasne


def pobierzZasoby():
    rymy = defaultdict(set)
    slowoPrzed = defaultdict(Counter)
    nazwyWlasne = set()
    zwykleSlowa = set()

    plikRymowIstnieje = os.path.exists(RYMY_PLIK)
    plikPoprzednieSlowoIstnieje = os.path.exists(POPRZEDNIE_SLOWO_PLIK);
    plikNazwyWlasneIstnieje = os.path.exists(NAZWY_WLASNE_PLIK);

    if plikRymowIstnieje:
        rymy = zaladujRymy()
    if plikPoprzednieSlowoIstnieje:
        slowoPrzed = zaladujPoprzednieSlowo()
    if plikNazwyWlasneIstnieje:
        nazwyWlasne = zaladujNazwyWlasne()

    if not plikRymowIstnieje or not plikPoprzednieSlowoIstnieje or not nazwyWlasne:
        if not os.path.exists('txt-liryka'):
            print('"txt-liryka" folder nie znaleziono')
        else:
            for sciezkaKatalogu, _, nazwyPlikow in os.walk('txt-liryka'):
                for nazwaPliku in nazwyPlikow:
                    sciezkaPliku = os.path.join(sciezkaKatalogu, nazwaPliku)
                    tekst = getText(sciezkaPliku)
                    tekst = usunLinieZRzymskimiNumerami(tekst)
                    tekst = usunZnak(tekst, ZNAKI_DO_USUNIECIA)
                    if not plikPoprzednieSlowoIstnieje:
                        UaktualnijPrzedSlowami(slowoPrzed, tekst)
                    if not plikNazwyWlasneIstnieje:
                        ZnajdzOdpowiedniaNazwe(nazwyWlasne, zwykleSlowa, tekst)
                    if not plikRymowIstnieje:
                        tekst = usunZnak(tekst, SEPARATORY_SENTENCJI)
                        znajdzRymy(rymy, tekst)
            if (not plikRymowIstnieje or silowoZasoby) and zapiszZasoby:
                zapiszRymy(rymy)
            if (not plikPoprzednieSlowoIstnieje or silowoZasoby) and zapiszZasoby:
                zapiszPoprzednieSlowo(slowoPrzed)
            nazwyWlasne2 = set()
            for nazwaWlasna in nazwyWlasne:
                zwykleSlowo = nazwaWlasna.lower()
                if zwykleSlowo not in zwykleSlowa:
                    nazwyWlasne2.add(nazwaWlasna)
            nazwyWlasne = nazwyWlasne2
            if (not plikNazwyWlasneIstnieje or silowoZasoby) and zapiszZasoby:
                zapiszNazwyWlasne(nazwyWlasne)

    return (rymy, slowoPrzed, nazwyWlasne)


if __name__ == '__main__':
    parser = OptionParser(usage='usage: %prog [opcje]')
    parser.add_option('-v', '--wersy', dest='wersy', type='int', help='liczba wersow (domyslnie jest 3)')
    parser.add_option("-r", "--wzor_rymu", dest="rymWzor", type='string',
                      help="wzor rymu np. ABAB (domyslnie)")
    parser.add_option("-s", "--wzor_sylab", dest="sylabWzor", type='string',
                      help="liczba  sylab w kazdej lini np. 8,8,8,8")
    parser.add_option("-d", "--nie_zapisuj_danych", action="store_false", dest="zapiszZasoby", default=True,
                      help="nie tworz zadnych plikow z zasobami (np. rymy")
    parser.add_option("-f", "--wymuszaj_zapisanie_zasobow", action="store_true", dest="silowoZasoby", default=False,
                      help="Wymusza nadpisywanie plików zasobów")
    parser.add_option("-q", "--poCichu", action="store_true", dest="poCichu", default=False,
                      help="Nie wypisuj niczego - przygotuj pliki zasobów w razie potrzeby")
    (opcje, argumenty) = parser.parse_args()

    liczbaWersow = 4
    if opcje.wersy:
        if (opcje.wersy >= 1):
            liczbaWersow = opcje.wersy
        else:
            print('Nieprawidlowa liczba wersow.')
            sys.exit(1)

    rymWzor = 'ABAB'
    if opcje.rymWzor:
        rymWzor = opcje.rymWzor

    sylabWzory = ((2,2,2,2), (3,3,3,3), (4,4,4,4))
    sylabWzor = random.choice(sylabWzory)
    if opcje.sylabWzor:
        liczby = opcje.sylabWzor.split(',')
        try:
            sylabWzor = [int(n) for n in liczby]
        except:
            print('Nieprawidlowy wzor sylab.')
            sys.exit(1)

    poCichu = opcje.poCichu

    zapiszZasoby = opcje.zapiszZasoby

    silowoZasoby = opcje.silowoZasoby

    rymy, slowoPrzed, nazwyWlasne = pobierzZasoby()
    if rymy and slowoPrzed and not poCichu:
        print(stworzWierszPoeto(liczbaWersow, rymWzor, sylabWzor))
