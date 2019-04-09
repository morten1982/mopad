import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from codeeditor import CodeeditorFrame
from dialog import OpenFileDialog, SettingsDialog, MessageDialog, SaveFileDialog
from configuration import Configuration
import keyword
import os
import gc
import webbrowser
import subprocess

class NotebookFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        try:
            self.overlord = self.parent.parent
        except:
            self.overlord = None
        
        self.filebrowserFrame = None
        
        self.initUI()
    
    def initUI(self):
        self.buttonFrame = ttk.Frame(self)
        self.initButtons()
        self.notebook = ttk.Notebook(self)
        
        self.buttonFrame.pack(side=tk.TOP, fill=tk.X)
        self.notebook.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        self.new()
    
    def initButtons(self):
        HOMEPATH = os.path.dirname(__file__) + '/'
        
        # Buttons
        newIcon = tk.PhotoImage(file=HOMEPATH + 'images/new.png')
        newButton = ttk.Button(self.buttonFrame, image=newIcon, command=self.new)
        newButton.image = newIcon
        newButton.pack(side=tk.LEFT)
        newButton_ttp = CreateToolTip(newButton, 'New')

        openIcon = tk.PhotoImage(file=HOMEPATH + 'images/open.png')
        openButton = ttk.Button(self.buttonFrame, image=openIcon, command=self.openFileDialog)
        openButton.image = openIcon
        openButton.pack(side=tk.LEFT)
        openButton_ttp = CreateToolTip(openButton, 'Open') 
        
        saveIcon = tk.PhotoImage(file=HOMEPATH + 'images/save.png')
        saveButton = ttk.Button(self.buttonFrame, image=saveIcon, command=self.save)
        saveButton.image = saveIcon
        saveButton.pack(side=tk.LEFT)
        saveButton_ttp = CreateToolTip(saveButton, 'Save')

        saveAsIcon = tk.PhotoImage(file=HOMEPATH + 'images/saveAs.png')
        saveAsButton = ttk.Button(self.buttonFrame, image=saveAsIcon, command=self.saveAs)
        saveAsButton.image = saveAsIcon
        saveAsButton.pack(side=tk.LEFT)
        saveAsButton_ttp = CreateToolTip(saveAsButton, 'Save As')

        printIcon = tk.PhotoImage(file=HOMEPATH + 'images/print.png')
        printButton = ttk.Button(self.buttonFrame, image=printIcon, command=self.printer)
        printButton.image = printIcon
        printButton.pack(side=tk.LEFT)
        printButton_ttp = CreateToolTip(printButton, "Print to HTML-File")

        undoIcon = tk.PhotoImage(file=HOMEPATH + 'images/undo.png')
        undoButton = ttk.Button(self.buttonFrame, image=undoIcon, command=self.undo)
        undoButton.image = undoIcon
        undoButton.pack(side=tk.LEFT)
        undoButton_ttp = CreateToolTip(undoButton, 'Undo')

        redoIcon = tk.PhotoImage(file=HOMEPATH + 'images/redo.png')
        redoButton = ttk.Button(self.buttonFrame, image=redoIcon, command=self.redo)
        redoButton.image = redoIcon
        redoButton.pack(side=tk.LEFT)
        redoButton_ttp = CreateToolTip(redoButton, "Redo")

        zoomInIcon = tk.PhotoImage(file=HOMEPATH + 'images/zoomIn.png')
        zoomInButton = ttk.Button(self.buttonFrame, image=zoomInIcon, command=self.zoomIn)
        zoomInButton.image = zoomInIcon
        zoomInButton.pack(side=tk.LEFT)
        zoomInButton_ttp = CreateToolTip(zoomInButton, "Zoom In")

        zoomOutIcon = tk.PhotoImage(file=HOMEPATH + 'images/zoomOut.png')
        zoomOutButton = ttk.Button(self.buttonFrame, image=zoomOutIcon, command=self.zoomOut)
        zoomOutButton.image = zoomOutIcon
        zoomOutButton.pack(side=tk.LEFT)
        zoomOutButton_ttp = CreateToolTip(zoomOutButton, "Zoom Out")

        settingsIcon = tk.PhotoImage(file=HOMEPATH + 'images/settings.png')
        settingsButton = ttk.Button(self.buttonFrame, image=settingsIcon, command=self.settings)
        settingsButton.image = settingsIcon
        settingsButton.pack(side=tk.LEFT)
        settingsButton_ttp = CreateToolTip(settingsButton, "Show Settings")

        runIcon = tk.PhotoImage(file=HOMEPATH + 'images/run.png')
        runButton = ttk.Button(self.buttonFrame, image=runIcon, command=self.run)
        runButton.image = runIcon
        runButton.pack(side=tk.RIGHT)
        runButton_ttp = CreateToolTip(runButton, "Run File")
        
        terminalIcon = tk.PhotoImage(file=HOMEPATH + 'images/terminal.png')
        terminalButton = ttk.Button(self.buttonFrame, image=terminalIcon, command=self.terminal)
        terminalButton.image = terminalIcon
        terminalButton.pack(side=tk.RIGHT)
        terminalButton_ttp = CreateToolTip(terminalButton, 'Open Terminal')

        interpreterIcon = tk.PhotoImage(file=HOMEPATH + 'images/interpreter.png')
        interpreterButton = ttk.Button(self.buttonFrame, image=interpreterIcon, command=self.interpreter)
        interpreterButton.image = interpreterIcon
        interpreterButton.pack(side=tk.RIGHT)
        interpreterButton_ttp = CreateToolTip(interpreterButton, "Open Python Interpreter")

        '''
        viewIcon = tk.PhotoImage(file=self.dir + 'images/view.png')
        viewButton = ttk.Button(self.rightBottomFrame, image=viewIcon, command=self.overview)
        viewButton.image = viewIcon
        viewButton.pack(side=tk.RIGHT)
        self.createToolTip(viewButton, 'Class Overview')
        '''
        
        searchIcon = tk.PhotoImage(file=HOMEPATH + 'images/search.png')
        searchButton = ttk.Button(self.buttonFrame, image=searchIcon, command=self.search)
        searchButton.image = searchIcon
        searchButton.pack(side=tk.RIGHT)
        searchButton_ttp = CreateToolTip(searchButton, "Search")


        self.searchBox = tk.Entry(self.buttonFrame, bg='black', fg='white')
        self.searchBox.configure(cursor="xterm green")
        self.searchBox.configure(insertbackground = "red")
        self.searchBox.configure(highlightcolor='#448dc4')

        #self.searchBox.bind('<Key>', self.OnSearchBoxChange)
        self.searchBox.bind('<Return>', self.search)
        self.searchBox.pack(side=tk.RIGHT, padx=5)
    
        
    def new(self, event=None):
        self.codeeditorFrame = CodeeditorFrame(self)
        self.notebook.add(self.codeeditorFrame, text='noname')
        self.frameName = self.notebook.select()

        self.textPad = self.codeeditorFrame.textPad
        
        self.notebook.bind("<ButtonRelease-1>", self.tabChanged)
        self.notebook.bind("<ButtonRelease-3>", self.closeContext)
        
        x = len(self.notebook.tabs()) - 1
        self.notebook.select(x)
        self.tabChanged()
    
    def open(self, filename=None, event=None):
        if not filename:
            filename = filedialog.askopenfilename()
        
            if not filename:
                return
        
        try:
            # open file for reading
            with open(filename, 'r') as f:
                text = f.read()
        
            # update textPad
            self.textPad.delete('1.0', tk.END)
            self.textPad.insert("1.0", text)
            self.textPad.filename = filename
            self.textPad.tag_all_lines()
        
        except Exception as e:
            MessageDialog(self, 'Error', '\n' + str(e) + '\n')
            return
            
        # update tab text
        file = self.textPad.filename.split('/')[-1]
        id = self.notebook.index(self.notebook.select())
        self.notebook.tab(id, text=file)
        
        # generate tabChanged event (get new textPad, etc)
        self.tabChanged()
        
        # update autocompleteList from codeeditor
        self.textPad.updateAutoCompleteList()
        self.filebrowserFrame.refreshTree()

    def openFileDialog(self):
        dialog = OpenFileDialog(parent=self.parent, notebookFrame=self, title='Open')

    def save(self, event=None):
        if not self.textPad:
            return
            
        if not self.textPad.filename:
            self.saveAs()
        
        filename = self.textPad.filename
        
        if not filename:
            return
        
        try:
            with open(filename, 'w') as f:
                text = self.textPad.get("1.0",'end-1c')
                f.write(text)
        
        except Exception as e:
            MessageDialog(self, 'Error', '\n' + str(e) + '\n')
        
        # update textPad
        self.textPad.filename = filename
        
        # update tab text
        file = self.textPad.filename.split('/')[-1]
        id = self.notebook.index(self.notebook.select())
        self.notebook.tab(id, text=file)
        
        # generate tabChanged event (get new textPad, etc)
        self.tabChanged()
        self.filebrowserFrame.refreshTree()
        
    def saveAs(self, event=None):
        dialog = SaveFileDialog(self, "Save as")
        filename = dialog.filename
        
        if not filename:
            return
        
        try:
            with open(filename, 'w') as f:
                text = self.textPad.get("1.0",'end-1c')
                f.write(text)
        
        except Exception as e:
            MessageDialog(self, 'Error', '\n' + str(e) + '\n')
        
        # update textPad
        self.textPad.filename = filename
        
        # update tab text
        file = self.textPad.filename.split('/')[-1]
        id = self.notebook.index(self.notebook.select())
        self.notebook.tab(id, text=file)
        
        # generate tabChanged event (get new textPad, etc)
        self.tabChanged()
        self.filebrowserFrame.refreshTree()

    def printer(self, event=None):
        # print file to html
        if not self.textPad:
            return
            
        if not self.textPad.filename:
            return

        text = self.textPad.get("1.0",'end-1c')
        filename = self.textPad.filename.split('/')[-1]
        kwList = keyword.kwlist
        
        output = "<head>" + filename + "</head>\n"
        output += "<body>\n"
        output += '<pre><code>\n'
        output += text + '\n'
        output += '</pre></code>\n'
        output += "</body>"

        fname = self.textPad.filename + "_.html"
        
        with open(fname, "w") as f:
            f.write(output)
        
        try:
            webbrowser.open(fname)
        
        except Exception as e:
            MessageDialog(self, 'Error', '\n' + str(e) + '\n')
            return
        
        self.filebrowserFrame.refreshTree()
        
    def undo(self, event=None):
        if self.textPad:
            self.textPad.undo()
        
    def redo(self, event=None):
        if self.textPad:
            self.textPad.redo()
        
    def zoomIn(self, event=None):
        if not self.textPad:
            return
        if self.textPad.font_size < 30:
            self.textPad.font_size += 1
            self.textPad.configFont()
            
            self.textPad.linenumber.font_size +=1
            self.textPad.linenumber.configFont()
            self.textPad.linenumber.redraw()

    def zoomOut(self, event=None):
        if not self.textPad:
            return
        if self.textPad.font_size > 5:
            self.textPad.font_size -= 1
            self.textPad.configFont()
            
            self.textPad.linenumber.font_size -=1
            self.textPad.linenumber.configFont()
            self.textPad.linenumber.redraw()

    def settings(self, event=None):
        dialog = SettingsDialog(self)

    def run(self, event=None):
        if not self.textPad:
            return
        
        filepath = self.textPad.filename
        
        if not filepath:
            return
        
        self.save()

        file = filepath.split('/')[-1]
    
        c = Configuration()     # -> in configuration.py
        system = c.getSystem()
        runCommand = c.getRun(system).format(file)

        subprocess.call(runCommand, shell=True)

    def terminal(self, event=None):
        c = Configuration()     # -> in configuration.py
        system = c.getSystem()
        terminalCommand = c.getTerminal(system)
        
        try:
            subprocess.call(terminalCommand, shell=True)
        except Exception as e:
            dialog = MessageDialog(self, 'Error', '\n' + str(e) + '\n')
            return


    def interpreter(self, event=None):
        c = Configuration()     # -> in configuration.py
        system = c.getSystem()
        interpreterCommand = c.getInterpreter(system)

        subprocess.call(interpreterCommand, shell=True)
    
    def search(self, start=None):
        if not self.textPad:
            return
            
        self.textPad.tag_remove('sel', "1.0", tk.END)
        
        toFind = self.searchBox.get()
        pos = self.textPad.index(tk.INSERT)
        result = self.textPad.search(toFind, str(pos), stopindex=tk.END)
        
        if result:
            length = len(toFind)
            row, col = result.split('.')
            end = int(col) + length
            end = row + '.' + str(end)
            self.textPad.tag_add('sel', result, end)
            self.textPad.mark_set('insert', end)
            self.textPad.see(tk.INSERT)
            self.textPad.focus_force()
        else:
            self.textPad.mark_set('insert', '1.0')
            self.textPad.see(tk.INSERT)
            self.textPad.focus()
            self.setEndMessage(400)
            self.searchBox.focus()
            return

    def setEndMessage(self, seconds):
            pathList = __file__.replace('\\', '/')
            pathList = __file__.split('/')[:-1]
        
            self.dir = ''
            for item in pathList:
                self.dir += item + '/'

            canvas = tk.Canvas(self.textPad, width=64, height=64)
            x = self.textPad.winfo_width() / 2
            y = self.textPad.winfo_height() / 2

            canvas.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            image = tk.PhotoImage(file = self.dir + 'images/last.png')
            canvas.create_image(0, 0,  anchor=tk.NW, image=image)
            
            self.textPad.update()
            self.after(seconds, self.textPad.entry.config(text='---'))
            
            canvas.destroy()
            self.textPad.update()


    def tabChanged(self, event=None):
        tabs = self.notebook.tabs()
        try:
            id = self.notebook.index(self.notebook.select())
        except:
            return 
            
        name = tabs[id]
        codeframe = self.notebook._nametowidget(name)
        
        self.textPad = codeframe.textPad
    
        self.updateMainWindow()
        self.textPad.focus()
        
    def updateMainWindow(self, event=None):
        if not self.textPad:
            return
            
        if not self.overlord:
            if self.textPad.filename:
                self.parent.title(self.textPad.filename)
            else:
                self.parent.title("MoPad - Morten's cross platform Python Pad")
        else:
            if self.textPad.filename:
                self.overlord.title(self.textPad.filename)
            else:
                self.overlord.title("MoPad - Morten's cross platform Python Pad")

        
    def closeContext(self, event=None):
        tabs = self.notebook.tabs()
        if not tabs:
            return
        
        menu = tk.Menu(self.notebook, tearoff=False, background='#000000',foreground='white',
                activebackground='blue', activeforeground='white')
        menu.add_command(label='Close', compound=tk.LEFT, command=self.closeTab)
        menu.tk_popup(event.x_root, event.y_root, 0)
        
    def closeTab(self, event=None):
        id = self.notebook.index(self.notebook.select())
        self.notebook.forget(id)
        
        try:
            x = len(self.notebook.tabs()) - 1
            self.notebook.select(x)
            self.tabChanged()
        except:
            self.textPad = None
            return
        
###################################################################
class CreateToolTip():
    """
    create a tooltip for a given widget
    -> this solution was found on stackoverlow.com :)
    """
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     # miliseconds
        self.wraplength = 180   # pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 1
        y += self.widget.winfo_rooty() + 40
        
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tw, text=self.text, justify='left',
                       background="#000000", foreground='yellow',
                       relief='solid', borderwidth=1,
                       wraplength = self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()
###################################################################


if __name__ == '__main__':
    root = tk.Tk()
    app = NotebookFrame(root)
    app.pack(fill=tk.BOTH, expand=True)
    root.mainloop()