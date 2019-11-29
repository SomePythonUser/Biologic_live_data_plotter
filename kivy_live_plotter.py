import matplotlib
matplotlib.use('module://kivy.garden.matplotlib.backend_kivy')
import matplotlib.pyplot as plt
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.config import Config
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvas
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.properties import ObjectProperty

import matplotlib.animation as animation
from mprReader import mprReader_full
import numpy as np

KV = '''
<Meta>:
    orientation: 'vertical'


<Body>:
    size_hint_y: None
    height:100
    GridLayout:
    	width: root.width
    	cols: 4
        Button:
            text: 'Choose file'
            font_size: 20
            on_press: root.show_load()
        Button:
            text: 'Plot 1 cycle'
            font_size: 20
            on_press: root.single_plot()
        Button:
            text: 'Plot n cycles (grad. colour - last black)'
            font_size: 20
            on_press: root.run_grad_plot_last_black()
        Button:
            text: 'Plot n cycles (seq. colour)'
            font_size: 20
            on_press: root.run_seq_plot()
        Button:
            text: 'Clear plot'
            font_size: 20
            on_press: root.clear_plot()
        Button:
            text: 'Plot n cycles (grad. colour)'
            font_size: 20
            on_press: root.run_grad_plot()
        Button:
            text: 'Linewidth up!'
            font_size: 20
            on_press: root.linewidth_up()
        Button:
            text: 'Linewidth down!'
            font_size: 20
            on_press: root.linewidth_down()
        Button:
            text: 'cycles up!'
            font_size: 20
            on_press: root.cycles_up()
        Button:
            text: 'cycles down!'
            font_size: 20
            on_press: root.cycles_down()

<LoadDialog>:
    BoxLayout:
        size: root.size
        pos: root.pos
        orientation: "vertical"
        FileChooserListView:
            id: filechooser
            path: "C:/Users/RDE-PC/Desktop/EC data"
            filters: ['*.mpr']
            multiselect: True

        BoxLayout:
            size_hint_y: None
            height: 30
            Button:
                text: "Cancel"
                on_release: root.cancel()

            Button:
                text: "Load"
                on_release: root.load(filechooser.path, filechooser.selection)
'''

Builder.load_string(KV)



class Graph(BoxLayout):
    def __init__(self, **kwargs):
        super(Graph, self).__init__(**kwargs)
        self.add_widget(self.graph())

    def graph(self):
        global fig1, ax, wid, file_name, line_width, n_cycles
        n_cycles = 3
        file_name = []
        fig1 = plt.figure()
        ax = fig1.add_subplot(111)
        ax.plot([],[])
        wid = FigureCanvas(fig1)
        line_width = 4
        #wid.size_hint_y=None
        #wid.height=1000
        return wid

