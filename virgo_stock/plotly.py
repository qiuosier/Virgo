from Aries.visual.plotly import PlotlyFigure

class Candlestick(PlotlyFigure):
    INCREASING_COLOR = '#4CAF50'
    DECREASING_COLOR = '#E53935'

    def __init__(self, data_frame, title=""):
        self.df = data_frame
        layout = dict(
            xaxis=dict(
                rangeslider=dict(
                    visible=False
                ),
                title="",
            ),
            yaxis=dict(
                title="",
                domain=[0.25, 1.0],
            ),
            yaxis2=dict(
                domain=[0.0, 0.2],
            ),
            margin=dict(
                t=30,
                b=30,
                r=30,
                l=30,
            )
        )
        super().__init__(plotly_layout=layout)
        self.set_title(title)
        if hasattr(data_frame, "symbol"):
            symbol = data_frame.symbol
        else:
            symbol = ""
        self.candle_stick(
            data_frame,
            increasing=dict(
                line=dict(
                    color=self.INCREASING_COLOR
                )
            ),
            decreasing=dict(
                line=dict(
                    color=self.DECREASING_COLOR
                )
            ),
            name=symbol
        )
        self.bar(
            data_frame.index, 
            data_frame.volume, 
            "Volume", 
            yaxis='y2',
            marker=dict(
                color=self.volume_colors()
            )
        )

    def volume_colors(self):
        colors = []
        size = len(self.df.close)
        for i in range(size):
            if i < size - 1:
                if self.df.close[i] >= self.df.close[i + 1]:
                    colors.append(self.INCREASING_COLOR)
                else:
                    colors.append(self.DECREASING_COLOR)
            else:
                if self.df.close[i] >= self.df.open[i]:
                    colors.append(self.INCREASING_COLOR)
                else:
                    colors.append(self.DECREASING_COLOR)
        return colors
    