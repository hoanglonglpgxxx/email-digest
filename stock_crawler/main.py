from vnstock import *
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go

def format_vnd_price(price):
    """Convert vnstock price (in thousands) to full VND with two decimals."""
    full_price = price * 1000
    return f"{full_price:,.2f} VND"

def format_price_delta(current, previous):
    """Compute delta in full VND."""
    return f"{(current - previous) * 1000:,.2f}"


# Page configuration
st.set_page_config(
    page_title="Vietnam Stock Data Crawler",
    page_icon="📈",
    layout="wide"
)

# Title and description
st.title("📈 Vietnam Stock Data Crawler")
st.caption("Real-time Vietnam stock market data powered by vnstock. Only for personal use; respect copyrights.")

# Sidebar inputs
st.sidebar.header("Stock Configuration")
symbol = st.sidebar.text_input("Stock Symbol", value="MBB", placeholder="Enter symbol (e.g., MBB, VIC, FPT)")
source = st.sidebar.selectbox(
    "Data Source",
    ["VCI", "TCBS", "MSN"],
    help="Choose your preferred data source"
)

# Date inputs
col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30))
with col2:
    end_date = st.date_input("End Date", value=datetime.now())

# Main content area
if symbol:
    try:
        with st.spinner(f"Fetching data for {symbol.upper()}..."):
            # Initialize stock object
            stock = Vnstock().stock(symbol=symbol.upper(), source=source)

            # Create tabs for different data views
            tab1, tab2, tab3, tab4 = st.tabs(
                ["📊 Current Price", "📈 Historical Data", "🏢 Company Info", "💰 Price Board"])

            with tab1:
                st.subheader(f"Current Stock Price - {symbol.upper()}")
                current_data = stock.quote.history(
                    start=datetime.now().strftime('%Y-%m-%d'),
                    end=datetime.now().strftime('%Y-%m-%d'),
                    interval='1D'
                )
                if not current_data.empty:
                    latest = current_data.iloc[-1]
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric(
                            label="Close Price",
                            value=format_vnd_price(latest['close']),
                            delta=format_price_delta(latest['close'], latest['open'])
                        )
                    with col2:
                        st.metric(label="Volume", value=f"{latest['volume']:,}")
                    with col3:
                        st.metric(label="High", value=format_vnd_price(latest['high']))
                    with col4:
                        st.metric(label="Low", value=format_vnd_price(latest['low']))

                    st.subheader("Today's Trading Data")
                    display_df = current_data.copy()
                    for col in ['open', 'high', 'low', 'close']:
                        display_df[col] = display_df[col] * 1000
                    st.dataframe(display_df.round(2), use_container_width=True)
                else:
                    st.warning("No current data available.")

            with tab2:
                st.subheader(f"Historical Price Chart - {symbol.upper()}")

                # Get historical data
                historical_data = stock.quote.history(
                    start=start_date.strftime('%Y-%m-%d'),
                    end=end_date.strftime('%Y-%m-%d'),
                    interval='1D'
                )

                if not historical_data.empty:
                    # Create candlestick chart
                    fig = go.Figure(data=go.Candlestick(
                        x=historical_data.index,
                        open=historical_data['open'],
                        high=historical_data['high'],
                        low=historical_data['low'],
                        close=historical_data['close'],
                        name=f"{symbol.upper()} Stock Price"
                    ))

                    fig.update_layout(
                        title=f"{symbol.upper()} Stock Price Movement",
                        xaxis_title="Date",
                        yaxis_title="Price (VND)",
                        height=500,
                        showlegend=False
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    # Display statistics
                    col1, col2 = st.columns(2)

                    with col1:
                        st.subheader("Price Statistics")
                        stats_df = pd.DataFrame({
                            'Metric': ['Average Close', 'Max Close', 'Min Close', 'Volatility (%)'],
                            'Value': [
                                f"{historical_data['close'].mean():,.0f} VND",
                                f"{historical_data['close'].max():,.0f} VND",
                                f"{historical_data['close'].min():,.0f} VND",
                                f"{(historical_data['close'].std() / historical_data['close'].mean() * 100):.2f}%"
                            ]
                        })
                        st.dataframe(stats_df, hide_index=True, use_container_width=True)

                    with col2:
                        st.subheader("Recent Historical Data")
                        st.dataframe(historical_data.tail(10), use_container_width=True)

                else:
                    st.error("No historical data found for the selected date range.")

            with tab3:
                st.subheader(f"Company Information - {symbol.upper()}")

                try:
                    # Get company overview
                    company_info = stock.company.overview()

                    if not company_info.empty:
                        info = company_info.iloc[0]

                        col1, col2 = st.columns(2)

                        with col1:
                            st.write("**Exchange:**", info.get('exchange', 'N/A'))
                            st.write("**Industry:**", info.get('industry', 'N/A'))
                            st.write("**Outstanding Shares:**", f"{info.get('outstandingShare', 0):,.0f}")

                        with col2:
                            st.write("**Market Cap:**",
                                     f"{info.get('marketCap', 0):,.0f} VND" if 'marketCap' in info else 'N/A')
                            st.write("**P/E Ratio:**", f"{info.get('pe', 0):.2f}" if 'pe' in info else 'N/A')
                            st.write("**EPS:**", f"{info.get('eps', 0):,.0f}" if 'eps' in info else 'N/A')

                        st.subheader("Complete Company Data")
                        st.dataframe(company_info, use_container_width=True)

                    else:
                        st.warning("Company information not available.")

                except Exception as e:
                    st.error(f"Could not fetch company information: {str(e)}")

            with tab4:
                st.subheader(f"Live Price Board - {symbol.upper()}")

                try:
                    # Get price board data
                    trading = Trading(source=source)
                    price_board = trading.price_board([symbol.upper()])

                    if not price_board.empty:
                        st.dataframe(price_board, use_container_width=True)
                    else:
                        st.warning("Price board data not available.")

                except Exception as e:
                    st.error(f"Could not fetch price board: {str(e)}")

    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        st.info("Please check if:")
        st.write("- The stock symbol is correct (e.g., MBB, VIC, FPT)")
        st.write("- The symbol is listed on Vietnam stock exchanges")
        st.write("- Your internet connection is stable")

        # Display formatted raw data
        st.subheader("Today's Trading Data")
        display_data = current_data.copy()

        # Format price columns
        price_columns = ['open', 'high', 'low', 'close']
        for col in price_columns:
            if col in display_data.columns:
                display_data[col] = display_data[col].apply(
                    lambda x: x * 1000 if x < 100 and x > 0 else x
                )

        st.dataframe(display_data.round(2), use_container_width=True)


else:
    st.info("Please enter a stock symbol to get started.")

    # Show instructions
    st.subheader("How to Use")
    st.write("1. Enter a Vietnam stock symbol (e.g., MBB, VIC, FPT)")
    st.write("2. Select your preferred data source")
    st.write("3. Choose date range for historical data")
    st.write("4. Explore different tabs for various information")

# Footer
st.markdown("---")
st.markdown("*Data provided by vnstock library. For educational purposes only.*")
