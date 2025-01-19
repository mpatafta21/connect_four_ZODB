# Connect Four Game

## Opis projekta
Connect Four je interaktivna igra razvijena u sklopu kolegija **Teorije baza podataka**. Cilj projekta bio je implementirati igru koristeći **ZODB** kao trajnu bazu podataka i **PyGame** za grafičko sučelje. Projekt je izrađen u **Pythonu** unutar razvojnog okruženja **Visual Studio Code** na Windows operativnom sustavu.


## Zahtjevi
Prije pokretanja projekta, potrebno je imati:
- **Python 3.8+**

Također je moguće da ćete morati instalirati sljedeće biblioteke:
- **PyGame**: Instalacija naredbom `pip install pygame`
- **ZODB**: Instalacija naredbom `pip install ZODB`

Ako se tijekom pokretanja aplikacije pojave greške vezane uz nedostatak ovih biblioteka, obavezno ih instalirajte koristeći navedene naredbe.

## Pokretanje projekta
1. **Navigiranje do direktorija projekta unutar terminala i pokrenite projekt sljedećom naredbom**
```bash
python game_ui.py
```
Zatim bi se trebala otvoriti aplikacija u novom PyGame prozoru

## Kako koristiti aplikaciju
1. Nakon pokretanja aplikacije, prikazuje se početna scena s tekstualnim poljima za unos korisničkih imena.
   
2. Igrači unose svoja imena i pritiskom na Enter započinje igra.
   
3. Igrač na svojem potezu odabire stupac i stavlja žeton
   
4. Po završetku igre, igrači mogu pregledavati statistike, povijest igara, rang listu, te brisati korisnike iz baze ili ponoviti igru.

## Struktura projekta
database.py: Implementacija ZODB baze podataka, upravljanje korisnicima i igrama.

game_ui.py: Glavna datoteka s implementacijom korisničkog sučelja.

test_database.py: Alat za testiranje funkcionalnosti baze podataka.

date.py: Modul za obradu datuma i vremena igara.

 
