"# Poezja" 
Program do generowania poezji, generowanych za pomocą Łańcuchów Markowa drugiego stopnia.
	Używa informacji, jakie słowa występują bezpośrednio obok siebie. Próbuje przy tym odkryć rymujące się wyrazy, badając końcówki wersów. Zapamiętuje także nazwy własne, aby były one pisane wielką literą w wynikowym tekście.
Z tak przygotowanych danych wybierane są najpierw rymujące się wyrazy, które będę kończyć linie w zwrotce, a następnie uzupełniana jest cała reszta tekstu na podstawie słownika wyrazów poprzedzających. Oczywiście zachowywana jest pewna, określona wcześniej, metryka sylab.
Dzięki zastosowanym mechanizmom, program potrafi generować wiersze o dowolnych parametrach podanych przez użytkownika, takich jak: liczba zwrotek, układ rymów oraz metryka sylab w zwrotce. Możliwe jest więc produkowanie na masową skalę zarówno ogromnych poematów pisanych szesnastozgłoskowcem, jak i krótkich, zabawnych wierszyków.

Zmiana parametrów następuję poprzez zmianę zmiennych:
*liczbaWersow- liczba wersow (domyslnie jest 4)  
*rymWzor -  wzor rymu np. ABAB (domyslnie) 
*sylabWzor - liczba  sylab w kazdej lini np. 8,8,8,8 
*zapiszZasoby - nie tworz zadnych plikow z zasobami (np.plik rymy)
*silowoZasoby - Wymusza nadpisywanie plików zasobów 
*poCichu - Nie wypisuj niczego - przygotuj pliki zasobów w razie potrzeby