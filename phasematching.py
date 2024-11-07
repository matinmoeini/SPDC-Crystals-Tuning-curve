from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPixmap, QImage
from numpy import sin, cos, sqrt, linspace, pi, nan
from scipy.optimize import least_squares
import matplotlib.pyplot as plt
import mplcursors
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLineEdit, QStackedWidget, QPushButton, QLabel, QFrame
)
from PyQt5.uic import loadUiType
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
import sys

# Load the .ui file and extract the class
Ui_MainWindow_BBO_SPDC, _ = loadUiType('phase matching BBO spdc.ui')
Ui_MainWindow_PPLN_SPDC, _ = loadUiType('phase matching PPLN spdc.ui')
Ui_MainWindow_PPLNMGOSPDC, _=loadUiType('phase matching PPLNMgO spdc.ui')
Ui_MainWindow_LiNbO3_SPDC, _=loadUiType('phase matching LiNbo3 spdc.ui')
Ui_MainWindow_KTP_SPDC, _=loadUiType('phase matching KTP spdc.ui')
Ui_MainWindow_LBO_SPDC, _=loadUiType('phase matching LBO spdc.ui')
Ui_MainWindow_PPKTP_SPDC, _=loadUiType('phase matching PPKTP spdc.ui')
selected_crystal="BBO"

def exception_hook(exctype, value, traceback):
    print(f"An unhandled exception occurred: {value}")

sys.excepthook = exception_hook

