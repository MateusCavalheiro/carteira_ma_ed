import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime, timedelta

st.set_page_config(
    page_title='Carteira MA-ED',
    page_icon='🏭',
    layout='wide')
def exclude_data(value):
    #value = datetime.strptime(value,"%d.%m.%Y - %H:%M")
    data_hora = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    #st.write(data_hora)
    conn = sqlite3.connect('data_ed.db')
    c = conn.cursor()
    c.execute(f"DELETE FROM backlog WHERE Data_inserida = '{data_hora}'")
    conn.commit()
    conn.close()
    #st.write(f'{value} é a data')
    #st.write(f'Registros com Data inserida = {value} excluídos do banco de dados.')
    st.success(f'Registros com **Data inserida ➡️ {str(datetime.strptime(value, "%Y-%m-%d %H:%M:%S").strftime("%d.%m.%Y"))}** excluídos do banco de dados.')
    refresh = st.button('🔃',help='Atualizar item')
    if refresh:
        st.rerun()
    
    #st.rerun()
def load_data():
    try:
        query = """SELECT DISTINCT(Data_inserida) as Lista FROM backlog          
                """
        conn = sqlite3.connect('data_ed.db')

        # Executar a consulta SQL
        df = pd.read_sql_query(query, conn)

        # Fechar a conexão com o banco de dados
        conn.close()
        st.write(len(df))

        for index, row in df.iterrows():
            col1, col2 = st.columns(2)
            col1.write(f'**• Tabela {index+1}** inserida: '+ str(datetime.strptime(row['Lista'], "%Y-%m-%d %H:%M:%S").strftime("%d.%m.%Y")))
            
            agora = datetime.now()
            data_especifica = datetime.strptime(row['Lista'], "%Y-%m-%d %H:%M:%S")
            diferenca =  agora - data_especifica
            if diferenca.days <= 5:
                st.text('Diferença em dias: ' + str(diferenca.days))
                st.text('Hoje:' + str(datetime.strftime(agora,"%d.%m.%Y - %H:%M")))
                index, var = index, col2.button('🗑️',key=index,help='Exclua essa tabela da base') #, on_click=exclude_data, args=row['Lista'])
                
                if var:
                    st.warning('Deseja realmente excluir este dado? Não será possível desfazer.')
                    col1_1, col2_2 = st.columns([1, 10])
                    accept = col1_1.button('✅',key=str(index) +"_" + str(index) ,help='Excluir',on_click=lambda: exclude_data(row['Lista']))
                    recuse = col2_2.button('❌',key=str(index) +"_" + str(index+1),help='Cancelar ação')
                    #if accept:
                    #  exclude_data(row['Lista'])
                    #  st.rerun
                    #elif recuse:
                    # ...
                        #var = False
            else:
                st.text('Diferença em dias: ' + str(diferenca.days))
                st.text('Hoje: ' + str(datetime.strftime(agora,"%d.%m.%Y - %H:%M")))
                index, var = index, col2.button('🗑️',key=index,help='Não é possível excluir pois excedeu 5 dias!',disabled=True) #, on_click=exclude_data, args=row['Lista'])
            st.divider()
    except:
        #st.write('Nenhuma tabela inserida até o momento')
        st.info('Nenhuma tabela inserida até o momento.', icon="ℹ")
                
def create_table(df):
    
    conn = sqlite3.connect('data_ed.db')
    c = conn.cursor()

    # Criação da tabela no SQLite
    #c.execute('''CREATE TABLE IF NOT EXISTS backlog (
                  #  Coluna_A INTEGER,
                   # Coluna_B TEXT
                 #)''')"""

    # Inserção dos dados na tabela
    df.to_sql('backlog', conn, if_exists='append', index=False)

    conn.commit()
    conn.close()
    return True

def main():
    st.title("Carregar dados para análise de carteira",anchor=False)
    st.subheader("Tabelas carregadas:",anchor=False)
    load_data()
    
    #dias =  int(st.text_input('dia')) #exc
    
    # Exibir o componente de upload de arquivo
    uploaded_file = st.file_uploader("Selecione o arquivo Excel", type=['xlsx','xls','csv'])
    

    if uploaded_file is not None:
        # Carregar o arquivo Excel em um DataFrame
        
        df = pd.read_excel(uploaded_file)
        
        # Define uma data para carregar na base de dados
        data_atual = datetime.now() #.strftime('%Y-%m-%d')
        data_acrescida = data_atual + timedelta(days=0)
        data_acrescida_formatada = data_acrescida.strftime('%Y-%m-%d')
        df['Data_inserida'] = pd.to_datetime(data_acrescida_formatada)
        df['Ano de entrada'] = df['Data de entrada'].apply(lambda x:str(x.year) )
        
        # Exibir uma mensagem de confirmação
        st.success("Tabela criada no banco de dados.")
        
        # Exibir os dados carregados
        st.write("Dados carregados:")
        st.write(df)

        # Criar tabela no SQLite
        create_table(df)
    

if __name__ == "__main__":
    main()
