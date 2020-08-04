from requests_html import HTMLSession
session = HTMLSession()

# TODO:
# - https://oddspedia.com/
# - https://www.oddsportal.com/

def oddschecker(url):

    # Example: https://www.oddschecker.com/football/english/championship/brentford-v-fulham/winner

    response = session.get(url)

    container = response.html.find("#oddsTableContainer", first=True)
    table = container.find("table", first=True)

    # Find Bookmakers
    table_header = table.find("thead", first=True)
    row = table_header.find("tr")[3]
    cells = row.find("td")[1:]

    bookmakers = []
    odds = []

    for cell in cells:
        link = cell.find("a", first=True)
        if link is None:
            continue
        bookmakers.append(link.attrs["title"])

    # Find odds
    table_body = table.find("tbody", first=True)
    rows = table_body.find("tr")
    options = []

    for row in rows:
        options.append(row.find("td")[1:])

    for i in range(len(options[0])):
        book = []

        for j in range(0, len(options)):
            book.append(options[j][i])
        # options[0][i], options[1][i], options[2][i]

        float_book = []

        for cell in book:
            if cell.text == "":
                continue
            print("Found Cell: "+cell.text)
            text = cell.text.split("/")
            try:
                if len(text) == 2:
                    float_book.append(round(int(text[0])/int(text[1])*100)/100)
                elif len(text) == 1:
                    float_book.append(int(text[0]))
                else:
                    print(text)
            except:
                print(text)

        if len(float_book) > 0:
            odds.append(float_book)



    return bookmakers, odds
