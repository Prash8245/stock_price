from select import select
import pandas as pd
from alpha_vantage.timeseries import TimeSeries
import streamlit as st
from statsmodels.tsa.seasonal import seasonal_decompose
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from pmdarima import auto_arima

st.set_page_config(
     page_title="Stock Price Prediction App",
     page_icon=":chart_with_upwards_trend:",
     layout="wide",
     initial_sidebar_state="expanded",
     menu_items={
         'Get Help': 'https://www.alphavantage.co/documentation/',
         'About': "This App is Created By **Prashanth**"
     }
 )
st.cache(suppress_st_warning=True)


st.image("image.jpg",)
st.title("Stock Price Prediction")

api_key = 'IVJUYAOTBM2RG2BI'
ts = TimeSeries(key=api_key, output_format='pandas')

sym = None
#st.write(type(sym))
sym = st.text_input('Enter the Stock Symbol For Prediction with .BSE extention')

if sym:
    data,meta_data = ts.get_daily(symbol=sym,outputsize='full')
    st.header("First 10 Data")
    st.write(data.head(10))  


    def assign(data2):
        value = pd.DataFrame(data2)                             #To predict Open Values
        value = value.asfreq('B',method='pad')
        return value


    open_ = assign(data['1. open'])
    high = assign(data['2. high'])
    low = assign(data['3. low'])
    close = assign(data['4. close'])


    decom = seasonal_decompose(high,model='additive')
    observed = decom.observed
    Trend = decom.trend
    seasonality = decom.seasonal

    dic = {
            'Observed' : observed,
            'Trend' : Trend,
            'Seasonality' : seasonality
        }

    daf = pd.DataFrame(dic)


    select = st.sidebar.selectbox('SELECT',('Select','Chart','Prediction','Previous History'))
    if(select == 'Chart'):
        st.subheader('Company Chart')
        high1 = pd.DataFrame(data['2. high'])
        st.line_chart(high1)

        st.subheader('Volume of Stock Sold')
        chr = pd.DataFrame(data['5. volume'])
        chr = chr.iloc[:100,:]
        high2 = pd.DataFrame(chr)
        st.line_chart(high2)

        st.subheader('Observed , Trend , Seasonality')
        inp = daf.iloc[:100,:]
        st.line_chart(inp)

    elif(select == 'Previous History'):
        st.subheader('Enter the Date to search')
        date_1= st.text_input('Enter the Date in YYYY-MM-DD Format')
        date_1= date_1+'T00:00:00'
        if(date_1):
            try:
                res = data.loc[date_1]
                st.write(res)
                st.write(meta_data)

            except:
                st.write("**This is Not A business Date Please Re-enter**")

    elif(select=='Select'):
        pass

    elif(select == 'Prediction'):
        def mode(data3):
            res = auto_arima(data3,trace=True)
            param = res.get_params()
            order1 = param['order']
            p = order1[0]
            d = order1[1]
            q = order1[2]

            model = ARIMA(data3, order=(p, d, q))
            m_fit = model.fit()
            pred = m_fit.forecast(10)
            pred = pd.DataFrame(pred)
            return pred

        pred_open = mode(open_)
        pred_high = mode(high)
        pred_low = mode(low)
        pred_close = mode(close)

        predicted = {
            'Open' : pred_open['predicted_mean'],
            'High' : pred_high['predicted_mean'],
            'Low' : pred_low['predicted_mean'],
            'Close' : pred_close['predicted_mean']
        }
        df = pd.DataFrame(predicted)
        #st.write(df)

        st.subheader('Enter the Date {should be less than 10 days far}')
        date_ = st.text_input('Enter the Date in YYYY-MM-DD Format')
        date_= date_+'T00:00:00'
        if(date_):
            try:
                predi = df.loc[date_]
                st.write(predi)

            except:
                st.write("**This is Not A business Date Please Re-enter**")


