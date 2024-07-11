import streamlit as st
import psycopg2 as dbdriver
import pandas as pd
import joblib
from prediction import predict

#connection denodo
denodoserver_name = "charizard"
denodoserver_odbc_port = "9996"
denodoserver_database = "admin"
denodoserver_uid = "admin"
denodoserver_pwd = "Fastcube#2024"


# partie functions 

def get_data():

    query = "select extract(year from date) as year,extract(month from date) as month,sum(extendedcost) as           Total_Cost,sum(consumedquantity) as total_consumedquantity from poc_finops.sv03_monthly_azurebilling_remote_table group by 1,2 order by 1 DESc"
    
    cnxn_str = "user=%s password=%s host=%s dbname=%s port=%s" %\
           (denodoserver_uid, denodoserver_pwd, denodoserver_name, denodoserver_database, denodoserver_odbc_port)
    
    cnxn = dbdriver.connect(cnxn_str)
    data = pd.read_sql(query, cnxn)
    cnxn.close()
    return data

def estimate_consumedquantity(data, year, month):
    past_data = data[(data['year'] == year) & (data['month'] <= month)]
    if past_data.empty:
        past_data = data[(data['year'] < year)]
    return past_data['total_consumedquantity'].mean()    
      
                                               

def main():
    st.title("Prédictions des couts Azure")

    # recuperer les donnees historique 
    data = get_data()
    show_data = st.checkbox("data")
    if show_data:
        st.write(data)

 #les parametres d entrees 
    year = st.number_input("Année", min_value=2020, max_value=2021, value=2020)
    month = st.slider("Mois", min_value=1, max_value=12, value=1)
    # total_consumedquantity = st.number_input("quantité consommee", min_value=0, value=12213318)
   

    #estimation de total_consumedquantity a venir conclu a partir de la moyenne des mois precidents 

    quant = estimate_consumedquantity(data, year, month)
    total_consumedquantity = st.number_input("quantity consommée", value = quant)
    
    # total_consumedquantity = estimate_consumedquantity(data, year, month)
    # st.write(f"quantité consommée {total_consumedquantity:,.2f}") 
                                             
   
#configurer les parametres d saisi d user
    data = pd.DataFrame({
        "year": [year],
        "month": [month],
        "total_consumedquantity": [total_consumedquantity]
    })

    #button predict basé sur le model entrainé sur les 6 mois de l annee 2020
    if st.button("Prédire"):
        result = predict(data)
        st.write(f"Cout prédit: {result[0]:,.2f}")
    
if __name__ == '__main__':
    main()

    







