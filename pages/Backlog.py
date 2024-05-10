import streamlit as st
import pandas as pd
import plotly.express as px
import time
from datetime import datetime
import sqlite3
from io import BytesIO
import altair as alt



st.set_page_config(
    page_title='Carteira MA-ED',
    page_icon='📇',
    layout='centered')
#print(pd.DataFrame(pd.read_excel('Planilha em Basis.xlsx')))
#@st.cache_data

def coment_get(coment):
    query = f"""SELECT DATA FROM comentarios WHERE coment = {coment}'           
                """
    conn = sqlite3.connect('data_ed.db')

    # Executar a consulta SQL
    df = pd.read_sql_query(query, conn)
    print(df)

    # Fechar a conexão com o banco de dados
    conn.close()
    return df['data'].tolist()[0] if len(df['data'].tolist()[0])>0 else ""
def coment_data(coment, data ):
    df = pd.DataFrame({'coment':[coment],'data':[data]})
    print(df)
    conn = sqlite3.connect('data_ed.db')
    c = conn.cursor()

# Inserção dos dados na tabela
    df.to_sql('comentarios', conn, if_exists='append', index=False)

    conn.commit()
    conn.close()

def status_user_sist(data):
    lista = data['Status usuário']
    lista_sist = data['Status sistema']
    linha_user =[]
    linha_sist = []
    for row in range(len(lista)):
        linha_split = lista[row].split()
        linha_split_sist = lista_sist[row].split()
        linha_user += linha_split
        linha_sist += linha_split_sist
        
    df_user = pd.DataFrame({'Status_user': linha_user})
    
    df_sist = pd.DataFrame({'Status_Sistema':linha_sist})
    
    df_user['Status_user'] = df_user['Status_user'].str.replace('*','')
    df_sist['Status_Sistema'] = df_sist['Status_Sistema'].str.replace('*','')
    return df_user['Status_user'].unique(), df_sist['Status_Sistema'].unique()
    #st.dataframe(df_user)
    #st.text(len(df_user))
    #st.dataframe(df_sist)
    #st.text(len(df_sist))
     
def tabelas_de_dados():
    #query = """SELECT * FROM backlog LIMIT 5000

    #"""
    query = """SELECT backlog.*, areas_operacionais.area_operacional
           FROM backlog
           LEFT JOIN areas_operacionais ON backlog.`Área operacion.` = areas_operacionais.numero_area_operacional
           LIMIT 5000;


    
    
    """
    
    conn = sqlite3.connect('data_ed.db')

    # Executar a consulta SQL
    data = pd.DataFrame(pd.read_sql_query(query, conn))
    
    # Fechar a conexão com o banco de dados
    conn.close()
    return data
