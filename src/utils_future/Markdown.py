class Markdown:
    ALIGN_LEFT = ':---'
    ALIGN_RIGHT = '---:'
    # ALIGN_CENTER = ':---:'

    @staticmethod
    def italic(text):
        return f'*{text}*'

    @staticmethod
    def bold(text):
        return f'**{text}**'

    @staticmethod
    def link(text, url):
        return f'[{text}]({url})'

    @staticmethod
    def wiki_link(text, label=None):
        if 'others' in text.lower():
            return Markdown.italic(text)
        url = 'https://en.wikipedia.org/wiki/' + text.replace(' ', '_')
        return Markdown.link(label or Markdown.italic(text), url)

    @staticmethod
    def image(alt, url):
        url_unix = url.replace('\\', '/')
        return f'![{alt}]({url_unix})'

    @staticmethod
    def image_html(alt, url, width=None, height=None):
        all_style = ""
        if width:
            all_style += f' width="{width}"'
        if height:
            all_style += f' height="{height}"'
        return f'<img src="{url}" alt="{alt}" {all_style} />'

    @staticmethod
    def table_row(cells):
        inner = ' | '.join([str(cell) for cell in cells])
        return f'| {inner} |'

    @staticmethod
    def table(*cells_list):
        first_cells = cells_list[0]
        for cells in cells_list[1:]:
            if len(cells) != len(first_cells):
                raise ValueError(
                    'All rows must have the same number of cells'
                )

        return [Markdown.table_row(cells) for cells in cells_list]

    @staticmethod
    def ref(child):
        return f'[{child}]'
