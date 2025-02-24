from tkinter import *
from tkinter import filedialog, messagebox,scrolledtext, ttk
import json, webbrowser, os
'import jpype'
# Syntax highlighting colors

COLORS = {
    "keyword": "blue",
    "string": "brown",
    "comment": "red",
    "tag": "blue",
    "attribute": "aqua",
    "selector": "green",
    "property": "navy",
    "value": "teal",
}
html = '<!DOCTYPE html>, <html></html>, <head></head>, <title></title>, <body></body>, <div></div>, <p></p>, <h1></h1>, <h2></h2>, <h3></h3>, <h4></h4>, <h5></h5>, <h6></h6>, <a></a>, <img>, <ul></ul>, <ol></ol>, <li></li>, <table></table>, <tr></tr>, <td></td>, <form></form>, <input>, <button></button>, <script></script>, <style></style>, <link>, <meta>, <br>, <hr>, class, id, href, src'.split(",")
py = """abs()
aiter()
all()
anext()
any()
ascii()

bin()
bool()
breakpoint()
bytearray()
bytes()


callable()
chr()
classmethod()
compile()
complex()


delattr()
dict()
dir()
divmod()


enumerate()
eval()
exec()


filter()
float()
format()
frozenset()


getattr()
globals()


hasattr()
hash()
help()
hex()


id()
input()
int()
isinstance()
issubclass()
iter()
L
len()
list()
locals()


map()
max()
memoryview()
min()


next()


object()
oct()
open()
ord()


pow()
print()
property()





range()
repr()
reversed()
round()


set()
setattr()
slice()
sorted()
staticmethod()
str()
sum()
super()


tuple()
type()


vars()


zip()

_
__import__()"""
py_list = ["False", "None", "True", "and", "as", "assert", "async", "await","break", "class", "continue", "def", "del", "elif", "else", "except","finally", "for", "from", "global", "if", "import", "in", "is", "lambda", "nonlocal", "not", "or", "pass", "raise", "return", "try", "while", "with", "yield", "range","print"]
py = py.replace("\n", "")
gh = py.split("()")
for v in gh:
    py_list.append(v)

suggestions = {
            'html': html,
            'css': ['color', 'background', 'font-size', 'margin', 'padding', 
                   'width', 'height', 'display', 'position', 'flex', 'grid'],
            'js': ['function', 'const', 'let', 'var', 'if', 'else', 'for', 'while',
                  'console.log', 'document.querySelector', 'addEventListener'],
            "py" : py_list
        }

