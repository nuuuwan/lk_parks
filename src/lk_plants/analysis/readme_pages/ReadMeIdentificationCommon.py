import os

from utils import Log

from lk_plants.core.plant_net.PlantNetResult import PlantNetResult
from lk_plants.core.plant_photo.PlantPhoto import PlantPhoto
from utils_future import Markdown, Plot

log = Log('ReadMeIdentification')


class ReadMeIdentificationCommon:
    COLORS_LIST = ['brown', 'red', 'orange', 'green']
    MIN_N = 15

    @staticmethod
    def get_analysis_by_key(get_key):
        plant_photo_list = PlantPhoto.list_all()
        idx = {}
        for plant_photo in plant_photo_list:
            key = str(get_key(plant_photo))
            plant_net_result = PlantNetResult.from_plant_photo(plant_photo)
            confidence = plant_net_result.top_confidence
            if not confidence:
                continue
            if key not in idx:
                idx[key] = []
            idx[key].append(confidence)
        return idx

    @staticmethod
    def get_func_key(label):
        if label in ['species', 'family']:

            def func_key(x):
                return sum(x[1]) / len(x[1])

            return func_key

        def func_key(x):
            return x[0]

        return func_key

    @staticmethod
    def get_data_for_key(label, get_key):
        idx = ReadMeIdentificationCommon.get_analysis_by_key(get_key)
        func_key = ReadMeIdentificationCommon.get_func_key(label)
        sorted_idx_items = sorted(idx.items(), key=func_key)

        x, y, x_mean, y_mean, y_mean_q1, y_mean_q3, color = [
            [] for _ in range(7)
        ]

        for key, conf_list in sorted_idx_items:
            sorted_conf_list = sorted(conf_list)
            n = len(sorted_conf_list)
            if n < ReadMeIdentificationCommon.MIN_N:
                continue

            x_mean.append(key)
            mean = sum(sorted_conf_list) / n
            y_mean.append(mean)
            y_mean_q1.append(sorted_conf_list[n // 4])
            y_mean_q3.append(sorted_conf_list[3 * n // 4])

            for i, conf in enumerate(sorted_conf_list):
                x.append(key)
                y.append(conf)
                color.append(
                    ReadMeIdentificationCommon.COLORS_LIST[
                        int(
                            len(ReadMeIdentificationCommon.COLORS_LIST)
                            * i
                            / n
                        )
                    ]
                )
        return x, y, x_mean, y_mean, y_mean_q1, y_mean_q3, color

    @staticmethod
    def get_lines_for_key(label, get_key):
        (
            x,
            y,
            x_mean,
            y_mean,
            y_mean_q1,
            y_mean_q3,
            color,
        ) = ReadMeIdentificationCommon.get_data_for_key(label, get_key)

        Plot.before()
        Plot.scatter_with_fill(
            x,
            y,
            x_mean,
            y_mean,
            y_mean_q1,
            y_mean_q3,
            color,
        )

        Plot.set_text(
            f'Plant Identification Confidence by {label.title()}',
            label.title(),
            'Confidence',
        )

        id = label.replace(' ', '-')
        chart_path = os.path.join('images', f'identification.{id}.png')
        Plot.write(chart_path)
        lines = [
            '### ' + label.title(),
            '',
            Markdown.image(chart_path, chart_path),
            '',
        ]
        return lines