def main():
    header1, header2 = st.columns([1,25])
    header1.image('img/logo-petrobras-horizontal-1536.png',width=150)
    header2.title("Backlog da Carteira MA-ED",anchor=False)
    try:
        data = tabelas_de_dados()
        data['Data_inserida'] = pd.to_datetime(data['Data_inserida']).dt.strftime("%d.%m.%Y")
        data['Ordem'] = data['Ordem'].astype(str)
        df_user, df_sist = status_user_sist(data)
        analise = st.sidebar.selectbox("Análise",data['Data_inserida'].unique()) #df['Month'].unique()
        
        area_op = st.sidebar.multiselect('Área Operacional', data['area_operacional'].unique(), default=data['area_operacional'].unique())
        
        df_filtered = df_filtered = data.loc[data['area_operacional'].isin(area_op) & (data['Data_inserida'] == analise)].sort_values('Ano de entrada')
        #df_filtered = data[data['Data_inserida'] == analise]
        #else:
        #    df_filtered = data[data['Data_inserida'] == analise].sort_values('Ano de entrada')
        df_filtered = df_filtered.rename(columns={'area_operacional':'Área Operacional'})
        
        df_filtered_fig1 = df_filtered.groupby(['Ano de entrada', 'Área Operacional']).size().reset_index(name='Total')
        
        def download_excel(data):
            output = BytesIO()
            writer = pd.ExcelWriter(output, engine='xlsxwriter')
            data.to_excel(writer, index=False, sheet_name='Planilha1')
            writer.close()
            output.seek(0)
            processed_data = output.getvalue()
            return processed_data
            
        data['Ordem'] = data['Ordem'].astype(str)
        # Exibir os dados
        #st.write("Extração do dia:", datetime.now().strftime("%d.%m.%Y - %H:%M"))
        
        
        #with st.popover(f'**{len(df_filtered)}** ordens na carteira'):
        with st.expander(f'**{len(df_filtered)}** Ordens na carteira',expanded=False):     #  '**Tabela 1** Registro 08-05-2024'):
            f'Tabela inserida no dia {analise}'
            if st.button('Baixar em Excel',type='primary'):
                excel_data = download_excel(df_filtered)
                st.download_button(label='Clique aqui para baixar',
                                data=excel_data,
                                file_name=f'dados_{analise}.xlsx',
                                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            st.dataframe(df_filtered)
        
        #contagem = data['Tipo ativid.PM'].value_counts()
        with st.container(border=True):
            cores = ['#008C4A','#29B09D', '#7DEFA1','#0AFF8D', '#BFDEBA', '#FFCE11','#FF8700','#3D3D3D', '#FFD16A','#52F4A9']
            st.header('Visão geral de ordens', anchor=False,)        
            with st.expander(label='**Ordens em aberto**',expanded=True):
                fig_date = px.bar(df_filtered_fig1,x="Ano de entrada",color='Área Operacional',y='Total',color_discrete_sequence=cores, text_auto=True)
                st.plotly_chart(fig_date,use_container_width=True)
            #st.bar_chart(data=df_filtered_fig1,x="Ano de entrada",color='Área Operacional',y='Total')
            if len(df_filtered['Área Operacional'].unique())>1:
                with st.expander(label='**Percentual por Área Operacional**',expanded=True):
                    fig_area = px.pie(df_filtered_fig1,values='Total',names='Área Operacional',color='Área Operacional',color_discrete_sequence=cores)
                    st.plotly_chart(fig_area,use_container_width=True,)
            
            
            st.header('Relação de Status', anchor=False)
            try:
                text_coment_stat = coment_get('coment_stat')
                coment_stat = st.text_area(key='coment_stat',value=text_coment_stat,label='Comentários para status: ',placeholder='Descreva observações relevantes para serem abordadas neste bloco.')
            except:    
                coment_stat = st.text_area(key='coment_stat',label='Comentários para status: ',placeholder='Descreva observações relevantes para serem abordadas neste bloco.')
            st.button('Salvar',on_click=lambda:coment_data('coment_stat',coment_stat))
            with st.expander('**Filtros** 📌'):
                ano = st.multiselect('Ano', options=df_filtered['Ano de entrada'].unique(),default=df_filtered['Ano de entrada'].unique())
                stat1, stat2 = st.columns(2)
                user_stat = stat1.multiselect('Status Usuário',options=df_user,default=['IMPD','FMAT','FDOC'])
                sist_stat = stat2.multiselect('Status Sistema', options=df_sist,default=['MATF'])
            tb_imp_df_filtered = df_filtered.loc[df_filtered['Ano de entrada'].isin(ano)]
            #print(user_stat)
            resultados = pd.DataFrame()

            for i_user_stat in user_stat:
                dinamic_table = tb_imp_df_filtered.groupby('Ano de entrada')['Status usuário'].apply(lambda x: x.str.contains(i_user_stat).sum())
                #st.text(user_stat[i_user_stat])
                #print(i_user_stat,': ')
                #print(dinamic_table)
                
                resultados[i_user_stat] = dinamic_table
                #if len(resultados)>1:
                #    resultados = resultados + pd.DataFrame({f'{i_user_stat}':dinamic_table})
                #else:
                #    resultados = pd.DataFrame({f'{i_user_stat}':dinamic_table})
            for i_sist_stat in sist_stat:
                dinamic_table = tb_imp_df_filtered.groupby('Ano de entrada')['Status sistema'].apply(lambda x: x.str.contains(i_sist_stat).sum())
                                
                resultados[i_sist_stat] = dinamic_table
            
            #matf_por_ano = tb_imp_df_filtered.groupby('Ano de entrada')['Status sistema'].apply(lambda x: x.str.contains('MATF').sum())

            # Contagem de IMPD por ano
            #impd_por_ano = tb_imp_df_filtered.groupby('Ano de entrada')['Status usuário'].apply(lambda x: x.str.contains('IMPD').sum())

            #fmtc_por_ano = tb_imp_df_filtered.groupby('Ano de entrada')['Status usuário'].apply(lambda x: x.str.contains('FMTC').sum())
            
            # Combinação em DataFrame
            #resultados = pd.DataFrame({'MATF': matf_por_ano,
                                      # 'IMPD': impd_por_ano,
                                     #  'FMTC': fmtc_por_ano})
            
            st.subheader(f'📊 {", ".join(resultados.columns.tolist())}',anchor=False)
            table1, data2 = st.columns(2)
            table1.dataframe(resultados)
            data2.caption(f'**Total de Ordens: :blue[{len(tb_imp_df_filtered)}]**')
            #data2.text('STAT: Total')
            for index in resultados.columns:
                #print(index)
                data2.caption(f'{index}: :blue[{resultados[index].sum()}]  |  Média: :green[{round(resultados[index].sum()/len(tb_imp_df_filtered),2)}]')
            
            
            try:
                text_coment_next = coment_get('coment_next')
                coment_next = st.text_area(key='coment_next1',value=text_coment_next,label='Comentários para status: ',placeholder='Descreva observações relevantes para serem abordadas neste bloco.')
            except:
                coment_next = st.text_area(key='coment_next2', label='Comentário para o próxima parte do relatório:',placeholder='Descreva observações relevantes para serem abordadas neste bloco.')
            st.button('Salvar',key='coment_next',on_click=lambda:coment_data('coment_next',coment_next))
    except Exception as e:
        with st.expander('Erro!'):
            st.exception(e)
            st.dataframe(data['area_operacional'].unique())
if __name__ == "__main__":
    main()