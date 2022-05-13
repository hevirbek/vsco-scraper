# Gerekli kütüphaneler
import pyppeteer
import asyncio
import wget
import os

# URL hazırlama kısmı
username = "evirbek"
url = f"https://vsco.co/{username}/gallery"

# kullanılacak listeler
hrefs, srcs = list(), list()


async def main():
    # tarayıcı başlatma ve yeni bir sayfa açma
    browser = await pyppeteer.launch()
    page = await browser.newPage()

    # vsco.co profil sayfasını açma
    await page.goto(url)

    # load more butonu varsa, tıklama
    button = await page.xpath('//*[@id="root"]/div/main/div/div[3]/section/div[2]/button')
    if button:
        await button[0].click()

    # figure elementlerini bulma
    figures = await page.xpath('//figure')

    # en aşağıya kadar kaydırma
    length = len(figures)
    while True:
        await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        await asyncio.sleep(1)
        figures = await page.xpath('//figure')
        if len(figures) == length:
            break
        length = len(figures)

    # figure elementlerinde hrefleri bulme
    for i, figure in enumerate(figures):
        # a tagını bul
        a = await figure.xpath('.//a')

        # hrefi bulma
        href = await a[0].getProperty('href')
        href = await href.jsonValue()

        # hrefi listeye ekleme
        hrefs.append(href)

    # hreflere gidip fotoğrafların src'lerini bulma
    for href in hrefs:
        # hrefe gitme
        await page.goto(href)

        # fotoğrafı bulma
        image = await page.xpath('//img')

        # src'i bulma
        src = await image[0].getProperty('src')
        src = await src.jsonValue()

        # src'i hazırlama
        start = "https://image-"
        src = src[2:src.find('?')]
        splitted = src.split('/')
        src = start + splitted[1] + '.vsco.co/' + "/".join(splitted[2:])

        # src'i listeye ekleme
        srcs.append(src)

    # kullanıcı adıyla sıfırdan klasör açma
    if not os.path.exists(username):
        os.mkdir(username)
    else:
        for file in os.listdir(username):
            os.remove(os.path.join(username, file))
        os.rmdir(username)
        os.mkdir(username)

    # fotoğrafları indirme
    for i, src in enumerate(srcs, 1):
        wget.download(src, username + os.sep + str(i) + ".jpg")

    # tarayıcıyı kapatma
    await browser.close()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
