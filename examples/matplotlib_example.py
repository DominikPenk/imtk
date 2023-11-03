import matplotlib.pyplot as plt
import numpy as np

import imtk
from imtk.backends.ttkbootstrap_impl import TTKBootstrapWindow as Window


class PlotApp(Window):
    def __init__(self, **kwargs):
        self.plot = imtk.Plot()
        self.num_plots = 2
        
        super().__init__(**kwargs)

        with self.plot:
            x = np.linspace(0, 1, 100)
            plt.plot(x, x**2)
            plt.plot(x, np.log(1 + x))

    def draw(self):
        imtk.plot(
            f"Plot with {self.num_plots} graphs", 
            self.plot,
            identifier="The Plot"
        )

        imtk.same_row()
        if imtk.button("Add Graph"):
            self.num_plots += 1
            with self.plot:
                x = np.linspace(0, 1, 100)
                e = np.random.uniform(0.125, 4.0)
                plt.plot(x, x**e)


if __name__ == '__main__':
    app = PlotApp()
    app.mainloop()