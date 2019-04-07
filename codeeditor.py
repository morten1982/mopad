import re
import keyword
import platform
import subprocess
import tkinter as tk
from tkinter import ttk
from tkinter import font
from configuration import Configuration
import importlib

class TextLineNumbers(tk.Canvas):
    '''
        Canvas for Linenumbers
    '''
    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        self.textwidget = None
        self.font_size = 14
        self.configFont()

        
    def configFont(self):
        '''font for linenumbers'''
        system = platform.system().lower()
        if system == "windows":
            self.font = font.Font(family='monospace', size=self.font_size)
        elif system == "linux":
            self.font = font.Font(family='monospace', size=self.font_size)
        else:
            self.font = font.Font(family='monospace', size=self.font_size)


    def attach(self, text_widget):
        self.textwidget = text_widget

    def redraw(self, *args):
        '''redraw line numbers'''
        self.delete("all")

        i = self.textwidget.index("@0,0")
        while True :
            dline= self.textwidget.dlineinfo(i)
            if dline is None: break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(1,y,anchor="nw", font=self.font, text=linenum, fill='white')
            i = self.textwidget.index("%s+1line" % i)
        

class CodeEditor(tk.Text):
    
    '''
        modified text Widget ... thanks to stackoverflow.com :)
    '''
    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)
        
        self.tk.eval('''
            proc widget_proxy {widget widget_command args} {

                # call the real tk widget command with the real args
                set result [uplevel [linsert $args 0 $widget_command]]

                # generate the event for certain types of commands
                if {([lindex $args 0] in {insert replace delete}) ||
                    ([lrange $args 0 2] == {mark set insert}) || 
                    ([lrange $args 0 1] == {xview moveto}) ||
                    ([lrange $args 0 1] == {xview scroll}) ||
                    ([lrange $args 0 1] == {yview moveto}) ||
                    ([lrange $args 0 1] == {yview scroll})} {

                    event generate  $widget <<Change>> -when tail
                }

                # return the result from the real widget command
                return $result
            }
            ''')
        self.tk.eval('''
            rename {widget} _{widget}
            interp alias {{}} ::{widget} {{}} widget_proxy {widget} _{widget}
        '''.format(widget=str(self)))
        
        # global variables
        self.filename = None
        self.tab_width = 4
        self.font_size = 14
        self.linenumber = None
        
        # make background black / foreground white
        self.config(insertbackground='#00FF00')
        self.config(background='#000000')
        self.config(foreground='#FFFFFF')
        
        # color when selection is used
        self.tag_config("sel", background="#053582", foreground="white")
        
        # config font
        self.configFont()

        # define keywords: thanks to github.comm
        # see Dvlv/Tkinter-By-Example
        self.KEYWORDS_1 = ["False", "class", "finally", "is",
                           "None", "continue", "lambda", "True", "def", "from",
                           "nonlocal", "and", "del", "global", "not", "as", 
                           "or", "yield", "assert", "import", "pass", "break",
                           "raise"]
        self.KEYWORDS_FLOW = ["if", "else", "elif", "try", "except", "for",\
                              "in", "while", "return", "with"]

        self.SPACES_REGEX = re.compile("^\s*")
        self.STRING_REGEX_SINGLE = re.compile("'[^'\r\n]*'")
        self.STRING_REGEX_DOUBLE = re.compile('"[^"\r\n]*"')
        self.NUMBER_REGEX = re.compile(r"\b(?=\(*)\d+\.?\d*(?=\)*\,*)\b")
        self.KEYWORDS_REGEX = re.compile("(?=\(*)(?<![a-z])(None|True|False)(?=\)*\,*)")
        self.SELF_REGEX = re.compile("(?=\(*)(?<![a-z])(self)(?=\)*\,*)")
        self.FUNCTIONS_REGEX = re.compile("(?=\(*)(?<![a-z])(print|list|dict|set|int|str|float|input|range|open|tuple)(?=\()")
        self.COMMENTS_REGEX = re.compile("#[^#\r\n]*")
        
        self.REGEX_TO_TAG = {
            self.STRING_REGEX_SINGLE : "string",
            self.STRING_REGEX_DOUBLE : "string",
            self.NUMBER_REGEX : "digit",
            self.KEYWORDS_REGEX : "keywordcaps",
            self.SELF_REGEX : "keyword1",
            self.FUNCTIONS_REGEX : "keywordfunc",
            self.COMMENTS_REGEX : "comment",
        }

        self.tag_config("keyword1", foreground="#448dc4")   
        self.tag_config("keywordcaps", foreground="#CC7A00")
        self.tag_config("keywordflow", foreground="#00b402")
        self.tag_config("keywordfunc", foreground="#ddd313")
        self.tag_config("decorator", foreground="#298fb5")
        self.tag_config("digit", foreground="#ff4d4d")
        self.tag_config("string", foreground="#8e98a1")
        self.tag_config("comment", foreground="#6b6b6b")
        
        # key bindings: 
        self.bind("<KeyRelease>", self.on_key_release, add='+')
        self.bind('<KeyRelease>', self.checkBraces, add='+')
        self.bind("<Tab>", self.tab)
        self.bind('<Return>', self.indent, add='+')
        self.bind('<Return>', self.updateAutoCompleteList, add='+')
        self.bind('<Key>', self.updateAutocompleteEntry, add='+')
        self.bind('<BackSpace>', self.backtab)
        self.bind("<ButtonRelease-3>", self.textPadPopUp)
        self.bind('<Control-x>', self.cut)
        self.bind('<Control-c>', self.copy)
        self.bind('<Control-v>', self.paste)
        
        # set autocompleteList
        self.SetAutoCompleteList()
        
        # other importan variables
        self.charstring = ''
        self.list = []

    
    def tag_keywords(self, event=None, current_index=None):
        if not current_index:
            current_index = self.index(tk.INSERT)
        line_number = current_index.split(".")[0]
        line_beginning = ".".join([line_number, "0"])
        line_text = self.get(line_beginning, line_beginning + " lineend")
        line_words = line_text.split()
        number_of_spaces = self.number_of_leading_spaces(line_text)
        y_position = number_of_spaces

        for tag in self.tag_names():
            self.tag_remove(tag, line_beginning, line_beginning + " lineend")

        self.add_regex_tags(line_number, line_text)

        for word in line_words:
            stripped_word = word.strip("():,")

            word_start = str(y_position)
            word_end = str(y_position + len(stripped_word))
            start_index = ".".join([line_number, word_start])
            end_index = ".".join([line_number, word_end])

            if stripped_word in self.KEYWORDS_1:
                self.tag_add("keyword1", start_index, end_index)
            elif stripped_word in self.KEYWORDS_FLOW:
                self.tag_add("keywordflow", start_index, end_index)
            elif stripped_word.startswith("@"):
                self.tag_add("decorator", start_index, end_index)

            y_position += len(word) + 1

    def tag_all_lines(self):
        final_index = self.index(tk.END)
        final_line_number = int(final_index.split(".")[0])
        
        for line_number in range(final_line_number):
            line_to_tag = ".".join([str(line_number), "0"])
            self.tag_keywords(None, line_to_tag)


    def number_of_leading_spaces(self, line):
        spaces = re.search(self.SPACES_REGEX, line)
        if spaces.group(0) is not None:
            number_of_spaces = len(spaces.group(0))
        else:
            number_of_spaces = 0

        return number_of_spaces

    def add_regex_tags(self, line_number, line_text):
        for regex, tag in self.REGEX_TO_TAG.items():
            for match in regex.finditer(line_text):
                start, end = match.span()
                start_index = ".".join([line_number, str(start)])
                end_index = ".".join([line_number, str(end)])
                self.tag_add(tag, start_index, end_index)

    def on_key_release(self, event=None):
        #print(event.keysym)
        if event.keysym in ("Up", "Down", "Left", "Right", "Shift_L", "Shift_R"):
            return
        else:
            self.tag_keywords()
        
        # look for colon in last line 
        if event.keysym == 'Return':
            index = self.index(tk.INSERT).split(".")
            actual_line = int(index[0])
            actual_line = self.get("%d.%d" % (actual_line, 0), "%d.end" % (actual_line))
            last_line = int(index[0]) - 1
            last_line_text = self.get("%d.%d" % (last_line, 0), "%d.end" % (last_line))
            
            # remove newline character to look after colon at end of line
            last_line_text = last_line_text.rstrip()
            # look if actual_line is only whitespace:
            actual_line = actual_line.strip(' \n')
            if last_line_text.endswith(':') and actual_line == '':
                self.insert(tk.INSERT, self.tab_width * ' ')

    # functions for autocomplete
    def SetAutoCompleteList(self):
        '''
            basic autocompleteList with keywords and some important things (for me)
        '''
        
        self.autocompleteList = ['__init__', '__main__','__name__', '__repr__', '__str__',
                '__dict__', 'args', 'kwargs', "self", "__file__", 'super()'] # autocomplete

        self.kwList = keyword.kwlist
        for item in self.kwList:
            self.autocompleteList.append(item)

    def updateAutoCompleteList(self, event=None):
        '''
            a simple algorithm for parsing the given text and filter important words
        '''
        self.SetAutoCompleteList()
            
        first_list = []
        second_list = []
        
        text = self.get(1.0, tk.END)
        text = text.replace("(", " ").replace(")", " ").replace\
                        ("[", " ").replace("]", " ").replace\
                        (':', " ").replace(',', " ").replace("<", " ").replace\
                        (">", " ").replace("/", " ").replace("=", " ").replace\
                        (";", " ").replace("self.", "").replace('.', ' ')
        
        first_list = text.split('\n')
        
        for row in first_list:
            if row.startswith('import '):
                try:
                    # try to import global variables from import 
                    # -> this could be made better ... :)
                    module_name = row.replace('import' , ' ')
                    module_name = module_name.split()[0]
                    
                    module = importlib.import_module(module_name, package=None)
                    x = dir(module)

                    for elem in x:
                        if elem.startswith('_'):
                            continue
                        else:
                            second_list.append(elem)
                
                except Exception as e:
                    #print(str(e))
                    continue
                        
            elif row.strip().startswith('#') or row.strip().startswith('"""') or\
               row.strip().startswith("'''"):
                continue
            else:
                word_list = row.split()
                for word in word_list:
                    if re.match("(^[0-9])", word):
                        continue
                    elif '#' in word:
                        continue
                    elif word in self.kwList:
                        continue
                    elif word in self.autocompleteList:
                        continue
                    elif not len(word) < 3:
                        w = re.sub("{}<>;,:]", '', word)
                        second_list.append(w)
        
        # delete doubled entries ...
        x = set(second_list)
        second_list = list(x)

        for word in second_list:
            if len(word) > 25:
                continue
            self.autocompleteList.append(word)
        #print()
        #print(self.autocompleteList)
        return


    def updateAutocompleteEntry(self, event=None):
        '''
            make new list for the input from the user
        '''
        char = event.char
        key = event.keycode
        sym = event.keysym
        
        # debugging ... :)
        #print(char)
        #print(key)
        
        self.list = []
        if sym in ("Up", "Down", "Left", "Right", "Space", \
                            "Control_R", "Control_L", "Alt_R", "Alt_L", \
                            "Backtab", "Return"):
            
            # set label and variables to none
            self.entry.config(text='---')
            self.list = []
            self.charstring = ''
        
        elif char in [".", "(", ")", '"', "'", ",", "="]:
            self.entry.config(text='---')
            self.list = []
            self.charstring = ''
        
        else:
            self.charstring += char
            for item in self.autocompleteList:
                if item.startswith(self.charstring):
                    self.list.append(item)
            
            
            if self.list and len(self.charstring)>=2:
                self.entry.config(text=self.list[0])                            
            else:
                self.entry.config(text='---')

            if len(self.list) == 3:
                self.entry.config(text=self.list[0])
                            


    def configFont(self):
        '''
            set the font .... tested only in windows .. if you want to make it cross platform
        '''
        system = platform.system().lower()
        if system == "windows":
            self.font = font.Font(family='Consolas', size=self.font_size)
            self.configure(font=self.font)
        elif system == "linux":
            self.font = font.Font(family='Mono', size=self.font_size)
            self.configure(font=self.font)

    def tab(self, event):
        '''
            make tab(4 * whitespaces) or insert autocomplete when using tab
        '''
        if not self.list:
            self.insert(tk.INSERT, " " * self.tab_width)
        else:
            l = len(self.charstring)
            x, y = self.index(tk.INSERT).split(".")
            y2 = int(y) - l
            y2 = str(y2)
            pos = x + '.' + y2
            self.mark_set('insert', pos)
            self.tag_add("sel", pos, '%d.%d' % (int(x), int(y)))
            self.insert(tk.INSERT, self.list[0])
            if self.tag_ranges("sel"):      # test if selection...
                self.delete('sel.first', 'sel.last')
            
        self.charstring == ''
        self.entry.config(text='---')
        self.list = []
        
        return 'break'

    def backtab(self, event):
        '''
            make backtab when using backspace
        '''
        self.entry.config(text='---')
        self.list = []
        self.charstring = ''

        chars = self.get("insert linestart", 'insert')
        if not self.tag_ranges("sel"):
            if chars.isspace():     # only if there are whitespaces !
                if len(chars) >= 4:
                    self.delete("insert-4c", "insert")
                    return 'break'

    def indent(self, event=None):
        '''
            make indent
        '''
        self.entry.config(text='---')
        self.list = []
        self.charstring = ''
        
        index = self.index(tk.INSERT).split(".")
        line_no = int(index[0])
        # position cursor:
        pos = int(index[1])
        
        
        self.updateAutoCompleteList()
        
        if pos == 0:
            return
        
        line_text = self.get("%d.%d" % (line_no, 0),  "%d.end" % (line_no))
        text_only = line_text.lstrip(" ")
        no_of_spaces = len(line_text) - len(text_only)
        
        # if enter was hit in a row that has leading spaces and spaces between
        # cursor and text 
        line_text_cursor = self.get("%d.%d" % (line_no, pos), "%d.end" % (line_no))
        spaces_betweeen = line_text_cursor.lstrip(" ")
        spaces_betweeen = spaces_betweeen.rstrip(" ")
        leading_spaces = len(line_text_cursor) - len(spaces_betweeen)
        #print(leading_spaces)
        
        # if so: delete them for a nice editing feeling
        if leading_spaces:
            no_of_spaces -= leading_spaces

        spaces = '\n' + " " * no_of_spaces
        
        self.insert(tk.INSERT, spaces)
        self.see(self.index(tk.INSERT)) 
        
        # on Return ends:
        return 'break'

    def checkBraces(self, event=None):
        'check braces, paren, brackets '
        key = event.keycode
        sym = event.keysym
        
        line = int(self.index(tk.INSERT).split('.')[0])
        line_text = self.get("%d.%d" % (line, 0), "%d.end" % (line))
        
        self.tag_configure("braceHighlight", foreground="red")
        self.tag_configure('parenHighlight', foreground='red')
        self.tag_configure('bracketHighlight', foreground='red')
        
        # paren ()
        if sym == 'parenleft':
            x = self.isBalancedParen(line_text)
            if x == False:
                z = line_text.rfind('(')
            else:
                z = False
            
            if z:
                self.tag_add("parenHighlight", "%d.%d"%(line, z), "%d.%d"%(line, z+1)) 
            else:
                self.tag_remove('parenHighlight', "%d.0"%(line), '%d.end'%(line))
        
        elif sym == 'parenright':
            x = self.isBalancedParen(line_text)
            if x == False:
                z = line_text.rfind(')')
            else:
                z = False
            
            if z:
                self.tag_add("parenHighlight", "%d.%d"%(line, z), "%d.%d"%(line, z+1)) 
            else:
                self.tag_remove('parenHighlight', "%d.0"%(line), '%d.end'%(line))
        
        # bracket []
        elif sym == 'bracketleft':
            x = self.isBalancedBracket(line_text)
            if x == False:
                z = line_text.rfind('[')
            else:
                z = False
            
            if z:
                self.tag_add("bracketHighlight", "%d.%d"%(line, z), "%d.%d"%(line, z+1)) 
            else:
                self.tag_remove('bracketHighlight', "%d.0"%(line), '%d.end'%(line))
        
        elif sym == 'bracketright':
            x = self.isBalancedBracket(line_text)
            if x == False:
                z = line_text.rfind(']')
            else:
                z = False
            
            if z:
                self.tag_add("bracketHighlight", "%d.%d"%(line, z), "%d.%d"%(line, z+1)) 
            else:
                self.tag_remove('bracketHighlight', "%d.0"%(line), '%d.end'%(line))
        
        # brace {}
        elif sym == 'braceleft':
            x = self.isBalancedBrace(line_text)
            if x == False:
                z = line_text.rfind('{')
            else:
                z = False
            
            if z:
                self.tag_add("braceHighlight", "%d.%d"%(line, z), "%d.%d"%(line, z+1)) 
            else:
                self.tag_remove('braceHighlight', "%d.0"%(line), '%d.end'%(line))
        
        elif sym == 'braceright':
            x = self.isBalancedBrace(line_text)
            if x == False:
                z = line_text.rfind('}')
            else:
                z = False
            
            if z:
                self.tag_add("braceHighlight", "%d.%d"%(line, z), "%d.%d"%(line, z+1)) 
            else:
                self.tag_remove('braceHighlight', "%d.0"%(line), '%d.end'%(line))


        else:
            return

    def isBalancedParen(self, txt):
        braced = 0
        for ch in txt:
            if ch == '(': braced += 1
            if ch == ')':
                braced -= 1
                if braced < 0: return False
        return braced == 0

    def isBalancedBracket(self, txt):
        braced = 0
        for ch in txt:
            if ch == '[': braced += 1
            if ch == ']':
                braced -= 1
                if braced < 0: return False
        return braced == 0

    def isBalancedBrace(self, txt):
        braced = 0
        for ch in txt:
            if ch == '{': braced += 1
            if ch == '}':
                braced -= 1
                if braced < 0: return False
        return braced == 0

    def textPadPopUp(self, event):
        menu = tk.Menu(self, tearoff=False, background='#000000',foreground='white',
                activebackground='blue', activeforeground='white')
        menu.add_command(label="Undo", compound=tk.LEFT, command=self.undo)
        menu.add_command(label="Redo", compound=tk.LEFT, command=self.redo)
        menu.add_separator()
        menu.add_command(label='Cut', compound=tk.LEFT, command=self.cut)
        menu.add_command(label="Copy", compound=tk.LEFT, command=self.copy)
        menu.add_command(label="Paste", compound=tk.LEFT, command=self.paste)
        menu.add_separator()
        menu.add_command(label="Select All", compound=tk.LEFT, command=self.selectAll)
        menu.add_separator()
        menu.add_command(label="Open Terminal", compound=tk.LEFT, command = self.terminal)
        menu.tk_popup(event.x_root, event.y_root, 0)
    
    def undo(self, event=None):
        try:
            self.edit_undo()
            self.highlightAll()
        except:
            return
    
    def redo(self, event=None):
        try:
            self.edit_redo()
            self.highlightAll()
        except:
            return
    
    def cut(self, event=None):
        self.event_generate("<<Cut>>")
        self.tag_keywords()
        return 'break'
    
    def copy(self, event=None):
        self.event_generate("<<Copy>>")
        self.tag_keywords()
        return 'break'
        
    def paste(self, event=None):
        self.event_generate("<<Paste>>")
        #self.tag_keywords()
        self.highlightAll()
        return 'break'
    
    def selectAll(self, event=None):
        self.tag_add('sel', '1.0', 'end')
    
    def goto(self, event=None):
        pass
    
    def terminal(self, event=None):
        c = Configuration()     # -> in configuration.py
        system = c.getSystem()
        terminalCommand = c.getTerminal(system)
        
        subprocess.call(terminalCommand, shell=True)
    
    def highlightAll(self):
        final_index = self.index(tk.END)
        final_line_number = int(final_index.split(".")[0])

        for line_number in range(final_line_number):
            line_to_tag = ".".join([str(line_number), "0"])
            self.tag_keywords(None, line_to_tag)



