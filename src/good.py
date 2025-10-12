from lxml import etree
import aiohttp


class Parser:
    "Yandex Market good page parser class."

    possible_price_paths = [
        "/html/body/div[2]/div/div[2]/div/div/div/div[1]/div\
        /div[1]/div[3]/div[4]/section[1]/div[2]/div/div/div/div\
        /div/div[2]/div[1]/div/div/div[1]/div/div[2]/div[2]\
        /div[1]/div/div/span[1]/span[1]",
        "/html/body/div[2]/div/div[2]/div/div/div/div[1]/div\
        /div[1]/div[3]/div[4]/section[1]/div[2]/div/div/div\
        /div/div/div[2]/div[1]/div/div/div[1]/div/div[2]/div[2]\
        /div[1]/div/div/div[2]/div[1]/div/div[1]/span[2]/span[1]",
    ]

    def __init__(self, body: str) -> None:
        tree = etree.HTML(body)

        self.title = tree.xpath(
            "/html/body/div[2]/div/div[2]/div/div/div/div[1]\
            /div/div[1]/div[3]/div[3]/div/div[2]/div/div/h1"
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
                "/html/body/div[2]/div/div[2]/div/div/div/div[1]/div/div[1]\
                /div[3]/div[5]/div[3]/div[1]/div/div/div/div/div[2]\
                /div/div[1]/div[1]/div/div"
            )[0].text
        except IndexError:
            self.description = None


class Good:
    MESSAGE_TEMPLATE = "Part number: {part_number}\nURL: [link]({url})\n\
Title: {title}\nPrice: {price} RUB"

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
            try:
                r = await session.get(self.url)
            except TimeoutError:
                return None

            if r.status != 200:
                return None

            try:
                text = await r.text()
                parsed = Parser(text)
            except IndexError:
                return None

            self.title = parsed.title
            self.price = parsed.price
            self.description = parsed.description

    def __str__(self) -> str:
        """This method is made to convert Good object into string that
        will be sent by the bot."""

        message = self.MESSAGE_TEMPLATE.format(
            part_number=self.part_number,
            url=self.url,
            title=self.title,
            price=self.price,
        )
        if self.description is not None:
            return f"{message}\nDescription: {self.description}"
        return message

    def __iter__(self) -> tuple[str | int]:
        return iter(
            [
                self.part_number,
                self.url,
                self.title,
                self.price,
                self.description,
            ]
        )

    @staticmethod
    def from_fields(
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
