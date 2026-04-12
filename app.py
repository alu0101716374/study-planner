import streamlit as st
from lib.auth import init_session, restore_session
from lib.ui import show_pages, load_css


def main():
    init_session()
    restore_session()
    show_pages()
    load_css() 

    

if __name__ == "__main__":
   main()
