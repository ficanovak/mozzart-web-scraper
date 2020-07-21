import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
from pprint import pprint
import sqlalchemy as sa
from datetime import datetime

engine = sa.create_engine('mssql+pyodbc://sa:INSERT USERNAME@INSERT SERVER ADDRESS?DRIVER={ODBC Driver 13 for SQL Server}',fast_executemany=True)


driver = webdriver.Chrome()
driver.get('https://www.mozzartbet.com/sr#/betting/?cid=11940&s=2')

# bypass cookiewall
elements = driver.find_element_by_class_name('accept-button')
elements.click()

# parse stranice
html = driver.page_source
soup = BeautifulSoup(html)

items = soup.select('article')

# iteracija kroz imena igraca
junk_player_data = []
for item in soup.find_all('a',{'class':'pairs'}):
    for igrac in item.find_all('span'):
        pdata = igrac.next
        junk_player_data.append(pdata)      
igraci = [item for item in junk_player_data[1::2]]

# iteracija kroz kvote
junk_limits_data = []
for item in soup.find_all('div',{'class':'partvar'}):
    ldata = item.next
    junk_limits_data.append(ldata)
kvote = [kvota for kvota in junk_limits_data[::6]]

ct = datetime.today()

# output tabele
players_stuff = pd.DataFrame(
    {
        'player': igraci,
        'points': kvote,
        'datetime' : ct,
    })

driver.quit()

c = engine.connect()
# brisanje stare tabele sa servera
sql_delete = (f"DELETE FROM nba.dbo.mozzart") 
deletion = c.execute(sql_delete)

# output kao tabela na serveru
players_stuff.to_sql('mozzart',con=engine)

# output kao csv fajl
# players_stuff.to_csv(r'mozzart.csv')
