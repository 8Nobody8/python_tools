from copy import deepcopy
from time import localtime, strftime
from typing import Any, Optional


def terminal_print():
    """
    Print msg to terminal along with a timestamp and optionally a label (useful
    for multiple threads or message types).
    """
    current_label = 0
    previous_label = 0

    def p(
        msg: str,
        label: Optional[Any] = None,
        use_timestamp: Optional[bool] = True,
        int_leading_zeros: Optional[int] = 2,
        float_leading_space: Optional[int] = 2,
        float_decimals: Optional[int] = 2,
        str_leading_space: Optional[int] = 0,
        end: str = "\n",
    ):
        
        nonlocal current_label
        nonlocal previous_label

        use_label = False if label is None else True

        current_label = label

        txt = ""
        if use_label and current_label != previous_label:
            txt += "\n"
        if use_timestamp:
            txt += f"{strftime('%H:%M:%S', localtime())} "
        if use_label:
            if isinstance(current_label, int):
                txt += f"[{current_label:0{int_leading_zeros}d}] "
            elif isinstance(current_label, float):
                txt += f"[{current_label: {float_leading_space}.{float_decimals}f}] "
            elif isinstance(current_label, str):
                txt += f"[{current_label:>{str_leading_space}}] "
            else:
                txt += f"[{current_label}] "
        txt += msg

        print(txt, end=end)

        previous_label = deepcopy(current_label)

    return p