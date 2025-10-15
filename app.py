import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# Try importing streamlit but allow the module to be imported in environments
# where streamlit isn't installed (tests, CI). Provide a no-op cache decorator
# when streamlit is missing so load_data can still be executed.
try:
    import streamlit as st
    _cache = st.cache_data
    STREAMLIT_AVAILABLE = True
except Exception:
    st = None
    STREAMLIT_AVAILABLE = False

    def _cache(func):
        return func


@_cache
def load_data(path: str):
    df = pd.read_csv(path)
    # Basic cleaning / types
    if 'Year' in df.columns:
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
    # Normalize string columns
    str_cols = [
        c
        for c in [
            'Fintech_Used', 'Country', 'Gender', 'Age_Group', 
            'Use_Case_1', 'Use_Case_2', 'Urban_Rural', 'Phone_Type'
        ] if c in df.columns
    ]
    for c in str_cols:
        df[c] = df[c].fillna('Unknown').astype(str)
    # Ensure numeric columns exist
    for n in ['Monthly_Transactions', 'Avg_Transaction_Value']:
        if n not in df.columns:
            df[n] = 0
    return df


def kpis(df):
    total = len(df)
    fintech_users = df[df['Fintech_Used'].str.lower() == 'yes'] if 'Fintech_Used' in df.columns else df.iloc[0:0]
    fintech_count = len(fintech_users)
    adoption_rate = fintech_count / total * 100 if total else 0
    # Monthly average users: average fintech users per month (if Year available)
    monthly_avg_users = 0
    if 'Year' in df.columns:
        by_year = df[df['Fintech_Used'].str.lower() == 'yes'].groupby('Year').size()
        monthly_avg_users = by_year.mean() if not by_year.empty else 0
    # Total countries
    total_countries = df['Country'].nunique() if 'Country' in df.columns else 0
    return total, fintech_count, adoption_rate, monthly_avg_users, total_countries


def overview_page(df):
    st.header('Overview')
    total, fintech_count, adoption_rate, monthly_avg_users, total_countries = kpis(df)

    # KPI cards with colored backgrounds
    kpi_style = """
    <style>
    .kpi-card {
        background: #f5f5f5;
        border-radius: 12px;
        padding: 18px 10px 10px 18px;
        margin: 0 10px 0 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-width: 160px;
        min-height: 70px;
        text-align: center;
    }
    .kpi-label {
        font-size: 13px;
        color: #00796b;
        margin-bottom: 2px;
        text-align: center;
    }
    .kpi-value {
        font-size: 22px;
        font-weight: bold;
        color: #004d40;
        text-align: center;
    }
    </style>
    """
    st.markdown(kpi_style, unsafe_allow_html=True)
    kpi_html = f"""
    <div style='display: flex; flex-direction: row; justify-content: space-between; width: 100%;'>
        <div class='kpi-card'>
            <div class='kpi-label'>Total Respondents</div>
            <div class='kpi-value'>{total:,}</div>
        </div>
        <div class='kpi-card'>
            <div class='kpi-label'>Fintech Users</div>
            <div class='kpi-value'>{fintech_count:,}</div>
        </div>
        <div class='kpi-card'>
            <div class='kpi-label'>Adoption Rate (%)</div>
            <div class='kpi-value'>{adoption_rate:.1f}%</div>
        </div>
        <div class='kpi-card'>
            <div class='kpi-label'>Total Countries</div>
            <div class='kpi-value'>{total_countries}</div>
        </div>
    </div>
    """
    st.markdown(kpi_html, unsafe_allow_html=True)

    st.markdown('---')
    left, right = st.columns([2, 3])
    with left:
        st.subheader('Respondents by country (top 15)')
        country_counts = df['Country'].value_counts().reset_index()
        country_counts.columns = ['Country', 'Count']
        fig_bar = px.bar(
            country_counts.head(15), x='Count', y='Country', orientation='h',
            labels={'Count':'Respondents', 'Country':'Country'}, template='plotly_white'
        )
        fig_bar.update_layout(margin=dict(l=10,r=10,t=30,b=10), height=320, font=dict(size=11))
        st.plotly_chart(fig_bar, use_container_width=True)

    with right:
        st.subheader('Geographic distribution')
        try:
            fig_map = px.choropleth(
                country_counts, locations='Country', locationmode='country names',
                color='Count', scope='africa', title='Respondents by country', template='plotly_white'
            )
            fig_map.update_layout(margin=dict(l=10,r=10,t=30,b=10), height=320, font=dict(size=11))
            st.plotly_chart(fig_map, use_container_width=True)
        except Exception:
            st.info('Choropleth map could not be rendered (country names may not match).')


