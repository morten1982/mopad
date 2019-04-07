import tkinter as tk
from tkinter import ttk, filedialog
import platform
import os
from os.path import expanduser
import shutil
import sys
import subprocess
from configuration import Configuration
from dialog import (RenameDialog, NewDirectoryDialog,
                    InfoDialog, HelpDialog, MessageYesNoDialog, MessageDialog)


class FilebrowserFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.initUI()
        #self.initStyle()

        self.selected = []
        self.sourceItem = None
        self.destinationItem = None
        
        self.notebookFrame = None
    
    def initUI(self):
        self.config
        
        treeScrollY = ttk.Scrollbar(self, orient=tk.VERTICAL)
        treeScrollY.config(cursor="double_arrow")
        treeScrollY.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree = ttk.Treeview(self)

        self.tree.tag_configure('pythonFile', background='black', foreground='green')
        self.tree.tag_configure('row', background='black', foreground='white')
        self.tree.tag_configure('folder', background='black', foreground='yellow')
        self.tree.tag_configure('subfolder', background='black', foreground='#448dc4')
        self.tree.tag_configure('hidden', background='black', foreground='gray')
    
        self.tree['show'] = 'tree'
        self.tree.bind("<Double-1>", self.OnDoubleClickTreeview)
        self.tree.bind("<Return>", self.OnReturnTreeview)
        self.tree.bind("<Button-1>", self.OnClickTreeview)
        self.tree.bind('<<TreeviewSelect>>', self.OnSelect)
        self.tree.bind("<ButtonRelease-3>", self.treePopUp)
        #self.tree.bind("<FocusIn>", self.refreshTree)
        
        # TreeView
        path = expanduser("~")
        os.chdir(path)
        
        
        root_node = self.tree.insert('', 'end', text=path, open=True, tags='folder')
        self.process_directory(root_node, path)

        self.tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        treeScrollY.config(command=self.tree.yview)
        self.tree.configure(yscrollcommand=treeScrollY.set)
    
    def OnReturnTreeview(self, event=None):
        item = self.tree.focus()

        if self.tree.item(item, "text") == '': 

            return
        
        elif self.tree.item(item, "text").startswith('>'):
            root = os.getcwd()
            sub = self.tree.item(item, "text").split()[1]
            dir = root + sub
            dir = self.checkPath(dir)
            try:
                os.chdir(dir)
            except Exception as e:
                MessageDialog(self, 'Error', '\n' + str(e) + '\n')

            self.selected = None
            self.refreshTree()
            self.parent.title(dir)
    
        elif '/' in self.tree.item(item, "text") or '\\' in self.tree.item(item, "text"):
            os.chdir('..')
            dir = self.checkPath(os.getcwd())
            self.parent.title(dir)
            self.refreshTree()
            return 'break'

        else:
            file = self.tree.item(item,"text")
            dir = os.getcwd()
            dir = self.checkPath(dir)
            filename = dir + '/' + file
            self.tree.config(cursor="X_cursor")
            self.tree.bind('<Double-1>', self.ignore)
            
            try:
                self.notebookFrame.new()
                self.notebookFrame.open(filename)

            except Exception as e:

                MessageDialog(self, 'Error', '\n' + str(e) + '\n')
                filename = self.notebookFrame.textPad.filename = None
                self.notebookFrame.tabChanged()
                self.notebookFrame.textPad.focus()
                

            self.tree.config(cursor='')
            self.tree.update()
            self.parent.title(filename)
            
            # workaround 
            # step 2
            self.refreshTree()
            self.tree.update()
            self.tree.after(500, self.bindit)
        
        self.refreshTree()

    
    def OnDoubleClickTreeview(self, event=None):
        item = self.tree.identify('item',event.x,event.y)
        #print("you clicked on", self.tree.item(item,"text"))
        if self.tree.item(item, "text") == '': 

            return
        
        elif self.tree.item(item, "text").startswith('>'):
            root = os.getcwd()
            sub = self.tree.item(item, "text").split()[1]
            dir = root + sub
            dir = self.checkPath(dir)
            try:
                os.chdir(dir)
            except Exception as e:
                MessageDialog(self, 'Error', '\n' + str(e) + '\n')

            self.selected = None
            self.refreshTree()
            self.parent.title(dir)
    
        elif '/' in self.tree.item(item, "text") or '\\' in self.tree.item(item, "text"):
            os.chdir('..')
            dir = self.checkPath(os.getcwd())
            self.parent.title(dir)
            self.refreshTree()
            return 'break'

        else:
            file = self.tree.item(item,"text")
            dir = os.getcwd()
            dir = self.checkPath(dir)
            filename = dir + '/' + file
            self.tree.config(cursor="X_cursor")
            self.tree.bind('<Double-1>', self.ignore)
            
            try:
                self.notebookFrame.new()
                self.notebookFrame.open(filename)

            except Exception as e:

                MessageDialog(self, 'Error', '\n' + str(e) + '\n')
                filename = self.notebookFrame.textPad.filename = None
                self.notebookFrame.tabChanged()
                self.notebookFrame.textPad.focus()
                #return

            self.tree.config(cursor='')
            self.tree.update()
            #self.rightPanel.textPad.mark_set("insert", "1.0")
            self.parent.title(filename)
            #self.rightPanel.textPad.focus_set()
            
            # workaround 
            # step 2
            self.refreshTree()
            self.tree.update()
            self.tree.after(500, self.bindit)
        
        self.refreshTree()

    def ignore(self, event):
        # workaround for dismiss OnDoubleClickTreeview to open file twice 
        # step 1
        return 'break'

    def bindit(self):
        # workaround 
        # step 3
        self.tree.bind('<Double-1>', self.OnDoubleClickTreeview)

    def OnClickTreeview(self, event=None):
        item = self.tree.identify('item',event.x,event.y)
        if '/' in self.tree.item(item,"text") or '\\' in self.tree.item(item, "text"):
            self.parent.title(self.checkPath(self.tree.item(item, 'text')))
                
        else:
            dir = self.checkPath(os.getcwd())
            self.parent.title(dir + '/' + self.checkPath(self.tree.item(item, 'text')))
        #print(item)

    
    def OnSelect(self, event=None):
        self.selected = event.widget.selection()

    def checkPath(self, path):
        if '\\' in path:
            path = path.replace('\\', '/')
        return path

    def treePopUp(self, event=None):
        item = self.tree.identify('item',event.x,event.y)
        self.tree.selection_set(item)
            
        menu = tk.Menu(self, tearoff=False, background='#000000',foreground='white',
                activebackground='blue', activeforeground='white')
        menu.add_command(label='Info', compound=tk.LEFT, command=self.treeGenerateInfo)
        menu.add_separator()
        menu.add_command(label="Create New Folder", compound=tk.LEFT, command=self.treeGenerateFolder)
        menu.add_separator()
        menu.add_command(label="Copy Item", compound=tk.LEFT, command=self.treeGenerateCopy)
        menu.add_command(label="Paste Item", compound=tk.LEFT, command=self.treeGeneratePaste)
        menu.add_command(label="Rename Item", compound=tk.LEFT, command=self.treeGenerateRename)

        menu.add_separator()
        menu.add_command(label="Delete Item", compound=tk.LEFT, command=self.treeGenerateDelete)
        menu.add_separator()
        menu.add_command(label="Open Terminal", compound=tk.LEFT, command = self.treeGenerateTerminal)
        menu.tk_popup(event.x_root, event.y_root, 0)

    def treeGenerateInfo(self):
        if not self.selected:
            self.parent.title('<No Selection>')
            return
        
        self.infoFile()

    def infoFile(self):
        rootDir = self.checkPath(os.getcwd())
        #print(rootDir)
        directory = None
        file = None
        size = None
        if self.selected:
            for idx in self.selected:
                try:
                    text = self.tree.item(idx)['text']
                except:
                    self.selected = []
                    return
            if '/' in text or '\\' in text:
                directory = True
            else:
                file = True
            if file == True:
                filename = rootDir + '/' + text
                size = os.path.getsize(filename)
                size = format(size, ',d')
            else:
                filename = text
            text = self.checkPath(text)
            InfoDialog(self, title='Info', text=text, directory=directory, file=file, size=size)
        
        else:
            return

    def treeGenerateFolder(self):
        self.newFolder()
    
    def newFolder(self):
        NewDirectoryDialog(self, title='Create directory')
        self.refreshTree()

    def treeGenerateCopy(self):
        if not self.selected:
            self.parent.title('<No Selection>')
            return

        self.copyFile()

    def copyFile(self):
        if not self.selected:
            self.clipboard = ''
            return
        else:
            for idx in self.selected:
                text = self.tree.item(idx)['text']
        
        self.clipboard = text
        self.homedir = self.checkPath(os.getcwd())
        
        if self.clipboard.startswith('>'):
            dir = self.clipboard.split()[1]
            self.sourceItem = self.homedir + dir
        elif '/' in self.clipboard or '\\' in self.clipboard:
            self.sourceItem = self.homedir
        else:
            self.sourceItem = self.homedir + '/' + self.clipboard
            self.sourceItem = self.checkPath(self.sourceItem)
        
        self.selected = None
        self.parent.title(self.sourceItem + ' -> marked')

    def treeGeneratePaste(self):
        if not self.sourceItem:
            self.parent.title('<No Selection>')
            return
            
        self.pasteFile()

    def pasteFile(self):
        if not self.sourceItem:
            self.parent.title('<No Selection>')
            return
        
        if not self.selected:
            currentDirectory = self.checkPath(os.getcwd())
            self.destinationItem = currentDirectory
            
        if self.selected:
            try:
                for idx in self.selected:
                    text = self.tree.item(idx)['text']
        
            except Exception as e:
                #print('this')
                MessageDialog(self, 'Error', '\n' + str(e) + '\n')
                return
        
            currentDirectory = self.checkPath(os.getcwd())
        
            if text.startswith('>'):
                dir = text.split()[1]
                self.destinationItem = currentDirectory + dir
        
            elif '/' in text or '\\' in text:
                self.destinationItem = currentDirectory

            else:
                self.destinationItem = currentDirectory + '/' + text
        
        #print('self.sourceItem:', self.sourceItem)
        #print('self.destinationItem:', self.destinationItem)
        
        if os.path.isfile(self.sourceItem):             # Source == file
            if os.path.isdir(self.destinationItem):     # Destination == directory
                destination = self.destinationItem      

                try:
                    shutil.copy2(self.sourceItem, destination)
                    self.refreshTree()

                except Exception as e:
                    MessageDialog(self, 'Error', '\n' + str(e) + '\n')
                    return
            
            elif os.path.isfile(self.destinationItem):  # Destination == file
                destination = os.path.dirname(self.destinationItem)

                try:
                    shutil.copy2(self.sourceItem, destination)
                    self.refreshTree()

                except Exception as e:
                    MessageDialog(self, 'Error', '\n' + str(e) + '\n')
                    return

        elif os.path.isdir(self.sourceItem):            # Source == directory
            if os.path.isdir(self.destinationItem):     # Destination == directory
                destination = self.destinationItem + '/'
                basename = self.sourceItem.split('/')[-1]
                destination = destination + basename
                destination = self.checkPath(destination)
                #print('destination:', destination)

                try:
                    shutil.copytree(self.sourceItem, destination)
                    self.refreshTree()
                
                except Exception as e:
                    MessageDialog(self, 'Error', '\n' + str(e) + '\n')
                    return
            
            elif os.path.isfile(self.destinationItem):   # Destination == file
                destination = os.path.dirname(self.destinationItem) + '/'
                destination = self.checkPath(destination)
                basename = self.sourceItem.split('/')[-1]
                destination = destination + basename
                #print('destination:', destination)
                
                try:
                    shutil.copytree(self.sourceItem, destination)
                    self.refreshTree()
                    
                except Exception as e:
                    MessageDialog(self, 'Error', '\n' + str(e) + '\n')
                    return
        
        self.selected = None
        self.sourceItem = None
        
        self.parent.title('Done !')

    
    def treeGenerateDelete(self):
        if not self.selected:
            self.parent.title('<No Selection>')
            return
        
        self.deleteFile()

    def deleteFile(self):
        rootDir = self.checkPath(os.getcwd())
        directory = None
        file = None
        size = None
        
        if self.selected:
            for idx in self.selected:
                try:
                    text = self.tree.item(idx)['text']
                except:
                    self.selected = []
                    return
            
            if '/' in text or '\\' in text:
                directory = True
            else:
                file = True
            
            if file == True:
                filename = rootDir + '/' + text
            else: # directory
                if text.startswith('>'):
                    dir = text.split()[-1]
                    filename = rootDir + dir
                elif '/' in text or '\\' in text:
                    filename = text
                
        else:
            return
        
        filename = self.checkPath(filename)
        
        dialog = MessageYesNoDialog(self, 'Delete', '\n\tDelete\n\n' + filename + '  ?\n\n')
        result = dialog.result
        
        if result == 1:
            if directory:
                try:
                    shutil.rmtree(filename)
                    self.refreshTree()
                    
                except Exception as e:
                    MessageDialog(self, 'Error', '\n' + str(e) + '\n')

                    
            elif file:
                try:
                    os.remove(filename)
                    self.refreshTree()
                
                except Exception as e:
                    MessageDialog(self, 'Error', '\n' + str(e) + '\n')
            
            self.parent.title('Done !')
    
    def treeGenerateRename(self):
        if not self.selected:
            self.parent.title('<No Selection>')
            return
            
        obj = self.tree.selection()
        item = self.tree.item(obj)['text']
        
        dialog = RenameDialog(self, title='Rename Item', item=item)
        result = dialog.result
        
        print(result)
        if result:
            self.parent.title('Done !')
        
        self.refreshTree()

    def treeGenerateTerminal(self):
        c = Configuration()     # -> in configuration.py
        system = c.getSystem()
        terminalCommand = c.getTerminal(system)
        
        subprocess.call(terminalCommand, shell=True)

    def process_directory(self, parent, path):
        try:
            l = []
            for p in os.listdir(path):
                abspath = os.path.join(path, p)
                isdir = os.path.isdir(abspath)

                if isdir:
                    item = '> /' + str(p)
                    l.append(item)

                else:
                    item = str(p)
                    l.append(item)
                
            l.sort()
            #l.reverse()
            
            for items in l:
                if items.startswith('>'):
                    self.tree.insert(parent, 'end', text=str(items), open=False, tags='subfolder')
                elif items.startswith('.'):
                    self.tree.insert(parent, 'end', text=str(items), open=False, tags='hidden')                    
                elif items.endswith('.py') or items.endswith('.pyw'):
                    self.tree.insert(parent, 'end', text=str(items), open=False, tags='pythonFile')
                else:
                    self.tree.insert(parent, 'end', text=str(items), open=False, tags='row')
       
        except Exception as e:
            print(str(e))
            return

    def refreshTree(self, event=None):
        for i in self.tree.get_children():
            self.tree.delete(i)
        path = '.'
        abspath = os.path.abspath(path)
        root_node = self.tree.insert('', 'end', text=abspath, open=True, tags='folder')
        self.process_directory(root_node, abspath)

if __name__ == '__main__':
    root = tk.Tk()
    app = FilebrowserFrame(root)
    app.pack(fill=tk.BOTH, expand=True)
    root.mainloop()