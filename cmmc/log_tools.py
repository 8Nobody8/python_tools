from copy import deepcopy
from time import localtime, strftime
from typing import Any, Optional


def terminal_print(
    msg: str,
    label: Optional[Any] = None,
    use_timestamp: Optional[bool] = True,
    int_leading_zeros: Optional[int] = 1,
    float_leading_space: Optional[int] = 1,
    float_decimals: Optional[int] = 2,
    str_leading_space: Optional[int] = 0,
) -> None:
    """
    Print msg to terminal along with a timestamp and optionally a label (useful
    for multiple threads or message types).
    """
    if label is None:
        use_label = False
    else:
        use_label = True

    current_label: Any = 0
    previous_label: Any = 0

    def p(
        msg,
        use_label,
        use_timestamp,
        int_leading_zeros,
        float_leading_space,
        float_decimals,
        str_leading_space,
    ):
        nonlocal current_label
        nonlocal previous_label

        txt = ""
        if use_label and current_label == previous_label:
            txt += "\n"
        if use_timestamp:
            txt += f"{strftime('%H:%M:%S'), localtime} "
        if use_label:
            if isinstance(current_label, int):
                txt += f"[{current_label:0{int_leading_zeros}d}]"
            elif isinstance(current_label, float):
                txt += f"[{current_label: {float_leading_space}.{float_decimals}f}]"
            elif isinstance(current_label, str):
                txt += f"[{current_label:>{str_leading_space}}]"
            else:
                txt += f"[{current_label}]"
        previous_label = deepcopy(current_label)

    p(
        msg,
        use_label,
        use_timestamp,
        int_leading_zeros,
        float_leading_space,
        float_decimals,
        str_leading_space,
    )
