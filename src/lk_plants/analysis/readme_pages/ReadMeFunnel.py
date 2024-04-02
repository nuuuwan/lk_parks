import os
from functools import cached_property

import matplotlib.pyplot as plt
from utils import Log

from lk_plants.analysis.InfoReadMe import InfoReadMe
from utils_future import Markdown, MarkdownPage

log = Log('ReadMeFunnel')


class ReadMeFunnel(MarkdownPage, InfoReadMe):
    FUNNEL_COLORS = ['#ccc', '#888', '#c00', '#f80', '#0808', '#080']
    @cached_property
    def file_path(self):
        return 'README.funnel.md'

    def build_chart(self):
        plt.close()
        funnel = self.get_funnel()['all']
        x = list(funnel.keys())[::-1]
        y = list(funnel.values())[::-1]
        color =ReadMeFunnel.FUNNEL_COLORS[::-1]
        bars = plt.barh(x, y, color=color)

        plt.grid(False)
        for spine in plt.gca().spines.values():
            spine.set_visible(False)

        plt.title('Plant Photo Funnel')
        prev_value = None
        for bar, value in zip(bars, y):
            text = f'{value:,}'
            if prev_value is not None:
                d_value = value - prev_value
                text += f' (+{d_value:,})'
            plt.text(bar.get_width() + 10, bar.get_y() + 0.3, text)
            prev_value = value
        chart_path = os.path.join('images', 'funnel.png')
        plt.savefig(chart_path)
        plt.close()
        chart_path_unix = chart_path.replace('\\', '/')
        os.startfile(chart_path)
        log.info(f'Wrote {chart_path_unix}')

        return Markdown.image('funnel', chart_path_unix)

    @cached_property
    def lines(self) -> list[str]:
        return [
            '## Plant Photo Funnel',
            '',
            'Of all the photos taken (**All**),',
            ' we filter photos that are',
            ' within the desired geographical area (**In Geo**)',
            '',
            'Next, we filter photos that are likely not ',
            'duplicates (**Deduped**).',
            '',
            'Finally, we only consider identifications',
            ' where the model confidence is at least ',
            '20% (**≥ 20%**). ',
            'We list statistics for 5% and 10% as well.',
            '',
            self.build_chart(),
            '',
        ]
