from PyQt5.QtWidgets import (QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QApplication,QGridLayout,QInputDialog, QLineEdit, QFileDialog,QComboBox, QLabel, QMessageBox)
from PyQt5 import QtWidgets, QtCore
from pyqtgraph import PlotWidget, plot
from pyqtgraph.Qt import QtGui
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os
import time
from random import randint
import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtGui import QPen, QIcon, QFont

from matplotlib.colors import ListedColormap, LinearSegmentedColormap


from mprReader import mprReader_full

# UI colors
background_black = '#3B3B3B'
#widget_color = '#424242'#widget_color = '#515151'

possible_colors = ['Orange','Blue','Green','Purple','Grey','Red']

class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #3B3B3B; color=#FFFFFF; font:12pt Verdana") 
        self.loaded_files = []
        self.initUI()

    def initUI(self):
 
        # Init graph
        graph_pen = pg.mkPen('#FFFFFF',width=5)

        self.graphWidget = pg.PlotWidget()
        self.graphWidget.setBackground(background_black)

        font=QtGui.QFont()
        font.setPixelSize(16)        
        self.graphWidget.getAxis('bottom').setStyle(tickFont=font)
        self.graphWidget.getAxis('left').setStyle(tickFont=font)
        
        styles = {"color": "white", "font-size": "24px"}
        self.graphWidget.setLabel("left", "🔌 Current [μA]", **styles)
        self.graphWidget.setLabel("bottom", "⚡ Potential [V]", **styles)
        self.graphWidget.addLegend()

        #Init UI
        self.grid = QGridLayout()

        
        ### FIRST GRID ROW

        # Button to open file browser and load file
        self.load_file_button = QPushButton('🗃 Load file')
        self.load_file_button.setStyleSheet("QPushButton {background-color: #102A43;color:#FFFFFF;font:20pt Comic Sans MS;text-decoration:underline}")
        self.load_file_button.setFixedWidth(170)
        self.load_file_button.setSizePolicy(QtWidgets.QSizePolicy.Preferred,QtWidgets.QSizePolicy.Expanding)
        self.load_file_button.clicked.connect(self.open_file_dialog)
        self.grid.addWidget(self.load_file_button, 0,0,3,1)

        self.file_box = QGridLayout()

        # Support display for color selection
        file_support_display = QLabel(self)
        file_support_display.setStyleSheet('background-color: #3B3B3B; color: #FFFFFF')
        file_support_display.setFixedWidth(200)
        file_support_display.setAlignment(QtCore.Qt.AlignCenter)
        file_support_display.setText('Selected file:')
        self.file_box.addWidget(file_support_display,0,0,1,1)

        # Combo box for browsing selected files
        self.file_selector_menu = QComboBox()
        self.file_selector_menu.setStyleSheet('background-color: #424242; color: #FFFFFF')
        self.file_selector_menu.addItem("No files loaded 🦧 🐒 🦧")
        self.selected_file = 'No file loaded'
        self.file_selector_menu.currentIndexChanged.connect(self.file_selection_change)
        self.file_box.addWidget(self.file_selector_menu,0,1,1,1)

        self.grid.addLayout(self.file_box,0,1)

        # Button for decreaing n_cycles
        remove_selected_file_button = QPushButton('❌ Remove selected file')
        remove_selected_file_button.setStyleSheet('background-color: #424242; color: #FFFFFF')
        remove_selected_file_button.setToolTip('Remove currently selected file from list of loaded files.')
        remove_selected_file_button.clicked.connect(self.remove_selected_file)
        self.grid.addWidget(remove_selected_file_button, 0,2,1,1)

        # Button for decreaing n_cycles
        clear_file_list_button = QPushButton('🗑 Clear file list')
        clear_file_list_button.setStyleSheet('background-color: #424242; color: #FFFFFF')
        clear_file_list_button.setToolTip('Clear list of loaded files.')
        clear_file_list_button.clicked.connect(self.clear_file_selector_menu)
        self.grid.addWidget(clear_file_list_button, 0,3,1,1)


        ### SECOND GRID ROW

        self.n_cycles_box = QGridLayout()

        self.n_cycles_display = QLabel(self)
        #self.n_cycles_display.setAlignment(QtCore.Qt.AlignCenter)
        self.n_cycles_display.setStyleSheet('background-color: #3B3B3B; color: #FFFFFF')
        self.n_cycles_display.setText('Number of cycles: NaN')
        self.n_cycles_display.setFixedWidth(200)
        self.n_cycles_box.addWidget(self.n_cycles_display,0,1,1,1)

        # Button for entering n_cycles
        self.set_n_cycles_button = QPushButton('🔢 Enter number of cycles')
        self.set_n_cycles_button.setStyleSheet('background-color: #424242; color: #FFFFFF')
        self.set_n_cycles_button.setToolTip('Enter the number of cycles to plot.')
        self.set_n_cycles_button.clicked.connect(self.set_n_cycles)
        self.n_cycles_box.addWidget(self.set_n_cycles_button,0,2,1,1)

        # Button for increaing n_cycles
        n_cycles_up_button = QPushButton('↑')
        n_cycles_up_button.setStyleSheet('background-color: #424242; color: #FFFFFF')
        n_cycles_up_button.setMaximumWidth(35)
        n_cycles_up_button.clicked.connect(self.increase_n_cycles)
        n_cycles_up_button.setToolTip('Increment number of plotted cycles by +1.')
        self.n_cycles_box.addWidget(n_cycles_up_button,0,3,1,1)

        # Button for decreaing n_cycles
        n_cycles_down_button = QPushButton('↓')
        n_cycles_down_button.setStyleSheet('background-color: #424242; color: #FFFFFF')
        n_cycles_down_button.setMaximumWidth(35)
        n_cycles_down_button.clicked.connect(self.decrease_n_cycles)
        n_cycles_down_button.setToolTip('Increment number of plotted cycles by -1.')
        self.n_cycles_box.addWidget(n_cycles_down_button,0,4,1,1)

        self.grid.addLayout(self.n_cycles_box,1,1)

        self.color_box = QGridLayout()

        # Support display for color selection
        color_support_display = QLabel(self)
        color_support_display.setStyleSheet('background-color: #3B3B3B; color: #FFFFFF')
        color_support_display.setAlignment(QtCore.Qt.AlignCenter)
        color_support_display.setText('Selected color:')
        self.color_box.addWidget(color_support_display,0,0,1,1)

        # Combo box color browsing for selected_file
        self.color_selector_menu = QComboBox()
        pathname = os.path.dirname(sys.argv[0])
        path = os.path.abspath(pathname)
        self.color_selector_menu.setStyleSheet('background-color: #424242; color: #FFFFFF')
        self.color_selector_menu.addItem(QIcon(path+"/icons/orange_line.png"), "Orange")
        self.color_selector_menu.addItem(QIcon(path+"/icons/blue_line.png"), "Blue")
        self.color_selector_menu.addItem(QIcon(path+"/icons/green_line.png"), "Green")
        self.color_selector_menu.addItem(QIcon(path+"/icons/purple_line.png"), "Purple")
        self.color_selector_menu.addItem(QIcon(path+"/icons/grey_line.png"), "Grey")
        self.color_selector_menu.addItem(QIcon(path+"/icons/red_line.png"), "Red")
        self.color_selector_menu.currentIndexChanged.connect(self.color_selection_change)
        self.color_box.addWidget(self.color_selector_menu,0,1,1,1)

        self.grid.addLayout(self.color_box,1,3)


        ### THIRD ROW

        self.first_cycle_box = QGridLayout()
        self.first_cycle_display = QLabel(self)
        #self.first_cycle_display.setAlignment(QtCore.Qt.AlignCenter)
        self.first_cycle_display.setStyleSheet('background-color: #3B3B3B; color: #FFFFFF')
        self.first_cycle_display.setText('First cycle plotted: NaN')
        self.first_cycle_display.setFixedWidth(200)
        self.first_cycle_box.addWidget(self.first_cycle_display,0,0,1,1)

        # Button for changing first cycle plotted
        self.goto_cycle_button = QPushButton('🔍 Go to cycle')
        self.goto_cycle_button.setStyleSheet('background-color: #424242; color: #FFFFFF')
        self.goto_cycle_button.clicked.connect(self.goto_cycle)
        self.goto_cycle_button.setToolTip('Choose which cycle to start plotting from.')
        self.first_cycle_box.addWidget(self.goto_cycle_button, 0,1,1,1)

        # Button for increaing n_cycles
        first_cycle_up_button = QPushButton('↑')
        first_cycle_up_button.setStyleSheet('background-color: #424242; color: #FFFFFF')
        first_cycle_up_button.setMaximumWidth(35)
        first_cycle_up_button.setToolTip('Increment first cycle plotted by +1.')
        first_cycle_up_button.clicked.connect(self.increase_first_cycle)
        self.first_cycle_box.addWidget(first_cycle_up_button,0,3,1,1)

        # Button for decreaing n_cycles
        first_cycle_down_button = QPushButton('↓')
        first_cycle_down_button.setStyleSheet('background-color: #424242; color: #FFFFFF')
        first_cycle_down_button.setMaximumWidth(35)
        first_cycle_down_button.setToolTip('Increment first cycle plotted by -1.')
        first_cycle_down_button.clicked.connect(self.decrease_first_cycle)
        self.first_cycle_box.addWidget(first_cycle_down_button,0,4,1,1)

        # Button for 'going live'
        go_live_button = QPushButton('🐣 Go live!')
        go_live_button.setStyleSheet('background-color: #424242; color: #FFFFFF')
        go_live_button.clicked.connect(self.go_live)
        go_live_button.setToolTip('Plot the latest cycles.')
        self.first_cycle_box.addWidget(go_live_button,0,2,1,1)

        self.grid.addLayout(self.first_cycle_box,2,1)

        # Button for setting x-limit
        self.set_x_limit_button = QPushButton('🔒 Set x-limit')
        self.set_x_limit_button.setStyleSheet('background-color: #424242; color: #FFFFFF')
        self.set_x_limit_button.clicked.connect(self.set_x_lim)
        self.grid.addWidget(self.set_x_limit_button,2,2,1,1)

        # Button for autoscaling x-limit
        upper_x_limit_button = QPushButton('🔓 Autoscale')
        upper_x_limit_button.setStyleSheet('background-color: #424242; color: #FFFFFF')
        upper_x_limit_button.clicked.connect(self.autoscale_x_lim)
        self.grid.addWidget(upper_x_limit_button,2,3,1,1)

        # Test button
        test_button = QPushButton('TEST')
        test_button.setStyleSheet('background-color: #424242; color: #FFFFFF')
        test_button.clicked.connect(self.test_func)
        self.grid.addWidget(test_button,1,2,1,1)


        ### Finalize UI initialisation
        self.ui_box = QVBoxLayout()
        self.ui_box.addWidget(self.graphWidget)
        self.ui_box.addLayout(self.grid)

     
        self.setLayout(self.ui_box)

        self.setGeometry(200, 200, 800, 600)
        self.setWindowTitle('EC data live plotter')
        self.show()

        # Define timer for updating of the plot
        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)    # Plot updates once evey 1000 ms
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

    # The function responsible for updating the plot with the newest data
    # For each file:
    #   - Data is loaded
    #   - Info about the file is loaded
    #   - Data is reduced to the needed bit
    #   - New data is plotted
    #   - Legend is remade in order to fit the latest cycle numbers
    def update_plot(self):
        self.graphWidget.plotItem.legend.clear()
        for file in self.loaded_files:
            data = mprReader_full(filename=file.get_filename())
            data_lines = file.get_data_lines()
            n_cycles = file.get_n_cycles()
            colormap = file.get_colormap()
            chosen_cycle = file.get_chosen_cycle()
            try:
                cycle_max = max(data.cycle_number)
            except ValueError:
                print('Empty file loaded')
                time.sleep(2)
                continue
            if chosen_cycle=='live':
                cycle_start = cycle_max-n_cycles+1
            else:
                cycle_start = chosen_cycle
            for i, data_line in enumerate(data_lines):
                data_reduced = data.loc[data['cycle_number'] == cycle_start+i]
                pen = pg.mkPen(colormap[i],width=2)
                x = data_reduced['ewe'].array
                y = data_reduced['i'].array*1e3
                data_line.setData(x,y,pen=pen)
                self.graphWidget.plotItem.legend.addItem(data_line, file.get_label()+' cycle '+str(int(cycle_start+i))) #Remake legend

    def test_func(self):
        print(self.selected_file.used_colors)

    # ERROR POPUPS
    def invalid_file_popup(self):
    	msg = QMessageBox()
    	msg.setText("One or more of the selected files were \ninvald")
    	msg.setInformativeText("Valid files are:\n- Of the .mpr file format\n- Of CVA type\n- Not empty (15 kB files are empty)\n\nAny valid files have been loaded.")
    	msg.setWindowTitle("Invalid file")
    	msg.setStandardButtons(QMessageBox.Ok)
    	msg.setDefaultButton(QMessageBox.Ok) 
    	msg.setStyleSheet('background-color: #3B3B3B; color: #FFFFFF;min-width:280 px;font:14px Verdana')

    	retval = msg.exec_()

    def invalid_x_range_popup(self):
    	msg = QMessageBox()
    	msg.setText("Invalid entry")
    	msg.setInformativeText("Limits on a plot can only be numbers 🤪 🤪 🤪")
    	msg.setWindowTitle("Error")
    	msg.setStandardButtons(QMessageBox.Ok)
    	msg.setDefaultButton(QMessageBox.Ok) 
    	msg.setStyleSheet('background-color: #3B3B3B; color: #FFFFFF;min-width:280 px;font:14px Verdana')

    	retval = msg.exec_()

    def too_many_files_loaded(self):
    	msg = QMessageBox()
    	msg.setText("Too many files loaded")
    	msg.setInformativeText("A maximum of 5 files may be loaded at any given time. \nAny files beyond the first 5 have not been loaded.")
    	msg.setWindowTitle("File error")
    	msg.setStandardButtons(QMessageBox.Ok)
    	msg.setDefaultButton(QMessageBox.Ok) 
    	msg.setStyleSheet('background-color: #3B3B3B; color: #FFFFFF;min-width:280 px;font:14px Verdana')

    	retval = msg.exec_()

    def set_x_lim(self):
        while True:
        	try:
		        lower,ok = QInputDialog.getText(self.set_x_limit_button,"Set x-limits","Enter lower potential limit")
		        upper,ok = QInputDialog.getText(self.set_x_limit_button,"Set x-limits","Enter upper potential limit")
		        self.graphWidget.setXRange(float(lower), float(upper), padding=0)
		        break
	        except ValueError:
	        	self.invalid_x_range_popup()

    def autoscale_x_lim(self):
        self.graphWidget.enableAutoRange(axis='x')

    def goto_cycle(self):
        num,ok = QInputDialog.getInt(self.goto_cycle_button,"Choose a cycle","Enter integer > 0")
        if num > 0:
            self.selected_file.change_chosen_cycle(num)
            self.update_first_cycle_display()

    def go_live(self):
        self.selected_file.change_chosen_cycle('live')
        self.update_first_cycle_display()

    def update_first_cycle_display(self):
        if self.loaded_files != []:
            self.first_cycle_display.setText('First cycle plotted: ' + str(self.selected_file.get_chosen_cycle()))
        else:
            self.first_cycle_display.setText('First cycle plotted: NaN')

    def increase_first_cycle(self):
        self.selected_file.increase_first_cycle()
        self.update_first_cycle_display()

    def decrease_first_cycle(self):
        self.selected_file.decrease_first_cycle()
        self.update_first_cycle_display()

    # Open file selector dialogue and add selected files to loaded_files
    def open_file_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        default_dir = 'C:/Users/asibjo/Google Drive/Uni/phd/data/EC data/20_02/06'      # Change to set default directory of the Load file button
        file_name, _ = QFileDialog.getOpenFileNames(self.goto_cycle_button,
                                                    "File Browser",
                                                    default_dir,
                                                    "mpr files (*.mpr)", 
                                                    options=options)
        if file_name != []:
            for file in file_name:
    	        try:
    	        	data = mprReader_full(filename=file)
    	        	#cycle_max = max(data.cycle_number)
    	        	try:
    	        		self.loaded_files.append(EC_file(self,filename=file))
    	        	except UnboundLocalError:
    	        		self.too_many_files_loaded()
    	        except (AttributeError):
            		self.invalid_file_popup()
            self.update_file_selector_menu()

    def update_file_selector_menu(self):
        self.file_selector_menu.clear()
        menu_items = []
        if self.loaded_files != []:
            for file in self.loaded_files:
                menu_items.append(file.get_label())
            self.file_selector_menu.addItems(menu_items)
        else:
            self.file_selector_menu.addItem('No files loaded  🤔 🤔 🤔')

    def file_selection_change(self):
        current_index = self.file_selector_menu.currentIndex()
        try:
            self.selected_file = self.loaded_files[current_index]
        except IndexError:
            pass
        self.update_n_cycles_display()
        self.update_first_cycle_display()
        self.update_color_selector_menu()
        
    def update_n_cycles_display(self):
        if self.loaded_files != []:
            self.n_cycles_display.setText('Number of cycles: ' + str(self.selected_file.get_n_cycles()))
        else:
            self.n_cycles_display.setText('Number of cycles: NaN')

    def remove_selected_file(self):
        self.selected_file.used_colors.remove(self.selected_file.get_plot_color())
        for i in range(len(self.selected_file.get_data_lines())):
            self.graphWidget.removeItem(self.selected_file.get_data_lines()[0])
            self.selected_file.get_data_lines().remove(self.selected_file.get_data_lines()[0])
        self.loaded_files.remove(self.selected_file)
        self.update_file_selector_menu()

    def clear_file_selector_menu(self):
        EC_file.used_colors = []
        for file in self.loaded_files:
            for i in range(len(file.get_data_lines())):
                self.graphWidget.removeItem(file.get_data_lines()[0])
                file.get_data_lines().remove(file.get_data_lines()[0])
        self.loaded_files = []
        self.update_file_selector_menu()

    def increase_n_cycles(self):
        self.selected_file.increase_n_cycles()
        self.update_n_cycles_display()

    def decrease_n_cycles(self):
        self.selected_file.decrease_n_cycles()
        self.update_n_cycles_display()

    def set_n_cycles(self):
        num,ok = QInputDialog.getInt(self.set_n_cycles_button,"Choose cycle number","Enter integer > 0")
        if num > 0:
            self.selected_file.change_n_cycles(num)
            self.update_n_cycles_display()

    def color_selection_change(self):
        old_color = self.selected_file.get_plot_color()
        self.selected_file.used_colors.remove(old_color)
        new_color = possible_colors[self.color_selector_menu.currentIndex()]
        self.selected_file.set_plot_color(new_color)

    def update_color_selector_menu(self):
    	new_color = self.selected_file.get_plot_color()
    	index = self.color_selector_menu.findText(new_color, QtCore.Qt.MatchFixedString)
    	self.color_selector_menu.setCurrentIndex(index)
            
