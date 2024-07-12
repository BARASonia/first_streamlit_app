import streamlit as st
import psycopg2 as dbdriver
import pandas as pd
import plotly.express as px
from prediction import predict  

# cnx à la base de données denodo
denodoserver_name = "charizard"
denodoserver_odbc_port = "9996"
denodoserver_database = "admin"
denodoserver_uid = "admin"
denodoserver_pwd = "Fastcube#2024"

# fonction pour recuperer les données depuis denodo
def get_data():
    query = "select extract(year from date) as year,extract(month from date) as month,sum(extendedcost) as           Total_Cost,sum(consumedquantity) as total_consumedquantity from poc_finops.sv03_monthly_azurebilling_remote_table group by 1,2 order by 1 DESc"

    cnxn_str = "user=%s password=%s host=%s dbname=%s port=%s" %\
           (denodoserver_uid, denodoserver_pwd, denodoserver_name, denodoserver_database, denodoserver_odbc_port)
    
    cnxn = dbdriver.connect(cnxn_str)
    data = pd.read_sql(query, cnxn)
    cnxn.close()
    return data

# fonction pour estimer la quantité consommée basé sur les mois precidents
def estimate_consumedquantity(data, year, month):
    past_data = data[(data['year'] == year) & (data['month'] <= month)]
    if past_data.empty:
        past_data = data[(data['year'] < year)]
    return past_data['total_consumedquantity'].mean()
        
    
def main():
    
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image('imgs/azure icone.png', width=100) 
    with col2:
        st.title("Prédictions des coûts Azure")
        
   
    

    # recuperer data histor
    data = get_data()

    # sidebar gauche pour les param
    st.sidebar.title("parametres")
    year = st.sidebar.number_input("année", min_value=2020, max_value=2021, value=2020)
    month = st.sidebar.slider("mois", min_value=1, max_value=12, value=1)

    #estimation de la quantité consommee 
    quant = estimate_consumedquantity(data, year, month)
    total_consumedquantity = st.sidebar.number_input("Quantité consommée", value = quant)

    # prediction basee sur le moele entrainé
    if st.sidebar.button("Prédire"):
        input_data = pd.DataFrame({
            "year": [year],
            "month": [month],
            "total_consumedquantity": [total_consumedquantity]
        })
        result = predict(input_data)
        st.sidebar.write(f"Cout prédit: {result[0]:,.2f}")

    #vis dans la partie centrale
    st.header("visualisation")
    l = data['total_cost']
    m = data['month']
    fig = px.line(data, x=m, y=l, title='Cout total par mois')
    
    #show data
    show_data = st.checkbox("data")
    if show_data:
        st.write(data)
        
    #show graph
    show_graph = st.checkbox("la courbe")
    if show_graph:
        option = st.selectbox(
            "Sélectionnez le champ",
            ("Mois", "Année")
        )
        st.write("le champ selectionné:", option)
        st.plotly_chart(fig, use_container_width=True)

 



if __name__ == '__main__':
    main()
