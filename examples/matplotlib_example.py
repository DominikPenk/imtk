import imtk
import ttkbootstrap as ttk
import matplotlib.pyplot as plt
import numpy as np

from imtk.backends.ttkbootstrap_impl import TTKBootstrapFrame as BaseFrame

class PlotFrame(BaseFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.plot = imtk.Plot()
        self.num_plots = 2

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



app = ttk.Window()
frame = PlotFrame(app)
frame.pack(fill='both', expand=True)
frame.refresh()
app.mainloop()