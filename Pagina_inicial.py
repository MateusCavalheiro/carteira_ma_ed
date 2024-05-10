import streamlit as st
import pandas as pd
import sqlite3
import os
#from Backlog import main as page1 #Pagina inicial
#from Carregar_tabela import main as page2 #carregar no banco de dados
#from back_log_ED_upload import main as page3 #Upload da planilha
st.set_page_config(
    page_title='Carteira MA-ED',
    page_icon='🪐',
    layout='wide')


st.markdown(f'<p style="background-color:#0066cc;color:#33ff33;font-size:24px;border-radius:2%;">{1}</p>', unsafe_allow_html=True)
st.text("header(the content you want to show)")


#def main():

    #navigation = st.sidebar.button('Página inicial',) , st.sidebar.button('Carregar Planilha')

    # Lógica para verificar qual botão foi clicado
    #if navigation[0]:
       # page1()
    #elif navigation[1]:
      #  page2()
    #else:
       # st.title("Aplicativo de Carteira MA-ED")

#if __name__ == "__main__":
   # main()