# The EC_file class is instantiated for every loaded file.
class EC_file():
    used_colors = []

    def __init__(self,main_plot,filename):
        self.label = filename[filename.index('EC data/'):][8:16] + ' CV_'+filename[:filename.index('_CVA')][-2:]
        self.n_cycles = 3
        self.filename = filename
        self.chosen_cycle = 'live'
        self.main_plot = main_plot
        self.data_lines = []
        self.plot_color = ''    # String value indicating the used color map

        self.remake_colormap()

        self.redraw_data_lines()
        
    def get_label(self):
        return self.label

    def get_n_cycles(self):
        return self.n_cycles

    def get_filename(self):
        return self.filename

    def get_data_lines(self):
        return self.data_lines

    def get_colormap(self):
        return self.colormap

    def get_chosen_cycle(self):
        return self.chosen_cycle

    def get_plot_color(self):
        return self.plot_color

    def increase_n_cycles(self):
        self.n_cycles+=1
        self.redraw_data_lines()
        self.remake_colormap()

    def decrease_n_cycles(self):
        self.n_cycles-=1
        self.redraw_data_lines()
        self.remake_colormap()

    def change_n_cycles(self,int):
        self.n_cycles = int
        self.redraw_data_lines()
        self.remake_colormap()

    def increase_first_cycle(self):
        self.chosen_cycle+=1
        self.redraw_data_lines()
        self.remake_colormap()

    def decrease_first_cycle(self):
        self.chosen_cycle-=1
        self.redraw_data_lines()
        self.remake_colormap()

    def change_chosen_cycle(self,num):
        self.chosen_cycle = num
        self.redraw_data_lines()
        self.remake_colormap()

    # Construct data lines for plotting
    def redraw_data_lines(self):
        if self.main_plot.loaded_files != []:
            for i in range(len(self.get_data_lines())):
                self.main_plot.graphWidget.removeItem(self.get_data_lines()[0])
                self.get_data_lines().remove(self.get_data_lines()[0])
        data = mprReader_full(filename=self.filename)
        for i in range(self.n_cycles):
            data_line = self.main_plot.graphWidget.plot([], [], name=self.label + ' cycle' + str(i))
            self.data_lines.append(data_line)

    # Construct colormap for plotting
    def remake_colormap(self, color=None):
        self.colormap = []
        if color != None:
            chosen_color_index = possible_colors.index(color)
            self.used_colors.append(color)
        elif self.plot_color != '':
            chosen_color_index = possible_colors.index(self.plot_color)
        else:
            for i,color in enumerate(possible_colors):
                if color == self.plot_color:
                    chosen_color_index = i
                    break
                if color in self.used_colors:
                    continue
                else:
                    chosen_color_index = i
                    self.used_colors.append(color)
                    self.plot_color = color
                    break
        colors = [plt.cm.Oranges(np.linspace(0.3,1,self.n_cycles))*250,plt.cm.Blues(np.linspace(0.3,1,self.n_cycles))*250,plt.cm.Greens(np.linspace(0.3,1,self.n_cycles))*250,plt.cm.Purples(np.linspace(0.3,1,self.n_cycles))*250,plt.cm.Greys(np.linspace(0.3,1,self.n_cycles))*250,plt.cm.Reds(np.linspace(0.3,1,self.n_cycles))*250]
        chosen_color = colors[chosen_color_index]
        for element in np.flipud(chosen_color):
            color_temp = element[0:3]
            self.colormap.append(color_temp)

    def set_plot_color(self,color):
        self.plot_color = color
        self.redraw_data_lines()
        self.remake_colormap(self.plot_color)

    def reset_legend(self):
        for i in range(self.n_cycles):
            self.main_plot.graphWidget.plotItem.legend.removeItem(self.get_label() + ' cycle' + str(i))


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    main_plot = MainWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()