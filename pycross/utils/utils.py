# -*- coding: utf-8 -*-
# Copyright: (c) 2019, Iskander Shafikov <s00mbre@gmail.com>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import sys, os, subprocess, traceback, uuid
import tempfile
from datetime import datetime, time
from .globalvars import ENCODING, FONT_WEIGHTS
from PyQt5 import QtGui, QtCore, QtWidgets

### ---------------------------- COMMON ---------------------------- ###

def print_err(what, file=sys.stderr):
    print(what, file=file)

def print_dbg(what, file=sys.stdout):    
    print(what, file=file)
        
def print_help(what, file=sys.stdout):
    print(what, file=file)

def is_iterable(obj):
    try:
        _ = iter(obj)
        return True
    except:
        return False

def generate_uuid():
    return uuid.uuid4().hex

def walk_dir(root_path, abs_path=True, recurse=True, dir_process_function=None, 
             file_process_function=None, file_types=None):
    """
    """
    if abs_path:
        root_path = os.path.abspath(root_path)
    for (d, dirs, files) in os.walk(root_path):
        if dir_process_function:
            for d_ in dirs:
                dir_process_function(os.path.join(d, d_))
        if file_process_function:
            for f in files:
                ext = os.path.splitext(f)[1][1:].lower()
                if (not file_types) or (ext in file_types):                
                    file_process_function(os.path.join(d, f))
        if not recurse: break

def run_exe(args, external=False, capture_output=True, stdout=subprocess.PIPE, encoding=ENCODING, 
             creationflags=subprocess.CREATE_NO_WINDOW, timeout=None, shell=False, **kwargs):
    try:
        if external:
            return subprocess.Popen(args, 
                creationflags=(subprocess.DETACHED_PROCESS | creationflags), 
                stdout=stdout, stderr=subprocess.STDOUT,
                encoding=encoding, shell=shell, **kwargs) if capture_output else \
                    subprocess.Popen(args, 
                creationflags=(subprocess.DETACHED_PROCESS | creationflags), 
                encoding=encoding, shell=shell, **kwargs)
        else:
            return subprocess.run(args, 
                capture_output=capture_output, encoding=encoding, 
                timeout=timeout, shell=shell, **kwargs)
    except Exception as err:
        traceback.print_exc(limit=None)
        raise

def datetime_to_str(dt=None, strformat='%Y-%m-%d %H-%M-%S'):
    if dt is None: dt = datetime.now()
    return dt.strftime(strformat)

def timestamp_to_str(ts=None, strformat='%Y-%m-%d %H-%M-%S'):
    if ts is None: ts = time.time()
    return datetime_to_str(datetime.fromtimestamp(ts), strformat)

def str_to_datetime(text, strformat='%Y-%m-%d %H-%M-%S'):
    return datetime.strptime(text, strformat)

def str_to_timestamp(text, strformat='%Y-%m-%d %H-%M-%S'):
    return str_to_datetime(text, strformat).timestamp()

def get_tempdir():
    return os.path.abspath(tempfile.gettempdir())

def make_abspath(filename, root=''):
    # default root = pycross\
    if not root: root = os.path.dirname(os.path.dirname(__file__))
    return os.path.abspath(os.path.join(root, filename))

