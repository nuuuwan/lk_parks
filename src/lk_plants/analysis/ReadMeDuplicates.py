import os
from datetime import datetime
from functools import cached_property

import matplotlib.pyplot as plt
from utils import Log

from lk_plants.analysis.InfoReadMe import InfoReadMe
from lk_plants.core.plant_photo.PlantPhoto import PlantPhoto
from utils_future import Markdown, MarkdownPage

log = Log('ReadMeDuplicates')


class ReadMeDuplicates(MarkdownPage, InfoReadMe):
    @cached_property
    def file_path(self):
        return 'README.duplicates.md'

    @cached_property
    def duplicates_by_date_stats(self) -> list[str]:
        plant_photo_list = PlantPhoto.list_all()
        idx = {}
        for plant_photo in plant_photo_list:
            date_str = plant_photo.date_str
            if date_str not in idx:
                idx[date_str] = []
            idx[date_str].append(plant_photo)

        latlng_str_set = set()
        stats = {}
        for date_str, plant_photo_list_for_date in sorted(
            idx.items(),
            key=lambda x: x[0],
        ):
            n_total = len(plant_photo_list_for_date)
            n_new = 0
            for plant_photo in plant_photo_list_for_date:
                latlng_str = str(plant_photo.latlng)
                if latlng_str not in latlng_str_set:
                    n_new += 1
                    latlng_str_set.add(latlng_str)
            stats[date_str] = dict(
                date_str=date_str,
                n_total=n_total,
                n_new=n_new,
            )

        return list(stats.values())

    @cached_property
    def lines_duplicates_by_date(self) -> list[str]:
        plt.close()
        stats = self.duplicates_by_date_stats
        MIN_DAYS_DISPLAY = 14
        if len(stats) > MIN_DAYS_DISPLAY:
            stats = stats[-MIN_DAYS_DISPLAY:]

        x = [datetime.strptime(s['date_str'], '%Y-%m-%d') for s in stats]
        y_duplicates = [s['n_total'] for s in stats]
        y_new = [s['n_new'] for s in stats]

        plt.figure(figsize=(16, 9))
        plt.tight_layout(pad=2.0)

        plt.xticks(rotation='vertical')
        plt.bar(x, y_duplicates, label='Duplicates', color="red")
        plt.bar(x, y_new, label='New', color="green")
        plt.legend()
        plt.title('Duplicates by Date ' + f'(Last {MIN_DAYS_DISPLAY})')

        chart_path = os.path.join('images', 'duplicates_by_date.png')
        plt.savefig(chart_path)
        plt.close()

        log.info(f'Wrote {chart_path}')
        os.startfile(chart_path)

        chart_path_unix = chart_path.replace('\\', '/')
        return Markdown.image('Duplicates by Date', chart_path_unix)

    @cached_property
    def lines(self) -> list[str]:
        return [
            '## Duplicates',
            '',
            'If the location of two plant photos is very close to each other, '
            'we tag these as *duplicates* and exclude them from our analysis.',
            '',
            self.lines_duplicates_by_date,
            '',
        ]
