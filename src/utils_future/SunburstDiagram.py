import colorsys
import math
import os
from functools import cached_property

from PIL import Image, ImageDraw, ImageFont
from utils import Log

log = Log('SunburstDiagram')


class SunburstDiagram:
    DEFAULT_OPTIONS = dict(
        width=2000,
        height=2000,
        font_path=os.path.join('src', 'utils_future', 'p22.ttf'),
    )

    @staticmethod
    def get_color(p_mid):
        h, s, l = 180 * p_mid, 100, 33
        r, g, b = colorsys.hls_to_rgb(h / 360, l / 100, s / 100)
        fill = '#%02x%02x%02x' % (int(r * 255), int(g * 255), int(b * 255))
        return fill

    def __init__(self, d_list, level_keys, value_key, options=None):
        self.d_list = d_list
        self.level_keys = level_keys
        self.value_key = value_key
        self.options = options

    @property
    def sorted_d_list(self):
        def key(d):
            return '-'.join([d[k] for k in self.level_keys])

        return sorted(self.d_list, key=key)

    def get_option(self, key):
        if self.options and key in self.options:
            return self.options[key]
        return SunburstDiagram.DEFAULT_OPTIONS[key]

    def draw_arcs(self, im, n_levels, i_level, label_to_n):
        draw = ImageDraw.Draw(im)

        total_n = sum(label_to_n.values())
        width = self.get_option('width')
        height = self.get_option('height')
        cx = width / 2
        cy = height / 2
        r_all = min(width, height) / 2
        r_unit = r_all / (n_levels - 0.5)
        if i_level == n_levels - 1:
            r = 0.5 * r_unit
        else:
            r = r_unit * (n_levels - i_level - 0.5)

        bbox = [cx - r, cy - r, cx + r, cy + r]
        BASE_FONT_SIZE = 200
        base_font = ImageFont.truetype(
            self.get_option('font_path'), BASE_FONT_SIZE
        )

        p_start = 0
        angle_offset = 0
        for label, n in label_to_n.items():
            p_label = n / total_n
            p_end = p_start + p_label
            p_mid = p_start + p_label / 2

            fill = SunburstDiagram.get_color(p_mid)

            angle_start = 360 * p_start + angle_offset
            angle_end = 360 * p_end + angle_offset
            angle_mid = 360 * p_mid + angle_offset
            draw.pieslice(bbox, start=angle_start, end=angle_end, fill=fill)
            draw.arc(
                bbox, start=angle_start, end=angle_end, fill='white', width=1
            )

            base_text_bbox = draw.textbbox((0, 0), label, base_font)
            base_text_width, base_text_height = (
                base_text_bbox[2] - base_text_bbox[0],
                base_text_bbox[3] - base_text_bbox[1],
            )
            font_color = "white"

            real_text_height = r_unit
            real_text_width = 2 * math.pi * (r - r_unit) * min(0.25, p_label)

            if real_text_width < real_text_height:
                real_text_width, real_text_height =  real_text_height, real_text_width
                direction = False
            else:
                direction = True

            scale_factor = min(real_text_width / base_text_width, real_text_height / base_text_height)
            font_size = int(BASE_FONT_SIZE * scale_factor)
            if font_size > BASE_FONT_SIZE:
                font_size = BASE_FONT_SIZE
            if font_size < 1:
                font_size = 1

            font = ImageFont.truetype(self.get_option('font_path'), font_size)
            text_bbox = draw.textbbox((0, 0), label, font)
            text_width, text_height = (
                text_bbox[2] - text_bbox[0],
                text_bbox[3] - text_bbox[1],
            )

            im_copy = Image.new('RGBA', im.size, (255, 255, 255, 0))
            im_copy_draw = ImageDraw.Draw(im_copy)

            x = cx + (r - r_unit * 0.5) * math.cos(math.radians(angle_mid))
            y = cy + (r - r_unit * 0.5) * math.sin(math.radians(angle_mid))
            im_copy_draw.text(
                (x - text_width / 2, y - text_height / 2),
                label,
                fill=font_color,
                font=font,
            )
            if p_mid < 0.5:
                angle_rotate = 90 - angle_mid
            else:
                angle_rotate = 270 - angle_mid

            if not direction:
                angle_rotate += 90
            im_copy_rotated = im_copy.rotate(
                angle_rotate, resample=Image.BICUBIC, center=(x, y)
            )
            im.paste(im_copy_rotated, mask=im_copy_rotated)

            p_start = p_end

    def draw_levels(self, im):
        sorted_d_list = self.sorted_d_list
        n_levels = len(self.level_keys)
        for i_level, level in enumerate(reversed(self.level_keys)):
            log.debug(f"Building {level}...")
            label_to_n = {}
            for d in sorted_d_list:
                label = d[level]
                if label not in label_to_n:
                    label_to_n[label] = 0
                label_to_n[label] += d[self.value_key]

            self.draw_arcs(im, n_levels, i_level, label_to_n)

    @cached_property
    def im(self):
        # create python
        im = Image.new(
            'RGB',
            (self.get_option('width'), self.get_option('height')),
            (255, 255, 255),
        )
        self.draw_levels(im)
        return im

    def write(self, path):
        self.im.save(path, dpi=(600,600))
