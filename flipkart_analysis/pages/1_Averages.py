import pandas as pd
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go
     
####################
###IMPORTING DATA###
####################

st.set_page_config(
    page_title='Flipkart Data',
    page_icon=r'flipkart-icon.png',
    layout='wide'
)

@st.cache_data
def get_data_from_csv():
    df=pd.read_csv(r'src/flipkart_scraping_output.csv',index_col=0)
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
    st.image(r'flipkart-icon.png')
    st.title('Flipkart Data')

###################
###VISUALIZATION###
###################

#---Average Discount Percentage by Brand---#
fig_brand_percentage = px.bar(
    percentage_sorted,
    x=percentage_sorted.index,
    y='DISCOUNT PERCENTAGE',
    title='<b>Average Discount Percentage by Brand</b>',
    color_discrete_sequence=['#3279BD'],
)
fig_brand_percentage.update_layout(
    xaxis_title='Brand Name',
    yaxis=dict(title='Discount Percentage', range=[0, 65]),
)
    
right_column.plotly_chart(fig_brand_percentage, use_container_width=True)
st.markdown('---')

#---Average Price by Brand---#
fig_price_sorted = go.Figure()
fig_true_sorted = fig_price_sorted.add_trace(go.Bar(
    x=true_price_sorted.index,
    y=true_price_sorted.values,
    name='True Price',
    marker_color='#F5DF1F'
))

fig_discount_sorted = fig_price_sorted.add_trace(go.Bar(
    x=discount_sorted.index,
    y=discount_sorted.values,
    name='Discount Price',
    marker_color='#3279BD'
))

fig_price_sorted.update_layout(
    title='<b>Average Price by Brand</b>',
    template='plotly_white',
    legend=dict(
        yanchor="top",
        y=1,
        xanchor="right",
        x=1
    ),
    xaxis=dict(title='Brand Name', tickangle=45),
    yaxis=dict(
        title='Price',
        range=[0, 200000]
    )
)

#---Average Rating vs Average Discount Price by Brand---#
fig_rating_discount = go.Figure()
 
fig_rating_sorted = fig_rating_discount.add_trace(go.Scatter(
    x=rating_sorted.index,
    y=rating_sorted.values,
    name='Rating',
    mode='lines',
    line=dict(color='#F5DF1F', width=2),
    opacity=0.7,
    yaxis='y2'
))

fig_disc_rating_sorted = fig_rating_discount.add_trace(go.Bar(
    x=discount_sorted.index,
    y=discount_sorted.values,
    name='Discount Price',
    marker_color='#3279BD',
    yaxis='y'
))
for brand, rating in zip(rating_sorted.index, rating_sorted.values):
    fig_rating_discount.add_annotation(
        x=brand,
        y=rating+0.3,
        text=str(round(rating,1)),
        yref='y2',
        showarrow=False,
        font=dict(
            size=14,
            color="#F5DF1F"
        )
    )

if 0 in rating_sorted.values:
    brands_with_no_ratings = brand_mean.loc[brand_mean['RATING'] == 0].index.tolist()
    no_ratings_text = f"No Ratings for {', '.join(brands_with_no_ratings)}"
    fig_rating_discount.add_trace(go.Scatter(
        mode='none',
        name=no_ratings_text,
        marker=dict(color='rgba(0,0,0,0)'),
        legendgroup='No Ratings',
        showlegend=True,
    ))

fig_rating_discount.update_layout(
    title='<b>Average Rating vs Average Discount Price by Brand</b>',
    xaxis=dict(title='Brand Name', tickangle=45),
    yaxis=dict(title='Discount Price', range=[0, 200000], gridcolor='rgba(50, 121, 189, 0.3)'),
    yaxis2=dict(title='Rating', range=[0, 5.2], overlaying='y', gridcolor='rgba(245, 223, 31, 0.3)', side='right'),
    legend=dict(
        yanchor="bottom",
        y=1,
        xanchor="right",
        x=1,
        traceorder="normal",
        itemsizing='constant',
    )
)

left_column, right_column = st.columns(2)
left_column.plotly_chart(fig_price_sorted, use_container_width=True)
right_column.plotly_chart(fig_rating_discount, use_container_width=True)

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