class BBOSPDC(QMainWindow, Ui_MainWindow_BBO_SPDC):

    def __init__(self):
        super(BBOSPDC, self).__init__()

        # Setup the UI
        self.setupUi(self)

        # Find the QVBoxLayout with the name 'placeholderMatplotlib'
        self.matplotlibplaceholder = self.findChild(QWidget, 'matplotlib')

        # Find the QLineEdit widget and connect it to a method
        self.lineEditLandapump = self.findChild(QWidget, 'landapump')

        # Default value for landapump
        self.landapump = 0.36
        # Initialize QLabel to None; it will be created dynamically
        self.labelErr = 1
        self.lineEditLandapump.setText('360')
        self.add_text()
        self.calculation()

        #change combobox
        self.comboChange()

        # Initialize plot
        self.mathPlotLib()

    def calculation(self):
        self.button.clicked.connect(self.updateLandapump)

    def comboChange(self):
        self.crystal.currentIndexChanged.connect(self.on_combo_box_changed)

    def on_combo_box_changed(self, index):
        # Access the selected item or text when the combo box value changes
        global selected_crystal
        selected_crystal = self.crystal.itemText(index)
        print(selected_crystal)
        self.combocheck()

    def combocheck(self):
        if selected_crystal == "BBO":
            #print because not calculate again BBO
            print("bbo")
        elif selected_crystal == "PPLN":
            self.gotoscreenPPLNSPDC()
        elif selected_crystal == "KTP":
            self.gotoscreenKTPSPDC()
        elif selected_crystal == "PPLN:MgO":
            self.gotoscreenPPLNMgOSPDC()
        elif selected_crystal == "LBO":
            self.gotoscreenLBOSPDC()
        elif selected_crystal == "PPKTP":
            self.gotoscreenPPKTPSPDC()
        elif selected_crystal == "LiNbO3":
            self.gotoscreenLiNbO3SPDC()


    def gotoscreenPPLNSPDC(self):
        pplnspdc = PPLNSPDC()
        widget.addWidget(pplnspdc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoscreenPPLNMgOSPDC(self):
        pplnmgospdc = PPLNMGOSPDC()
        widget.addWidget(pplnmgospdc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoscreenLiNbO3SPDC(self):
        linbo3spdc = LiNbO3SPDC()
        widget.addWidget(linbo3spdc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoscreenKTPSPDC(self):
        ktpspdc = KTPSPDC()
        widget.addWidget(ktpspdc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoscreenLBOSPDC(self):
        lbospdc = LBOSPDC()
        widget.addWidget(lbospdc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoscreenPPKTPSPDC(self):
        ppktpspdc = PPKTPSPDC()
        widget.addWidget(ppktpspdc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def updateLandapump(self):
        try:
            self.label.hide()
            del self.label
            self.labelErr = 1
            self.add_text()
            # Update landapump based on the input from QLineEdit
            self.landapump = float(self.lineEditLandapump.text()) * 0.001
            print(f"Updated landapump: {self.landapump}")
            if self.landapump < 0.36 or self.landapump > 1.2:
                self.labelErr = 0
                self.add_text()
                self.lineEditLandapump.setText('360')
                self.landapump = float(self.lineEditLandapump.text()) * 0.001
        except ValueError:
            self.labelErr = 0
            self.add_text()
            # Fallback in case of invalid input
            self.lineEditLandapump.setText('360')
            self.landapump = float(self.lineEditLandapump.text()) * 0.001

        # Update the plot with new landapump value
        self.mathPlotLib()

    def add_text(self):
        # Dynamically create the QLabel and add text to it
        #self.labelErr for zero means  error and 1 means empty error
        if self.labelErr == 0:
            self.label = QLabel(self)
            self.label.setText("Please Enter a number from 360 _ 1100")
            self.label.setObjectName('labelError')
            self.label.move(110, 390)  # Position the text at (110, 390)
            self.label.setStyleSheet("color: red;")  # Set the text color to red
            self.label.adjustSize()  # Adjust the size to fit the text
            self.label.show()  # Show the label

        # If you want to update the text dynamically:
        else:
            self.label = QLabel(self)
            self.label.setText("")
            self.label.adjustSize()
            self.label.show()  # Show the label

    def mathPlotLib(self):
        # Check if the figure and axes already exist
        if not hasattr(self, 'fig') or not self.fig:
            # Create the figure and axes if they don't exist
            self.fig, self.ax = plt.subplots(figsize=(8, 6))
            self.canvas = FigureCanvas(self.fig)
            layout = QVBoxLayout(self.matplotlibplaceholder)
            layout.addWidget(self.canvas)
            central_widget = QWidget(self)
            central_widget.setLayout(layout)
            central_widget.setGeometry(370, 60, 850, 650)
        else:
            # Clear the existing axes to update the plot
            self.ax.clear()
            # Refresh hover functionality
            global cursor

        try:
            nopump = 2.7359 + (0.01878 / (self.landapump ** 2 - 0.01822)) - (0.01354 * (self.landapump ** 2))
            nepump = 2.3753 + (0.01224 / (self.landapump ** 2 - 0.01667)) - (0.01516 * (self.landapump ** 2))
        except ZeroDivisionError:
            nopump = float('inf')
            nepump = float('inf')

        # Theta values in radians
        theta_values = np.linspace(0, 90, 280) * (np.pi / 180)

        # Arrays to store solutions
        arrlanda1type1 = []
        arrlanda2type1 = []
        arrlanda1type2 = []
        arrlanda2type2 = []

        def equations(vars, nethetapump_value):
            landa1type1, landa2type1 = vars
            no1type1 = 2.7359 + (0.01878 / (landa1type1 ** 2 - 0.01822)) - (0.01354 * (landa1type1 ** 2))
            no2type1 = 2.7359 + (0.01878 / (landa2type1 ** 2 - 0.01822)) - (0.01354 * (landa2type1 ** 2))
            eq1 = 2*pi*((1 / self.landapump) - ((1 / landa1type1) + (1 / landa2type1)))
            eq2 = 2*pi*((nethetapump_value / self.landapump) - ((no1type1 / landa1type1) + (no2type1 / landa2type1)))
            return [eq1, eq2]

        def equationstype2(varstype2, nethetapump_value, theta):
            landa1type2, landa2type2 = varstype2
            ne1type2 = 2.3753 + (0.01224 / (landa1type2 ** 2 - 0.01667)) - (0.01516 * (landa1type2 ** 2))
            no1type2 = 2.7359 + (0.01878 / (landa1type2 ** 2 - 0.01822)) - (0.01354 * (landa1type2 ** 2))
            netheta1type2 = np.sqrt(1 / ((np.sin(theta) ** 2 / ne1type2 ** 2) + (np.cos(theta) ** 2 / no1type2 ** 2)))
            no2type2 = 2.7359 + (0.01878 / (landa2type2 ** 2 - 0.01822)) - (0.01354 * (landa2type2 ** 2))
            eq1type2 = 2*pi*((1 / self.landapump) - ((1 / landa1type2) + (1 / landa2type2)))
            eq2type2 = 2*pi*((nethetapump_value / self.landapump) - ((netheta1type2 / landa1type2) + (no2type2 / landa2type2)))
            return [eq1type2, eq2type2]

        initial_guess = [1.5, 0.4]
        initial_guesstype2 = [1.5, 0.4]

        bounds_type1 = ([0.2, 0.2], [2.3, 2.3])
        bounds_type2 = ([0.2, 0.2], [2.3, 2.3])

        for theta in theta_values:
            nethetapump = np.sqrt(1 / ((np.sin(theta) ** 2 / nepump ** 2) + (np.cos(theta) ** 2 / nopump ** 2)))

            result_type1 = least_squares(equations, initial_guess, args=(nethetapump,), bounds=bounds_type1)
            landa1type1, landa2type1 = result_type1.x
            eq1, eq2 = equations([landa1type1, landa2type1], nethetapump)
            tolerance=1e-4
            if eq1 < tolerance and eq2 < tolerance:
                arrlanda1type1.append(landa1type1)
                arrlanda2type1.append(landa2type1)
            else:
                arrlanda1type1.append(np.nan)
                arrlanda2type1.append(np.nan)

            initial_guesstype2 = [landa1type1, landa2type1]

            result_type2 = least_squares(equationstype2, initial_guesstype2, args=(nethetapump, theta),
                                         bounds=bounds_type2)
            landa1type2, landa2type2 = result_type2.x
            eq1type2, eq2type2 = equationstype2([landa1type2, landa2type2], nethetapump, theta)

            #tolerance is near zero and it means phase will be match
            if eq1type2 < tolerance and eq2type2 < tolerance and landa1type2 > landa2type2:
                arrlanda1type2.append(landa1type2)
                arrlanda2type2.append(landa2type2)
            else:
                arrlanda1type2.append(np.nan)
                arrlanda2type2.append(np.nan)

        # Plotting the results
        self.ax.plot(theta_values * 180 / np.pi, arrlanda1type1, color='red', label='landa idler type1')
        self.ax.plot(theta_values * 180 / np.pi, arrlanda2type1, color='blue', label='landa signal type1')
        self.ax.plot(theta_values * 180 / np.pi, arrlanda1type2, color='green', label='landa idler type2')
        self.ax.plot(theta_values * 180 / np.pi, arrlanda2type2, color='yellow', label='landa signal type2')
        self.ax.set_xlabel('Theta (degree)')
        self.ax.set_ylabel('Wavelength [µm]')
        self.ax.legend()
        self.ax.set_title(f'λpump: {self.landapump:.2f} µm')

        # Set initial zoom factor
        zoom_factor = 1.0

        def on_scroll(event):
            nonlocal zoom_factor
            # Get current axis limits
            cur_xlim = self.ax.get_xlim()
            cur_ylim = self.ax.get_ylim()

            # Determine the current position of the mouse in data coordinates
            xdata = event.xdata
            ydata = event.ydata

            # Check if zooming in or out
            if event.button == 'up':
                zoom_factor = 1.1  # Zoom in factor
            else:
                zoom_factor = 0.9  # Zoom out factor

            # Calculate the new limits based on the zoom factor
            new_width = (cur_xlim[1] - cur_xlim[0]) * zoom_factor
            new_height = (cur_ylim[1] - cur_ylim[0]) * zoom_factor

            # Calculate the new limits centered around the cursor position
            relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
            rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])

            new_xlim = [xdata - new_width * (1 - relx), xdata + new_width * relx]
            new_ylim = [ydata - new_height * (1 - rely), ydata + new_height * rely]

            # Apply the new limits
            self.ax.set_xlim(new_xlim)
            self.ax.set_ylim(new_ylim)
            self.fig.canvas.draw_idle()

        # Connect the scroll event to the function
        self.fig.canvas.mpl_connect('scroll_event', on_scroll)

        # Redraw the canvas
        self.canvas.draw()

        # Refresh hover functionality
        cursor = mplcursors.cursor(self.ax, hover=True)

        # Set the subtitle of the chart
        self.fig.suptitle("the values are for comparison between a couple of landa pump if you dont want it right click on it", fontsize=10, color='gray',y="0.03")

        @cursor.connect("add")
        def on_add(sel):
            sel.annotation.set(text=f"θ: {sel.target[0]:.2f}\nλ[µm]: {sel.target[1]:.2f}")

class MyMainWindow(QMainWindow):
    def __init__(self):
        super(MyMainWindow, self).__init__()
        self.bbospdc = BBOSPDC()
        self.setCentralWidget(self.bbospdc)

class PPLNSPDC(QMainWindow, Ui_MainWindow_PPLN_SPDC):
    def __init__(self):
        super(PPLNSPDC, self).__init__()
        # Set up the UI
        self.setupUi(self)
        # Find the QVBoxLayout with the name 'placeholderMatplotlib'
        self.matplotlibplaceholder = self.findChild(QWidget, 'matplotlib')

        # Find the QLineEdit widget and connect it to a method
        self.lineEditLandapump = self.findChild(QWidget, 'landapump')
        self.horizontalSliderTempreture()
        # Default value for landapump
        self.landapump = 400
        self.degreeNumber.display(313)
        self.lineEditLandapump.setText('400')
        # initial value
        self.graphshape.clicked.connect(self.toggleDisplay)
        self.labelErr=1
        self.calculation()

        # Initialize QLabel to None; it will be created dynamically
        self.label = None
        self.add_text()
        self.current_display = "matplotlib"
        # change combobox
        self.comboChange()

        # Initialize plot
        self.mathPlotLib()

    def toggleDisplay(self):
        # Check if self.matplotlibplaceholder is None
        if self.current_display == "matplotlib":
            self.shapePPLN()
            self.current_display = "image"
        else:
            # Hide or delete the shapePPLN (image placeholder)
            if hasattr(self, 'shapeplaceholder'):
                self.shapeplaceholder.hide()  # Optionally, delete if you prefer
                del self.shapeplaceholder
            self.mathPlotLib()
            self.current_display = "matplotlib"

    def calculation(self):
        self.calculate.clicked.connect(self.updateLandapump)

    def comboChange(self):
        self.crystal.currentIndexChanged.connect(self.on_combo_box_changed)

    def on_combo_box_changed(self, index):
        # Access the selected item or text when the combo box value changes
        global selected_crystal
        selected_crystal = "PPLN"
        selected_crystal = self.crystal.itemText(index)
        self.combocheck()

    def combocheck(self):
        if selected_crystal == "BBO":
            self.gotoscreenBBOSPDC()
        elif selected_crystal == "PPLN":
            self.gotoscreenPPLNSPDC()
        elif selected_crystal == "KTP":
            self.gotoscreenKTPSPDC()
        elif selected_crystal == "LBO":
            self.gotoscreenLBOSPDC()
        elif selected_crystal == "PPLN:MgO":
            self.gotoscreenPPLNMgOSPDC()
        elif selected_crystal == "PPKTP":
            self.gotoscreenPPKTPSPDC()
        elif selected_crystal == "LiNbO3":
            self.gotoscreenLiNbO3SPDC()

    def gotoscreenBBOSPDC(self):
        bbospdc = BBOSPDC()
        widget.addWidget(bbospdc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoscreenPPLNMgOSPDC(self):
        pplnmgospdc = PPLNMGOSPDC()
        widget.addWidget(pplnmgospdc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoscreenLiNbO3SPDC(self):
        linbo3spdc = LiNbO3SPDC()
        widget.addWidget(linbo3spdc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoscreenKTPSPDC(self):
        ktpspdc = KTPSPDC()
        widget.addWidget(ktpspdc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoscreenLBOSPDC(self):
        lbospdc = LBOSPDC()
        widget.addWidget(lbospdc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoscreenPPKTPSPDC(self):
        ppktpspdc = PPKTPSPDC()
        widget.addWidget(ppktpspdc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def add_text(self):
        # Dynamically create the QLabel and add text to it
        #self.labelErr for zero means  error and 1 means empty error
        if self.labelErr == 0:
            self.label = QLabel(self)
            self.label.setText("Please Enter a number from 400 _ 1999")
            self.label.setObjectName('labelError')
            self.label.move(110, 390)  # Position the text at (110, 390)
            self.label.setStyleSheet("color: red;")  # Set the text color to red
            self.label.adjustSize()  # Adjust the size to fit the text
            self.label.show()  # Show the label
        # If you want to update the text dynamically:
        else:
            self.label = QLabel(self)
            self.label.setText("")
            self.label.adjustSize()
            self.label.show()  # Show the label
    def horizontalSliderTempreture(self):
        self.degreeSlider.setMinimum(313)
        self.degreeSlider.setMaximum(773)
        # Set initial value
        self.degreeSlider.setValue(313)

        # Connect the slider to a function
        self.degreeSlider.valueChanged.connect(self.onSliderTempretureChange)


    def onSliderTempretureChange(self, value):
        # Update the label text when the slider value changes
        self.degreeNumber.display(value)

    def updateLandapump(self):

        try:
            self.label.hide()
            del self.label
            self.labelErr=1
            self.add_text()
            # Update landapump based on the input from QLineEdit
            self.landapump = float(self.lineEditLandapump.text())
            print(f"Updated landapump: {self.landapump}")
            if self.landapump < 400 or self.landapump > 1999:
                self.labelErr = 0
                self.add_text()
                self.lineEditLandapump.setText('400')
                self.landapump = float(self.lineEditLandapump.text())
        except ValueError:
            self.labelErr=0
            self.add_text()
            # Fallback in case of invalid input
            self.lineEditLandapump.setText('400')
            self.landapump=float(self.lineEditLandapump.text())

        # Update the plot with new landapump value
        self.mathPlotLib()

    def shapePPLN(self):
        if self.matplotlibplaceholder is None:
            self.shapeplaceholder = QFrame(self)
            self.shapeplaceholder.setGeometry(370, 60, 850, 650)
            self.shapeplaceholder.show()  # Make sure the placeholder is visible
            # Access the current layout of the matplotlibplaceholder
        layout = self.shapeplaceholder.layout()
        if hasattr(self, 'fig'):
            self.fig.clear()
            self.canvas.close()
            del self.fig
            del self.canvas

            # If the layout does not exist, create it
        if layout is None:
            layout = QVBoxLayout(self.shapeplaceholder)
            self.shapeplaceholder.setLayout(layout)

        # Create a new label widget to display the image
        self.label = QLabel(self.shapeplaceholder)

        # Load the image using QImage
        image = QImage("PPLN1.png")

        if image.isNull():
            print("Error: The image file could not be loaded.")
            return

        # Resize the image while maintaining quality
        scaled_image = image.scaled(850, 1000, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Convert the scaled QImage to QPixmap
        scaled_pixmap = QPixmap.fromImage(scaled_image)
        # Set the pixmap to the label
        self.label.setPixmap(scaled_pixmap)

        # Resize the label to fit the image size
        self.label.resize(scaled_pixmap.width(), scaled_pixmap.height())

        # Add the label with the image to the layout
        layout.addWidget(self.label)

        # Optional: Resize the placeholder to fit the image size
        self.shapeplaceholder.resize(scaled_pixmap.width(), scaled_pixmap.height())

    def mathPlotLib(self):
        # Hide or delete the shapePPLN (image placeholder)
        if hasattr(self, 'shapeplaceholder'):
            self.shapeplaceholder.hide()  # Optionally, delete if you prefer
            del self.shapeplaceholder
        # Check if the figure and axes already exist
        if not hasattr(self, 'fig') or not self.fig:
            # Create the figure and axes if they don't exist
            self.fig, self.ax = plt.subplots(figsize=(8, 6))
            self.canvas = FigureCanvas(self.fig)
            self.matplotlib.addWidget(self.canvas)
        else:
            # Clear the existing axes to update the plot
            self.ax.clear()
            # Refresh hover functionality
            global cursor

        try:
            nepumppower2=4.5567+2.605*1e-7*self.degreeSlider.value()**2+((0.970*1e5+2.7*1e-2*self.degreeSlider.value()**2)/(self.landapump**2-(2.01*1e2+5.4*1e-5*self.degreeSlider.value()**2)**2))-2.24*1e-8*self.landapump**2
            nepump = sqrt(nepumppower2)
        except ZeroDivisionError:
            nepump = float('inf')
        # Theta values in radians
        period = np.linspace(1, 90, 180)

        # Arrays to store solutions
        arrlanda1type0 = []
        arrlanda2type0 = []
        arrlanda1type1 = []
        arrlanda2type1 = []
        arrlanda1type2 = []
        arrlanda2type2 = []

        def equations(vars, nepump,periods):
            landa1type0, landa2type0 = vars
            ne1type0power2 = 4.5567 + 2.605 * 1e-7 * self.degreeSlider.value() ** 2 + ((0.970 * 1e5 + 2.7 * 1e-2 * self.degreeSlider.value() ** 2) / (
                        landa1type0 ** 2 - (
                            2.01*1e2+5.4*1e-5*self.degreeSlider.value()**2)**2)) - 2.24 * 1e-8 * landa1type0 ** 2
            ne2type0power2 = 4.5567 + 2.605 * 1e-7 * self.degreeSlider.value() ** 2 + ((0.970 * 1e5 + 2.7 * 1e-2 * self.degreeSlider.value() ** 2) / (landa2type0**2-(2.01*1e2+5.4*1e-5*self.degreeSlider.value()**2)**2)) - 2.24 * 1e-8 * landa2type0 ** 2
            ne1type0 = sqrt(ne1type0power2)
            ne2type0 = sqrt(ne2type0power2)
            eq1 = (1 / (self.landapump*0.001)) - ((1 / (landa1type0*0.001)) + (1 / (landa2type0*0.001)))
            eq2 = (nepump /  (self.landapump*0.001)) - ((ne1type0 / (landa1type0*0.001)) + (ne2type0 / (landa2type0*0.001))+1/periods)
            return [eq1, eq2]

        def equationstype1(varstype1, nepump,periods):
            landa1type1, landa2type1 = varstype1
            no1type1power2 = 4.9130 + ((1.173 * 1e5 + 1.65 * 1e-2 * self.degreeSlider.value() ** 2) / (landa1type1 ** 2 - (2.12 * 1e2 + 2.7 * 1e-5 * self.degreeSlider.value() ** 2) ** 2)) - 2.78 * 1e-8 * landa1type1 ** 2
            no2type1power2 = 4.9130 + ((1.173 * 1e5 + 1.65 * 1e-2 * self.degreeSlider.value() ** 2) / (
                        landa2type1 ** 2 - (2.12 * 1e2 + 2.7 * 1e-5 * self.degreeSlider.value() ** 2) ** 2)) - 2.78 * 1e-8 * landa2type1 ** 2
            no1type1 = sqrt(no1type1power2)
            no2type1 = sqrt(no2type1power2)
            eq1type1 = (1 / (self.landapump*0.001)) - ((1 / (landa1type1*0.001)) + (1 / (landa2type1*0.001)))
            eq2type1 = (nepump / (self.landapump*0.001)) - ((no1type1 / (landa1type1*0.001)) + (no2type1 / (landa2type1*0.001))+1/periods)
            return [eq1type1, eq2type1]

        def equationstype2(varstype2, nepump,periods):
            landa1type2, landa2type2 = varstype2
            ne1type2power2 = 4.5567 + 2.605 * 1e-7 * self.degreeSlider.value() ** 2 + ((0.970 * 1e5 + 2.7 * 1e-2 * self.degreeSlider.value() ** 2) / (
                        landa1type2 ** 2 - (
                            2.01*1e2+5.4*1e-5*self.degreeSlider.value()**2)**2)) - 2.24 * 1e-8 * landa1type2 ** 2
            no2type2power2 = 4.9130 + ((1.173 * 1e5 + 1.65 * 1e-2 * self.degreeSlider.value() ** 2) / (landa2type2**2-(2.12 * 1e2 + 2.7 * 1e-5 * self.degreeSlider.value() ** 2) ** 2)) - 2.78 * 1e-8 * landa2type2 ** 2
            ne1type2 = sqrt(ne1type2power2)
            no2type2 = sqrt(no2type2power2)
            eq1type2 = (1 / (self.landapump*0.001)) - ((1 / (landa1type2*0.001)) + (1 / (landa2type2*0.001)))
            print(f'eq1type2:{eq1type2}\n landa1type2:{landa1type2}\n landa2type2:{landa2type2}')
            eq2type2 = (nepump / (self.landapump*0.001)) - ((ne1type2 / (landa1type2*0.001)) + (no2type2 / (landa2type2*0.001))+1/periods)
            return [eq1type2, eq2type2]

        initial_guess = [1500, 400]
        initial_guesstype1 = [1500, 400]
        #دقت شود که درون حلقه هم تکرار شده است.
        initial_guesstype2 = [1500, 400]
        bounds_type0 = ([400, 400], [5000, 5000])
        bounds_type1 = ([400, 400], [5000, 5000])
        bounds_type2 = ([400, 400], [5000, 5000])
        tolerance=1e-4
        for periods in period:
            result_type0 = least_squares(equations, initial_guess, args=(nepump,periods), bounds=bounds_type0)
            landa1type0, landa2type0 = result_type0.x
            eq1, eq2 = equations([landa1type0, landa2type0], nepump,periods)

            if eq1 < tolerance and eq2  < tolerance:
                arrlanda1type0.append(landa1type0)
                arrlanda2type0.append(landa2type0)
            else:
                arrlanda1type0.append(np.nan)
                arrlanda2type0.append(np.nan)
            #the camma in args make tuple
            result_type1 = least_squares(equationstype1, initial_guesstype1, args=(nepump,periods), bounds=bounds_type1)
            landa1type1, landa2type1 = result_type1.x
            eq1type1, eq2type1 = equationstype1([landa1type1, landa2type1], nepump,periods)

            # tolerance is near zero and it means phase will be match
            if eq1type1 < tolerance and eq2type1 < tolerance:
                arrlanda1type1.append(landa1type1)
                arrlanda2type1.append(landa2type1)
            else:
                arrlanda1type1.append(np.nan)
                arrlanda2type1.append(np.nan)

            #numerical method for solve n equation and n passive
            result_type2 = least_squares(equationstype2, initial_guesstype2, args=(nepump,periods),
                                         bounds=bounds_type2)
            landa1type2, landa2type2 = result_type2.x
            eq1type2, eq2type2 = equationstype2([landa1type2, landa2type2], nepump, periods)
            if eq1type2 < tolerance and eq2type2 < tolerance and landa1type2 > landa2type2:
                arrlanda1type2.append(landa1type2)
                arrlanda2type2.append(landa2type2)
            else:
                arrlanda1type2.append(np.nan)
                arrlanda2type2.append(np.nan)
        # Plotting the results
        self.ax.plot(period, arrlanda1type1, color='red', label='landa signal type1')
        self.ax.plot(period, arrlanda2type1, color='blue', label='landa idler type1')
        self.ax.plot(period, arrlanda1type2, color='green', label='landa idler type2')
        self.ax.plot(period, arrlanda2type2, color='yellow', label='landa signal type2')
        self.ax.plot(period, arrlanda1type0, color='black', label='landa idler type0')
        self.ax.plot(period, arrlanda2type0, color='orange', label='landa signal type0')
        self.ax.set_xlabel('period [µm]')
        self.ax.set_ylabel('Wavelength [µm]')
        self.ax.legend()
        self.ax.set_title(f'λpump: {self.landapump:.2f} nm')

        # Set initial zoom factor
        zoom_factor = 1.0

        def on_scroll(event):
            nonlocal zoom_factor
            # Get current axis limits
            cur_xlim = self.ax.get_xlim()
            cur_ylim = self.ax.get_ylim()

            # Determine the current position of the mouse in data coordinates
            xdata = event.xdata
            ydata = event.ydata

            # Check if zooming in or out
            if event.button == 'up':
                zoom_factor = 1.1  # Zoom in factor
            else:
                zoom_factor = 0.9  # Zoom out factor

            # Calculate the new limits based on the zoom factor
            new_width = (cur_xlim[1] - cur_xlim[0]) * zoom_factor
            new_height = (cur_ylim[1] - cur_ylim[0]) * zoom_factor

            # Calculate the new limits centered around the cursor position
            relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
            rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])

            new_xlim = [xdata - new_width * (1 - relx), xdata + new_width * relx]
            new_ylim = [ydata - new_height * (1 - rely), ydata + new_height * rely]

            # Apply the new limits
            self.ax.set_xlim(new_xlim)
            self.ax.set_ylim(new_ylim)
            self.fig.canvas.draw_idle()

        # Connect the scroll event to the function
        self.fig.canvas.mpl_connect('scroll_event', on_scroll)
        # Redraw the canvas
        self.canvas.draw()

        # Refresh hover functionality
        cursor = mplcursors.cursor(self.ax, hover=True)

        # Set the subtitle of the chart
        self.fig.suptitle(
            "the values are for comparison between a couple of landa pump if you dont want it right click on it",
            fontsize=10, color='gray', y="0.03")

        @cursor.connect("add")
        def on_add(sel):
            sel.annotation.set(text=f"Λ[µm]: {sel.target[0]:.2f}\nλ[µm]: {sel.target[1]:.2f}")

class PPLNMGOSPDC(QMainWindow, Ui_MainWindow_PPLNMGOSPDC):
    def __init__(self):
        super(PPLNMGOSPDC, self).__init__()
        # Set up the UI
        self.setupUi(self)
        # Find the QVBoxLayout with the name 'placeholderMatplotlib'
        self.matplotlibplaceholder = self.findChild(QWidget, 'matplotlib')

        # Find the QLineEdit widget and connect it to a method
        self.lineEditLandapump = self.findChild(QWidget, 'landapump')
        self.horizontalSliderTempreture()
        self.degreeNumber.display(298)
        # Default value for landapump
        self.landapump = 400*0.001

        self.lineEditLandapump.setText('400')
        # initial value
        self.graphshape.clicked.connect(self.toggleDisplay)
        self.labelErr=1
        self.calculation()

        # Initialize QLabel to None; it will be created dynamically
        self.label = None
        self.add_text()
        self.current_display = "matplotlib"
        # change combobox
        self.comboChange()

        # Initialize plot
        self.mathPlotLib()

    def toggleDisplay(self):
        # Check if self.matplotlibplaceholder is None
        if self.current_display == "matplotlib":
            self.shapePPLN()
            self.current_display = "image"
        else:
            # Hide or delete the shapePPLN (image placeholder)
            if hasattr(self, 'shapeplaceholder'):
                self.shapeplaceholder.hide()  # Optionally, delete if you prefer
                del self.shapeplaceholder
            self.mathPlotLib()
            self.current_display = "matplotlib"

    def calculation(self):
        self.calculate.clicked.connect(self.updateLandapump)

    def comboChange(self):
        self.crystal.currentIndexChanged.connect(self.on_combo_box_changed)

    def on_combo_box_changed(self, index):
        # Access the selected item or text when the combo box value changes

        global selected_crystal
        selected_crystal = "PPLN"
        selected_crystal = self.crystal.itemText(index)
        print(selected_crystal)
        self.combocheck()

    def combocheck(self):
        if selected_crystal == "BBO":
            self.gotoscreenBBOSPDC()
        elif selected_crystal == "PPLN":
            self.gotoscreenPPLNSPDC()
        elif selected_crystal == "KTP":
            self.gotoscreenKTPSPDC()
        elif selected_crystal == "LBO":
            self.gotoscreenLBOSPDC()
        elif selected_crystal == "PPLN:MgO":
            self.gotoscreenPPLNMgOSPDC()
        elif selected_crystal == "PPKTP":
            self.gotoscreenPPKTPSPDC()
        elif selected_crystal == "LiNbO3":
            self.gotoscreenLiNbO3SPDC()

    def gotoscreenBBOSPDC(self):
        bbospdc = BBOSPDC()
        widget.addWidget(bbospdc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoscreenPPLNSPDC(self):
        pplnspdc = PPLNSPDC()
        widget.addWidget(pplnspdc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoscreenPPLNMgOSPDC(self):
        pplnmgospdc = PPLNMGOSPDC()
        widget.addWidget(pplnmgospdc)
        widget.setCurrentIndex(widget.currentIndex() + 1)


    def gotoscreenLiNbO3SPDC(self):
        linbo3spdc = LiNbO3SPDC()
        widget.addWidget(linbo3spdc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoscreenKTPSPDC(self):
        ktpspdc = KTPSPDC()
        widget.addWidget(ktpspdc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoscreenLBOSPDC(self):
        lbospdc = LBOSPDC()
        widget.addWidget(lbospdc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoscreenPPKTPSPDC(self):
        ppktpspdc = PPKTPSPDC()
        widget.addWidget(ppktpspdc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def add_text(self):
        # Dynamically create the QLabel and add text to it
        #self.labelErr for zero means  error and 1 means empty error
        if self.labelErr == 0:
            self.label = QLabel(self)
            self.label.setText("Please Enter a number from 500 _ 1700")
            self.label.setObjectName('labelError')
            self.label.move(110, 390)  # Position the text at (110, 390)
            self.label.setStyleSheet("color: red;")  # Set the text color to red
            self.label.adjustSize()  # Adjust the size to fit the text
            self.label.show()  # Show the label
        # If you want to update the text dynamically:
        else:
            self.label = QLabel(self)
            self.label.setText("")
            self.label.adjustSize()
            self.label.show()  # Show the label
    def horizontalSliderTempreture(self):
        self.degreeSlider.setMinimum(298)
        self.degreeSlider.setMaximum(773)

        # Set initial value
        self.degreeSlider.setValue(298)

        # Connect the slider to a function
        self.degreeSlider.valueChanged.connect(self.onSliderTempretureChange)


    def onSliderTempretureChange(self, value):
        # Update the label text when the slider value changes
        self.degreeNumber.display(value)

    def updateLandapump(self):
        try:
            self.label.hide()
            del self.label
            self.labelErr=1
            self.add_text()
            # Update landapump based on the input from QLineEdit
            self.landapump = float(self.lineEditLandapump.text())*0.001
            print(f"Updated landapump: {self.landapump}")
            if self.landapump < 0.5 or self.landapump > 1.7:
                self.labelErr = 0
                self.add_text()
                self.lineEditLandapump.setText('500')
                self.landapump = float(self.lineEditLandapump.text())*0.001
        except ValueError:
            self.labelErr=0
            self.add_text()
            # Fallback in case of invalid input
            self.lineEditLandapump.setText('500')
            self.landapump=float(self.lineEditLandapump.text())*0.001

        # Update the plot with new landapump value
        self.mathPlotLib()

    def shapePPLN(self):
        if self.matplotlibplaceholder is None:
            self.shapeplaceholder = QFrame(self)
            self.shapeplaceholder.setGeometry(370, 60, 850, 650)
            self.shapeplaceholder.show()  # Make sure the placeholder is visible
            # Access the current layout of the matplotlibplaceholder
        layout = self.shapeplaceholder.layout()
        if hasattr(self, 'fig'):
            self.fig.clear()
            self.canvas.close()
            del self.fig
            del self.canvas

            # If the layout does not exist, create it
        if layout is None:
            layout = QVBoxLayout(self.shapeplaceholder)
            self.shapeplaceholder.setLayout(layout)

        # Create a new label widget to display the image
        self.label = QLabel(self.shapeplaceholder)

        # Load the image using QImage
        image = QImage("PPLN1.png")

        if image.isNull():
            print("Error: The image file could not be loaded.")
            return

        # Resize the image while maintaining quality
        scaled_image = image.scaled(850, 1000, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Convert the scaled QImage to QPixmap
        scaled_pixmap = QPixmap.fromImage(scaled_image)
        # Set the pixmap to the label
        self.label.setPixmap(scaled_pixmap)

        # Resize the label to fit the image size
        self.label.resize(scaled_pixmap.width(), scaled_pixmap.height())

        # Add the label with the image to the layout
        layout.addWidget(self.label)

        # Optional: Resize the placeholder to fit the image size
        self.shapeplaceholder.resize(scaled_pixmap.width(), scaled_pixmap.height())

    def mathPlotLib(self):
        #constants
        a1e = 5.756
        a2e = 0.0983
        a3e = 0.2020
        a4e = 189.32
        a5e = 12.52
        a6e = 1.32*1e-2
        b1e = 2.860 * 1e-6
        b2e = 4.70 * 1e-8
        b3e = 6.113 * 1e-8
        b4e = 1.516*1e-4
        a1o = 5.653
        a2o = 0.1185
        a3o = 0.2091
        a4o = 89.61
        a5o = 10.85
        a6o = 1.97*1e-2
        b1o = 7.941 * 1e-7
        b2o = 3.134 * 1e-8
        b3o = -4.641 * 1e-9
        b4o = -2.188 * 1e-6
        f = (self.degreeSlider.value() - 297.5) * (self.degreeSlider.value() + 297.82)
        alpha = 1.53 * 1e-5
        beta = 5.3 * 1e-9

        # Hide or delete the shapePPLN (image placeholder)
        if hasattr(self, 'shapeplaceholder'):
            self.shapeplaceholder.hide()  # Optionally, delete if you prefer
            del self.shapeplaceholder
        # Check if the figure and axes already exist
        if not hasattr(self, 'fig') or not self.fig:
            # Create the figure and axes if they don't exist
            self.fig, self.ax = plt.subplots(figsize=(8, 6))
            self.canvas = FigureCanvas(self.fig)
            self.matplotlib.addWidget(self.canvas)
        else:
            # Clear the existing axes to update the plot
            self.ax.clear()
            # Refresh hover functionality
            global cursor

        try:
            nepumppower2 = a1e + (b1e * f) + ((a2e + b2e * f) / (self.landapump ** 2 - (a3e +b3e*f)** 2)) + (
                        (a4e + b4e * f) / (self.landapump ** 2 - a5e ** 2)) - (a6e * self.landapump ** 2)
            nepump = sqrt(nepumppower2)
        except ZeroDivisionError:
            nepump = float('inf')
        # Theta values in radians
        period = np.linspace(1, 90, 300)
        # Arrays to store solutions
        arrlanda1type0 = []
        arrlanda2type0 = []
        arrlanda1type1 = []
        arrlanda2type1 = []
        arrlanda1type2 = []
        arrlanda2type2 = []
        def equations(vars, nepump,periods):
            landa1type0, landa2type0 = vars
            period = periods*(1+alpha*(self.degreeSlider.value()-292)+beta*(self.degreeSlider.value()-292)**2)
            ne1type0power2 = a1e + (b1e * f) + ((a2e + b2e * f) / (landa1type0 ** 2 - (a3e + b3e * f) ** 2)) + (
                    (a4e + b4e * f) / (landa1type0 ** 2 - a5e ** 2)) - (a6e * landa1type0 ** 2)
            ne2type0power2 = a1e + (b1e * f) + ((a2e + b2e * f) / (landa2type0 ** 2 - (a3e + b3e * f) ** 2)) + (
                    (a4e + b4e * f) / (landa2type0 ** 2 - a5e ** 2)) - (a6e * landa2type0 ** 2)
            ne1type0 = sqrt(ne1type0power2)
            ne2type0 = sqrt(ne2type0power2)
            eq1 = (1 / self.landapump) - ((1 / landa1type0) + (1 / landa2type0))
            eq2 = (nepump /  self.landapump) - ((ne1type0 / landa1type0) + (ne2type0 / landa2type0)+1/period)
            return [eq1, eq2]


        def equationstype1(varstype1, nepump,periods):
            landa1type1, landa2type1 = varstype1
            period = periods * (1 + alpha * (self.degreeSlider.value() - 292) + beta * (self.degreeSlider.value() - 292) ** 2)
            no1type1power2 = a1o + (b1o * f) + ((a2o + b2o * f) / (landa1type1 ** 2 - (a3o + b3o * f) ** 2)) + (
                    (a4o + b4o * f) / (landa1type1 ** 2 - a5o ** 2)) - (a6o * landa1type1 ** 2)
            no2type1power2 = a1o + (b1o * f) + ((a2o + b2o * f) / (landa2type1 ** 2 - (a3o + b3o * f) ** 2)) + (
                    (a4o + b4o * f) / (landa2type1 ** 2 - a5o ** 2)) - (a6o * landa2type1 ** 2)
            no1type1 = sqrt(no1type1power2)
            no2type1 = sqrt(no2type1power2)
            eq1type1 = (1 / self.landapump) - ((1 / landa1type1) + (1 / landa2type1))
            eq2type1 = (nepump / self.landapump) - ((no1type1 / landa1type1) + (no2type1 / landa2type1)+1/period)
            return [eq1type1, eq2type1]

        def equationstype2(varstype2, nepump,periods):
            landa1type2, landa2type2 = varstype2
            period = periods * (
                        1 + alpha * (self.degreeSlider.value() - 292) + beta * (self.degreeSlider.value() - 292) ** 2)
            ne1type2power2 = a1e + (b1e * f) + ((a2e + b2e * f) / (landa1type2 ** 2 - (a3e + b3e * f) ** 2)) + (
                    (a4e + b4e * f) / (landa1type2 ** 2 - a5e ** 2)) - (a6e * landa1type2 ** 2)
            no2type2power2 = a1o + (b1o * f) + ((a2o + b2o * f) / (landa2type2 ** 2 - (a3o + b3o * f) ** 2)) + (
                    (a4o + b4o * f) / (landa2type2 ** 2 - a5o ** 2)) - (a6o * landa2type2 ** 2)
            ne1type2 = sqrt(ne1type2power2)
            no2type2 = sqrt(no2type2power2)
            eq1type2 = 2*pi*((1 / self.landapump) - ((1 / landa1type2) + (1 / landa2type2)))
            eq2type2 = (nepump / self.landapump) - ((ne1type2 / landa1type2) + (no2type2 / landa2type2)+1/period)
            return [eq1type2, eq2type2]

        initial_guess = [1.5, 0.5]
        initial_guesstype1 = [1.5, 0.5]
        #دقت شود که درون حلقه هم تکرار شده است.
        initial_guesstype2 = [1.5, 0.5]
        bounds_type0 = ([0.5, 0.5], [4, 4])
        bounds_type1 = ([0.5, 0.5], [4, 4])
        bounds_type2 = ([0.4, 0.5], [4, 4])
        tolerance=1e-5
        for periods in period:
            result_type0 = least_squares(equations, initial_guess, args=(nepump,periods), bounds=bounds_type0)
            landa1type0, landa2type0 = result_type0.x
            eq1, eq2 = equations([landa1type0, landa2type0], nepump,periods)

            if eq1 < tolerance and eq2  < tolerance:
                arrlanda1type0.append(landa1type0)
                arrlanda2type0.append(landa2type0)
            else:
                arrlanda1type0.append(np.nan)
                arrlanda2type0.append(np.nan)
            #the camma in args make tuple
            result_type1 = least_squares(equationstype1, initial_guesstype1, args=(nepump,periods), bounds=bounds_type1)
            landa1type1, landa2type1 = result_type1.x
            eq1type1, eq2type1 = equationstype1([landa1type1, landa2type1], nepump,periods)

            # tolerance is near zero and it means phase will be match
            if eq1type1 < tolerance and eq2type1 < tolerance:
                arrlanda1type1.append(landa1type1)
                arrlanda2type1.append(landa2type1)
            else:
                arrlanda1type1.append(np.nan)
                arrlanda2type1.append(np.nan)
            #numerical method for solve n equation and n passive
            result_type2 = least_squares(equationstype2, initial_guesstype2, args=(nepump,periods),
                                         bounds=bounds_type2)
            landa1type2, landa2type2 = result_type2.x
            eq1type2, eq2type2 = equationstype2([landa1type2, landa2type2], nepump, periods)
            if eq1type2 < tolerance and eq2type2 < tolerance and landa1type2 > landa2type2:
                arrlanda1type2.append(landa1type2)
                arrlanda2type2.append(landa2type2)
            else:
                arrlanda1type2.append(np.nan)
                arrlanda2type2.append(np.nan)

        # Plotting the results
        self.ax.plot(period, arrlanda1type0, color='black', label='landa idler type0')
        self.ax.plot(period, arrlanda2type0, color='orange', label='landa signal type0')
        self.ax.plot(period, arrlanda1type1, color='yellow', label='landa idler type1')
        self.ax.plot(period, arrlanda2type1, color='green', label='landa signal type1')
        self.ax.plot(period, arrlanda1type2, color='blue', label='landa idler type2')
        self.ax.plot(period, arrlanda2type2, color='red', label='landa signal type2')
        self.ax.set_xlabel('period [µm]')
        self.ax.set_ylabel('Wavelength [µm]')
        self.ax.legend()
        self.ax.set_title(f'λpump: {self.landapump*1000:.2f} nm')

        # Set initial zoom factor
        zoom_factor = 1.0

        def on_scroll(event):
            nonlocal zoom_factor
            # Get current axis limits
            cur_xlim = self.ax.get_xlim()
            cur_ylim = self.ax.get_ylim()

            # Determine the current position of the mouse in data coordinates
            xdata = event.xdata
            ydata = event.ydata

            # Check if zooming in or out
            if event.button == 'up':
                zoom_factor = 1.1  # Zoom in factor
            else:
                zoom_factor = 0.9  # Zoom out factor

            # Calculate the new limits based on the zoom factor
            new_width = (cur_xlim[1] - cur_xlim[0]) * zoom_factor
            new_height = (cur_ylim[1] - cur_ylim[0]) * zoom_factor

            # Calculate the new limits centered around the cursor position
            relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
            rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])

            new_xlim = [xdata - new_width * (1 - relx), xdata + new_width * relx]
            new_ylim = [ydata - new_height * (1 - rely), ydata + new_height * rely]

            # Apply the new limits
            self.ax.set_xlim(new_xlim)
            self.ax.set_ylim(new_ylim)
            self.fig.canvas.draw_idle()

        # Connect the scroll event to the function
        self.fig.canvas.mpl_connect('scroll_event', on_scroll)
        # Redraw the canvas
        self.canvas.draw()

        # Refresh hover functionality
        cursor = mplcursors.cursor(self.ax, hover=True)

        # Set the subtitle of the chart
        self.fig.suptitle(
            "the values are for comparison between a couple of landa pump if you dont want it right click on it",
            fontsize=10, color='gray', y="0.03")

        @cursor.connect("add")
        def on_add(sel):
            sel.annotation.set(text=f"Λ[µm]: {sel.target[0]:.2f}\nλ[µm]: {sel.target[1]:.2f}")

class LiNbO3SPDC(QMainWindow, Ui_MainWindow_LiNbO3_SPDC):
    def __init__(self):
        super(LiNbO3SPDC, self).__init__()
        # Set up the UI
        self.setupUi(self)
        # Find the QVBoxLayout with the name 'placeholderMatplotlib'
        self.matplotlibplaceholder = self.findChild(QWidget, 'matplotlib')

        # Find the QLineEdit widget and connect it to a method
        self.lineEditLandapump = self.findChild(QWidget, 'landapump')

        # Default value for landapump
        self.landapump = 400
        self.lineEditLandapump.setText('400')
        # initial value
        self.labelErr=1
        self.calculation()

        # Initialize QLabel to None; it will be created dynamically
        self.label = None
        self.add_text()

        # change combobox
        self.comboChange()

        # Initialize plot
        self.mathPlotLib()

    def calculation(self):
        self.calculate.clicked.connect(self.updateLandapump)

    def comboChange(self):
        self.crystal.currentIndexChanged.connect(self.on_combo_box_changed)

    def on_combo_box_changed(self, index):
        # Access the selected item or text when the combo box value changes
        global selected_crystal
        selected_crystal = "PPLN"
        selected_crystal = self.crystal.itemText(index)
        print(selected_crystal)
        self.combocheck()

    def combocheck(self):
        if selected_crystal == "BBO":
            self.gotoscreenBBOSPDC()
        elif selected_crystal == "PPLN":
            self.gotoscreenPPLNSPDC()
        elif selected_crystal == "KTP":
            self.gotoscreenKTPSPDC()
        elif selected_crystal == "LBO":
            self.gotoscreenLBOSPDC()
        elif selected_crystal == "PPLN:MgO":
            self.gotoscreenPPLNMgOSPDC()
        elif selected_crystal == "PPKTP":
            self.gotoscreenPPKTPSPDC()
        elif selected_crystal == "LiNbO3":
            self.gotoscreenLiNbO3SPDC()

    def gotoscreenBBOSPDC(self):
        bbospdc = BBOSPDC()
        widget.addWidget(bbospdc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoscreenPPLNSPDC(self):
        pplnspdc = PPLNSPDC()
        widget.addWidget(pplnspdc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoscreenPPLNMgOSPDC(self):
        pplnmgospdc = PPLNMGOSPDC()
        widget.addWidget(pplnmgospdc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoscreenLiNbO3SPDC(self):
        linbo3spdc = LiNbO3SPDC()
        widget.addWidget(linbo3spdc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoscreenKTPSPDC(self):
        ktpspdc = KTPSPDC()
        widget.addWidget(ktpspdc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoscreenLBOSPDC(self):
        lbospdc = LBOSPDC()
        widget.addWidget(lbospdc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoscreenPPKTPSPDC(self):
        ppktpspdc = PPKTPSPDC()
        widget.addWidget(ppktpspdc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def add_text(self):
        # Dynamically create the QLabel and add text to it
        #self.labelErr for zero means  error and 1 means empty error
        if self.labelErr == 0:
            self.label = QLabel(self)
            self.label.setText("Please Enter a number from 400 _ 1999")
            self.label.setObjectName('labelError')
            self.label.move(110, 390)  # Position the text at (110, 390)
            self.label.setStyleSheet("color: red;")  # Set the text color to red
            self.label.adjustSize()  # Adjust the size to fit the text
            self.label.show()  # Show the label
        # If you want to update the text dynamically:
        else:
            self.label = QLabel(self)
            self.label.setText("")
            self.label.adjustSize()
            self.label.show()  # Show the label


    def updateLandapump(self):
        try:
            self.label.hide()
            del self.label
            self.labelErr=1
            self.add_text()
            # Update landapump based on the input from QLineEdit
            self.landapump = float(self.lineEditLandapump.text())
            print(f"Updated landapump: {self.landapump}")
            if self.landapump < 400 or self.landapump > 1999:
                self.labelErr = 0
                self.add_text()
                self.lineEditLandapump.setText('400')
                self.landapump = float(self.lineEditLandapump.text())
        except ValueError:
            self.labelErr=0
            self.add_text()
            # Fallback in case of invalid input
            self.lineEditLandapump.setText('400')
            self.landapump=float(self.lineEditLandapump.text())
        # Update the plot with new landapump value
        self.mathPlotLib()

    def mathPlotLib(self):
        # Check if the figure and axes already exist
        if not hasattr(self, 'fig') or not self.fig:
            # Create the figure and axes if they don't exist
            self.fig, self.ax = plt.subplots(figsize=(8, 6))
            self.canvas = FigureCanvas(self.fig)
            self.matplotlib.addWidget(self.canvas)
        else:
            # Clear the existing axes to update the plot
            self.ax.clear()
            # Refresh hover functionality
            global cursor

        # Tempreture in kelvin
        T = np.linspace(313, 773, 500)

        # Arrays to store solutions
        arrlanda1type1 = []
        arrlanda2type1 = []
        arrlanda1type2 = []
        arrlanda2type2 = []


        def equationstype1(varstype1, nepump,Tempretures):
            landa1type1, landa2type1 = varstype1
            no1type1power2 = 4.9130 + ((1.173 * 1e5 + 1.65 * 1e-2 * Tempretures ** 2) / (landa1type1 ** 2 - (2.12 * 1e2 + 2.7 * 1e-5 * Tempretures ** 2) ** 2)) - 2.78 * 1e-8 * landa1type1 ** 2
            no2type1power2 = 4.9130 + ((1.173 * 1e5 + 1.65 * 1e-2 * Tempretures ** 2) / (
                        landa2type1 ** 2 - (2.12 * 1e2 + 2.7 * 1e-5 * Tempretures ** 2) ** 2)) - 2.78 * 1e-8 * landa2type1 ** 2
            no1type1 = sqrt(no1type1power2)
            no2type1 = sqrt(no2type1power2)
            eq1type1 = (1 / (self.landapump*0.001)) - ((1 / (landa1type1*0.001)) + (1 / (landa2type1*0.001)))
            eq2type1 = (nepump / (self.landapump*0.001)) - ((no1type1 / (landa1type1*0.001)) + (no2type1 / (landa2type1*0.001)))
            return [eq1type1, eq2type1]

        def equationstype2(varstype2, nepump,Tempretures):
            landa1type2, landa2type2 = varstype2
            ne1type2power2 = 4.5567 + 2.605 * 1e-7 * Tempretures ** 2 + ((0.970 * 1e5 + 2.7 * 1e-2 * Tempretures ** 2) / (
                        landa1type2 ** 2 - (
                            2.01*1e2+5.4*1e-5*Tempretures**2)**2)) - 2.24 * 1e-8 * landa1type2 ** 2
            no2type2power2 = 4.9130 + ((1.173 * 1e5 + 1.65 * 1e-2 * Tempretures ** 2) / (landa2type2**2-(2.12 * 1e2 + 2.7 * 1e-5 * Tempretures ** 2) ** 2)) - 2.78 * 1e-8 * landa2type2 ** 2
            ne1type2 = sqrt(ne1type2power2)
            no2type2 = sqrt(no2type2power2)
            eq1type2 = (1 / (self.landapump*0.001)) - ((1 / (landa1type2*0.001)) + (1 / (landa2type2*0.001)))
            eq2type2 = (nepump / (self.landapump*0.001)) - ((ne1type2 / (landa1type2*0.001)) + (no2type2 / (landa2type2*0.001)))
            return [eq1type2, eq2type2]


        initial_guesstype1 = [1500, 400]
        #دقت شود که درون حلقه هم تکرار شده است.
        initial_guesstype2 = [1500, 400]
        bounds_type1 = ([400, 400], [5000, 5000])
        bounds_type2 = ([400, 400], [5000, 5000])
        tolerance=1e-5
        for Tempretures in T:
            try:
                nepumppower2 = 4.5567 + 2.605 * 1e-7 * Tempretures ** 2 + ((0.970 * 1e5 + 2.7 * 1e-2 * Tempretures ** 2) / (
                        self.landapump ** 2 - (
                            2.01 * 1e2 + 5.4 * 1e-5 * Tempretures ** 2) ** 2)) - 2.24 * 1e-8 * self.landapump ** 2
                nepump = sqrt(nepumppower2)
            except ZeroDivisionError:
                nepump = float('inf')
            #the camma in args make tuple
            result_type1 = least_squares(equationstype1, initial_guesstype1, args=(nepump,Tempretures), bounds=bounds_type1)
            landa1type1, landa2type1 = result_type1.x
            eq1type1, eq2type1 = equationstype1([landa1type1, landa2type1], nepump,Tempretures)
            # tolerance is near zero and it means phase will be match
            if eq1type1 < tolerance and eq2type1 < tolerance:
                arrlanda1type1.append(landa1type1)
                arrlanda2type1.append(landa2type1)
            else:
                arrlanda1type1.append(np.nan)
                arrlanda2type1.append(np.nan)

            result_type2 = least_squares(equationstype2, initial_guesstype2, args=(nepump,Tempretures),
                                         bounds=bounds_type2)
            landa1type2, landa2type2 = result_type2.x
            eq1type2, eq2type2 = equationstype2([landa1type2, landa2type2], nepump, Tempretures)

            if eq1type2 < tolerance and eq2type2 < tolerance and landa1type2 > landa2type2:
                arrlanda1type2.append(landa1type2)
                arrlanda2type2.append(landa2type2)
            else:
                arrlanda1type2.append(np.nan)
                arrlanda2type2.append(np.nan)

        # Plotting the results
        self.ax.plot(T, arrlanda1type1, color='red', label='landa signal type1')
        self.ax.plot(T, arrlanda2type1, color='blue', label='landa idler type1')
        self.ax.plot(T, arrlanda1type2, color='green', label='landa idler type2')
        self.ax.plot(T, arrlanda2type2, color='yellow', label='landa signal type2')
        self.ax.set_xlabel('T [K]')
        self.ax.set_ylabel('Wavelength [nm]')
        self.ax.legend()
        self.ax.set_title(f'λpump: {self.landapump:.2f} nm')

        # Set initial zoom factor
        zoom_factor = 1.0

        def on_scroll(event):
            nonlocal zoom_factor
            # Get current axis limits
            cur_xlim = self.ax.get_xlim()
            cur_ylim = self.ax.get_ylim()

            # Determine the current position of the mouse in data coordinates
            xdata = event.xdata
            ydata = event.ydata

            # Check if zooming in or out
            if event.button == 'up':
                zoom_factor = 1.1  # Zoom in factor
            else:
                zoom_factor = 0.9  # Zoom out factor

            # Calculate the new limits based on the zoom factor
            new_width = (cur_xlim[1] - cur_xlim[0]) * zoom_factor
            new_height = (cur_ylim[1] - cur_ylim[0]) * zoom_factor

            # Calculate the new limits centered around the cursor position
            relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
            rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])

            new_xlim = [xdata - new_width * (1 - relx), xdata + new_width * relx]
            new_ylim = [ydata - new_height * (1 - rely), ydata + new_height * rely]

            # Apply the new limits
            self.ax.set_xlim(new_xlim)
            self.ax.set_ylim(new_ylim)
            self.fig.canvas.draw_idle()

        # Connect the scroll event to the function
        self.fig.canvas.mpl_connect('scroll_event', on_scroll)

        # Redraw the canvas
        self.canvas.draw()

        # Refresh hover functionality
        cursor = mplcursors.cursor(self.ax, hover=True)

        # Set the subtitle of the chart
        self.fig.suptitle(
            "the values are for comparison between a couple of landa pump if you dont want it right click on it",
            fontsize=10, color='gray', y="0.03")

        @cursor.connect("add")
        def on_add(sel):

            sel.annotation.set(text=f"T [K]: {sel.target[0]:.2f}\nλ[µm]: {sel.target[1]:.2f}")

class KTPSPDC(QMainWindow, Ui_MainWindow_KTP_SPDC):

    def __init__(self):
        super(KTPSPDC, self).__init__()

        # Setup the UI
        self.setupUi(self)

        # Find the QVBoxLayout with the name 'placeholderMatplotlib'
        self.matplotlibplaceholder = self.findChild(QWidget, 'matplotlib')

        # Find the QLineEdit widget and connect it to a method
        self.lineEditLandapump = self.findChild(QWidget, 'landapump')
        self.horizontalSliderTempreture()
        self.degreeNumber.display(1)

        # Default value for landapump
        self.landapump = 0.430
        # Initialize QLabel to None; it will be created dynamically
        self.labelErr = 1
        self.lineEditLandapump.setText('430')
        self.add_text()
        self.calculation()

        #change combobox
        self.comboChange()

        # Initialize plot
        self.mathPlotLib()

    def calculation(self):
        self.button.clicked.connect(self.updateLandapump)

    def comboChange(self):
        self.crystal.currentIndexChanged.connect(self.on_combo_box_changed)

    def on_combo_box_changed(self, index):
        # Access the selected item or text when the combo box value changes
        global selected_crystal
        selected_crystal = self.crystal.itemText(index)
        print(selected_crystal)
        self.combocheck()

    def combocheck(self):
        if selected_crystal == "BBO":
            self.gotoscreenBBOSPDC()
        elif selected_crystal == "PPLN":
            self.gotoscreenPPLNSPDC()
        elif selected_crystal == "KTP":
            self.gotoscreenKTPSPDC()
        elif selected_crystal == "PPLN:MgO":
            self.gotoscreenPPLNMgOSPDC()
        elif selected_crystal == "LBO":
            self.gotoscreenLBOSPDC()
        elif selected_crystal == "PPKTP":
            self.gotoscreenPPKTPSPDC()
        elif selected_crystal == "LiNbO3":
            self.gotoscreenLiNbO3SPDC()

    def gotoscreenBBOSPDC(self):
        bbospdc = BBOSPDC()
        widget.addWidget(bbospdc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoscreenPPLNSPDC(self):
        pplnspdc = PPLNSPDC()
        widget.addWidget(pplnspdc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoscreenPPLNMgOSPDC(self):
        pplnmgospdc = PPLNMGOSPDC()
        widget.addWidget(pplnmgospdc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoscreenLiNbO3SPDC(self):
        linbo3spdc = LiNbO3SPDC()
        widget.addWidget(linbo3spdc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoscreenKTPSPDC(self):
        ktpspdc = KTPSPDC()
        widget.addWidget(ktpspdc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoscreenLBOSPDC(self):
        lbospdc = LBOSPDC()
        widget.addWidget(lbospdc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoscreenPPKTPSPDC(self):
        ppktpspdc = PPKTPSPDC()
        widget.addWidget(ppktpspdc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def updateLandapump(self):
        try:
            self.label.hide()
            del self.label
            self.labelErr = 1
            self.add_text()
            # Update landapump based on the input from QLineEdit
            self.landapump = float(self.lineEditLandapump.text()) * 0.001
            print(f"Updated landapump: {self.landapump}")
            if self.landapump < 0.430 or self.landapump > 1.7:
                self.labelErr = 0
                self.add_text()
                self.lineEditLandapump.setText('430')
                self.landapump = float(self.lineEditLandapump.text()) * 0.001
        except ValueError:
            self.labelErr = 0
            self.add_text()
            # Fallback in case of invalid input
            self.lineEditLandapump.setText('430')
            self.landapump = float(self.lineEditLandapump.text()) * 0.001

        # Update the plot with new landapump value
        self.mathPlotLib()

    def add_text(self):
        # Dynamically create the QLabel and add text to it
        #self.labelErr for zero means  error and 1 means empty error
        if self.labelErr == 0:
            self.label = QLabel(self)
            self.label.setText("Please Enter a number from 430 _ 1700")
            self.label.setObjectName('labelError')
            self.label.move(110, 390)  # Position the text at (110, 390)
            self.label.setStyleSheet("color: red;")  # Set the text color to red
            self.label.adjustSize()  # Adjust the size to fit the text
            self.label.show()  # Show the label

        # If you want to update the text dynamically:
        else:
            self.label = QLabel(self)
            self.label.setText("")
            self.label.adjustSize()
            self.label.show()  # Show the label

    def horizontalSliderTempreture(self):
        self.degreeSlider.setMinimum(0)
        self.degreeSlider.setMaximum(180)

        # Set initial value
        self.degreeSlider.setValue(1)

        # Connect the slider to a function
        self.degreeSlider.valueChanged.connect(self.onSliderTempretureChange)


    def onSliderTempretureChange(self, value):
        # Update the label text when the slider value changes
        self.degreeNumber.display(value)

    def mathPlotLib(self):
        # Check if the figure and axes already exist
        if not hasattr(self, 'fig') or not self.fig:
            # Create the figure and axes if they don't exist
            self.fig, self.ax = plt.subplots(figsize=(8, 6))
            self.canvas = FigureCanvas(self.fig)
            layout = QVBoxLayout(self.matplotlibplaceholder)
            layout.addWidget(self.canvas)
            central_widget = QWidget(self)
            central_widget.setLayout(layout)
            central_widget.setGeometry(370, 60, 850, 650)
        else:
            # Clear the existing axes to update the plot
            self.ax.clear()
            # Refresh hover functionality
            global cursor

        # Theta values in radians
        phi_values = np.linspace(0, 90, 120) * (np.pi / 180)
        # n fast means lower refractive index that is for n pump to phase match
        #biaxial crystal have three refractive index and two for polarization in ellipsoid
        nxpump = np.sqrt(3.29100 + (0.04140 / (self.landapump ** 2 - 0.03978)) + (9.35522/(self.landapump ** 2 - 31.45571)))
        nypump = np.sqrt(
                3.45018 + (0.04341 / (self.landapump ** 2 - 0.04597)) + (16.98825 / (self.landapump ** 2 - 39.43799)))
        nzpump = np.sqrt(
                4.59423 + (0.06206 / (self.landapump ** 2 - 0.04763)) + (110.80672 / (self.landapump ** 2 - 86.12171)))
        #omegapump is omega for refractive index og pump and omega is angle between z and optic axis
        omegapump = np.arcsin((nzpump/nypump)*np.sqrt((nypump**2-nxpump**2)/(nzpump**2-nxpump**2)))

        # Arrays to store solutions
        arrlanda1type1 = []
        arrlanda2type1 = []
        arrlanda1type2 = []
        arrlanda2type2 = []

        def equations(vars, npumpfast):
            landa1type1, landa2type1 = vars
            nx1type1 = np.sqrt(
                3.29100 + (0.04140 / (landa1type1 ** 2 - 0.03978)) + (9.35522 / (landa1type1 ** 2 - 31.45571)))
            ny1type1 = np.sqrt(
                3.45018 + (0.04341 / (landa1type1 ** 2 - 0.04597)) + (16.98825 / (landa1type1 ** 2 - 39.43799)))
            nz1type1 = np.sqrt(
                4.59423 + (0.06206 / (landa1type1 ** 2 - 0.04763)) + (110.80672 / (landa1type1 ** 2 - 86.12171)))
            # omegapump is omega for refractive index og pump and omega is angle between z and optic axis
            omega1 = np.arcsin(
                (nz1type1 / ny1type1) * np.sqrt((ny1type1 ** 2 - nx1type1 ** 2) / (nz1type1 ** 2 - nx1type1 ** 2)))

            if self.degreeSlider.value() > 90:
                thetazegond = -np.arctan(np.tan(self.degreeSlider.value() * np.pi / 180) * np.cos(phi))
                # theta1 is angle between k and c1(first optic axis) and theta2 is angle between k and c2
                # optic axis move with wavelength in the other hand is wavelength dependent
                theta1_1type1 = np.arccos(
                    (np.cos(self.degreeSlider.value() * np.pi / 180) / np.cos(thetazegond)) * np.cos(
                        omega1 - thetazegond))
                theta2_1type1 = np.arccos(
                    (np.cos(self.degreeSlider.value() * np.pi / 180) / np.cos(thetazegond)) * np.cos(
                        omega1 + thetazegond))
            elif self.degreeSlider.value() < 90:
                thetazegond = np.arctan(np.tan(self.degreeSlider.value() * np.pi / 180) * np.cos(phi))

                theta1_1type1 = np.arccos(
                    (np.cos(self.degreeSlider.value() * np.pi / 180) / np.cos(thetazegond)) * np.cos(
                        omega1 - thetazegond))
                theta2_1type1 = np.arccos(
                    (np.cos(self.degreeSlider.value() * np.pi / 180) / np.cos(thetazegond)) * np.cos(
                        omega1 + thetazegond))
            elif self.degreeSlider.value() == 90:
                theta1_1type1 = np.arccos(np.sin(omega1) * np.cos(phi))
                theta2_1type1 = np.arccos(-np.sin(omega1) * np.cos(phi))

            # n1 and n2 is polarization refractive index in ellipsoid
            n1_1type1 = (nx1type1 * nz1type1) / (np.sqrt(
                nz1type1 ** 2 * np.cos((theta1_1type1 + theta2_1type1) / 2) ** 2 + nx1type1 ** 2 * np.sin(
                    (theta1_1type1 + theta2_1type1) / 2) ** 2))
            n2_1type1 = (nx1type1 * nz1type1) / (np.sqrt(
                nz1type1 ** 2 * np.cos((theta1_1type1 - theta2_1type1) / 2) ** 2 + nx1type1 ** 2 * np.sin(
                    (theta1_1type1 - theta2_1type1) / 2) ** 2))
            if n1_1type1 > n2_1type1:
                n_1slow = n1_1type1
            else:
                n_1slow = n2_1type1
            # //////////////////////////////////////////////////////////////////////////////////////////////////
            nx2type1 = np.sqrt(
                3.29100 + (0.04140 / (landa2type1 ** 2 - 0.03978)) + (9.35522 / (landa2type1 ** 2 - 31.45571)))
            ny2type1 = np.sqrt(
                3.45018 + (0.04341 / (landa2type1 ** 2 - 0.04597)) + (16.98825 / (landa2type1 ** 2 - 39.43799)))
            nz2type1 = np.sqrt(
                4.59423 + (0.06206 / (landa2type1 ** 2 - 0.04763)) + (110.80672 / (landa2type1 ** 2 - 86.12171)))
            # omega2 is omega for refractive index og landa2 and omega is angle between z and optic axis
            omega2 = np.arcsin(
                (nz2type1 / ny2type1) * np.sqrt((ny2type1 ** 2 - nx2type1 ** 2) / (nz2type1 ** 2 - nx2type1 ** 2)))
            if self.degreeSlider.value() > 90:
                thetazegond = -np.arctan(np.tan(self.degreeSlider.value() * np.pi / 180) * np.cos(phi))
                # theta1 is angle between k and c1(first optic axis) and theta2 is angle between k and c2
                # optic axis move with wavelength in the other hand is wavelength dependent
                theta1_2type1 = np.arccos(
                    (np.cos(self.degreeSlider.value() * np.pi / 180) / np.cos(thetazegond)) * np.cos(
                        omega2 - thetazegond))
                theta2_2type1 = np.arccos(
                    (np.cos(self.degreeSlider.value() * np.pi / 180) / np.cos(thetazegond)) * np.cos(
                        omega2 + thetazegond))
            elif self.degreeSlider.value() < 90:
                thetazegond = np.arctan(np.tan(self.degreeSlider.value() * np.pi / 180) * np.cos(phi))
                theta1_2type1 = np.arccos(
                    (np.cos(self.degreeSlider.value() * np.pi / 180) / np.cos(thetazegond)) * np.cos(
                        omega2 - thetazegond))
                theta2_2type1 = np.arccos(
                    (np.cos(self.degreeSlider.value() * np.pi / 180) / np.cos(thetazegond)) * np.cos(
                        omega2 + thetazegond))
            elif self.degreeSlider.value() == 90:
                theta1_2type1 = np.arccos(np.sin(omega2) * np.cos(phi))
                theta2_2type1 = np.arccos(-np.sin(omega2) * np.cos(phi))

                # n1 and n2 is polarization refractive index in ellipsoid
                #first number is refractive index of polarization and second number is for landa2
            n1_2type1 = (nx2type1 * nz2type1) / (np.sqrt(
                nz2type1 ** 2 * np.cos((theta1_2type1 + theta2_2type1) / 2) ** 2 + nx2type1 ** 2 * np.sin(
                    (theta1_2type1 + theta2_2type1) / 2) ** 2))
            n2_2type1 = (nx2type1 * nz2type1) / (np.sqrt(
                nz2type1 ** 2 * np.cos((theta1_2type1 - theta2_2type1) / 2) ** 2 + nx2type1 ** 2 * np.sin(
                    (theta1_2type1 - theta2_2type1) / 2) ** 2))
            if n1_2type1 > n2_2type1:
                n_2slow = n1_2type1
            else:
                n_2slow = n2_2type1

            eq1 = (1 / self.landapump) - ((1 / landa1type1) + (1 / landa2type1))
            eq2 = (npumpfast / self.landapump) - ((n_1slow / landa1type1) + (n_2slow / landa2type1))
            return [eq1, eq2]

        def equationstype2(varstype2, npumpfast):
            landa1type2, landa2type2 = varstype2
            nx1type2 = np.sqrt(
                3.29100 + (0.04140 / (landa1type2 ** 2 - 0.03978)) + (9.35522 / (landa1type2 ** 2 - 31.45571)))
            ny1type2 = np.sqrt(
                3.45018 + (0.04341 / (landa1type2 ** 2 - 0.04597)) + (16.98825 / (landa1type2 ** 2 - 39.43799)))
            nz1type2 = np.sqrt(
                4.59423 + (0.06206 / (landa1type2 ** 2 - 0.04763)) + (110.80672 / (landa1type2 ** 2 - 86.12171)))
            # omegapump is omega for refractive index of pump and omega is angle between z and optic axis
            omega1 = np.arcsin(
                (nz1type2 / ny1type2) * np.sqrt((ny1type2 ** 2 - nx1type2 ** 2) / (nz1type2 ** 2 - nx1type2 ** 2)))

            if self.degreeSlider.value() > 90:
                thetazegond = -np.arctan(np.tan(self.degreeSlider.value() * np.pi / 180) * np.cos(phi))
                # theta1 is angle between k and c1(first optic axis) and theta2 is angle between k and c2
                # optic axis move with wavelength in the other hand is wavelength dependent
                theta1_1type2 = np.arccos(
                    (np.cos(self.degreeSlider.value() * np.pi / 180) / np.cos(thetazegond)) * np.cos(
                        omega1 - thetazegond))
                theta2_1type2 = np.arccos(
                    (np.cos(self.degreeSlider.value() * np.pi / 180) / np.cos(thetazegond)) * np.cos(
                        omega1 + thetazegond))
            elif self.degreeSlider.value() < 90:
                thetazegond = np.arctan(np.tan(self.degreeSlider.value() * np.pi / 180) * np.cos(phi))

                theta1_1type2 = np.arccos(
                    (np.cos(self.degreeSlider.value() * np.pi / 180) / np.cos(thetazegond)) * np.cos(
                        omega1 - thetazegond))
                theta2_1type2 = np.arccos(
                    (np.cos(self.degreeSlider.value() * np.pi / 180) / np.cos(thetazegond)) * np.cos(
                        omega1 + thetazegond))
            elif self.degreeSlider.value() == 90:
                theta1_1type2 = np.arccos(np.sin(omega1) * np.cos(phi))
                theta2_1type2 = np.arccos(-np.sin(omega1) * np.cos(phi))

            # n1 and n2 is polarization refractive index in ellipsoid
            n1_1type2 = (nx1type2 * nz1type2) / (np.sqrt(
                nz1type2 ** 2 * np.cos((theta1_1type2 + theta2_1type2) / 2) ** 2 + nx1type2 ** 2 * np.sin(
                    (theta1_1type2 + theta2_1type2) / 2) ** 2))
            n2_1type2 = (nx1type2 * nz1type2) / (np.sqrt(
                nz1type2 ** 2 * np.cos((theta1_1type2 - theta2_1type2) / 2) ** 2 + nx1type2 ** 2 * np.sin(
                    (theta1_1type2 - theta2_1type2) / 2) ** 2))
            if n1_1type2 > n2_1type2:
                n_1fast = n2_1type2
            else:
                n_1fast = n1_1type2
            # //////////////////////////////////////////////////////////////////////////////////////////////////
            nx2type2 = np.sqrt(
                3.29100 + (0.04140 / (landa2type2 ** 2 - 0.03978)) + (9.35522 / (landa2type2 ** 2 - 31.45571)))
            ny2type2 = np.sqrt(
                3.45018 + (0.04341 / (landa2type2 ** 2 - 0.04597)) + (16.98825 / (landa2type2 ** 2 - 39.43799)))
            nz2type2 = np.sqrt(
                4.59423 + (0.06206 / (landa2type2 ** 2 - 0.04763)) + (110.80672 / (landa2type2 ** 2 - 86.12171)))
            # omega2 is omega for refractive index og landa2 and omega is angle between z and optic axis
            omega2 = np.arcsin(
                (nz2type2 / ny2type2) * np.sqrt((ny2type2 ** 2 - nx2type2 ** 2) / (nz2type2 ** 2 - nx2type2 ** 2)))
            if self.degreeSlider.value() > 90:
                thetazegond = -np.arctan(np.tan(self.degreeSlider.value() * np.pi / 180) * np.cos(phi))
                # theta1 is angle between k and c1(first optic axis) and theta2 is angle between k and c2
                # optic axis move with wavelength in the other hand is wavelength dependent
                theta1_2type2 = np.arccos(
                    (np.cos(self.degreeSlider.value() * np.pi / 180) / np.cos(thetazegond)) * np.cos(
                        omega2 - thetazegond))
                theta2_2type2 = np.arccos(
                    (np.cos(self.degreeSlider.value() * np.pi / 180) / np.cos(thetazegond)) * np.cos(
                        omega2 + thetazegond))
            elif self.degreeSlider.value() < 90:
                thetazegond = np.arctan(np.tan(self.degreeSlider.value() * np.pi / 180) * np.cos(phi))

                theta1_2type2 = np.arccos(
                    (np.cos(self.degreeSlider.value() * np.pi / 180) / np.cos(thetazegond)) * np.cos(
                        omega2 - thetazegond))
                theta2_2type2 = np.arccos(
                    (np.cos(self.degreeSlider.value() * np.pi / 180) / np.cos(thetazegond)) * np.cos(
                        omega2 + thetazegond))
            elif self.degreeSlider.value() == 90:
                theta1_2type2 = np.arccos(np.sin(omega2) * np.cos(phi))
                theta2_2type2 = np.arccos(-np.sin(omega2) * np.cos(phi))

                # n1 and n2 is polarization refractive index in ellipsoid
                # first number is refractive index of polarization and second number is for landa2
            n1_2type2 = (nx2type2 * nz2type2) / (np.sqrt(
                nz2type2 ** 2 * np.cos((theta1_2type2 + theta2_2type2) / 2) ** 2 + nx2type2 ** 2 * np.sin(
                    (theta1_2type2 + theta2_2type2) / 2) ** 2))
            n2_2type2 = (nx2type2 * nz2type2) / (np.sqrt(
                nz2type2 ** 2 * np.cos((theta1_2type2 - theta2_2type2) / 2) ** 2 + nx2type2 ** 2 * np.sin(
                    (theta1_2type2 - theta2_2type2) / 2) ** 2))
            if n1_2type2 > n2_2type2:
                n_2slow = n1_2type2
            else:
                n_2slow = n2_2type2

            eq1type2 = (1 / self.landapump) - ((1 / landa1type2) + (1 / landa2type2))
            eq2type2 = (npumpfast / self.landapump) - ((n_1fast / landa1type2) + (n_2slow / landa2type2))
            return [eq1type2, eq2type2]

        initial_guess = [1.5, 0.43]
        initial_guesstype2 = [1.5, 0.43]

        bounds_type1 = ([0.430, 0.430], [3.54, 3.54])
        bounds_type2 = ([0.430, 0.430], [3.54, 3.54])

        for phi in phi_values:
            #image of k in xz plane is k2 and theatzegond is angle between z and k2
            if self.degreeSlider.value()>90:
                thetazegond=-np.arctan(np.tan(self.degreeSlider.value()*np.pi/180)*np.cos(phi))

                # theta1 is angle between k and c1(first optic axis) and theta2 is angle between k and c2
                # optic axis move with wavelength in the other hand is wavelength dependent
                theta1pump = np.arccos(
                    (np.cos(self.degreeSlider.value() * np.pi / 180) / np.cos(thetazegond)) * np.cos(
                        omegapump - thetazegond))
                theta2pump = np.arccos(
                    (np.cos(self.degreeSlider.value() * np.pi / 180) / np.cos(thetazegond)) * np.cos(
                        omegapump + thetazegond))
            elif self.degreeSlider.value()<90:
                thetazegond = np.arctan(np.tan(self.degreeSlider.value()*np.pi/180) * np.cos(phi))
                print(f"thetazegond:{thetazegond*180/np.pi}")
                theta1pump = np.arccos(
                    (np.cos(self.degreeSlider.value() * np.pi / 180) / np.cos(thetazegond)) * np.cos(
                        omegapump - thetazegond))
                theta2pump = np.arccos(
                    (np.cos(self.degreeSlider.value() * np.pi / 180) / np.cos(thetazegond)) * np.cos(
                        omegapump + thetazegond))
            elif self.degreeSlider.value()==90:
                theta1pump = np.arccos(np.sin(omegapump)*np.cos(phi))
                theta2pump = np.arccos(-np.sin(omegapump) * np.cos(phi))

            # n1 and n2 is polarization refractive index in ellipsoid
            n1pump=(nxpump*nzpump)/(np.sqrt(nzpump**2*np.cos((theta1pump+theta2pump)/2)**2+nxpump**2*np.sin((theta1pump+theta2pump)/2)**2))
            n2pump = (nxpump * nzpump)/ (np.sqrt(
                nzpump ** 2 * np.cos((theta1pump - theta2pump) / 2) ** 2 + nxpump ** 2 * np.sin(
                    (theta1pump - theta2pump) / 2) ** 2))
            if n1pump>n2pump:
                npumpfast=n2pump
            else:
                npumpfast = n1pump

            result_type1 = least_squares(equations, initial_guess, args=(npumpfast,), bounds=bounds_type1)
            landa1type1, landa2type1 = result_type1.x
            eq1, eq2 = equations([landa1type1, landa2type1], npumpfast)
            tolerance=1e-5
            # tolerance is near zero and it means phase will be match
            if eq1 < tolerance and eq2 < tolerance:
                arrlanda1type1.append(landa1type1)
                arrlanda2type1.append(landa2type1)
            else:
                arrlanda1type1.append(np.nan)
                arrlanda2type1.append(np.nan)

            initial_guesstype2 = [landa1type1, landa2type1]
            result_type2 = least_squares(equationstype2, initial_guesstype2, args=(npumpfast,),
                                         bounds=bounds_type2)
            landa1type2, landa2type2 = result_type2.x
            eq1type2, eq2type2 = equationstype2([landa1type2, landa2type2],npumpfast)

            if eq1type2 < tolerance and eq2type2 < tolerance and landa1type2 > landa2type2:
                arrlanda1type2.append(landa1type2)
                arrlanda2type2.append(landa2type2)
            else:
                arrlanda1type2.append(np.nan)
                arrlanda2type2.append(np.nan)

        # Plotting the results
        self.ax.plot(phi_values * 180 / np.pi, arrlanda1type1, color='red', label='landa idler type1')
        self.ax.plot(phi_values * 180 / np.pi, arrlanda2type1, color='blue', label='landa signal type1')
        self.ax.plot(phi_values * 180 / np.pi, arrlanda1type2, color='green', label='landa idler type2')
        self.ax.plot(phi_values * 180 / np.pi, arrlanda2type2, color='yellow', label='landa signal type2')
        self.ax.set_xlabel('phi (degree)')
        self.ax.set_ylabel('Wavelength [µm]')
        self.ax.legend()
        self.ax.set_title(f'λpump: {self.landapump:.3f} µm')

        # Set initial zoom factor
        zoom_factor = 1.0

        def on_scroll(event):
            nonlocal zoom_factor
            # Get current axis limits
            cur_xlim = self.ax.get_xlim()
            cur_ylim = self.ax.get_ylim()

            # Determine the current position of the mouse in data coordinates
            xdata = event.xdata
            ydata = event.ydata

            # Check if zooming in or out
            if event.button == 'up':
                zoom_factor = 1.1  # Zoom in factor
            else:
                zoom_factor = 0.9  # Zoom out factor

            # Calculate the new limits based on the zoom factor
            new_width = (cur_xlim[1] - cur_xlim[0]) * zoom_factor
            new_height = (cur_ylim[1] - cur_ylim[0]) * zoom_factor

            # Calculate the new limits centered around the cursor position
            relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
            rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])

            new_xlim = [xdata - new_width * (1 - relx), xdata + new_width * relx]
            new_ylim = [ydata - new_height * (1 - rely), ydata + new_height * rely]

            # Apply the new limits
            self.ax.set_xlim(new_xlim)
            self.ax.set_ylim(new_ylim)
            self.fig.canvas.draw_idle()

        # Connect the scroll event to the function
        self.fig.canvas.mpl_connect('scroll_event', on_scroll)

        # Redraw the canvas
        self.canvas.draw()

        # Refresh hover functionality
        cursor = mplcursors.cursor(self.ax, hover=True)

        # Set the subtitle of the chart
        self.fig.suptitle("the values are for comparison between a couple of landa pump if you dont want it right click on it", fontsize=10, color='gray',y="0.03")

        @cursor.connect("add")
        def on_add(sel):

            sel.annotation.set(text=f"Φ: {sel.target[0]:.2f}\nλ[µm]: {sel.target[1]:.3f}")

class LBOSPDC(QMainWindow, Ui_MainWindow_LBO_SPDC):

    def __init__(self):
        super(LBOSPDC, self).__init__()

        # Setup the UI
        self.setupUi(self)

        # Find the QVBoxLayout with the name 'placeholderMatplotlib'
        self.matplotlibplaceholder = self.findChild(QWidget, 'matplotlib')

        # Find the QLineEdit widget and connect it to a method
        self.lineEditLandapump = self.findChild(QWidget, 'landapump')

        self.horizontalSliderTempreture()
        self.degreeNumber.display(20)

        # Default value for landapump
        self.landapump = 0.532
        # Initialize QLabel to None; it will be created dynamically

        self.labelErr = 1
        self.lineEditLandapump.setText('532')
        self.add_text()
        self.button.clicked.connect(self.calculationCPM)
        self.button_2.clicked.connect(self.calculationNCPM)

        #change combobox
        self.comboChange()
        # Initialize plot
        self.mathPlotLib()

    def calculationCPM(self):
        try:
            self.label.hide()
            del self.label
            self.labelErr = 1
            self.add_text()
            # Update landapump based on the input from QLineEdit
            self.landapump = float(self.lineEditLandapump.text()) * 0.001
            if self.landapump < 0.16 or self.landapump > 1.064:
                self.labelErr = 0
                self.add_text()
                self.lineEditLandapump.setText('532')
                self.landapump = float(self.lineEditLandapump.text()) * 0.001
        except ValueError:
            self.labelErr = 0
            self.add_text()
            # Fallback in case of invalid input
            self.lineEditLandapump.setText('532')
            self.landapump = float(self.lineEditLandapump.text()) * 0.001

        # Update the plot with new landapump value
        self.mathPlotLib()

    def calculationNCPM(self):
        try:
            self.label.hide()
            del self.label
            self.labelErr = 1
            self.add_text()
            # Update landapump based on the input from QLineEdit
            self.landapump = float(self.lineEditLandapump.text()) * 0.001
            if self.landapump < 0.16 or self.landapump > 1.064:
                self.labelErr = 0
                self.add_text()
                self.lineEditLandapump.setText('532')
                self.landapump = float(self.lineEditLandapump.text()) * 0.001
        except ValueError:
            self.labelErr = 0
            self.add_text()
            # Fallback in case of invalid input
            self.lineEditLandapump.setText('532')
            self.landapump = float(self.lineEditLandapump.text()) * 0.001

        # Update the plot with new landapump value
        self.mathPlotLibNCPM()

    def comboChange(self):
        self.crystal.currentIndexChanged.connect(self.on_combo_box_changed)

    def on_combo_box_changed(self, index):
        # Access the selected item or text when the combo box value changes
        global selected_crystal
        selected_crystal = self.crystal.itemText(index)
        print(selected_crystal)
        self.combocheck()

    def combocheck(self):
        if selected_crystal == "BBO":
            self.gotoscreenBBOSPDC()
        elif selected_crystal == "PPLN":
            self.gotoscreenPPLNSPDC()
        elif selected_crystal == "KTP":
            self.gotoscreenLBOSPDC()
        elif selected_crystal == "PPLN:MgO":
            self.gotoscreenPPLNMgOSPDC()
        elif selected_crystal == "LBO":
            print("LBO")
        elif selected_crystal == "PPKTP":
            self.gotoscreenPPKTPSPDC()
        elif selected_crystal == "LiNbO3":
            self.gotoscreenLiNbO3SPDC()

    def gotoscreenBBOSPDC(self):
        bbospdc = BBOSPDC()
        widget.addWidget(bbospdc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoscreenPPLNSPDC(self):
        pplnspdc = PPLNSPDC()
        widget.addWidget(pplnspdc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoscreenPPLNMgOSPDC(self):
        pplnmgospdc = PPLNMGOSPDC()
        widget.addWidget(pplnmgospdc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoscreenLiNbO3SPDC(self):
        linbo3spdc = LiNbO3SPDC()
        widget.addWidget(linbo3spdc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoscreenKTPSPDC(self):
        ktpspdc = KTPSPDC()
        widget.addWidget(ktpspdc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoscreenPPKTPSPDC(self):
        ppktpspdc = PPKTPSPDC()
        widget.addWidget(ppktpspdc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def add_text(self):
        # Dynamically create the QLabel and add text to it
        #self.labelErr for zero means  error and 1 means empty error
        if self.labelErr == 0:
            self.label = QLabel(self)
            self.label.setText("Please Enter a number from 160 _ 1064")
            self.label.setObjectName('labelError')
            self.label.move(110, 390)  # Position the text at (110, 390)
            self.label.setStyleSheet("color: red;")  # Set the text color to red
            self.label.adjustSize()  # Adjust the size to fit the text
            self.label.show()  # Show the label

        # If you want to update the text dynamically:
        else:
            self.label = QLabel(self)
            self.label.setText("")
            self.label.adjustSize()
            self.label.show()  # Show the label

    def horizontalSliderTempreture(self):
        self.degreeSlider.setMinimum(20)
        self.degreeSlider.setMaximum(450)

        # Set initial value
        self.degreeSlider.setValue(20)

        # Connect the slider to a function
        self.degreeSlider.valueChanged.connect(self.onSliderTempretureChange)


    def onSliderTempretureChange(self, value):
        # Update the label text when the slider value changes
        self.degreeNumber.display(value)

    def mathPlotLib(self):
        # Set initial range as disabled
        if not self.degreeSlider.isEnabled():
            # If the slider is disabled, enable it and perform your action
            self.degreeSlider.setEnabled(True)
            self.horizontalSliderTempreture()
        # Check if the figure and axes already exist
        if not hasattr(self, 'fig') or not self.fig:
            # Create the figure and axes if they don't exist
            self.fig, self.ax = plt.subplots(figsize=(8, 6))
            self.canvas = FigureCanvas(self.fig)
            layout = QVBoxLayout(self.matplotlibplaceholder)
            layout.addWidget(self.canvas)
            central_widget = QWidget(self)
            central_widget.setLayout(layout)
            central_widget.setGeometry(370, 60, 850, 650)
        else:
            # Clear the existing axes to update the plot
            self.ax.clear()
            # Refresh hover functionality
            global cursor

        # Theta values in radians
        phi_values = np.linspace(0, 90, 400) * (np.pi / 180)
        # n fast means lower refractive index that is for n pump to phase match
        #biaxial crystal have three refractive index and two for polarization in ellipsoid
        nxpump = np.sqrt(2.4542 + (0.01125 / (self.landapump ** 2 - 0.01135)) - (0.01388*self.landapump**2))+((-3.76*self.landapump+2.3)*1e-6*((self.degreeSlider.value()-20)+(29.13*1e-3*(self.degreeSlider.value()-20)**2)))
        nypump = np.sqrt(2.5390 + (0.01277 / (self.landapump ** 2 - 0.01189)) - (0.01848*self.landapump**2))+((6.01*self.landapump-19.4)*1e-6*((self.degreeSlider.value()-20)+(32.89*1e-4*(self.degreeSlider.value()-20)**2)))
        nzpump = np.sqrt(2.5865 + (0.01310 / (self.landapump ** 2 - 0.01223)) - (0.01861*self.landapump**2))+((1.50*self.landapump-9.7)*1e-6*((self.degreeSlider.value()-20)+(74.49*1e-4*(self.degreeSlider.value()-20)**2)))
        #omegapump is omega for refractive index og pump and omega is angle between z and optic axis
        omegapump = np.arcsin((nzpump/nypump)*np.sqrt((nypump**2-nxpump**2)/(nzpump**2-nxpump**2)))
        # Arrays to store solutions
        arrlanda1type1 = []
        arrlanda2type1 = []
        arrlanda3type1 = []
        arrlanda4type1 = []

        def equations(vars, npumpfast):
            landa1type1, landa2type1,landa3type1, landa4type1 = vars
            nx1type1 = np.sqrt(2.4542 + (0.01125 / (landa1type1 ** 2 - 0.01135)) - (0.01388*landa1type1**2))+((-3.76*landa1type1+2.3)*1e-6*((self.degreeSlider.value()-20)+(29.13*1e-3*(self.degreeSlider.value()-20)**2)))
            ny1type1 = np.sqrt(2.5390 + (0.01277 / (landa1type1 ** 2 - 0.01189)) - (0.01848*landa1type1**2))+((6.01*landa1type1-19.4)*1e-6*((self.degreeSlider.value()-20)+(32.89*1e-4*(self.degreeSlider.value()-20)**2)))
            nz1type1 = np.sqrt(2.5865 + (0.01310 / (landa1type1 ** 2 - 0.01223)) - (0.01861*landa1type1**2))+((1.50*landa1type1-9.7)*1e-6*((self.degreeSlider.value()-20)+(74.49*1e-4*(self.degreeSlider.value()-20)**2)))

            # omegapump is omega for refractive index og pump and omega is angle between z and optic axis
            omega1 = np.arcsin(
                (nz1type1 / ny1type1) * np.sqrt((ny1type1 ** 2 - nx1type1 ** 2) / (nz1type1 ** 2 - nx1type1 ** 2)))

            theta1_1type1 = np.arccos(np.sin(omega1) * np.cos(phi))
            theta2_1type1 = np.arccos(-np.sin(omega1) * np.cos(phi))


            # n1 and n2 is polarization refractive index in ellipsoid
            n1_1type1 = (nx1type1 * nz1type1) / (np.sqrt(
                nz1type1 ** 2 * np.cos((theta1_1type1 + theta2_1type1) / 2) ** 2 + nx1type1 ** 2 * np.sin(
                    (theta1_1type1 + theta2_1type1) / 2) ** 2))
            n2_1type1 = (nx1type1 * nz1type1) / (np.sqrt(
                nz1type1 ** 2 * np.cos((theta1_1type1 - theta2_1type1) / 2) ** 2 + nx1type1 ** 2 * np.sin(
                    (theta1_1type1 - theta2_1type1) / 2) ** 2))
            if n1_1type1 > n2_1type1:
                n_1slow = n1_1type1
            else:
                n_1slow = n2_1type1
            nx3type1 = np.sqrt(2.4542 + (0.01125 / (landa3type1 ** 2 - 0.01135)) - (0.01388 * landa3type1 ** 2)) +((-3.76*landa3type1+2.3)*1e-6*((self.degreeSlider.value()-20)+(29.13*1e-3*(self.degreeSlider.value()-20)**2)))
            ny3type1 = np.sqrt(2.5390 + (0.01277 / (landa3type1 ** 2 - 0.01189)) - (0.01848 * landa3type1 ** 2)) +((6.01*landa3type1-19.4)*1e-6*((self.degreeSlider.value()-20)+(32.89*1e-4*(self.degreeSlider.value()-20)**2)))
            nz3type1 = np.sqrt(2.5865 + (0.01310 / (landa3type1 ** 2 - 0.01223)) - (0.01861 * landa3type1 ** 2)) +((1.50*landa3type1-9.7)*1e-6*((self.degreeSlider.value()-20)+(74.49*1e-4*(self.degreeSlider.value()-20)**2)))
            # omegapump is omega for refractive index og pump and omega is angle between z and optic axis
            omega3 = np.arcsin(
                (nz3type1 / ny3type1) * np.sqrt((ny3type1 ** 2 - nx3type1 ** 2) / (nz3type1 ** 2 - nx3type1 ** 2)))
            theta1_3type1 = np.arccos(np.sin(omega3) * np.cos(phi))
            theta2_3type1 = np.arccos(-np.sin(omega3) * np.cos(phi))
            # n1 and n2 is polarization refractive index in ellipsoid
            n1_3type1 = (nx3type1 * nz3type1) / (np.sqrt(
                nz3type1 ** 2 * np.cos((theta1_3type1 + theta2_3type1) / 2) ** 2 + nx3type1 ** 2 * np.sin(
                    (theta1_3type1 + theta2_3type1) / 2) ** 2))
            n2_3type1 = (nx3type1 * nz3type1) / (np.sqrt(
                nz3type1 ** 2 * np.cos((theta1_3type1 - theta2_3type1) / 2) ** 2 + nx3type1 ** 2 * np.sin(
                    (theta1_3type1 - theta2_3type1) / 2) ** 2))
            if n1_3type1 > n2_3type1:
                n_3slow = n1_3type1
            else:
                n_3slow = n2_3type1
            # //////////////////////////////////////////////////////////////////////////////////////////////////
            nx2type1 = np.sqrt(2.4542 + (0.01125 / (landa2type1 ** 2 - 0.01135)) - (0.01388 * landa2type1 ** 2)) +((-3.76*landa2type1+2.3)*1e-6*((self.degreeSlider.value()-20)+(29.13*1e-3*(self.degreeSlider.value()-20)**2)))
            ny2type1 = np.sqrt(2.5390 + (0.01277 / (landa2type1 ** 2 - 0.01189)) - (0.01848 * landa2type1 ** 2)) +((6.01*landa2type1-19.4)*1e-6*((self.degreeSlider.value()-20)+(32.89*1e-4*(self.degreeSlider.value()-20)**2)))
            nz2type1 = np.sqrt(2.5865 + (0.01310 / (landa2type1 ** 2 - 0.01223)) - (0.01861 * landa2type1 ** 2)) +((1.50*landa2type1-9.7)*1e-6*((self.degreeSlider.value()-20)+(74.49*1e-4*(self.degreeSlider.value()-20)**2)))
            # omega2 is omega for refractive index og landa2 and omega is angle between z and optic axis
            omega2 = np.arcsin(
                (nz2type1 / ny2type1) * np.sqrt((ny2type1 ** 2 - nx2type1 ** 2) / (nz2type1 ** 2 - nx2type1 ** 2)))
            theta1_2type1 = np.arccos(np.sin(omega2) * np.cos(phi))
            theta2_2type1 = np.arccos(-np.sin(omega2) * np.cos(phi))
            n1_2type1 = (nx2type1 * nz2type1) / (np.sqrt(
                nz2type1 ** 2 * np.cos((theta1_2type1 + theta2_2type1) / 2) ** 2 + nx2type1 ** 2 * np.sin(
                    (theta1_2type1 + theta2_2type1) / 2) ** 2))
            n2_2type1 = (nx2type1 * nz2type1) / (np.sqrt(
                nz2type1 ** 2 * np.cos((theta1_2type1 - theta2_2type1) / 2) ** 2 + nx2type1 ** 2 * np.sin(
                    (theta1_2type1 - theta2_2type1) / 2) ** 2))
            if n1_2type1 > n2_2type1:
                n_2slow = n1_2type1
            else:
                n_2slow = n2_2type1
            nx4type1 = np.sqrt(2.4542 + (0.01125 / (landa4type1 ** 2 - 0.01135)) - (0.01388 * landa4type1 ** 2)) +((-3.76*landa4type1+2.3)*1e-6*((self.degreeSlider.value()-20)+(29.13*1e-3*(self.degreeSlider.value()-20)**2)))
            ny4type1 = np.sqrt(2.5390 + (0.01277 / (landa4type1 ** 2 - 0.01189)) - (0.01848 * landa4type1 ** 2)) +((6.01*landa4type1-19.4)*1e-6*((self.degreeSlider.value()-20)+(32.89*1e-4*(self.degreeSlider.value()-20)**2)))
            nz4type1 = np.sqrt(2.5865 + (0.01310 / (landa4type1 ** 2 - 0.01223)) - (0.01861 * landa4type1 ** 2)) +((1.50*landa4type1-9.7)*1e-6*((self.degreeSlider.value()-20)+(74.49*1e-4*(self.degreeSlider.value()-20)**2)))
            # omega2 is omega for refractive index og landa2 and omega is angle between z and optic axis
            omega4 = np.arcsin(
                (nz4type1 / ny4type1) * np.sqrt((ny4type1 ** 2 - nx4type1 ** 2) / (nz4type1 ** 2 - nx4type1 ** 2)))

            theta1_4type1 = np.arccos(np.sin(omega4) * np.cos(phi))
            theta2_4type1 = np.arccos(-np.sin(omega4) * np.cos(phi))
                # n1 and n2 is polarization refractive index in ellipsoid
                #first number is refractive index of polarization and second number is for landa2
            n1_4type1 = (nx4type1 * nz4type1) / (np.sqrt(
                nz4type1 ** 2 * np.cos((theta1_4type1 + theta2_4type1) / 2) ** 2 + nx4type1 ** 2 * np.sin(
                    (theta1_4type1 + theta2_4type1) / 2) ** 2))
            n2_4type1 = (nx4type1 * nz4type1) / (np.sqrt(
                nz4type1 ** 2 * np.cos((theta1_4type1 - theta2_4type1) / 2) ** 2 + nx4type1 ** 2 * np.sin(
                    (theta1_4type1 - theta2_4type1) / 2) ** 2))
            if n1_4type1 > n2_4type1:
                n_4slow = n1_4type1
            else:
                n_4slow = n2_4type1

            eq1 = (1 / self.landapump) - ((1 / landa1type1) + (1 / landa2type1))
            eq2 = (npumpfast / self.landapump) - ((n_1slow / landa1type1) + (n_2slow / landa2type1))
            eq3 = (1 / self.landapump) - ((1 / landa3type1) + (1 / landa4type1))
            eq4 = (npumpfast / self.landapump) - ((n_3slow / landa3type1) + (n_4slow / landa4type1))
            return [eq1, eq2, eq3, eq4]

        initial_guess = [1.5,0.4,2.5, 0.3]
        bounds_type1 = ([0.16, 0.16,0.16, 0.16], [2.6, 2.6,2.6, 2.6])

        for phi in phi_values:
            theta1pump = np.arccos(np.sin(omegapump)*np.cos(phi))
            theta2pump = np.arccos(-np.sin(omegapump) * np.cos(phi))

            # n1 and n2 is polarization refractive index in ellipsoid
            n1pump=(nxpump*nzpump)/(np.sqrt(nzpump**2*np.cos((theta1pump+theta2pump)/2)**2+nxpump**2*np.sin((theta1pump+theta2pump)/2)**2))
            n2pump = (nxpump * nzpump)/ (np.sqrt(
                nzpump ** 2 * np.cos((theta1pump - theta2pump) / 2) ** 2 + nxpump ** 2 * np.sin(
                    (theta1pump - theta2pump) / 2) ** 2))
            if n1pump>n2pump:
                npumpfast=n2pump
            else:
                npumpfast = n1pump

            result_type1 = least_squares(equations, initial_guess, args=(npumpfast,), bounds=bounds_type1)
            landa1type1, landa2type1, landa3type1, landa4type1 = result_type1.x
            eq1, eq2, eq3, eq4 = equations([landa1type1, landa2type1,landa3type1, landa4type1], npumpfast)
            tolerance=1e-5
            if eq1 < tolerance and eq2 < tolerance and landa1type1 > landa2type1:
                arrlanda1type1.append(landa1type1)
                arrlanda2type1.append(landa2type1)
            else:
                arrlanda1type1.append(np.nan)
                arrlanda2type1.append(np.nan)

            if eq3 < tolerance and eq4 < tolerance and landa3type1 > landa4type1:
                arrlanda3type1.append(landa3type1)
                arrlanda4type1.append(landa4type1)
            else:
                arrlanda3type1.append(np.nan)
                arrlanda4type1.append(np.nan)

        # Plotting the results
        self.ax.plot(phi_values * 180 / np.pi, arrlanda1type1, color='red')
        self.ax.plot(phi_values * 180 / np.pi, arrlanda2type1, color='blue')
        self.ax.plot(phi_values * 180 / np.pi, arrlanda3type1, color='red', label='landa idler type1')
        self.ax.plot(phi_values * 180 / np.pi, arrlanda4type1, color='blue', label='landa signal type1')
        self.ax.set_xlabel('phi (degree)')
        self.ax.set_ylabel('Wavelength [µm]')
        self.ax.legend()
        self.ax.set_title(f'λpump: {self.landapump:.3f} µm')

        # Set initial zoom factor
        zoom_factor = 1.0

        def on_scroll(event):
            nonlocal zoom_factor
            # Get current axis limits
            cur_xlim = self.ax.get_xlim()
            cur_ylim = self.ax.get_ylim()

            # Determine the current position of the mouse in data coordinates
            xdata = event.xdata
            ydata = event.ydata

            # Check if zooming in or out
            if event.button == 'up':
                zoom_factor = 1.1  # Zoom in factor
            else:
                zoom_factor = 0.9  # Zoom out factor

            # Calculate the new limits based on the zoom factor
            new_width = (cur_xlim[1] - cur_xlim[0]) * zoom_factor
            new_height = (cur_ylim[1] - cur_ylim[0]) * zoom_factor

            # Calculate the new limits centered around the cursor position
            relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
            rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])

            new_xlim = [xdata - new_width * (1 - relx), xdata + new_width * relx]
            new_ylim = [ydata - new_height * (1 - rely), ydata + new_height * rely]

            # Apply the new limits
            self.ax.set_xlim(new_xlim)
            self.ax.set_ylim(new_ylim)
            self.fig.canvas.draw_idle()

        # Connect the scroll event to the function
        self.fig.canvas.mpl_connect('scroll_event', on_scroll)

        # Redraw the canvas
        self.canvas.draw()

        # Refresh hover functionality
        cursor = mplcursors.cursor(self.ax, hover=True)

        # Set the subtitle of the chart
        self.fig.suptitle("the values are for comparison between a couple of landa pump if you dont want it right click on it", fontsize=10, color='gray',y="0.03")

        @cursor.connect("add")
        def on_add(sel):
            sel.annotation.set(text=f"Φ: {sel.target[0]:.3f}\nλ[µm]: {sel.target[1]:.3f}")


    def mathPlotLibNCPM(self):
        # Set initial range as disabled
        self.degreeSlider.setEnabled(False)
        self.degreeNumber.display("--")
        # Check if the figure and axes already exist
        if not hasattr(self, 'fig') or not self.fig:
            # Create the figure and axes if they don't exist
            self.fig, self.ax = plt.subplots(figsize=(8, 6))
            self.canvas = FigureCanvas(self.fig)
            layout = QVBoxLayout(self.matplotlibplaceholder)
            layout.addWidget(self.canvas)
            central_widget = QWidget(self)
            central_widget.setLayout(layout)
            central_widget.setGeometry(370, 60, 850, 650)
        else:
            # Clear the existing axes to update the plot
            self.ax.clear()
            # Refresh hover functionality
            global cursor

        # Theta values in radians
        tempratures = np.linspace(20, 450, 200)

        # Arrays to store solutions
        arrlanda1type1 = []
        arrlanda2type1 = []
        arrlanda3type1 = []
        arrlanda4type1 = []

        def equations(vars, npumpfast):
            landa1type1, landa2type1,landa3type1, landa4type1 = vars
            nx1type1 = np.sqrt(2.4542 + (0.01125 / (landa1type1 ** 2 - 0.01135)) - (0.01388*landa1type1**2))+((-3.76*landa1type1+2.3)*1e-6*((temprature-20)+(29.13*1e-3*(temprature-20)**2)))
            ny1type1 = np.sqrt(2.5390 + (0.01277 / (landa1type1 ** 2 - 0.01189)) - (0.01848*landa1type1**2))+((6.01*landa1type1-19.4)*1e-6*((temprature-20)+(32.89*1e-4*(temprature-20)**2)))
            nz1type1 = np.sqrt(2.5865 + (0.01310 / (landa1type1 ** 2 - 0.01223)) - (0.01861*landa1type1**2))+((1.50*landa1type1-9.7)*1e-6*((temprature-20)+(74.49*1e-4*(temprature-20)**2)))

            # omegapump is omega for refractive index og pump and omega is angle between z and optic axis
            omega1 = np.arcsin(
                (nz1type1 / ny1type1) * np.sqrt((ny1type1 ** 2 - nx1type1 ** 2) / (nz1type1 ** 2 - nx1type1 ** 2)))

            theta1_1type1 = np.arccos(np.sin(omega1) * np.cos(0))
            theta2_1type1 = np.arccos(-np.sin(omega1) * np.cos(0))


            # n1 and n2 is polarization refractive index in ellipsoid
            n1_1type1 = (nx1type1 * nz1type1) / (np.sqrt(
                nz1type1 ** 2 * np.cos((theta1_1type1 + theta2_1type1) / 2) ** 2 + nx1type1 ** 2 * np.sin(
                    (theta1_1type1 + theta2_1type1) / 2) ** 2))
            n2_1type1 = (nx1type1 * nz1type1) / (np.sqrt(
                nz1type1 ** 2 * np.cos((theta1_1type1 - theta2_1type1) / 2) ** 2 + nx1type1 ** 2 * np.sin(
                    (theta1_1type1 - theta2_1type1) / 2) ** 2))
            if n1_1type1 > n2_1type1:
                n_1slow = n1_1type1
            else:
                n_1slow = n2_1type1
            nx3type1 = np.sqrt(2.4542 + (0.01125 / (landa3type1 ** 2 - 0.01135)) - (0.01388 * landa3type1 ** 2)) +((-3.76*landa3type1+2.3)*1e-6*((temprature-20)+(29.13*1e-3*(temprature-20)**2)))
            ny3type1 = np.sqrt(2.5390 + (0.01277 / (landa3type1 ** 2 - 0.01189)) - (0.01848 * landa3type1 ** 2)) +((6.01*landa3type1-19.4)*1e-6*((temprature-20)+(32.89*1e-4*(temprature-20)**2)))
            nz3type1 = np.sqrt(2.5865 + (0.01310 / (landa3type1 ** 2 - 0.01223)) - (0.01861 * landa3type1 ** 2)) +((1.50*landa3type1-9.7)*1e-6*((temprature-20)+(74.49*1e-4*(temprature-20)**2)))
            # omegapump is omega for refractive index og pump and omega is angle between z and optic axis
            omega3 = np.arcsin(
                (nz3type1 / ny3type1) * np.sqrt((ny3type1 ** 2 - nx3type1 ** 2) / (nz3type1 ** 2 - nx3type1 ** 2)))
            theta1_3type1 = np.arccos(np.sin(omega3) * np.cos(0))
            theta2_3type1 = np.arccos(-np.sin(omega3) * np.cos(0))
            # n1 and n2 is polarization refractive index in ellipsoid
            n1_3type1 = (nx3type1 * nz3type1) / (np.sqrt(
                nz3type1 ** 2 * np.cos((theta1_3type1 + theta2_3type1) / 2) ** 2 + nx3type1 ** 2 * np.sin(
                    (theta1_3type1 + theta2_3type1) / 2) ** 2))
            n2_3type1 = (nx3type1 * nz3type1) / (np.sqrt(
                nz3type1 ** 2 * np.cos((theta1_3type1 - theta2_3type1) / 2) ** 2 + nx3type1 ** 2 * np.sin(
                    (theta1_3type1 - theta2_3type1) / 2) ** 2))
            if n1_3type1 > n2_3type1:
                n_3slow = n1_3type1
            else:
                n_3slow = n2_3type1
            # //////////////////////////////////////////////////////////////////////////////////////////////////
            nx2type1 = np.sqrt(2.4542 + (0.01125 / (landa2type1 ** 2 - 0.01135)) - (0.01388 * landa2type1 ** 2)) +((-3.76*landa2type1+2.3)*1e-6*((temprature-20)+(29.13*1e-3*(temprature-20)**2)))
            ny2type1 = np.sqrt(2.5390 + (0.01277 / (landa2type1 ** 2 - 0.01189)) - (0.01848 * landa2type1 ** 2)) +((6.01*landa2type1-19.4)*1e-6*((temprature-20)+(32.89*1e-4*(temprature-20)**2)))
            nz2type1 = np.sqrt(2.5865 + (0.01310 / (landa2type1 ** 2 - 0.01223)) - (0.01861 * landa2type1 ** 2)) +((1.50*landa2type1-9.7)*1e-6*((temprature-20)+(74.49*1e-4*(temprature-20)**2)))
            # omega2 is omega for refractive index og landa2 and omega is angle between z and optic axis
            omega2 = np.arcsin(
                (nz2type1 / ny2type1) * np.sqrt((ny2type1 ** 2 - nx2type1 ** 2) / (nz2type1 ** 2 - nx2type1 ** 2)))
            theta1_2type1 = np.arccos(np.sin(omega2) * np.cos(0))
            theta2_2type1 = np.arccos(-np.sin(omega2) * np.cos(0))
            n1_2type1 = (nx2type1 * nz2type1) / (np.sqrt(
                nz2type1 ** 2 * np.cos((theta1_2type1 + theta2_2type1) / 2) ** 2 + nx2type1 ** 2 * np.sin(
                    (theta1_2type1 + theta2_2type1) / 2) ** 2))
            n2_2type1 = (nx2type1 * nz2type1) / (np.sqrt(
                nz2type1 ** 2 * np.cos((theta1_2type1 - theta2_2type1) / 2) ** 2 + nx2type1 ** 2 * np.sin(
                    (theta1_2type1 - theta2_2type1) / 2) ** 2))
            if n1_2type1 > n2_2type1:
                n_2slow = n1_2type1
            else:
                n_2slow = n2_2type1
            nx4type1 = np.sqrt(2.4542 + (0.01125 / (landa4type1 ** 2 - 0.01135)) - (0.01388 * landa4type1 ** 2)) +((-3.76*landa4type1+2.3)*1e-6*((temprature-20)+(29.13*1e-3*(temprature-20)**2)))
            ny4type1 = np.sqrt(2.5390 + (0.01277 / (landa4type1 ** 2 - 0.01189)) - (0.01848 * landa4type1 ** 2)) +((6.01*landa4type1-19.4)*1e-6*((temprature-20)+(32.89*1e-4*(temprature-20)**2)))
            nz4type1 = np.sqrt(2.5865 + (0.01310 / (landa4type1 ** 2 - 0.01223)) - (0.01861 * landa4type1 ** 2)) +((1.50*landa4type1-9.7)*1e-6*((temprature-20)+(74.49*1e-4*(temprature-20)**2)))
            # omega2 is omega for refractive index og landa2 and omega is angle between z and optic axis
            omega4 = np.arcsin(
                (nz4type1 / ny4type1) * np.sqrt((ny4type1 ** 2 - nx4type1 ** 2) / (nz4type1 ** 2 - nx4type1 ** 2)))

            theta1_4type1 = np.arccos(np.sin(omega4) * np.cos(0))
            theta2_4type1 = np.arccos(-np.sin(omega4) * np.cos(0))
                # n1 and n2 is polarization refractive index in ellipsoid
                #first number is refractive index of polarization and second number is for landa2
            n1_4type1 = (nx4type1 * nz4type1) / (np.sqrt(
                nz4type1 ** 2 * np.cos((theta1_4type1 + theta2_4type1) / 2) ** 2 + nx4type1 ** 2 * np.sin(
                    (theta1_4type1 + theta2_4type1) / 2) ** 2))
            n2_4type1 = (nx4type1 * nz4type1) / (np.sqrt(
                nz4type1 ** 2 * np.cos((theta1_4type1 - theta2_4type1) / 2) ** 2 + nx4type1 ** 2 * np.sin(
                    (theta1_4type1 - theta2_4type1) / 2) ** 2))
            if n1_4type1 > n2_4type1:
                n_4slow = n1_4type1
            else:
                n_4slow = n2_4type1

            eq1 = (1 / self.landapump) - ((1 / landa1type1) + (1 / landa2type1))
            eq2 = (npumpfast / self.landapump) - ((n_1slow / landa1type1) + (n_2slow / landa2type1))
            eq3 = (1 / self.landapump) - ((1 / landa3type1) + (1 / landa4type1))
            eq4 = (npumpfast / self.landapump) - ((n_3slow / landa3type1) + (n_4slow / landa4type1))
            return [eq1, eq2, eq3, eq4]

        initial_guess = [1.5, 0.4, 2.5, 0.3]
        bounds_type1 = ([0.16, 0.16, 0.16, 0.16], [2.6, 2.6, 2.6, 2.6])

        for temprature in tempratures:
            # n fast means lower refractive index that is for n pump to phase match
            # biaxial crystal have three refractive index and two for polarization in ellipsoid
            nxpump = np.sqrt(2.4542 + (0.01125 / (self.landapump ** 2 - 0.01135)) - (0.01388 * self.landapump ** 2)) + (
                        (-3.76 * self.landapump + 2.3) * 1e-6 * (
                            (temprature - 20) + (29.13 * 1e-3 * (temprature - 20) ** 2)))
            nypump = np.sqrt(2.5390 + (0.01277 / (self.landapump ** 2 - 0.01189)) - (0.01848 * self.landapump ** 2)) + (
                        (6.01 * self.landapump - 19.4) * 1e-6 * (
                            (temprature - 20) + (32.89 * 1e-4 * (temprature - 20) ** 2)))
            nzpump = np.sqrt(2.5865 + (0.01310 / (self.landapump ** 2 - 0.01223)) - (0.01861 * self.landapump ** 2)) + (
                        (1.50 * self.landapump - 9.7) * 1e-6 * (
                            (temprature - 20) + (74.49 * 1e-4 * (temprature - 20) ** 2)))
            # omegapump is omega for refractive index og pump and omega is angle between z and optic axis
            omegapump = np.arcsin(
                (nzpump / nypump) * np.sqrt((nypump ** 2 - nxpump ** 2) / (nzpump ** 2 - nxpump ** 2)))
            theta1pump = np.arccos(np.sin(omegapump)*np.cos(0))
            theta2pump = np.arccos(-np.sin(omegapump) * np.cos(0))

            # n1 and n2 is polarization refractive index in ellipsoid
            n1pump=(nxpump*nzpump)/(np.sqrt(nzpump**2*np.cos((theta1pump+theta2pump)/2)**2+nxpump**2*np.sin((theta1pump+theta2pump)/2)**2))
            n2pump = (nxpump * nzpump)/ (np.sqrt(
                nzpump ** 2 * np.cos((theta1pump - theta2pump) / 2) ** 2 + nxpump ** 2 * np.sin(
                    (theta1pump - theta2pump) / 2) ** 2))
            if n1pump>n2pump:
                npumpfast=n2pump
            else:
                npumpfast = n1pump

            result_type1 = least_squares(equations, initial_guess, args=(npumpfast,), bounds=bounds_type1)
            landa1type1, landa2type1, landa3type1, landa4type1 = result_type1.x
            eq1, eq2, eq3, eq4 = equations([landa1type1, landa2type1,landa3type1, landa4type1], npumpfast)
            tolerance=1e-6
            if eq1 < tolerance and eq2 < tolerance and landa1type1 > landa2type1:
                arrlanda1type1.append(landa1type1)
                arrlanda2type1.append(landa2type1)
            else:
                arrlanda1type1.append(np.nan)
                arrlanda2type1.append(np.nan)

            if eq3 < tolerance and eq4 < tolerance and landa3type1 > landa4type1:
                arrlanda3type1.append(landa3type1)
                arrlanda4type1.append(landa4type1)
            else:
                arrlanda3type1.append(np.nan)
                arrlanda4type1.append(np.nan)

        # Plotting the results
        self.ax.plot(tempratures, arrlanda1type1, color='red')
        self.ax.plot(tempratures, arrlanda2type1, color='blue')
        self.ax.plot(tempratures, arrlanda3type1, color='red', label='landa idler type1')
        self.ax.plot(tempratures, arrlanda4type1, color='blue', label='landa signal type1')
        self.ax.set_xlabel('T (°C)')
        self.ax.set_ylabel('Wavelength [µm]')
        self.ax.legend()
        self.ax.set_title(f'λpump: {self.landapump:.3f} µm')

        # Set initial zoom factor
        zoom_factor = 1.0

        def on_scroll(event):
            nonlocal zoom_factor
            # Get current axis limits
            cur_xlim = self.ax.get_xlim()
            cur_ylim = self.ax.get_ylim()

            # Determine the current position of the mouse in data coordinates
            xdata = event.xdata
            ydata = event.ydata

            # Check if zooming in or out
            if event.button == 'up':
                zoom_factor = 1.1  # Zoom in factor
            else:
                zoom_factor = 0.9  # Zoom out factor

            # Calculate the new limits based on the zoom factor
            new_width = (cur_xlim[1] - cur_xlim[0]) * zoom_factor
            new_height = (cur_ylim[1] - cur_ylim[0]) * zoom_factor

            # Calculate the new limits centered around the cursor position
            relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
            rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])

            new_xlim = [xdata - new_width * (1 - relx), xdata + new_width * relx]
            new_ylim = [ydata - new_height * (1 - rely), ydata + new_height * rely]

            # Apply the new limits
            self.ax.set_xlim(new_xlim)
            self.ax.set_ylim(new_ylim)
            self.fig.canvas.draw_idle()

        # Connect the scroll event to the function
        self.fig.canvas.mpl_connect('scroll_event', on_scroll)

        # Redraw the canvas
        self.canvas.draw()

        # Refresh hover functionality
        cursor = mplcursors.cursor(self.ax, hover=True)

        # Set the subtitle of the chart
        self.fig.suptitle("the values are for comparison between a couple of landa pump if you dont want it right click on it", fontsize=10, color='gray',y="0.03")

        @cursor.connect("add")
        def on_add(sel):
            sel.annotation.set(text=f"T: {sel.target[0]:.3f}\nλ[µm]: {sel.target[1]:.3f}")

class PPKTPSPDC(QMainWindow, Ui_MainWindow_PPKTP_SPDC):

    def __init__(self):
        super(PPKTPSPDC, self).__init__()

        # Setup the UI
        self.setupUi(self)

        # Find the QVBoxLayout with the name 'placeholderMatplotlib'
        self.matplotlibplaceholder = self.findChild(QWidget, 'matplotlib')

        # Find the QLineEdit widget and connect it to a method
        self.lineEditLandapump = self.findChild(QWidget, 'landapump')

        self.horizontalSliderphi()
        self.degreeNumber.display(1)

        # Default value for landapump
        self.landapump = 0.430
        # Initialize QLabel to None; it will be created dynamically
        self.graphshape.clicked.connect(self.toggleDisplay)
        self.labelErr = 1
        self.lineEditLandapump.setText('430')
        self.add_text()
        self.current_display = "matplotlib"
        self.calculation()

        #change combobox
        self.comboChange()

        # Initialize plot
        self.mathPlotLib()

    def calculation(self):
        self.calculate.clicked.connect(self.updateLandapump)

    def comboChange(self):
        self.crystal.currentIndexChanged.connect(self.on_combo_box_changed)

    def on_combo_box_changed(self, index):
        # Access the selected item or text when the combo box value changes
        global selected_crystal
        selected_crystal = self.crystal.itemText(index)
        print(selected_crystal)
        self.combocheck()

    def combocheck(self):
        if selected_crystal == "BBO":
            self.gotoscreenBBOSPDC()
        elif selected_crystal == "PPLN":
            self.gotoscreenPPLNSPDC()
        elif selected_crystal == "KTP":
            self.gotoscreenKTPSPDC()
        elif selected_crystal == "PPLN:MgO":
            self.gotoscreenPPLNMgOSPDC()
        elif selected_crystal == "LBO":
            self.gotoscreenLBOSPDC()
        elif selected_crystal == "PPKTP":
            print("PPKTP")
        elif selected_crystal == "LiNbO3":
            self.gotoscreenLiNbO3SPDC()

    def gotoscreenBBOSPDC(self):
        bbospdc = BBOSPDC()
        widget.addWidget(bbospdc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoscreenPPLNSPDC(self):
        pplnspdc = PPLNSPDC()
        widget.addWidget(pplnspdc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoscreenPPLNMgOSPDC(self):
        pplnmgospdc = PPLNMGOSPDC()
        widget.addWidget(pplnmgospdc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoscreenLiNbO3SPDC(self):
        linbo3spdc = LiNbO3SPDC()
        widget.addWidget(linbo3spdc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoscreenKTPSPDC(self):
        ktpspdc = KTPSPDC()
        widget.addWidget(ktpspdc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoscreenLBOSPDC(self):
        lbospdc = LBOSPDC()
        widget.addWidget(lbospdc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def updateLandapump(self):
        try:
            self.label.hide()
            del self.label
            self.labelErr = 1
            self.add_text()
            # Update landapump based on the input from QLineEdit
            self.landapump = float(self.lineEditLandapump.text()) * 0.001
            print(f"Updated landapump: {self.landapump}")
            if self.landapump < 0.430 or self.landapump > 1.7:
                self.labelErr = 0
                self.add_text()
                self.lineEditLandapump.setText('430')
                self.landapump = float(self.lineEditLandapump.text()) * 0.001
        except ValueError:
            self.labelErr = 0
            self.add_text()
            # Fallback in case of invalid input
            self.lineEditLandapump.setText('430')
            self.landapump = float(self.lineEditLandapump.text()) * 0.001

        # Update the plot with new landapump value
        self.mathPlotLib()

    def add_text(self):
        # Dynamically create the QLabel and add text to it
        #self.labelErr for zero means  error and 1 means empty error
        if self.labelErr == 0:
            self.label = QLabel(self)
            self.label.setText("Please Enter a number from 430 _ 1700")
            self.label.setObjectName('labelError')
            self.label.move(110, 390)  # Position the text at (110, 390)
            self.label.setStyleSheet("color: red;")  # Set the text color to red
            self.label.adjustSize()  # Adjust the size to fit the text
            self.label.show()  # Show the label

        # If you want to update the text dynamically:
        else:
            self.label = QLabel(self)
            self.label.setText("")
            self.label.adjustSize()
            self.label.show()  # Show the label

    def horizontalSliderphi(self):
        self.degreeSlider.setMinimum(0)
        self.degreeSlider.setMaximum(90)

        # Set initial value
        self.degreeSlider.setValue(1)

        # Connect the slider to a function
        self.degreeSlider.valueChanged.connect(self.onSliderphiChange)


    def onSliderphiChange(self, value):
        # Update the label text when the slider value changes
        self.degreeNumber.display(value)

    def toggleDisplay(self):
        # Check if self.matplotlibplaceholder is None
        if self.current_display == "matplotlib":
            self.shapePPLN()
            self.current_display = "image"
        else:
            # Hide or delete the shapePPLN (image placeholder)
            if hasattr(self, 'shapeplaceholder'):
                self.shapeplaceholder.hide()  # Optionally, delete if you prefer
                del self.shapeplaceholder
            self.mathPlotLib()
            self.current_display = "matplotlib"

    def shapePPLN(self):
        if self.matplotlibplaceholder is None:
            self.shapeplaceholder = QFrame(self)
            self.shapeplaceholder.setGeometry(370, 60, 850, 650)
            self.shapeplaceholder.show()  # Make sure the placeholder is visible
            # Access the current layout of the matplotlibplaceholder
        layout = self.shapeplaceholder.layout()
        if hasattr(self, 'fig'):
            self.fig.clear()
            self.canvas.close()
            del self.fig
            del self.canvas

            # If the layout does not exist, create it
        if layout is None:
            layout = QVBoxLayout(self.shapeplaceholder)
            self.shapeplaceholder.setLayout(layout)

        # Create a new label widget to display the image
        self.label = QLabel(self.shapeplaceholder)

        # Load the image using QImage
        image = QImage("PPLN1.png")

        if image.isNull():
            print("Error: The image file could not be loaded.")
            return

        # Resize the image while maintaining quality
        scaled_image = image.scaled(850, 1000, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Convert the scaled QImage to QPixmap
        scaled_pixmap = QPixmap.fromImage(scaled_image)
        # Set the pixmap to the label
        self.label.setPixmap(scaled_pixmap)

        # Resize the label to fit the image size
        self.label.resize(scaled_pixmap.width(), scaled_pixmap.height())

        # Add the label with the image to the layout
        layout.addWidget(self.label)

        # Optional: Resize the placeholder to fit the image size
        self.shapeplaceholder.resize(scaled_pixmap.width(), scaled_pixmap.height())

    def mathPlotLib(self):
        # Hide or delete the shapePPLN (image placeholder)
        if hasattr(self, 'shapeplaceholder'):
            self.shapeplaceholder.hide()  # Optionally, delete if you prefer
            del self.shapeplaceholder
        # Check if the figure and axes already exist
        if not hasattr(self, 'fig') or not self.fig:
            # Create the figure and axes if they don't exist
            self.fig, self.ax = plt.subplots(figsize=(8, 6))
            self.canvas = FigureCanvas(self.fig)
            self.matplotlib.addWidget(self.canvas)
        else:
            # Clear the existing axes to update the plot
            self.ax.clear()
            # Refresh hover functionality
            global cursor

        # Check if the figure and axes already exist
        if not hasattr(self, 'fig') or not self.fig:
            # Create the figure and axes if they don't exist
            self.fig, self.ax = plt.subplots(figsize=(8, 6))
            self.canvas = FigureCanvas(self.fig)
            layout = QVBoxLayout(self.matplotlibplaceholder)
            layout.addWidget(self.canvas)
            central_widget = QWidget(self)
            central_widget.setLayout(layout)
            central_widget.setGeometry(370, 60, 850, 650)
        else:
            # Clear the existing axes to update the plot
            self.ax.clear()
            # Refresh hover functionality
            global cursor

        # Theta values in radians
        period = np.linspace(1, 90, 280)

        # n fast means lower refractive index that is for n pump to phase match
        #biaxial crystal have three refractive index and two for polarization in ellipsoid
        nxpump = np.sqrt(3.29100 + (0.04140 / (self.landapump ** 2 - 0.03978)) + (9.35522/(self.landapump ** 2 - 31.45571)))
        nypump = np.sqrt(
                3.45018 + (0.04341 / (self.landapump ** 2 - 0.04597)) + (16.98825 / (self.landapump ** 2 - 39.43799)))
        nzpump = np.sqrt(
                4.59423 + (0.06206 / (self.landapump ** 2 - 0.04763)) + (110.80672 / (self.landapump ** 2 - 86.12171)))
        #omegapump is omega for refractive index og pump and omega is angle between z and optic axis
        omegapump = np.arcsin((nzpump/nypump)*np.sqrt((nypump**2-nxpump**2)/(nzpump**2-nxpump**2)))
        theta1pump = np.arccos(np.sin(omegapump) * np.cos(self.degreeSlider.value()* (np.pi / 180)))
        theta2pump = np.arccos(-np.sin(omegapump) * np.cos(self.degreeSlider.value()* (np.pi / 180)))

        # n1 and n2 is polarization refractive index in ellipsoid
        n1pump = (nxpump * nzpump) / (np.sqrt(
            nzpump ** 2 * np.cos((theta1pump + theta2pump) / 2) ** 2 + nxpump ** 2 * np.sin(
                (theta1pump + theta2pump) / 2) ** 2))
        n2pump = (nxpump * nzpump) / (np.sqrt(
            nzpump ** 2 * np.cos((theta1pump - theta2pump) / 2) ** 2 + nxpump ** 2 * np.sin(
                (theta1pump - theta2pump) / 2) ** 2))
        if n1pump > n2pump:
            npumpfast = n2pump
            npumpslow = n1pump
        else:
            npumpfast = n1pump
            npumpslow = n2pump

        # Arrays to store solutions
        arrlanda1type0 = []
        arrlanda2type0 = []
        arrlanda1type1 = []
        arrlanda2type1 = []
        arrlanda1type2 = []
        arrlanda2type2 = []

        def equationstype0(varstype0, npumpslow,periods):
            landa1type0, landa2type0 = varstype0
            nx1type0 = np.sqrt(
                3.29100 + (0.04140 / (landa1type0 ** 2 - 0.03978)) + (9.35522 / (landa1type0 ** 2 - 31.45571)))
            ny1type0 = np.sqrt(
                3.45018 + (0.04341 / (landa1type0 ** 2 - 0.04597)) + (16.98825 / (landa1type0 ** 2 - 39.43799)))
            nz1type0 = np.sqrt(
                4.59423 + (0.06206 / (landa1type0 ** 2 - 0.04763)) + (110.80672 / (landa1type0 ** 2 - 86.12171)))
            # omegapump is omega for refractive index og pump and omega is angle between z and optic axis
            omega1 = np.arcsin(
                (nz1type0 / ny1type0) * np.sqrt((ny1type0 ** 2 - nx1type0 ** 2) / (nz1type0 ** 2 - nx1type0 ** 2)))

            theta1_1type0 = np.arccos(np.sin(omega1) * np.cos(self.degreeSlider.value()* (np.pi / 180)))
            theta2_1type0 = np.arccos(-np.sin(omega1) * np.cos(self.degreeSlider.value()* (np.pi / 180)))

            # n1 and n2 is polarization refractive index in ellipsoid
            n1_1type0 = (nx1type0 * nz1type0) / (np.sqrt(
                nz1type0 ** 2 * np.cos((theta1_1type0 + theta2_1type0) / 2) ** 2 + nx1type0 ** 2 * np.sin(
                    (theta1_1type0 + theta2_1type0) / 2) ** 2))
            n2_1type0 = (nx1type0 * nz1type0) / (np.sqrt(
                nz1type0 ** 2 * np.cos((theta1_1type0 - theta2_1type0) / 2) ** 2 + nx1type0 ** 2 * np.sin(
                    (theta1_1type0 - theta2_1type0) / 2) ** 2))
            if n1_1type0 > n2_1type0:
                n_1slow = n1_1type0
            else:
                n_1slow = n2_1type0

            # //////////////////////////////////////////////////////////////////////////////////////////////////
            nx2type0 = np.sqrt(
                3.29100 + (0.04140 / (landa2type0 ** 2 - 0.03978)) + (9.35522 / (landa2type0 ** 2 - 31.45571)))
            ny2type0 = np.sqrt(
                3.45018 + (0.04341 / (landa2type0 ** 2 - 0.04597)) + (16.98825 / (landa2type0 ** 2 - 39.43799)))
            nz2type0 = np.sqrt(
                4.59423 + (0.06206 / (landa2type0 ** 2 - 0.04763)) + (110.80672 / (landa2type0 ** 2 - 86.12171)))
            # omega2 is omega for refractive index og landa2 and omega is angle between z and optic axis
            omega2 = np.arcsin(
                (nz2type0 / ny2type0) * np.sqrt((ny2type0 ** 2 - nx2type0 ** 2) / (nz2type0 ** 2 - nx2type0 ** 2)))

            theta1_2type0 = np.arccos(np.sin(omega2) * np.cos(self.degreeSlider.value()* (np.pi / 180)))
            theta2_2type0 = np.arccos(-np.sin(omega2) * np.cos(self.degreeSlider.value()* (np.pi / 180)))
            print(f'theta1_2type0 + theta2_2type0:{theta1_2type0 + theta2_2type0},theta1_2type0 - theta2_2type0:{theta1_2type0 - theta2_2type0}')
                # n1 and n2 is polarization refractive index in ellipsoid
                #first number is refractive index of polarization and second number is for landa2
            n1_2type0 = (nx2type0 * nz2type0) / (np.sqrt(
                nz2type0 ** 2 * np.cos((theta1_2type0 + theta2_2type0) / 2) ** 2 + nx2type0 ** 2 * np.sin(
                    (theta1_2type0 + theta2_2type0) / 2) ** 2))
            n2_2type0 = (nx2type0 * nz2type0) / (np.sqrt(
                nz2type0 ** 2 * np.cos((theta1_2type0 - theta2_2type0) / 2) ** 2 + nx2type0 ** 2 * np.sin(
                    (theta1_2type0 - theta2_2type0) / 2) ** 2))
            print(f'n1_2type0:{n1_2type0},n2_2type0:{n2_2type0}')
            if n1_2type0 > n2_2type0:
                n_2slow = n1_2type0
            else:
                n_2slow = n2_2type0

            eq1type0 = (1 / self.landapump) - ((1 / landa1type0) + (1 / landa2type0))
            eq2type0 = (npumpslow / self.landapump) - ((n_1slow / landa1type0) + (n_2slow / landa2type0)+(1/periods))
            return [eq1type0, eq2type0]


        def equations(vars, npumpfast,periods):
            landa1type1, landa2type1 = vars
            nx1type1 = np.sqrt(
                3.29100 + (0.04140 / (landa1type1 ** 2 - 0.03978)) + (9.35522 / (landa1type1 ** 2 - 31.45571)))
            ny1type1 = np.sqrt(
                3.45018 + (0.04341 / (landa1type1 ** 2 - 0.04597)) + (16.98825 / (landa1type1 ** 2 - 39.43799)))
            nz1type1 = np.sqrt(
                4.59423 + (0.06206 / (landa1type1 ** 2 - 0.04763)) + (110.80672 / (landa1type1 ** 2 - 86.12171)))
            # omegapump is omega for refractive index og pump and omega is angle between z and optic axis
            omega1 = np.arcsin(
                (nz1type1 / ny1type1) * np.sqrt((ny1type1 ** 2 - nx1type1 ** 2) / (nz1type1 ** 2 - nx1type1 ** 2)))

            theta1_1type1 = np.arccos(np.sin(omega1) * np.cos(self.degreeSlider.value()* (np.pi / 180)))
            theta2_1type1 = np.arccos(-np.sin(omega1) * np.cos(self.degreeSlider.value()* (np.pi / 180)))

            # n1 and n2 is polarization refractive index in ellipsoid
            n1_1type1 = (nx1type1 * nz1type1) / (np.sqrt(
                nz1type1 ** 2 * np.cos((theta1_1type1 + theta2_1type1) / 2) ** 2 + nx1type1 ** 2 * np.sin(
                    (theta1_1type1 + theta2_1type1) / 2) ** 2))
            n2_1type1 = (nx1type1 * nz1type1) / (np.sqrt(
                nz1type1 ** 2 * np.cos((theta1_1type1 - theta2_1type1) / 2) ** 2 + nx1type1 ** 2 * np.sin(
                    (theta1_1type1 - theta2_1type1) / 2) ** 2))
            if n1_1type1 > n2_1type1:
                n_1slow = n1_1type1
            else:
                n_1slow = n2_1type1

            # //////////////////////////////////////////////////////////////////////////////////////////////////
            nx2type1 = np.sqrt(
                3.29100 + (0.04140 / (landa2type1 ** 2 - 0.03978)) + (9.35522 / (landa2type1 ** 2 - 31.45571)))
            ny2type1 = np.sqrt(
                3.45018 + (0.04341 / (landa2type1 ** 2 - 0.04597)) + (16.98825 / (landa2type1 ** 2 - 39.43799)))
            nz2type1 = np.sqrt(
                4.59423 + (0.06206 / (landa2type1 ** 2 - 0.04763)) + (110.80672 / (landa2type1 ** 2 - 86.12171)))
            # omega2 is omega for refractive index og landa2 and omega is angle between z and optic axis
            omega2 = np.arcsin(
                (nz2type1 / ny2type1) * np.sqrt((ny2type1 ** 2 - nx2type1 ** 2) / (nz2type1 ** 2 - nx2type1 ** 2)))

            theta1_2type1 = np.arccos(np.sin(omega2) * np.cos(self.degreeSlider.value()* (np.pi / 180)))
            theta2_2type1 = np.arccos(-np.sin(omega2) * np.cos(self.degreeSlider.value()* (np.pi / 180)))

                # n1 and n2 is polarization refractive index in ellipsoid
                #first number is refractive index of polarization and second number is for landa2
            n1_2type1 = (nx2type1 * nz2type1) / (np.sqrt(
                nz2type1 ** 2 * np.cos((theta1_2type1 + theta2_2type1) / 2) ** 2 + nx2type1 ** 2 * np.sin(
                    (theta1_2type1 + theta2_2type1) / 2) ** 2))
            n2_2type1 = (nx2type1 * nz2type1) / (np.sqrt(
                nz2type1 ** 2 * np.cos((theta1_2type1 - theta2_2type1) / 2) ** 2 + nx2type1 ** 2 * np.sin(
                    (theta1_2type1 - theta2_2type1) / 2) ** 2))
            if n1_2type1 > n2_2type1:
                n_2slow = n1_2type1
            else:
                n_2slow = n2_2type1
            eq1 = (1 / self.landapump) - ((1 / landa1type1) + (1 / landa2type1))
            eq2 = (npumpfast / self.landapump) - ((n_1slow / landa1type1) + (n_2slow / landa2type1)+(1/periods))
            return [eq1, eq2]

        def equationstype2(varstype2, npumpfast,periods):
            landa1type2, landa2type2 = varstype2
            nx1type2 = np.sqrt(
                3.29100 + (0.04140 / (landa1type2 ** 2 - 0.03978)) + (9.35522 / (landa1type2 ** 2 - 31.45571)))
            ny1type2 = np.sqrt(
                3.45018 + (0.04341 / (landa1type2 ** 2 - 0.04597)) + (16.98825 / (landa1type2 ** 2 - 39.43799)))
            nz1type2 = np.sqrt(
                4.59423 + (0.06206 / (landa1type2 ** 2 - 0.04763)) + (110.80672 / (landa1type2 ** 2 - 86.12171)))
            # omegapump is omega for refractive index of pump and omega is angle between z and optic axis
            omega1 = np.arcsin(
                (nz1type2 / ny1type2) * np.sqrt((ny1type2 ** 2 - nx1type2 ** 2) / (nz1type2 ** 2 - nx1type2 ** 2)))
            theta1_1type2 = np.arccos(np.sin(omega1) * np.cos(self.degreeSlider.value()* (np.pi / 180)))
            theta2_1type2 = np.arccos(-np.sin(omega1) * np.cos(self.degreeSlider.value()* (np.pi / 180)))

            # n1 and n2 is polarization refractive index in ellipsoid
            n1_1type2 = (nx1type2 * nz1type2) / (np.sqrt(
                nz1type2 ** 2 * np.cos((theta1_1type2 + theta2_1type2) / 2) ** 2 + nx1type2 ** 2 * np.sin(
                    (theta1_1type2 + theta2_1type2) / 2) ** 2))
            n2_1type2 = (nx1type2 * nz1type2) / (np.sqrt(
                nz1type2 ** 2 * np.cos((theta1_1type2 - theta2_1type2) / 2) ** 2 + nx1type2 ** 2 * np.sin(
                    (theta1_1type2 - theta2_1type2) / 2) ** 2))
            if n1_1type2 > n2_1type2:
                n_1fast = n2_1type2
            else:
                n_1fast = n1_1type2
            # //////////////////////////////////////////////////////////////////////////////////////////////////
            nx2type2 = np.sqrt(
                3.29100 + (0.04140 / (landa2type2 ** 2 - 0.03978)) + (9.35522 / (landa2type2 ** 2 - 31.45571)))
            ny2type2 = np.sqrt(
                3.45018 + (0.04341 / (landa2type2 ** 2 - 0.04597)) + (16.98825 / (landa2type2 ** 2 - 39.43799)))
            nz2type2 = np.sqrt(
                4.59423 + (0.06206 / (landa2type2 ** 2 - 0.04763)) + (110.80672 / (landa2type2 ** 2 - 86.12171)))
            # omega2 is omega for refractive index og landa2 and omega is angle between z and optic axis
            omega2 = np.arcsin(
                (nz2type2 / ny2type2) * np.sqrt((ny2type2 ** 2 - nx2type2 ** 2) / (nz2type2 ** 2 - nx2type2 ** 2)))

            theta1_2type2 = np.arccos(np.sin(omega2) * np.cos(self.degreeSlider.value()* (np.pi / 180)))
            theta2_2type2 = np.arccos(-np.sin(omega2) * np.cos(self.degreeSlider.value()* (np.pi / 180)))

                # n1 and n2 is polarization refractive index in ellipsoid
                # first number is refractive index of polarization and second number is for landa2
            n1_2type2 = (nx2type2 * nz2type2) / (np.sqrt(
                nz2type2 ** 2 * np.cos((theta1_2type2 + theta2_2type2) / 2) ** 2 + nx2type2 ** 2 * np.sin(
                    (theta1_2type2 + theta2_2type2) / 2) ** 2))
            n2_2type2 = (nx2type2 * nz2type2) / (np.sqrt(
                nz2type2 ** 2 * np.cos((theta1_2type2 - theta2_2type2) / 2) ** 2 + nx2type2 ** 2 * np.sin(
                    (theta1_2type2 - theta2_2type2) / 2) ** 2))
            if n1_2type2 > n2_2type2:
                n_2slow = n1_2type2
            else:
                n_2slow = n2_2type2
            eq1type2 = (1 / self.landapump) - ((1 / landa1type2) + (1 / landa2type2))
            eq2type2 = (npumpfast / self.landapump) - ((n_1fast / landa1type2) + (n_2slow / landa2type2)+(1/periods))
            return [eq1type2, eq2type2]

        initial_guess = [1.5, 0.44]
        initial_guesstype2 = [1.5, 0.44]
        bounds_type0 = ([0.430, 0.430], [3.54, 3.54])
        bounds_type1 = ([0.430, 0.430], [3.54, 3.54])
        bounds_type2 = ([0.430, 0.430], [3.54, 3.54])

        for periods in period:
            # image of k in xz plane is k2 and theatzegond is angle between z and k2
            result_type0 = least_squares(equationstype0, initial_guess, args=(npumpslow, periods), bounds=bounds_type0)
            landa1type0, landa2type0 = result_type0.x
            eq1type0, eq2type0 = equationstype0([landa1type0, landa2type0], npumpslow, periods)
            tolerance = 1e-5
            if eq1type0 < tolerance and eq2type0 < tolerance:
                arrlanda1type0.append(landa1type0)
                arrlanda2type0.append(landa2type0)
            else:
                arrlanda1type0.append(np.nan)
                arrlanda2type0.append(np.nan)

            #image of k in xz plane is k2 and theatzegond is angle between z and k2
            result_type1 = least_squares(equations, initial_guess, args=(npumpfast,periods), bounds=bounds_type1)
            landa1type1, landa2type1 = result_type1.x
            eq1, eq2 = equations([landa1type1, landa2type1], npumpfast,periods)
            tolerance=1e-5
            if eq1 < tolerance and eq2 < tolerance:
                arrlanda1type1.append(landa1type1)
                arrlanda2type1.append(landa2type1)
            else:
                arrlanda1type1.append(np.nan)
                arrlanda2type1.append(np.nan)

            initial_guesstype2 = [landa1type1, landa2type1]

            result_type2 = least_squares(equationstype2, initial_guesstype2, args=(npumpfast,periods),
                                         bounds=bounds_type2)
            landa1type2, landa2type2 = result_type2.x
            eq1type2, eq2type2 = equationstype2([landa1type2, landa2type2],npumpfast,periods)

            if eq1type2 < tolerance and eq2type2 < tolerance and landa1type2 > landa2type2:
                arrlanda1type2.append(landa1type2)
                arrlanda2type2.append(landa2type2)
            else:
                arrlanda1type2.append(np.nan)
                arrlanda2type2.append(np.nan)

        # Plotting the results
        self.ax.plot(period, arrlanda1type0, color='black', label='landa idler type0')
        self.ax.plot(period, arrlanda2type0, color='yellow', label='landa signal type0')
        self.ax.plot(period, arrlanda1type1, color='red', label='landa idler type1')
        self.ax.plot(period, arrlanda2type1, color='blue', label='landa signal type1')
        self.ax.plot(period, arrlanda1type2, color='green', label='landa idler type2')
        self.ax.plot(period, arrlanda2type2, color='yellow', label='landa signal type2')
        self.ax.set_xlabel('period(µm)')
        self.ax.set_ylabel('Wavelength [µm]')
        self.ax.legend()
        self.ax.set_title(f'λpump: {self.landapump:.2f} µm')

        # Set initial zoom factor
        zoom_factor = 1.0

        def on_scroll(event):
            nonlocal zoom_factor
            # Get current axis limits
            cur_xlim = self.ax.get_xlim()
            cur_ylim = self.ax.get_ylim()

            # Determine the current position of the mouse in data coordinates
            xdata = event.xdata
            ydata = event.ydata

            # Check if zooming in or out
            if event.button == 'up':
                zoom_factor = 1.1  # Zoom in factor
            else:
                zoom_factor = 0.9  # Zoom out factor

            # Calculate the new limits based on the zoom factor
            new_width = (cur_xlim[1] - cur_xlim[0]) * zoom_factor
            new_height = (cur_ylim[1] - cur_ylim[0]) * zoom_factor

            # Calculate the new limits centered around the cursor position
            relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
            rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])

            new_xlim = [xdata - new_width * (1 - relx), xdata + new_width * relx]
            new_ylim = [ydata - new_height * (1 - rely), ydata + new_height * rely]

            # Apply the new limits
            self.ax.set_xlim(new_xlim)
            self.ax.set_ylim(new_ylim)
            self.fig.canvas.draw_idle()

        # Connect the scroll event to the function
        self.fig.canvas.mpl_connect('scroll_event', on_scroll)

        # Redraw the canvas
        self.canvas.draw()

        # Refresh hover functionality
        cursor = mplcursors.cursor(self.ax, hover=True)

        # Set the subtitle of the chart
        self.fig.suptitle("the values are for comparison between a couple of landa pump if you dont want it right click on it", fontsize=10, color='gray',y="0.03")

        @cursor.connect("add")
        def on_add(sel):
            sel.annotation.set(text=f"Λ[µm]: {sel.target[0]:.2f}\nλ[µm]: {sel.target[1]:.2f}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = QStackedWidget()
    widget.setWindowTitle("collinear Phase Matching - Matin Moeini")
    widget.setGeometry(200, 200, 1295, 773)
    window = MyMainWindow()
    widget.addWidget(window)
    widget.show()
    sys.exit(app.exec())
