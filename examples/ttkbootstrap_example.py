import imtk

# Select your implementation by importing the desired Frame
from imtk.backends.ttkbootstrap_impl import TTKBootstrapWindow

class SimpleApp(TTKBootstrapWindow):
    def __init__(self, **kwargs):
        super().__init__(title="TTKBootstrap Example", **kwargs)
        self.checked = True
        self.input_text = "Write here ..."
        self.float_val = 1.0
        self.int_val = 50
        self.selected = 0


    def draw(self) -> None:
        imtk.text("Just some random text")
        text = f"The text   {self.input_text}\n" \
               f"The float  {self.float_val:.1f}\n" \
               f"The int    {self.int_val}"
        imtk.text(text, "test")
        changed, self.checked = imtk.checkbox("Checkbox", self.checked)

        with imtk.labelframe("Buttons in a Grid"):
            for i in range(9):
                if i % 3 != 0:
                    imtk.same_row()
                if imtk.button(f"Button#{i}"):
                    print(f"Button {i} was pressed")


        if changed:
            print("Checked state changed:", self.checked)

        imtk.horizontal_separator("a separator", bootstyle='info')

        with imtk.frame("This frame is invisible"), imtk.row():
            for i in range(2):
                if imtk.button(f"Row Button#{i}", bootstyle='outline danger'):
                    print(f"Row Button {i} pressed")

        changed, self.selected = imtk.combo_box(
            "A Combobox",
            self.selected,
            values=["Option A", "Option B", "Option C"],
            label_position='left'
        )
        if changed:
            print("Combo box changed")

        imtk.progress_bar(
            "Progress", 
            self.float_val, 
            show_progress=True, 
            max_=2,
            bootstyle='striped info'
        )

        _, self.input_text = imtk.input_text("#Text input without label", self.input_text)
        _, self.input_text = imtk.input_text("Text input with label", self.input_text)
        _, self.float_val = imtk.float_slider("A float", self.float_val, vmax=2)
        _, self.float_val = imtk.input_float("A float#spin", self.float_val, vmax=2)
        _, self.int_val = imtk.int_slider("An int", self.int_val, bootstyle='warning')
        _, self.int_val = imtk.input_int('An int#spin', self.int_val)


if __name__ == '__main__':
    app = SimpleApp()
    app.geometry("400x300")
    # You may choose to repeatedly call refresh instead.
    # To do so set the refresh engine to 'loop'.
    # The default method 'callback' uses 
    # tkinter callbacks to trigger only refreshes on user input
    #
    # WARNING: Currently 'loop' does not play well with window resize and
    #          combobox widgets 
    # app.set_refresh_engine('loop')
    app.mainloop()