class CodeeditorFrame(ttk.Frame):
    '''
        Codeeditor + Linenumber Frame
    '''

    def __init__(self, master=None):
        super().__init__(master)
        self.pack(expand=True, fill=tk.BOTH)
        self.initUI()

    def initUI(self):
        
        # frame1
        frame1 = ttk.Frame(self)
        frame1.pack(fill=tk.BOTH, expand=True)
        
        # autocompleteEntry (packed on bottom)
        self.autocompleteEntry = ttk.Label(frame1, text='---', font=('Mono', 14))
        self.autocompleteEntry.pack(side='bottom', fill='y')
        
        # scrollbar y
        textScrollY = ttk.Scrollbar(frame1, orient=tk.VERTICAL)
        textScrollY.config(cursor="double_arrow")
        textScrollY.pack(side=tk.RIGHT, fill=tk.Y)
        
        # in tkinter it is important what to pack first (!)
        self.linenumber = TextLineNumbers(frame1, width=45, bg='#000000')
        self.linenumber.pack(side="left", fill="y")
        
        # scrollbar x (packed on bottom)
        textScrollX = ttk.Scrollbar(frame1, orient=tk.HORIZONTAL)
        textScrollX.config(cursor="sb_h_double_arrow")
        textScrollX.pack(side=tk.BOTTOM, fill=tk.X)

        self.textPad = CodeEditor(frame1, undo=True, maxundo=-1, 
                                  autoseparators=True, wrap='none')
        self.textPad.filename = None
        self.textPad.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

        textScrollY.config(command=self.textPad.yview)
        textScrollX.config(command=self.textPad.xview)
        self.textPad.configure(yscrollcommand=textScrollY.set)
        self.textPad.configure(xscrollcommand=textScrollX.set)
        self.linenumber.attach(self.textPad)


        self.textPad.entry = self.autocompleteEntry
        self.textPad.linenumber = self.linenumber
        
        self.textPad.bind("<<Change>>", self.on_change)
        self.textPad.bind("<Configure>", self.on_change)


    def on_change(self, event):
        self.linenumber.redraw()


if __name__ == '__main__':
    root = tk.Tk()
    root['bg'] = 'black'
    
    app = CodeeditorFrame()
    
    app.mainloop()