from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import unquote
import math_engine as en
import webscraper as ws
import webbrowser

def main():
    global odds, websites

    odds = []
    websites = []

    hostName = "localhost"
    serverPort = 8080

    print("Starting")
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started")

    webbrowser.open("http://127.0.0.1:8080")

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    print("Stopping Server")
    webServer.server_close()
    print("Server stopped")

def find_bets(budget):
    best, ids = en.find_best_odds(odds)
    arbitrage = en.get_arbitrage(best)
    bets = en.calculate_bets(budget, best, arbitrage)

    website_list = []

    for id in ids:
        website_list.append(websites[id])

    return website_list, bets, best, arbitrage

def find_bets_direct(budget, odds):
    arbitrage = en.get_arbitrage(odds)
    bets = en.calculate_bets(budget, odds, arbitrage)

    return bets, arbitrage

def autofind(type:str, url:str):
    global websites, odds
    if type == "oddschecker":
        websites, odds = ws.oddschecker(url)


class MyServer(BaseHTTPRequestHandler):

    def _format_index(self):

        with open("html/interface.html") as file:
            interface_html = file.read()

        list_html = ""

        for i in range(len(odds)):
            row = odds[i]
            website = websites[i]

            list_html += "<tr>"
            list_html += "<td>"+website+"</td>"

            for cell in row:
                list_html += "<td>"+str(cell)+"</td>"

        return interface_html.replace("[TABLE_ROWS]", list_html)


    def _format_find(self, budget):
        with open("html/find.html") as file:
            interface_html = file.read()

        list_html = ""

        website_list, bets, odds, arbitrage = find_bets(budget)

        for i in range(len(bets)):
            bet = round(bets[i]*100)/100
            win_ret = round(bet*odds[i]*100)/100
            row = "<tr>"

            row += "<td>"+str(i)+"</td>"
            row += "<td>"+website_list[i]+"</td>"
            row += "<td>"+str(odds[i])+"</td>"
            row += "<td>"+str(bet)+"</td>"
            row += "<td>"+str(win_ret)+"</td>"

            row += "</tr>"

            list_html += row

        ret_html = interface_html.replace("[TABLE_ROWS]", list_html)
        ret_html = ret_html.replace("[ARBITRAGE]", str(round(arbitrage*100)/100))

        return ret_html

    def _format_find_direct(self, bookmakers, budget, odds):
        with open("html/find_direct.html") as file:
            interface_html = file.read()

        bets, arbitrage = find_bets_direct(budget, odds)
        list_html = ""

        for i in range(len(bets)):
            bet = round(bets[i]*100)/100
            win_ret = round(bet*odds[i]*100)/100

            row = "<tr>"

            row += "<td>"+str(i)+"</td>"
            row += "<td>"+bookmakers[i].replace("+", " ")+"</td>"
            row += "<td>"+str(odds[i])+"</td>"
            row += "<td>"+str(bet)+"</td>"
            row += "<td>"+str(win_ret)+"</td>"

            row += "</tr>"

            list_html += row

        ret_html = interface_html.replace("[TABLE_ROWS]", list_html)
        ret_html = ret_html.replace("[ARBITRAGE]", str(round(arbitrage*100)/100))

        return ret_html

    def _format_find_direct_empty(self):

        with open("html/find_direct.html") as file:
            interface_html = file.read()

        ret_html = interface_html.replace("[TABLE_ROWS]", "")
        ret_html = ret_html.replace("[ARBITRAGE]", "0")

        return ret_html

    def _send_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        global odds, websites
        self._send_headers()

        if self.path == "/reset":
            odds = []
            websites = []

        if self.path == "/find_direct":
            self.wfile.write(bytes(self._format_find_direct_empty(), "utf-8"))
        elif self.path == "/favicon.ico":
            pass
        elif self.path == "/shutdown":
            self.wfile.write(bytes("Shutting Down", "utf-8"))
            exit()
        else:
            self.wfile.write(bytes(self._format_index(), "utf-8"))

    def do_POST(self):
        global odds, websites
        self._send_headers()

        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length).decode("utf8")


        if self.path == "/submit":

            data = body.split("&")
            website = data.pop(0)
            website = website[website.find("=")+1:]
            website = website.replace("+", " ")
            websites.append(website)

            for i in range(len(data)):
                data[i] = data[i].replace("%2C", ".")
                cut_pos = data[i].find("=")
                data[i] = data[i][cut_pos+1:]
                if data[i] != "":
                    data[i] = float(data[i])
                else:
                    del data[i]

            odds.append(data)


            self.wfile.write(bytes(self._format_index(), "utf-8"))

            #response = BytesIO()
            #response.write(b'This is POST request. ')
            #response.wite(body)

        elif self.path == "/find":

            data = body.split("&")
            index = data[0].find("=")+1
            budget = int(data[0][index:])
            self.wfile.write(bytes(self._format_find(budget), "utf-8"))

        elif self.path == "/autofill":

            data = body.split("&")
            index = data[0].find("=")+1
            type = data[0][index:]

            index = data[1].find("=")+1
            url = unquote(data[1][index:])

            autofind(type, url)

            self.wfile.write(bytes(self._format_index(), "utf-8"))

        elif self.path == "/find_direct":
            print("Find Firect")
            data = body.split("&")
            raw_data = []

            for point in data:
                index = point.find("=")+1
                raw_data.append(unquote(point[index:]))

            bookies = raw_data[0:3]
            best_odds = raw_data[3:6]
            budget = int(raw_data[6])

            for i in range(len(best_odds)):
                if best_odds[i] == "":
                    del best_odds[i]
                    continue

                best_odds[i] = float(best_odds[i].replace(",", "."))

            self.wfile.write(bytes(self._format_find_direct(bookies, budget, best_odds), "utf-8"))


if __name__ == '__main__':
    main()