def trends_page(df):
    st.header('Trends')
    if 'Year' in df.columns:
        df_year = df.copy().dropna(subset=['Year'])
        df_year['Year'] = df_year['Year'].astype(int)

        total_by_year = df_year.groupby('Year').size().reset_index(name='Total')
        fintech_by_year = df_year[df_year['Fintech_Used'].str.lower() == 'yes'].groupby('Year').size().reset_index(name='Fintech_Users')
        merged = total_by_year.merge(fintech_by_year, on='Year', how='left').fillna(0)
        merged = merged.sort_values('Year')
        merged['Adoption_Rate'] = merged['Fintech_Users'] / merged['Total'] * 100

        a, b = st.columns(2)
        with a:
            st.subheader('Counts over time')
            fig = px.line(merged, x='Year', y=['Total', 'Fintech_Users'], labels={'value':'Count', 'variable':'Series'}, template='plotly_white')
            fig.update_layout(margin=dict(l=10,r=10,t=30,b=10), height=300, font=dict(size=11))
            st.plotly_chart(fig, use_container_width=True)

        with b:
            st.subheader('Adoption rate')
            fig2 = px.bar(merged, x='Year', y='Adoption_Rate', labels={'Adoption_Rate':'Adoption %'}, template='plotly_white')
            fig2.update_layout(margin=dict(l=10,r=10,t=30,b=10), height=300, font=dict(size=11))
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info('No Year column available.')