def bytes_human(value, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(value) < 1024.0:
            return f"{value:3.1f}{unit}{suffix}"
        value /= 1024.0
    return f"{value:.1f}Yi{suffix}"

### ---------------------------- GUI ---------------------------- ###

class QThreadStump(QtCore.QThread):

    sig_error = QtCore.pyqtSignal(QtCore.QThread, str)

    def __init__(self, default_priority=QtCore.QThread.NormalPriority, 
                 on_start=None, on_finish=None, on_run=None, on_error=None,
                 start_signal=None, stop_signal=None, 
                 free_on_finish=False, start_now=False, can_terminate=True):
        super().__init__()
        self.init(default_priority, on_start, on_finish, on_run, on_error, 
                  start_signal, stop_signal, free_on_finish, can_terminate)
        if start_now: self.start()
    
    def __del__(self):
        try:
            self.wait()
        except:
            pass

    def init(self, default_priority=QtCore.QThread.NormalPriority, 
             on_start=None, on_finish=None, on_run=None, on_error=None,
             start_signal=None, stop_signal=None, 
             free_on_finish=False, can_terminate=True):
        try:
            self.started.disconnect()
            self.finished.disconnect()
            self.sig_error.disconnect()
        except:
            pass

        self.setTerminationEnabled(can_terminate)
        if on_start: self.started.connect(on_start)
        if on_finish: self.finished.connect(on_finish)        
        if free_on_finish: self.finished.connect(self.deleteLater)
        if start_signal: start_signal.connect(self.start)        
        if stop_signal: stop_signal.connect(self.terminate)
        if on_error: self.sig_error.connect(on_error)
        self.default_priority = default_priority if default_priority != QtCore.QThread.InheritPriority else QtCore.QThread.NormalPriority 
        self.on_run = on_run
        self.mutex = QtCore.QMutex()

    def lock(self):
        self.mutex.lock()

    def unlock(self):
        self.mutex.unlock()

    def run(self):
        self.setPriority(self.default_priority)
        if self.on_run and not self.isInterruptionRequested(): 
            try:
                self.on_run()
            except Exception as err:                
                traceback.print_exc(limit=None)
                self.sig_error.emit(self, str(err))

## ------------------------------------------------------------------------ ##      
        
def make_font(family, size=-1, weight=-1, italic=False, font_unit='pt'):
    font = QtGui.QFont(family)
    if font_unit == 'pt':
        font.setPointSize(size)
    else:
        font.setPixelSize(size)
    font.setWeight(weight)
    font.setItalic(italic)
    #print(f"make_font: font_unit={font_unit}, family={font.family()}, size(pt) = {font.pointSize()}, size(px)={font.pixelSize()}")
    return font
    
def MsgBox(what, parent=None, title='pyCross', msgtype='info', btn=None):
    if msgtype == 'error':
        msgtype = QtWidgets.QMessageBox.Critical
        if btn is None: btn = QtWidgets.QMessageBox.Ok
    elif msgtype == 'warn':
        msgtype = QtWidgets.QMessageBox.Warning
        if btn is None: btn = QtWidgets.QMessageBox.Ok
    elif msgtype == 'ask':
        msgtype = QtWidgets.QMessageBox.Question
        if btn is None: btn = QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
    else:
        msgtype = QtWidgets.QMessageBox.Information
        if btn is None: btn = QtWidgets.QMessageBox.Ok
    return QtWidgets.QMessageBox(msgtype, title, what, btn, parent).exec()

def UserInput(dialogtype='text', parent=None, title='pyCross', label='', value=None, textmode='normal',
              valrange=None, decimals=1, step=1, comboeditable=True, comboitems=[]):
    modes = {'normal': QtWidgets.QLineEdit.Normal, 'noecho': QtWidgets.QLineEdit.NoEcho,
             'password': QtWidgets.QLineEdit.Password, 'passwordonedit': QtWidgets.QLineEdit.PasswordEchoOnEdit}
    if dialogtype == 'text':
        mode = modes[textmode]
        return QtWidgets.QInputDialog.getText(parent, title, label,
                echo=mode, text=str(value) if value else '')
    elif dialogtype == 'multitext':
        return QtWidgets.QInputDialog.getMultiLineText(parent, title, label,
                text=str(value) if value else '')
    elif dialogtype == 'int':
        return QtWidgets.QInputDialog.getInt(parent, title, label,
                value=int(value) if value else 0, min=valrange[0] if valrange else -2147483647,
                max=valrange[1] if valrange else 2147483647, step=step)
    elif dialogtype == 'float':
        return QtWidgets.QInputDialog.getDouble(parent, title, label,
                value=float(value) if value else 0, min=valrange[0] if valrange else -2147483647,
                max=valrange[1] if valrange else 2147483647, decimals=decimals)
    elif dialogtype == 'item':
        return QtWidgets.QInputDialog.getMultiLineText(parent, title, label,
                comboitems, current=value if value else 0, editable=comboeditable)

def clipboard_copy(value, valtype='text'):
    clip = QtWidgets.qApp.clipboard()
    if valtype == 'text':
        clip.setText(value)
    elif valtype == 'mime':
        clip.setMimeData(value)
    elif valtype == 'pixmap':
        clip.setPixmap(value)
    elif valtype == 'image':
        clip.setImage(value)

def clipboard_get(valtype='text'):
    clip = QtWidgets.qApp.clipboard()
    if valtype == 'text':
        return clip.text()
    elif valtype == 'mime':
        return clip.mimeData()
    elif valtype == 'pixmap':
        return clip.pixmap()
    elif valtype == 'image':
        return clip.image()
    return None

def clipboard_clear():
    QtWidgets.qApp.clipboard().clear()
        
def stylesheet_load(style, dequote=True, strip_sz=True, units=('pt', 'px')):
    ls_style = [s.strip() for s in style.split(';')]
    d = {}
    def unq(s):
        if s.startswith('"') and s.endswith('"'):
            return s[1:-1]
        return s                
    for pair in ls_style:
        st = [s.strip() for s in pair.split(':')]
        if len(st) != 2: continue
        if dequote: st[1] = unq(st[1])
        if strip_sz:
            for unit in units:
                if st[1].endswith(unit):
                    st[1] = int(st[1][:-2].strip())
                    break
        if st[1] == 'true': st[1] = True
        if st[1] == 'false': st[1] = False
        d[st[0]] = st[1]
    #print(f"_stylesheet_load: {d}")
    return d     

def stylesheet_dump(d, quoted_keys=('font-family',), add_units={'font-size': 'pt', 'border': 'px', 'border-width': 'px'}):
    l = []
    for key in d:
        val = d[key]
        for qk in quoted_keys:
            if key == qk and not (val.startswith('"') and val.endswith('"')):
                val = f'"{val}"'
                break
        unit = add_units.get(key, '')
        if unit: val = f'{val}{unit}'
        if isinstance(val, bool): val = str(val).lower()
        l.append(f'{key}: {str(val)}')
    s = '; '.join(l)  
    #print(f"_stylesheet_dump: {s}")
    return s

def font_weight_css2qt(weight, default=0):
    if weight == 'normal':
        weight = QtGui.QFont.Normal
    elif weight == 'bold':
        weight = QtGui.QFont.Bold
    else:
        weight = FONT_WEIGHTS.get(int(weight), default)
    return weight  

def font_weight_qt2css(weight, default=0):    
    for w in FONT_WEIGHTS:
        if FONT_WEIGHTS[w] == weight:
            return w
    return default
        
def font_from_stylesheet(style, font_unit='pt', default_font=None):
    dic_style = stylesheet_load(style)
    if not 'font-family' in dic_style: 
        if not default_font:
            return None
        else:
            dic_style['font-family'] = default_font.family()
    if not 'font-size' in dic_style: 
        if not default_font:
            return None
        else:
            dic_style['font-size'] = default_font.pointSize() if font_unit == 'pt' else default_font.pixelSize()
    if not 'font-weight' in dic_style: 
        if not default_font:
            return None
        else:
            dic_style['font-weight'] = font_weight_qt2css(default_font.weight())
    if not 'font-style' in dic_style: 
        dic_style['font-style'] = 'normal'
        
    font =  make_font(dic_style['font-family'], dic_style['font-size'], font_weight_css2qt(dic_style['font-weight']), (dic_style['font-style'] == 'italic'), font_unit)
    #print(f"FONT: font_unit={font_unit}, family={font.family()}, size(pt)={font.pointSize()}, size(px)={font.pixelSize()}, weight={font.weight()}")
    return font   

def font_to_stylesheet(font, style, font_unit='pt'):
    dic_style = stylesheet_load(style)
    dic_style['font-family'] = font.family()
    dic_style['font-size'] = font.pointSize() if font_unit == 'pt' else font.pixelSize()
    dic_style['font-weight'] = font_weight_qt2css(font.weight())
    dic_style['font-style'] = 'italic' if font.italic() else 'normal'
    return stylesheet_dump(dic_style, add_units={'font-size': font_unit})

def color_from_stylesheet(style, tag='background-color', default='black'):
    dic_style = stylesheet_load(style)
    return QtGui.QColor(dic_style.get(tag, default))

def color_to_stylesheet(color, style, tag='background-color'):
    dic_style = stylesheet_load(style)
    dic_style[tag] = color.name(1)
    return stylesheet_dump(dic_style)

def property_to_stylesheet(propname, propvalue, style):
    dic_style = stylesheet_load(style)
    dic_style[propname] = propvalue
    return stylesheet_dump(dic_style)

def property_from_stylesheet(propname, style, default=None):
    dic_style = stylesheet_load(style)
    return dic_style.get(propname, default)
        
