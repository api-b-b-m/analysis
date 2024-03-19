import pandas as pd
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go
     
####################
###IMPORTING DATA###
####################

st.set_page_config(
    page_title='Flipkart Data',
    page_icon='flipkart-icon.png',
    layout='wide'
)

@st.cache_data
def get_data_from_csv():
    df=pd.read_csv('src/flipkart_scraping_output.csv',index_col=0)
    return df

####################
###FILTERING DATA###
####################

flip_df=get_data_from_csv()
flip_df.loc[flip_df['BRAND NAME']=='Hp','BRAND NAME']='HP'
flip_df.loc[flip_df['BRAND NAME']=='Msi','BRAND NAME']='MSI'
flip_df.loc[flip_df['BRAND NAME']=='Axl','BRAND NAME']='AXL'
flip_df.loc[flip_df['BRAND NAME']=='Iball','BRAND NAME']='iBall'
flip_df['RATING'].fillna(0,inplace=True)
flip_df['DISCOUNT PERCENTAGE'].fillna(0,inplace=True)
unique_brands=flip_df['BRAND NAME'].unique()
unique_rating=sorted(flip_df['RATING'].unique())
unique_price=sorted(flip_df['DISCOUNT PRICE'].unique())
unique_percentage=sorted(flip_df['DISCOUNT PERCENTAGE'].unique())

def filter_rating(filter_df):
    filter_rating_df=pd.DataFrame()
    filter_unique_rating=unique_rating
    filter_start_rating=float(rating_pin)
    filter_stop_rating=float(rating_cap)
    filter_start_index=filter_unique_rating.index(filter_start_rating)
    filter_stop_index=filter_unique_rating.index(filter_stop_rating)+1
    rating_filtered=filter_unique_rating[filter_start_index:filter_stop_index]
    filter_rating_df=filter_df[filter_df['RATING'].isin(rating_filtered)]
    return filter_rating_df

def filter_price(filter_df):
    filter_price_df=pd.DataFrame()
    filter_unique_price=unique_price
    filter_start_price=int(price_pin)
    filter_stop_price=int(price_cap)
    filter_start_index=filter_unique_price.index(filter_start_price)
    filter_stop_index=filter_unique_price.index(filter_stop_price)+1
    price_filtered=filter_unique_price[filter_start_index:filter_stop_index]
    filter_price_df=filter_df[filter_df['DISCOUNT PRICE'].isin(price_filtered)]
    return filter_price_df

def filter_percentage(filter_df):
    filter_percentage_df=pd.DataFrame()
    filter_unique_percentage=unique_percentage
    filter_start_percentage=int(percentage_pin)
    filter_stop_percentage=int(percentage_cap)
    filter_start_index=filter_unique_percentage.index(filter_start_percentage)
    filter_stop_index=filter_unique_percentage.index(filter_stop_percentage)+1
    percentage_filtered=filter_unique_percentage[filter_start_index:filter_stop_index]
    filter_percentage_df=filter_df[filter_df['DISCOUNT PERCENTAGE'].isin(percentage_filtered)]
    return filter_percentage_df
     
#############
###SIDEBAR###
#############

st.sidebar.header('Please Choose Filter:')
brand_selection=st.sidebar.selectbox(
    'Brands:', ['All available brands','Select brands manually']
)    
if brand_selection == 'Select brands manually':
    brand = st.sidebar.multiselect(
        'Select the brands manually:',
        options=unique_brands,
        key='manual_brand_selection'
    )
elif brand_selection == 'All available brands':
    brand = unique_brands
else:
    st.warning('Please select at least one brand')

df_brand_selection=flip_df[flip_df['BRAND NAME'].isin(brand)]

rating_pin,rating_cap=st.sidebar.select_slider('Select the rating range:', unique_rating, [0, 5.0])
price_pin,price_cap=st.sidebar.select_slider('Select the price range:', unique_price, [8000, 361990])
percentage_pin,percentage_cap=st.sidebar.select_slider('Select the discount range:', unique_percentage, [0, 71])

filtered_rating=filter_rating(df_brand_selection)
filtered_price=filter_price(filtered_rating)
filtered_percentage=filter_percentage(filtered_price)
brand_mean=filtered_percentage.groupby('BRAND NAME').mean(numeric_only=True)
discount_sorted=brand_mean['DISCOUNT PRICE'].sort_values(ascending=False)
rating_sorted=brand_mean['RATING'].sort_values(ascending=False)
true_price_sorted=brand_mean['TRUE PRICE'].sort_values(ascending=False)
percentage_sorted=brand_mean['DISCOUNT PERCENTAGE'].sort_values(ascending=False)

###########
###TITLE###
###########

left_column, right_column = st.columns(2)
with left_column:
    st.image('flipkart-icon.png')
    st.title('Flipkart Data')

###################
###VISUALIZATION###
###################

#---Rating vs True Price---#
na_ratings=filtered_percentage.loc[(filtered_percentage['RATING'] != 0) | ((filtered_percentage['RATING COUNT'] != 0) & (~filtered_percentage['RATING COUNT'].isna()))]
fig_true_rating = px.scatter(
    na_ratings,
    x='RATING',
    y='TRUE PRICE',
    color='BRAND NAME',
    title='<b>Rating vs True Price</b>',
)
fig_true_rating.update_layout(
    xaxis_title='Rating',
    yaxis_title='True Price'
)

right_column.plotly_chart(fig_true_rating, use_container_width=True)

#---Discount Price vs True Price---#
fig_true_discount = px.scatter(
    filtered_percentage,
    x='DISCOUNT PRICE',
    y='TRUE PRICE',
    color='BRAND NAME',
    title='<b>Discount Price vs True Price</b>',
)
fig_true_discount.update_layout(
    xaxis_title='Discount Price',
    yaxis_title='True Price'
)

#---Discount Percentage vs True Price---#
fig_true_percentage = px.scatter(
    filtered_percentage,
    x='DISCOUNT PERCENTAGE',
    y='TRUE PRICE',
    color='BRAND NAME',
    title='<b>Discount Percentage vs True Price</b>',
)
fig_true_percentage.update_layout(
    yaxis=dict(title='True Price', range=[0, 500000]),
    xaxis=dict(title='Discount Percentage', range=[0, 75]),
)

left_column, right_column = st.columns(2)
left_column.plotly_chart(fig_true_discount, use_container_width=True)
right_column.plotly_chart(fig_true_percentage, use_container_width=True)

######################
###STREAMLIT STYLES###
######################

custom_css = """
<style>
/* Customize select_slider background color */
div[data-testid="stSlider"] .de1vC {
    background-color: #262730 !important;
}
/* Customize select_slider handle color */
div[data-testid="stSlider"] .dq2wD {
    background-color: #262730 !important;
    border-color: #F5DF1F !important;
}
/* Customize text color */
div[data-testid="stText"] {
    color: white !important;
}
</style>
"""

hide_st_style="""
<style>
#Mainmenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}
</style>
"""

#---Apply custom CSS styles---#
st.markdown(custom_css, unsafe_allow_html=True)
st.markdown(hide_st_style,unsafe_allow_html=True)