def demographics_page(df):
    st.header('Demographics')
    cols = st.columns([1, 1])
    with cols[0]:
        st.subheader('Gender vs Fintech usage')
        if 'Gender' in df.columns and 'Fintech_Used' in df.columns:
            ct = pd.crosstab(df['Gender'], df['Fintech_Used']).reset_index()
            fig = px.bar(ct, x='Gender', y=[c for c in ct.columns if c != 'Gender'], barmode='relative', template='plotly_white')
            fig.update_layout(margin=dict(l=10,r=10,t=30,b=10), height=300, font=dict(size=11))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info('Gender or Fintech_Used column missing')

    with cols[1]:
        st.subheader('Age group distribution')
        if 'Age_Group' in df.columns:
            ag = df['Age_Group'].value_counts().reset_index()
            ag.columns = ['Age_Group', 'Count']
            fig = px.pie(ag, names='Age_Group', values='Count', title='Age group share')
            fig.update_layout(margin=dict(l=10,r=10,t=30,b=10), height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info('Age_Group column missing')

    st.subheader('Phone type & urban/rural')
    if 'Phone_Type' in df.columns and 'Urban_Rural' in df.columns:
        pt = pd.crosstab(df['Phone_Type'], df['Urban_Rural']).reset_index()
        fig = px.bar(pt, x='Phone_Type', y=[c for c in pt.columns if c != 'Phone_Type'], barmode='group', template='plotly_white')
        fig.update_layout(margin=dict(l=10,r=10,t=30,b=10), height=300, font=dict(size=11))
        st.plotly_chart(fig, use_container_width=True)


def usecases_page(df):
    st.header('Use cases & Transactions')
    st.subheader('Top primary use cases')
    if 'Use_Case_1' in df.columns:
        uc = df['Use_Case_1'].replace('nan', 'Unknown').value_counts().reset_index()
        uc.columns = ['Use Case', 'Count']
        fig = px.bar(uc.head(15), x='Count', y='Use Case', orientation='h', template='plotly_white')
        fig.update_layout(margin=dict(l=10,r=10,t=30,b=10), height=300, font=dict(size=11))
        st.plotly_chart(fig, use_container_width=True)

    st.subheader('Monthly transactions distribution (positive only)')
    if 'Monthly_Transactions' in df.columns:
        sub = df[df['Monthly_Transactions'] > 0]
        if len(sub) > 0:
            fig = px.histogram(sub, x='Monthly_Transactions', nbins=30, template='plotly_white')
            fig.update_layout(margin=dict(l=10,r=10,t=30,b=10), height=300, font=dict(size=11))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info('No positive Monthly_Transactions values to show')


def conclusion_page(df):
    st.header('Conclusion')
    top_usecases = ['N/A']*3
    if 'Use_Case_1' in df.columns:
        uc = df['Use_Case_1'].replace('nan', 'Unknown').value_counts().head(3)
        top_usecases = uc.index.tolist()

    top_barriers = ['N/A']*3
    if 'Barrier' in df.columns:
        br = df['Barrier'].replace('nan', 'Unknown').value_counts().head(3)
        top_barriers = br.index.tolist()

    percent_active = 0
    if 'Fintech_Used' in df.columns:
        total = len(df)
        active = (df['Fintech_Used'].str.lower() == 'yes').sum()
        percent_active = (active / total * 100) if total else 0

    # Tile styling
    tile_style = """
    <style>
    .tile-container { display: flex; flex-direction: row; justify-content: space-between; gap: 24px; margin-top: 16px; flex-wrap: nowrap; }
    .tile-card { background: #ffffff; border-radius: 18px; padding: 22px; flex: 1; min-width: 0; max-width: 33%; min-height: 150px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; transition: transform 0.2s ease, box-shadow 0.2s ease; }
    .tile-card:hover { transform: translateY(-4px); box-shadow: 0 6px 14px rgba(0, 0, 0, 0.12); }
    .tile-label { font-size: 14px; color: #555555; margin-bottom: 10px; font-weight: 500; letter-spacing: 0.3px; }
    .tile-value { font-size: 18px; font-weight: 600; color: #222222; line-height: 1.6; }
    .tile-value span { display: block; font-size: 13px; color: #444444; border-bottom: 1px solid #e5e5e5; padding-bottom: 4px; margin-bottom: 4px; }
    .tile-value span:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
    @media screen and (max-width: 768px) { .tile-container { flex-wrap: wrap; } .tile-card { max-width: 100%; } }
    </style>
    """
    st.markdown(tile_style, unsafe_allow_html=True)

    usecase_html = "".join([f"<span>{uc}</span>" for uc in top_usecases])
    barrier_html = "".join([f"<span>{b}</span>" for b in top_barriers])

    tile_html = f"""
    <div class='tile-container'>
      <div class='tile-card'>
        <div class='tile-label'>Top 3 Use Cases</div>
        <div class='tile-value'>{usecase_html}</div>
      </div>
      <div class='tile-card'>
        <div class='tile-label'>Top 3 Barriers</div>
        <div class='tile-value'>{barrier_html}</div>
      </div>
      <div class='tile-card'>
        <div class='tile-label'>% Active Users</div>
        <div class='tile-value'>{percent_active:.1f}%</div>
      </div>
    </div>
    """
    st.markdown(tile_html, unsafe_allow_html=True)

    conclusion_text = """
    <div style='margin-top:28px; padding:16px 20px; background:#f5f5f5; border-radius:10px; font-size:15px; color:#333; line-height:1.6;'>
    <b>Conclusion:</b> Fintech adoption in Africa is growing steadily, driven by popular use cases like bill payments, P2P transfers, and airtime top-ups. However, persistent barriers such as lack of trust, network issues, and digital literacy gaps continue to slow broader adoption. Addressing these barriers will unlock new opportunities for financial inclusion and innovation.
    </div>
    """
    st.markdown(conclusion_text, unsafe_allow_html=True)


def main():
    df = load_data('datasets/fintech_usage_africa.csv')
    page = st.sidebar.selectbox('Select Page', ['Overview', 'Trends', 'Demographics', 'Conclusion'])

    # Filters only for non-Conclusion pages
    if page != 'Conclusion':
        filter_cols = st.columns([1, 1, 1, 1, 1])
        with filter_cols[0]:
            countries = ['All'] + sorted(df['Country'].dropna().unique().tolist()) if 'Country' in df.columns else ['All']
            country = st.selectbox('Country', countries, index=0, key=f'country_filter_{page}')
        with filter_cols[1]:
            years = None
            if 'Year' in df.columns:
                min_y = int(df['Year'].dropna().min())
                max_y = int(df['Year'].dropna().max())
                years = st.slider('Year range', min_value=min_y, max_value=max_y, value=(min_y, max_y), key=f'year_filter_{page}')
        with filter_cols[2]:
            genders = ['All'] + sorted(df['Gender'].dropna().unique().tolist()) if 'Gender' in df.columns else ['All']
            gender = st.selectbox('Gender', genders, index=0, key=f'gender_filter_{page}')
        with filter_cols[3]:
            ages = ['All'] + sorted(df['Age_Group'].dropna().unique().tolist()) if 'Age_Group' in df.columns else ['All']
            age_group = st.selectbox('Age group', ages, index=0, key=f'age_filter_{page}')
        with filter_cols[4]:
            location = ['All'] + sorted(df['Urban_Rural'].dropna().unique().tolist()) if 'Urban_Rural' in df.columns else ['All']
            location_sel = st.selectbox('Location', location, index=0, key=f'location_filter_{page}')
    else:
        country = gender = age_group = location_sel = years = None

    # Apply filters
    df_filtered = df.copy()
    if country and country != 'All':
        df_filtered = df_filtered[df_filtered['Country'] == country]
    if years is not None:
        df_filtered = df_filtered[(df_filtered['Year'] >= years[0]) & (df_filtered['Year'] <= years[1])]
    if gender and gender != 'All':
        df_filtered = df_filtered[df_filtered['Gender'] == gender]
    if age_group and age_group != 'All':
        df_filtered = df_filtered[df_filtered['Age_Group'] == age_group]
    if location_sel and location_sel != 'All':
        df_filtered = df_filtered[df_filtered['Urban_Rural'] == location_sel]

    if page == 'Overview':
        overview_page(df_filtered)
    elif page == 'Trends':
        trends_page(df_filtered)
    elif page == 'Demographics':
        demographics_page(df_filtered)
    elif page == 'Conclusion':
        conclusion_page(df_filtered)


if __name__ == '__main__':
    main()
