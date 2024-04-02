import matplotlib.pyplot as plt
from utils import Log

log = Log('Plot')


class Plot:
    @staticmethod
    def before():
        plt.close()
        plt.tight_layout(pad=2.0)
        plt.figure(figsize=(16, 9))
        plt.xticks(rotation='vertical')

    @staticmethod
    def set_text(
        title: str,
        xlabel: str,
        ylabel: str,
    ):
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

    @staticmethod
    def write(chart_path: str):
        plt.savefig(chart_path)
        plt.close()
        log.debug(f'Wrote {chart_path}')

    @staticmethod
    def scatter_with_fill(
        x,
        y,
        x_mean,
        y_mean,
        y_mean_q1,
        y_mean_q3,
        color,
    ):
        plt.scatter(x, y, color=color, alpha=0.3, s=100, edgecolors='none')
        plt.plot(
            x_mean, y_mean, color='black', linewidth=2, linestyle='dashed'
        )
        plt.fill_between(
            x_mean, y_mean_q1, y_mean_q3, color='black', alpha=0.1
        )
