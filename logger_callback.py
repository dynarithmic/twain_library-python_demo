from ctypes import *
import ctypes as ct

dtwain_logger_callback_proc = None

def enable_logger_callback_console(dtwain_dll, state):
    @dtwain_dll.SETLOGGERPROCA_TYPE
    def logger_callback(msg, user_data):
        if msg:
            raw = ct.cast(msg, ct.c_char_p).value
            if raw:
                text = raw.decode("utf-8", errors="replace")
                print(text)

        return 1

    state.dtwain_logger_callback_proc = logger_callback
    return dtwain_dll.DTWAIN_SetLoggerCallbackA(state.dtwain_logger_callback_proc,0)

def disable_logger_callback(dtwain_dll, state):
    try:
        dtwain_dll.DTWAIN_SetLoggerCallbackA(None, 0)
        state.dtwain_logger_callback_proc = None
    except Exception:
        pass

    state.dtwain_logger_callback_proc = None