# Keywords for HTML, CSS, and JavaScript
HTML_KEYWORDS = ["!DOCTYPE", "html", "head", "title", "body", "div", "p", "h1", "h2", "h3", "h4", "h5", "h6", "a", "img", "ul", "ol", "li", "table", "tr", "td", "form", "input", "button", "script", "style", "link", "meta", "br", "hr"]
CSS_KEYWORDS = ["color", "background", "font", "margin", "padding", "border", "width", "height", "display", "position", "float", "clear", "text-align", "vertical-align", "line-height", "z-index", "opacity", "visibility", "overflow", "cursor", "box-shadow", "transition", "animation"]
JS_KEYWORDS = ["function", "var", "let", "const", "if", "else", "for", "while", "do", "switch", "case", "break", "continue", "return", "try", "catch", "finally", "throw", "new", "this", "class", "extends", "super", "import", "export", "async", "await", "Promise", "console", "document", "window"]
PY_KEYWORDS = py_list
text = []
class CodeEditor:
    def __init__(self, root):
        self.root = root
        self.dirr = os.getcwd()
        self.s = ttk.Style()

        # 1. Configure the style FIRST
        self.s.configure('e.TPanedWindow', 
                        background="black", 
                        foreground="white",
                        bordercolor="#444")
        self.s.configure('e.Treeview', 
                background="black", 
                foreground="white",
                bordercolor="#444")

        # 2. Create layout (critical for ttk.PanedWindow)
        self.s.layout('e.TPanedWindow', [
            ('PanedWindow.background', {
                'sticky': 'nswe'
            })
        ])

        # 3. Then create widgets with the style
        self.paned_windo = ttk.PanedWindow(
            self.root, 
            orient=VERTICAL, 
            style="e.TPanedWindow"
        )

        self.paned_window = ttk.PanedWindow(self.paned_windo, orient=HORIZONTAL,  style="e.TPanedWindow")
        self.paned_wind = ttk.PanedWindow(self.paned_windo, orient=HORIZONTAL,  style="e.TPanedWindow")
        self.paned_windo.add(self.paned_wind, weight=1)
        self.paned_windo.add(self.paned_window, weight=44)
        self.file = ttk.Treeview(self.paned_window, padding="2")
        self.file = ttk.Treeview(
    self.root,
    style="e.Treeview"
)
        # For default tree column (hidden)

        
        self.paned_window.add(self.file, weight=1)
        img = PhotoImage(file="logo.png")
        self.note = ttk.Notebook(self.paned_window, height=100)
        self.root.iconphoto(1, img)
        self.roo = Frame(self.note)
        self.note.add(self.roo, text="untitled")
        self.root.title("Code Editor")
        self.root.geometry("800x600")
        file_path = "untitled"
        # Language selection
        self.language = StringVar(value="html")
        self.language_menu = ttk.Combobox(self.root,justify="left", background="black", textvariable=self.language, values=["html", "css", "js", "py"])
        self.paned_wind.add(ttk.Button(self.root, text="❌", command=self.ex), weight=1)
        self.paned_wind.add(self.language_menu, weight=4)
        
        self.language_menu.bind("<<ComboboxSelected>>", self.update_syntax_highlighting)
        self.root.dark_mode = True
        self.paned_windo.pack(side="top", fill="both", expand=1, padx=0, pady=0)
        

        self.bracket_pairs = {'(': ')', '[': ']', '{': '}', '\"': '\"','\'': '\''}

        self.patterns = {
            'keywords': r'\b(and|as|assert|break|class|continue|def|del|elif|else|except|False|finally|for|from|global|if|import|in|is|lambda|None|nonlocal|not|or|pass|raise|return|True|try|while|with|yield)\b',
            'string': r'"[^"\\]*(\\.[^"\\]*)*"|\'[^\'\\]*(\\.[^\'\\]*)*\'',
            'comment': r'#.*$'
        }
        # Text area with line numbers
        self.text_area = Text(self.roo,undo=True, wrap="none",fg="white", background="black", font=("Bookman Old Style", 12))
        self.text_area.insert(END, """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>
    
</body>
</html>""")
        text.append(self.text_area)
        for tt in text:
            tt.pack(fill="both", expand=1)
        current_tab = self.note.nametowidget(self.note.select())
        texts = current_tab.winfo_children()[0]
        self.fra = Frame(self.root)
        self.line_numbers = LineNumbers(self.fra, texts, width=5)
        self.line_numbers.pack(fill="both", expand=1)
        self.paned_window.add(self.note, weight=4)

        self.paned_window.add(self.fra, weight=1)
        self.s.configure("TNotebook", background="black", foreground="white")
        
        # Scrollbars
        self.scroll_y = Scrollbar(self.text_area, orient="vertical", command=self.text_area.yview)
        self.scroll_y.pack(side="right", fill="y")
        self.scroll_x = Scrollbar(self.text_area, orient="horizontal", command=self.text_area.xview)
        self.scroll_x.pack(side="bottom", fill="x")
        self.text_area.configure(yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set)
        self.load_extension_suggestions("html.txt")
        # Line numbers
        
        menu_bar = Menu(self.root, background="#1e1e1e", foreground="white")
        # Menu bar

        self.root.bind("<Control-n>", lambda event: self.new_file())
        self.root.bind("<Control-o>", lambda event: self.open_file())
        self.root.bind("<Control-s>", lambda event: self.save_file())
        self.root.bind("<Control-Shift-S>", lambda event: self.save_file_as())
        self.root.bind("<Control-f>", lambda event:self.find_text())
        self.root.bind("<KeyRelease>", self.show_suggestions)
        self.root.bind("<KeyPress>", self.show_suggestions)
        
        
        
        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="New Window", command=self.new_file, accelerator="Ctrl+Shift+N")
        file_menu.add_command(label="Open...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Workspace", command=self.load_directory)

        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.save_file_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        run_menu = Menu(menu_bar, tearoff=0)
        run_menu.add_command(label="Run", command=self.run_code)
        run_menu.add_command(label="Run HTML", command=self.run_html)
        menu_bar.add_cascade(label="Run", menu=run_menu)

        # Edit Menu
        edit_menu = Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Undo", command=self.text_area.edit_undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.text_area.edit_redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self.cut_text, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self.copy_text, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.paste_text, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Find...", command=self.find_text, accelerator="Ctrl+F")
        edit_menu.add_command(label="Replace...", command=self.replace_text, accelerator="Ctrl+H")
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All", command=lambda:self.text_area.event_generate("<<Control-a>>"), accelerator="Ctrl+A")
        menu_bar.add_cascade(label="Edit", menu=edit_menu)

        # Format Menu
        format_menu = Menu(menu_bar, tearoff=0)
        self.word_wrap = BooleanVar()
        format_menu.add_checkbutton(label="Word Wrap", variable=self.word_wrap, command=self.toggle_word_wrap)
        format_menu.add_command(label="Font...", command=self.change_font)
        menu_bar.add_cascade(label="Format", menu=format_menu)

        # View Menu
   

        # Help Menu
        help_menu = Menu(menu_bar, tearoff=0)
        vh = Menu(menu_bar, tearoff=0)
        vh.add_command(label="HTML tutorials", command=lambda:webbrowser.open(f"file:///{os.getcwd()}\\tut\\html_tutorial.pdf"))
        vh.add_command(label="JavaScript tutorials", command=lambda:webbrowser.open(f"file:///{os.getcwd()}\\tut\\javascript_tutorial.pdf"))
        vh.add_command(label="Python tutorials", command=lambda:webbrowser.open(f"file:///{os.getcwd()}\\tut\\Tutorial_EDIT.pdf"))
        vh.add_command(label="Java tutorials", command=lambda:webbrowser.open(f"file:///{os.getcwd()}\\tut\\java_tutorial.pdf"))
        help_menu.add_cascade(label="View Help", menu=vh)
        help_menu.add_command(label="Send Feedback")
        help_menu.add_separator()
        help_menu.add_command(label="About Code Editors", command=self.about)
        menu_bar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menu_bar)

        # Bind events        
        self.text_area.bind("<KeyRelease>", self.update_syntax_highlighting)
        self.text_area.bind("<KeyRelease>", self.handle_key_press)
        self.note.bind("<ButtonPress>", self.sal)
        self.root.bind("<KeyRelease>", self.line_numbers.bind_events)
        self.note.bind("<Enter>", self.line_numbers.bind_events)
        self.note.bind("<Enter>", self.sal)
        ()
        self.update_syntax_highlighting()
        self.file.heading('#0', text='Workspace', anchor=W)
        self.file.bind("<Double-1>", self.on_tree_double_click)
        self.root.bind("<Control-d>", lambda event : self.ins())
    def run_html(self, event=None):
        some = os.getcwd()
        os.chdir(self.dirr)
        print(os.getcwd(), self.dirr)        
        current_tab = self.note.nametowidget(self.note.select())
        texts = current_tab.winfo_children()[0]
        from tkhtmlview import HTMLLabel
        win = Toplevel(self.root)
        win.title("HTML")
        code = HTMLLabel(win, html=texts.get(1.0, END)).pack(expand=1, fill=BOTH)
        os.chdir(some)
    def add_new_tab(self):
        new_tab = ttk.Frame(self.note)
        self.note.add(new_tab, text="New Tab")

        text_widget = Text(new_tab)
        text_widget.pack(side=RIGHT, fill=BOTH, expand=True)

        line_numbers = LineNumbers(text_widget, new_tab)  # Pass the text widget
        line_numbers.pack(side=LEFT, fill=Y)

        # Bind events
        text_widget.bind("<KeyRelease>", line_numbers.redraw)
        text_widget.bind("<MouseWheel>", line_numbers.redraw)
        text_widget.bind("<Configure>", line_numbers.redraw)
    def ins(self):
        current_tab = self.note.nametowidget(self.note.select())
        texts = current_tab.winfo_children()[0]
        texts.insert(INSERT, """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>
    
</body>
</html>""")
    def run_code(self):
        current_tab = self.note.nametowidget(self.note.select())
        some = os.getcwd()
        os.chdir(self.dirr)
        print(os.getcwd())
        # Check if current_tab is valid
        if not current_tab:
            messagebox.showerror("Error", "No tab selected.")
            return

        # Check if current_tab has children
        children = current_tab.winfo_children()
        print(children)
        file = self.note.tab(self.note.select())
        if file["text"] == "untitled":
            pass
        else:
            file_path = file["text"]
        texts = children[0]  # Access the first child

        # Get file path, handle potential errors if the item is not found
        

        if file_path.endswith('.py'):
            code = texts.get(1.0, END)  # Get the code from the text area
            exec(code)  # Execute Python code
       
        elif file_path.endswith('.java'):
            from py4j.java_gateway import JavaGateway

            gateway = JavaGateway()  # Connect to the JVM
            java_code = texts.get(1.0, END)  # Get the Java code

            try:
                # Assuming you have a Java class that can evaluate the code
                # and it's exposed through the py4j gateway.  Adjust as necessary.
                result = gateway.entry_point.executeCode(java_code)
                print("Java execution result:", result) #print result in the console
            except Exception as e:
                messagebox.showerror("Error", f"Error executing Java code: {e}")

            gateway.close() # Close gateway connection


        else:
            try:
                webbrowser.open_new(file_path)
            except:
                self.save_file_as()
        os.chdir(some)
    def find_text(self):
        current_tab = self.note.nametowidget(self.note.select())
        texts = current_tab.winfo_children()[0]
        """Open a dialog to find text in the editor."""
        self.find_dialog = Toplevel(self.root)
        self.find_dialog.title("Find")
        self.find_dialog.geometry("300x100")

        Label(self.find_dialog, text="Find:").pack()
        self.find_entry = Entry(self.find_dialog, width=25)
        self.find_entry.pack(pady=5)

        Button(self.find_dialog, text="Find Next", command=self.find_next).pack(pady=5)

    def find_next(self):
        """Find the next occurrence of the text."""
        current_tab = self.note.nametowidget(self.note.select())
        texts = current_tab.winfo_children()[0]
        search_text = self.find_entry.get()
        if search_text:
            start = texts.search(search_text, 1.0, stopindex=END)
            if start:
                end = f"{start}+{len(search_text)}c"
                texts.tag_remove("found", 1.0, END)
                texts.tag_add("found", start, end)
                texts.tag_config("found", background="yellow")
                texts.mark_set(INSERT, end)
                texts.see(INSERT)
            else:
                messagebox.showinfo("Find", "No more occurrences found.")
    def current(self):
        current_tab = self.note.nametowidget(self.note.select())
        texts = current_tab.winfo_children()[0]
        return text
    def replace_text(self):
        """Open a dialog to replace text in the editor."""
        self.replace_dialog = Toplevel(self.root)
        self.replace_dialog.title("Replace")

        Label(self.replace_dialog, text="Find:").pack()
        self.replace_find_entry = Entry(self.replace_dialog, width=25)
        self.replace_find_entry.pack(pady=5)

        Label(self.replace_dialog, text="Replace with:").pack()
        self.replace_entry = Entry(self.replace_dialog, width=25)
        self.replace_entry.pack(pady=5)

        Button(self.replace_dialog, text="Replace", command=self.replace_next).pack(pady=5)
        Button(self.replace_dialog, text="Replace All", command=self.replace_all).pack(pady=5)

    def replace_next(self):
        """Replace the next occurrence of the text."""
        current_tab = self.note.nametowidget(self.note.select())
        texts = current_tab.winfo_children()[0]
        find_text = self.replace_find_entry.get()
        replace_text = self.replace_entry.get()
        if find_text:
            start = texts.search(find_text, 1.0, stopindex=END)
            if start:
                end = f"{start}+{len(find_text)}c"
                texts.delete(start, end)
                texts.insert(start, replace_text)
                texts.tag_remove("found", 1.0, END)
                texts.tag_add("found", start, f"{start}+{len(replace_text)}c")
                texts.tag_config("found", background="yellow")
                texts.mark_set(INSERT, f"{start}+{len(replace_text)}c")
                texts.see(INSERT)
            else:
                messagebox.showinfo("Replace", "No more occurrences found.")
    def sal(self, event):

        self.line_numbers.redraw()
        current_tab = self.note.nametowidget(self.note.select())
        texts = current_tab.winfo_children()[0]
        self.line_numbers.text_widget = texts


    def replace_all(self):
        current_tab = self.note.nametowidget(self.note.select())
        texts = current_tab.winfo_children()[0]
        """Replace all occurrences of the text."""
        find_text = self.replace_find_entry.get()
        replace_text = self.replace_entry.get()
        if find_text:
            texts.tag_remove("found", 1.0, END)
            start = 1.0
            while True:
                start = texts.search(find_text, start, stopindex=END)
                if not start:
                    break
                end = f"{start}+{len(find_text)}c"
                texts.delete(start, end)
                texts.insert(start, replace_text)
                texts.tag_add("found", start, f"{start}+{len(replace_text)}c")
                texts.tag_config("found", background="yellow")
                start = f"{start}+{len(replace_text)}c"
            messagebox.showinfo("Replace All", "All occurrences have been replaced.")

    def load_directory(self):
        path = filedialog.askdirectory()
        self.dirr = path
        print(self.dirr, "sjugyg")
        self.h = path
        self.file.delete(*self.file.get_children())
        for item in os.listdir(path):
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                node = self.file.insert('', 'end', text=item, values=[full_path])
                self.file.insert(node, "end")
            else:
                self.file.insert('', 'end', text=item, values=[full_path])
            
    def on_tree_double_click(self, event):
        item = self.file.selection()[0]
        path = self.file.item(item, 'values')[0]
        if os.path.isfile(path):
            self.open_file(path)
        else:
            
            pathe = path
            self.file.delete(*self.file.get_children())
            self.file.insert('', 'end', text="⬅", values=[self.h])

            for item in os.listdir(pathe):
                full_path = os.path.join(path, item)
                if os.path.isdir(full_path):
                    node = self.file.insert('', 'end', text=item, values=[full_path])
                    self.file.insert(node, "end")
                else:
                    self.file.insert('', 'end', text=item, values=[full_path])

    def load_extension_suggestions(self, file_ext):
        if not file_ext:
            return
        ext_file = f"{file_ext}"
        try:
            with open(ext_file) as f:
                data = json.load(f)
                self.current_suggestions = data.get('suggestions', [])
        except json.JSONDecodeError:
            self.current_suggestions = []

    def show_suggestions(self, event):
        current_tab = self.note.nametowidget(self.note.select())
        text_widget = current_tab.winfo_children()[0]
        word = text_widget.get("insert-1c wordstart", "insert-1c")
        if len(word) < 1:
            return
        
        
        

        x, y, _, _ = text_widget.bbox(INSERT)
        x += text_widget.winfo_x() + 20
        y += text_widget.winfo_y() + 25

        try:
            self.suggestion_listbox.destroy()
        except:
            pass

        self.suggestion_listbox = Listbox(self.root, height=5)
        self.suggestion_listbox.place(x=x, y=y)
        lists = []
        for x,y in suggestions.items():
            if self.language_menu.get() == x:
                y = list(y)
                for cc in y:
                    
                    if word in cc:
                        lists.append(cc)
                        self.suggestion_listbox.insert(END, cc)
        
        self.suggestion_listbox.bind("<Double-Button-1>", 
                                   self.insert_suggestion)
                                   
    def insert_suggestion(self, event):
        current_tab = self.note.nametowidget(self.note.select())
        text_widget = current_tab.winfo_children()[0]
        if not self.suggestion_listbox:
            return

        selection = self.suggestion_listbox.get(ACTIVE)
        text_widget.delete("insert-1c wordstart", "insert-1c")
        text_widget.insert(INSERT, selection)
        self.suggestion_listbox.destroy()
        self.suggestion_listbox = None
    def new_file(self):
        global file_path
        self.roo2 = Frame(self.note, width=12)
        self.note.add(self.roo2, text="Untitled")
        """Clear the text area for a new file."""
        self.text_area2 = Text(self.roo2,undo=True, wrap="none",fg="white", background="black", font=("Bookman Old Style", 12))
        text.append(self.text_area2)
        self.text_area2.insert(END, """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>
    
</body>
</html>""")
        self.root.bind("<KeyPress>", self.update_syntax_highlighting)
        self.root.bind("<KeyRelease>", self.handle_key_press)
        self.root.bind("<KeyPress>", self.update_syntax_highlighting)
        self.text_area2.pack(fill="both", expand=True)
    def add_new_tab(self):
        new_tab = ttk.Frame(self.note)
        self.note.add(new_tab, text="New Tab")
        
        text_widget = Text(new_tab)
        text_widget.pack(side=RIGHT, fill=BOTH, expand=True)

        line_numbers = LineNumbers(text_widget, new_tab)  # Pass the text widget
        line_numbers.pack(side=LEFT, fill=Y)

        # Bind events
        text_widget.bind("<KeyRelease>", line_numbers.redraw)
        text_widget.bind("<MouseWheel>", line_numbers.redraw)
        text_widget.bind("<Configure>", line_numbers.redraw)

    def handle_key_press(self, event):
        global text
        
        current_tab = self.note.nametowidget(self.note.select())
        texts = current_tab.winfo_children()[0]
        
        if event.char in self.bracket_pairs:
            texts.insert(INSERT, self.bracket_pairs[event.char])
            texts.mark_set(INSERT, f"{INSERT}-1c")
            return "break"
        
        if event.char in self.bracket_pairs.values():
            next_char = texts.get(INSERT, f"{INSERT}+1c")
            if next_char == event.char:
                text.mark_set(INSERT, f"{INSERT}+1c")
                return "break"
    def open_file(self, select = None):
        global file_path
        if select == None:
            """Open a file and load its content into the text area."""
            file_path = filedialog.askopenfilename(filetypes=[("HTML Files", "*.html"), ("CSS Files", "*.css"), ("JS Files", "*.js"),("Python Files", "*.py"), ("All Files", "*.*")])
            file_pat = file_path.split("\\")
            if file_path:
                with open(file_path, "r") as file:

                    self.roo2 = Frame(self.note)
                    self.note.add(self.roo2, text=file_pat[len(file_pat)-1])

                    self.text_area2 = Text(self.roo2,undo=True, wrap="none", fg="white", background="black", font=("Bookman Old Style", 12))

                    self.text_area2.insert(END, file.read())
                    self.text_area2.pack(fill="both", expand=True)
                    text.append(self.text_area2)
        else:
            file_path = select
            file_pat = file_path.split("\\")
            if file_path:
                with open(file_path, "r") as file:

                    self.roo2 = Frame(self.note)
                    self.note.add(self.roo2, text=file_path)

                    self.text_area2 = Text(self.roo2,undo=True, wrap="none", fg="white", background="black", font=("Bookman Old Style", 12))

                    self.text_area2.insert(END, file.read())
                    self.text_area2.pack(fill="both", expand=True)
                    text.append(self.text_area2)
        self.root.bind("<KeyPress>", self.update_syntax_highlighting)
        self.root.bind("<KeyRelease>", self.handle_key_press)
        self.root.bind("<KeyPress>", self.update_syntax_highlighting)
     

                

    def save_file(self):
        global file_path
        try: 
            file_path
        except NameError:
            file_path = "untitled"
        """Save the current content to the file."""
        current_tab = self.note.nametowidget(self.note.select())
        texts = current_tab.winfo_children()[0]
        file = self.note.tab(self.note.select())
        if file["text"] == "untitled":
            pass
        else:
            file_path = file["text"]
        if file_path != "untitled":
            with open(file_path, "w") as file:
                file.write(texts.get(1.0, END))
            messagebox.showinfo("Saved", "File saved successfully!")
        else:
            self.save_file_as()
    def ex(self):
        current_tab = self.note.nametowidget(self.note.select())
        self.note.forget(current_tab)

    def save_file_as(self):
        global file_path
        current_tab = self.note.nametowidget(self.note.select())
        texts = current_tab.winfo_children()[0]
        file = self.note.tab(self.note.select())
        if file["text"] == "untitled":
            pass
        else:
            file_path = file["text"]
        """Save the current content to a new file."""
        file_path = filedialog.asksaveasfilename(defaultextension=".html",
                                                 filetypes=[("HTML Files", "*.html"), ("CSS Files", "*.css"), ("JS Files", "*.js"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(texts.get(1.0, END))
            self.file_path = file_path
            self.root.title(f"Code Editor - {file_path}")
            messagebox.showinfo("Saved", "File saved successfully!")

    def exit_editor(self):
        """Exit the editor."""
        self.root.quit()

    def cut_text(self):
        """Cut selected text."""
        self.text_area.event_generate("<<Cut>>")

    def copy_text(self):
        """Copy selected text."""
        self.text_area.event_generate("<<Copy>>")
        
    def paste_text(self):
        """Paste text from clipboard."""
        self.text_area.event_generate("<<Paste>>")
    def toggle_word_wrap(self):
        if self.word_wrap.get():
            self.text_area.config(wrap=WORD)
        else:
            self.text_area.config(wrap=NONE)

    def change_font(self):
        # Implement font selection dialog
        pass

    def zoom_in(self):
        # Implement zoom in functionality
        pass

    def zoom_out(self):
        # Implement zoom out functionality
        pass

    def zoom_default(self):
        # Implement default zoom functionality
        pass

    def about(self):
        messagebox.showinfo("About Notepad", "Simple Code Editor Application\nCreated with Tkinter by Terra Codes written by owolabi kehinde.")

    
    def update_syntax_highlighting(self, event=None):
        """Apply syntax highlighting based on the selected language."""
        for text_area in text:
            text_area.tag_remove("keyword", 1.0, END)
            text_area.tag_remove("string", 1.0, END)
            text_area.tag_remove("comment", 1.0, END)
            text_area.tag_remove("tag", 1.0, END)
            text_area.tag_remove("attribute", 1.0, END)
            text_area.tag_remove("selector", 1.0, END)
            text_area.tag_remove("property", 1.0, END)
            text_area.tag_remove("value", 1.0, END)

        language = self.language.get()
        if language == "html":
            self.highlight_html()
        elif language == "css":
            self.highlight_css()
        elif language == "js":
            self.highlight_js()
        elif language == "py":
            self.highlight_js()
    def highlight_html(self):
        for tag in PY_KEYWORDS:
            start = 1.0
            while True:
                start = self.text_area.search(tag, start, stopindex=END)
                if not start:
                    break
                end = f"{start}+{len(tag)}c"
                self.text_area.tag_add("tag", start, end)
                start = end

        
    def highlight_html(self):
        """Apply syntax highlighting for HTML."""
        # Highlight tags
        for text_area in text:

            for tag in HTML_KEYWORDS:
                start = 1.0
                while True:
                    
                    start = text_area.search(tag, start, stopindex=END)
                    if not start:
                        break
                    end = f"{start}+{len(tag)}c"
                    text_area.tag_add("tag", start, end)
                    start = end
            # Highlight attributes
            start = 1.0
            while True:
                start = text_area.search(r'\w+="', start, stopindex=END, regexp=True)
                if not start:
                    break
                end = text_area.search('"', f"{start}+1c", stopindex=END)
                if not end:
                    break
                end = f"{end}+1c"
                text_area.tag_add("attribute", start, end)
                start = end

            # Highlight comments
            self.highlight_comments()

    def highlight_css(self):
        """Apply syntax highlighting for CSS."""
        # Highlight selectors
        for text_area in text:

            for selector in CSS_KEYWORDS:
                start = 1.0
                while True:
                    start = text_area.search(selector, start, stopindex=END)
                    if not start:
                        break
                    end = f"{start}+{len(selector)}c"
                    text_area.tag_add("selector", start, end)
                    start = end

            # Highlight properties and values
            start = 1.0
            while True:
                start = text_area.search(r"\{", start, stopindex=END, regexp=True)
                if not start:
                    break
                end = text_area.search(r"\}", start, stopindex=END, regexp=True)
                if not end:
                    break
                text_area.tag_add("property", start, end)
                start = end

            # Highlight comments
            self.highlight_comments()

    def highlight_js(self):
        """Apply syntax highlighting for JavaScript."""
        # Highlight keywords
        for text_area in text:

            for keyword in JS_KEYWORDS:
                start = 1.0
                while True:
                    start = text_area.search(keyword, start, stopindex=END)
                    if not start:
                        break
                    end = f"{start}+{len(keyword)}c"
                    text_area.tag_add("keyword", start, end)
                    start = end

            # Highlight strings
            start = 1.0
            while True:
                start = text_area.search(r'("|\')', start, stopindex=END, regexp=True)
                if not start:
                    break
                end = text_area.search(r'("|\')', f"{start}+1c", stopindex=END, regexp=True)
                if not end:
                    break
                end = f"{end}+1c"
                text_area.tag_add("string", start, end)
                start = end

            # Highlight comments
            self.highlight_comments()

    def highlight_comments(self):
        """Highlight comments in the text area."""
        for text_area in text:

            start = 1.0
            while True:
                start = text_area.search(r"<!--|//|/\*", start, stopindex=END, regexp=True)
                if not start:
                    break
                if text_area.get(start, f"{start}+4c") == "<!--":
                    end = text_area.search("-->", start, stopindex=END)
                    if not end:
                        end = END
                    else:
                        end = f"{end}+3c"
                elif text_area.get(start, f"{start}+2c") == "//":
                    end = text_area.search("\n", start, stopindex=END)
                    if not end:
                        end = END
                else:
                    end = text_area.search(r"\*/", start, stopindex=END)
                    if not end:
                        end = END
                    else:
                        end = f"{end}+2c"
                text_area.tag_add("comment", start, end)
                start = end

        # Configure tag colors
            text_area.tag_config("keyword", foreground=COLORS["keyword"])
            text_area.tag_config("string", foreground=COLORS["string"])
            text_area.tag_config("comment", foreground=COLORS["comment"])
            text_area.tag_config("tag", foreground=COLORS["tag"])
            text_area.tag_config("attribute", foreground=COLORS["attribute"])
            text_area.tag_config("selector", foreground=COLORS["selector"])
            text_area.tag_config("property", foreground=COLORS["property"])
            text_area.tag_config("value", foreground=COLORS["value"])
class LineNumbers(Canvas):
    def __init__(self, parent, text_widget, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.text_widget = text_widget
        self.configure(width=60, bg="black", highlightthickness=0)
        self.bind_events()
   
    def bind_events(self, event=None):
        self.text_widget.bind("<KeyRelease>", self.redraw)
        self.text_widget.bind("<MouseWheel>", self.redraw)
        self.text_widget.bind("<Configure>", self.redraw)

    def redraw(self, event=None):
        self.delete("all")
        i = self.text_widget.index("@0,0")
        while True:
            dline = self.text_widget.dlineinfo(i)
            if dline is None: break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(40, y, anchor=NE, text=linenum, fill="white", font=("Consolas", 10))
            i = self.text_widget.index(f"{i}+1line")

# Run the application
if __name__ == "__main__":
    root = Tk()
    root.geometry("700x300")
    editor = CodeEditor(root)
    root.mainloop()
