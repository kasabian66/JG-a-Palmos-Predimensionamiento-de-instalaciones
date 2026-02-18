from __future__ import annotations
import streamlit as st
from typing import List
def warnings_box(msgs: List[str]) -> None:
    for m in msgs:
        st.warning(m)
