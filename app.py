import streamlit as st
from lib.auth import restore_session
from lib.ui import show_pages, load_css
from lib.state_manager import init_session

def main():
    init_session()
    restore_session()
    show_pages()
    load_css() 

    

if __name__ == "__main__":
   main()