class Body(Widget):

    def grad_plot(self, last_black):
        plt.cla()
        ax = fig1.add_subplot(111)
        if last_black == True:
            colour_maps = [plt.cm.Oranges(np.linspace(0.4,1,n_cycles-1)), plt.cm.Greens(np.linspace(0.4,1,n_cycles-1)), plt.cm.Blues(np.linspace(0.4,1,n_cycles-1)), plt.cm.Purples(np.linspace(0.4,1,n_cycles-1)), plt.cm.Greys(np.linspace(0.4,1,n_cycles-1))]
        if last_black == False:
            colour_maps = [plt.cm.Oranges(np.linspace(0.4,1,n_cycles)), plt.cm.Greens(np.linspace(0.4,1,n_cycles)), plt.cm.Blues(np.linspace(0.4,1,n_cycles)), plt.cm.Purples(np.linspace(0.4,1,n_cycles)), plt.cm.Greys(np.linspace(0.4,1,n_cycles))]
        for n_file, name in enumerate(file_name):
            label_string = "CV_"+file_name[n_file][:file_name[n_file].index("_CVA")][-2:]
            data = mprReader_full(filename=name)
            colour_array = colour_maps[n_file]
            try:
                cycle_max = max(data.cycle_number)
                data_good = True
            except ValueError:
                print("Empty file selected. Files of size 15 kB are empty!")
                data_good = False
            if data_good == True:
                cycle_start = cycle_max-n_cycles+1
                for i in range(n_cycles):
                    data_reduced = data.loc[data['cycle_number'] == cycle_start+i]
                    if i != n_cycles-1:
                        ax.plot(data_reduced['ewe'],data_reduced['i'],label=label_string+' cycle %s' %(i+int(cycle_start)),color=colour_array[i], linewidth=line_width)
                    else:
                        if last_black==True:
                            ax.plot(data_reduced['ewe'],data_reduced['i'],label=label_string+' cycle %s' %(i+int(cycle_start)),color='k', linewidth=line_width)
                        if last_black==False:
                            ax.plot(data_reduced['ewe'],data_reduced['i'],label=label_string+' cycle %s' %(i+int(cycle_start)),color=colour_array[i], linewidth=line_width)
            ax.minorticks_on()
            ax.grid(b=True, which='major', linestyle='-',linewidth=1.5)
            ax.grid(b=True, which='minor', linestyle='--')
            ax.tick_params(axis='both', which='major', labelsize=14)
            n_leg = n_cycles*len(file_name)
            if n_leg<=10:
                plt.legend(fontsize=18)
            plt.xlabel('Potential [V] vs RHE',fontsize=18,fontweight='bold')
            plt.ylabel('Current [mA]',fontsize=18,fontweight='bold')

            wid.draw()

    def single_plot(self):
        plt.cla()
        ax = fig1.add_subplot(111)
        colour_array = ['tab:red', 'tab:blue', 'tab:brown', 'tab:purple', 'tab:grey', 'tab:orange', 'tab:green', 'tab:pink', 'tab:olive', 'tab:cyan', 'k']
        for n_file, name in enumerate(file_name):
            label_string = "CV_"+file_name[n_file][:file_name[n_file].index("_CVA")][-2:]
            data = mprReader_full(filename=name)
            try:
                cycle_max = max(data.cycle_number)
                data_good = True
            except ValueError:
                print("Empty file selected. Files of size 15 kB are empty!")
                data_good = False
            if data_good == True:
                cycle_max = max(data.cycle_number)
                data_reduced = data.loc[data['cycle_number'] == cycle_max-1]
                ax.plot(data_reduced['ewe'],data_reduced['i'],label=label_string+' cycle %s' %(round(cycle_max-1)),color=colour_array[n_file], linewidth=line_width)
            ax.minorticks_on()
            ax.grid(b=True, which='major', linestyle='-',linewidth=1.5)
            ax.grid(b=True, which='minor', linestyle='--')
            ax.tick_params(axis='both', which='major', labelsize=14)
            n_leg = len(file_name)
            if n_leg<=10:
                plt.legend(fontsize=18)
            plt.xlabel('Potential [V] vs RHE',fontsize=18,fontweight='bold')
            plt.ylabel('Current [mA]',fontsize=18,fontweight='bold')

            wid.draw()

    def run_grad_plot_last_black(self, last_black=True):
        self.grad_plot(last_black=True)

    def run_grad_plot(self, last_black=False):
        self.grad_plot(last_black=False)

    def seq_plot(self):
        global cycle_max_old, n_color_start
        plt.cla()
        ax = fig1.add_subplot(111)
        for n_file, name in enumerate(file_name):
            label_string = "CV_"+file_name[n_file][:file_name[n_file].index("_CVA")][-2:]
            data = mprReader_full(filename=name)
            n_color_start = 0
            try:
            	cycle_max_old = max(data.cycle_number)
            	data_good = True
            except ValueError:
            	print("Empty file selected. Files of size 15 kB are empty!")
            	data_good = False
            if data_good == True:
                cycle_max = max(data.cycle_number)
                color_array = ['tab:red', 'tab:blue', 'tab:brown', 'tab:purple', 'tab:grey', 'tab:orange', 'tab:green', 'tab:pink', 'tab:olive', 'tab:cyan', 'k']
                cycle_start = cycle_max-n_cycles+1
                #ax.clear()
                if cycle_max != cycle_max_old:
                    n_color_start += 1
                if n_color_start > len(color_array):
                    n_color_start = 0
                n_color = n_color_start
                for i in range(n_cycles):
                    data_reduced = data.loc[data['cycle_number'] == cycle_start+i]
                    if n_color > len(color_array)-1:
                        n_color = 0
                    ax.plot(data_reduced['ewe'],data_reduced['i'],label=label_string+' cycle %s' %(i+int(cycle_start)),color=color_array[n_color], linewidth=4)
                    n_color += 1
            ax.minorticks_on()
            ax.grid(b=True, which='major', linestyle='-',linewidth=1.5)
            ax.grid(b=True, which='minor', linestyle='--')
            if n_leg<=10:
                plt.legend(fontsize=18)
            plt.xlabel('Potential [V] vs RHE',fontsize=18,fontweight='bold')
            plt.ylabel('Current [mA]',fontsize=18,fontweight='bold')
            #ax.set_title('File name: '+file_name)
            cycle_max_old = cycle_max

            wid.draw()

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self):
        ax.cla()
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filename):
        global file_name
        self.dismiss_popup()
        for file in filename:
            file_name.append("../../"+file[24:])

    def clear_plot(self):
        global file_name
        file_name = []
        ax.clear()
        wid.draw()
    
    def linewidth_up(self):
        global line_width
        line_width += 1
    
    def linewidth_down(self):
        global line_width
        line_width -= 1

    def cycles_up(self):
        global n_cycles
        n_cycles += 1

    def cycles_down(self):
        global n_cycles
        n_cycles -= 1


class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

class Meta(BoxLayout):
    def __init__(self, **kwargs):
        super(Meta, self).__init__(**kwargs)
        self.add_widget(Graph())
        self.add_widget(Body())
        
class Builder(App):
    def build(self):
        return Meta()

if __name__ == "__main__":
    Builder().run()