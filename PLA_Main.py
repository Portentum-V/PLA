import csv # Handling a tab seperated file to start
import requests # For scraping Serebii
from bs4 import BeautifulSoup # Parsing Pages


def parse_csv_mons( filename: str, delimiter: str ='\t'):
    mon_list = []
    with open(filename) as f:
        reader = csv.reader(f, delimiter='\t')
        for i in reader:
            mon_list.append(i)
    return mon_list


def get_serebii_dex(url: str = "https://www.serebii.net/legendsarceus/hisuipokedex.shtml"):
    page = requests.get(url)
    return page


def parse_serebii_dex(soup):
    result = soup.findAll('table')[1]
    mon_list = []
    for i in result.findAll('a', href=True):
        if ".shtml" not in i['href']:
            mon_list.append(i['href'].split('/')[2])
    return list(set(mon_list))


def build_mon_list():
    page = get_serebii_dex()
    soup = BeautifulSoup(page.content, "html.parser")
    return parse_serebii_dex(soup)


def get_serebii_mon(mon:str):
    mon_url = f'https://www.serebii.net/pokedex-swsh/{mon.lower()}/'
    page = requests.get(mon_url)
    return page


def parse_serebii_name(soup):
    result = soup.find('h1')
    return result.text.split()[1]


def parse_serebii_num(soup):
    result = soup.find(text='Hisui')
    raw_numbers = result.findParent('table').text
    split_numbers = raw_numbers.strip().split("\n")
    region = ["National", "Hisui"]
    number_list = []
    for i in split_numbers:
        if any(x in i for x in region):
            name, num_str = i.split(":")
            num = "".join(filter(str.isdigit, num_str))
            number_list.append([name, num])
    return number_list
            

def parse_serebii_gender(soup):
    # raw_gender = soup.findAll('td',{"class":"fooinfo"})[4].text
    # I don't like doing this by index but it works
    male = "0%"
    female = "0%"
    try:
        result = soup.find(text='♂')
        raw_gender = result.findParent('table').text
        # Example: ' Male ♂:88.14%Female ♀:11.86%'
        male, female = raw_gender.split('Female')
        male = male.split(":")[1]
        female = female.split(":")[1]
    except AttributeError:
        pass
    return male, female


def parse_type_href(bs_href:str):
    tmp_type = []
    for i in bs_href.findAll('a', href=True):
        tmp_type.append(i['href'].split("/")[2].split(".shtml")[0])
    return "/".join(tmp_type)


def parse_serebii_type(soup):
    result = soup.findAll('img',{"class":"typeimg"})
    mon_types = []
    try:
        result_table = result[0].findParent('table')
        rows = result_table.findAll('tr')
        if rows:
            for row in rows:
                mon_types.append(parse_type_href(row))
        else:
            mon_types.append(parse_type_href(result_table))
    except IndexError:
        pass
    mon_types = [i for i in mon_types if i]
    return mon_types


def parse_serebii_location(soup):
    raw_location = soup.find('td', text='Legends: Arceus').find_next_sibling("td")
    for br in raw_location.findAll("br"):
        br.replace_with("\n")
    locations_split = raw_location.text.split("\n")
    locations = []
    for location in locations_split:
        locations.append([e.strip() for e in location.split(":")])
    return locations


def parse_serebii_research(soup):
    result = soup.find('a',{"name":"research"})
    research_table = result.findParent('table')
    research_list = []
    rows = research_table.find_all('tr')
    for row in rows:
        columns = row.find_all('td')
        columns = [element.text.strip() for element in columns]
        research_list.append([element for element in columns if element])

    for i in research_list:
        if len(i) <= 1:
            research_list.remove(i)

    rl = []
    for i in research_list:
        name = i.pop(0)
        rl.append([name, i])

    return rl


def parse_serebii_mon(page):
    soup = BeautifulSoup(page.content, "html.parser")
    name = parse_serebii_name(soup)
    numbers = parse_serebii_num(soup)
    male, female = parse_serebii_gender(soup)
    mon_type = parse_serebii_type(soup)
    location = parse_serebii_location(soup)
    research = parse_serebii_research(soup)
    mon_dict = {
        "name":name,
        "numbers":numbers,
        "gender":[("male", male),("female", female)],
        "type":mon_type,
        "location":location,
        "research":research        
        }
    return mon_dict


def build_mon_entry(mon):
    page = get_serebii_mon(mon)
    entry = parse_serebii_mon(page)
    return {mon:entry}

def print_mon_entry(entry):
    name = entry['name']
    hisui_num = entry['numbers'][1][1]
    male = entry['gender'][0][1]
    female = entry['gender'][1][1]
    mon_type = " | ".join(entry['type'])
    print(f"#{hisui_num}: {name}; {mon_type}")
    print(f"Male {male}; Female {female}")
    print(f"Location(s)")
    for location in entry['location']:
        print(f"\t{location[0]}: {location[1]}")
    print(f"Research Tasks")
    for research in entry['research']:
        print(f"\t{research[0]}: {research[1]}")


def main():
    mons = build_mon_list()
    full_dex = {}
    for c, mon in enumerate(mons):
        print(f"{c+1}: {mon}")
        full_dex = full_dex | build_mon_entry(mon)
    return full_dex