from ebooklib import epub
from ebooklib.epub import EpubBook
from bs4 import BeautifulSoup


class BookParser:
    """
    Base class of BookParser
    """

    author = ''
    title = ''
    _AVERAGE_WORD_LENGTH = 5

    def __init__(self, parse_text=True, words_per_page: int = 1024):
        self._pages = []
        self._words_per_page = words_per_page
        self._chars_per_page = self._words_per_page * self._AVERAGE_WORD_LENGTH

        self._parse_meta()

        if parse_text:
            self._parse_text()

    def get_page(self, page: int = 1) -> str:
        """
        Get text by page.
        Return an empty string if page doesn't exist.
        """

        # Make it list-friendly
        page = page - 1

        if page not in range(0, len(self._pages)):
            return ''

        return self._pages[page]

    def is_empty(self) -> bool:
        """Check if book is empty"""
        return not bool(self._pages)

    def _parse_meta(self):
        """Parse META data"""
        pass

    def _parse_text(self):
        """Parse and paginate text from ebook file"""
        pass

    def _splitter(self, text_buffer: str) -> (int, str):
        """
        Paginator, recursively splits big text to chunk
        Returns last page and unused text.
        """

        if len(text_buffer) > self._chars_per_page:
            # Index of the space after the max words
            index = self._find_page_end(text_buffer)
            # Put this text until the index in the paginator
            self._pages.append(text_buffer[:index])

            # Check the rest
            return self._splitter(text_buffer[index+1:])

        return len(self._pages), text_buffer

    def _find_page_end(self, text: str) -> int:
        """
        Finds where the chunk of text ends with a space
        to make a correct split without chopping out some words.
        """

        for i, v in enumerate(text[self._chars_per_page:]):
            if v == ' ':
                return self._chars_per_page + i

        return len(text)

    def __str__(self):
        """Returns author and title of the book"""
        return f'{self.author} - {self.title}'

    def __len__(self):
        """Returns amount of the pages starting from 1"""
        return len(self._pages)


class EpubParser(BookParser):
    book = EpubBook

    def __init__(self, path: str, parse_text=True):
        self.book = epub.read_epub(path)
        super().__init__(parse_text)

    def _parse_meta(self):
        self.title = self.book.title
        author_meta = self.book.get_metadata('DC', 'creator')
        self.author = ', '.join(i[0] for i in author_meta)

    def _parse_text(self):
        text_buffer = ''

        for item in self.book.get_items():
            # I didn't find any other way to check item for the chapter
            if hasattr(item, '_template_name') and item._template_name == 'chapter':
                soup = BeautifulSoup(item.get_body_content(), 'html.parser')
                text = soup.get_text()
                text_buffer += f'{text}'.rstrip()
                page, text_buffer = self._splitter(text_buffer)

        # Write remains and clear the buffer
        self._pages.append(text_buffer)
        del text_buffer
