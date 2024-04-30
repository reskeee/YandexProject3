import requests
from bs4 import BeautifulSoup
from colorama import Back

URL = "https://rus.hitmotop.com/search"
tracks_amount = 5


async def find_track(track_name: str):
    response = requests.get(f"{URL}?q={track_name}")
    # print(response.url)
    soup = BeautifulSoup(response.content, features="html.parser")
    # print(soup, type(soup))

    html = open("index.html", "wb")
    html.write(response.content)

    track_list = soup.findAll("div", "track__info")[0:tracks_amount:]
    # print(track_list)
    track_dict = {}

    for track in track_list:
        name = track.findAll("div", "track__title")[
            0].string.replace("\n", '').replace(' ', '')
        artist = track.find("div", "track__desc").string
        time = track.find("div", "track__fulltime").string
        href = track.findAll("a")[1].get("href")

        # print(name, artist, time, href)
        track_dict[f'{artist} - {name}'] = (href, time)

    return track_dict


async def dowloand_track(href, name):
    req = requests.get(href, stream=True)
    with open(f"music/{name}.mp3", "wb") as file:
        file.write(req.content)

    print(Back.GREEN + "Успешно установлено")
    print(Back.BLACK)


if __name__ == "__main__":
    print(find_track("metallica"))
