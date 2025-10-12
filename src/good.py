from lxml import etree
from urllib.error import HTTPError
from aiogram.utils.formatting import Text, Bold, Url
import aiohttp


class Parser:
    "Yandex Market good page parser class."

    possible_price_paths = [
        '//*[@id="/content/page/fancyPage/defaultPage/mainDO/price/priceOffer"]/div/div[1]/div/div[1]/button/span/span[1]',
        '//*[@id="/content/page/fancyPage/defaultPage/mainDO/price/priceOffer"]/div/div[1]/div/div[1]/span/span[1]',
        '//*[@id="/content/page/fancyPage/defaultPage/mainDO/price/priceOffer"]/div/div[1]/div[1]/span/span[1]',
    ]

    def __init__(self, body: str) -> None:
        tree = etree.HTML(body)

        self.title = tree.xpath(
            '//*[@id="/content/page/fancyPage/defaultPage/productTitle"]/div/div/h1'
        )[0].text

        for path in self.possible_price_paths:
            try:
                price = (
                    tree.xpath(path)[0]
                    .text.encode("ascii", "ignore")
                    .decode("utf-8")
                )
                break
            except IndexError:
                price = None
                continue

        if price is None:
            raise IndexError
        self.price = int(price)

        try:
            self.description = tree.xpath(
                '//*[@id="product-description"]/div[1]/div[1]/div/div'
            )[0].text
        except IndexError:
            self.description = None


class Good:
    def __init__(self, part_number: int) -> None:
        if not isinstance(part_number, int):
            raise ValueError
        self.part_number = part_number
        self.url = f"https://market.yandex.ru/card/_/{self.part_number}"
        self.title: str
        self.price: int
        self.description: str | None

    async def __call__(self) -> None:
        """That should be called, if title, price and description
        attributes are not initialized. That means, there is no tuple
        corresponding to the url in a database."""

        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(7)
        ) as session:
            r = await session.get(self.url)
            if r.status != 200:
                raise HTTPError
            text = await r.text()
            parsed = Parser(text)
        self.title = parsed.title
        self.price = parsed.price
        self.description = parsed.description

    def to_message(self) -> Text:
        """This method is made to convert Good object into Text object that
        will be sent by the bot."""

        args = [
            Bold("Title: "),
            f"{self.title}\n",
            Bold("Part number: "),
            f"{self.part_number}\n",
            Bold("Price: "),
            f"{self.price}\n",
            Bold("URL: "),
            Url(self.url),
            "\n",
        ]
        if self.description is not None:
            args.extend([Bold("Description: "), f"{self.description}\n"])
        return Text(*args)

    def __iter__(self) -> tuple[str | int]:
        return iter(
            [
                self.part_number,
                self.title,
                self.price,
                self.description,
            ]
        )

    @staticmethod
    def from_tuple(
        part_number: int,
        title: str,
        price: int,
        description: str | None = None,
    ) -> str:
        """This method is made for restoring Good object from a
        database tuple."""

        good = Good(part_number)
        good.title = title
        good.price = price
        good.description = description
        return good
