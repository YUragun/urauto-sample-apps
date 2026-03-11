import os
import sys
import logging
import subprocess
import time
import traceback
from typing import Dict, Any

import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# --------------------------------------------------------------------
# Helper – API keys
# --------------------------------------------------------------------

def get_api_key(provider: str) -> str | None:
    provider = provider.upper()
    if provider == "OPENAI":
        return st.session_state.get("openai_api_key") or os.getenv("OPENAI_API_KEY")
    if provider == "ANTHROPIC":
        return st.session_state.get("anthropic_api_key") or os.getenv("ANTHROPIC_API_KEY")
    return None

# --------------------------------------------------------------------
# Session initialiser (replaces legacy initialize())
# --------------------------------------------------------------------

def initialize() -> None:
    st.session_state["pattern_recognition_settings"] = {"history": []}

# --------------------------------------------------------------------
# ANALYSIS HELPERS (time‑series shown; others unchanged)
# --------------------------------------------------------------------

def perform_time_series_analysis(data: pd.DataFrame, column: str, periods: int = 10) -> Dict[str, Any]:
    try:
        from statsmodels.tsa.seasonal import seasonal_decompose
        from statsmodels.tsa.arima.model import ARIMA
        from statsmodels.tsa.stattools import adfuller
    except ImportError:
        st.warning("Installing statsmodels…")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "statsmodels"])
        from statsmodels.tsa.seasonal import seasonal_decompose
        from statsmodels.tsa.arima.model import ARIMA
        from statsmodels.tsa.stattools import adfuller

    series = data[column].sort_index()
    res: Dict[str, Any] = {}
    adf = adfuller(series.dropna())
    res["stationarity"] = {"test_statistic": adf[0], "p_value": adf[1], "is_stationary": adf[1] < 0.05}
    if len(series) >= 12:
        dec = seasonal_decompose(series, model="additive", period=min(12, len(series)//2))
        res["decomposition"] = {"trend": dec.trend, "seasonal": dec.seasonal, "residual": dec.resid}
    try:
        model = ARIMA(series, order=(1, 1, 1)).fit()
        fc = model.forecast(steps=periods)
        last = series.index[-1]
        if isinstance(last, pd.Timestamp):
            idx = pd.date_range(start=last, periods=periods+1, freq=pd.infer_freq(series.index) or "D")[1:]
        else:
            idx = np.arange(last+1, last+periods+1)
        res["forecast"], res["forecast_index"] = fc, idx
    except Exception as e:
        res["forecast_error"] = str(e)
    res["original_data"] = series
    return res

# --------------------------------------------------------------------
# MAIN UI
# --------------------------------------------------------------------

def pattern_recognition_ui() -> None:

    """Render UI – now using Streamlit's *wide* mode to maximise space."""

    # IMPORTANT: this must run before any other st.* calls in the session that has not
    # already configured the page.  If another page in a multi‑page app called
    # set_page_config earlier (e.g. with layout="centered"), our layout won't change.
    # To guarantee width we therefore ALSO override Streamlit's default max‑width with CSS.
    st.set_page_config(page_title="Pattern Recognition", layout="wide")

    # ----------------------------------------------------------------
    # CSS tweaks – kill the built‑in ~700 px cap even if another page
    # configured a centred layout earlier, but keep a bit of padding.
    # ----------------------------------------------------------------
    st.markdown(
        """
        <style>
          .stVerticalBlock{gap:0.75rem !important;}
          /* Remove the hard‑coded max‑width so the app can really stretch */
          .appview-container .main .block-container{
              padding-left:2rem;
              padding-right:2rem;
              padding-top:3rem;
              max-width:100% !important;   /* <-- key change */
          }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Session defaults
    st.session_state.setdefault("openai_api_key", "")
    st.session_state.setdefault("anthropic_api_key", "")
    if "pattern_recognition_settings" not in st.session_state:
        initialize()

    tab_main, tab_settings = st.tabs(["Pattern Recognition", "Settings"])

    # -- Settings -----------------------------------------------------
    with tab_settings:
        st.subheader("API Keys (session only)")
        oa = st.text_input("OpenAI API Key", type="password", value=st.session_state["openai_api_key"])
        if oa:
            st.session_state["openai_api_key"] = oa
        an = st.text_input("Anthropic API Key", type="password", value=st.session_state["anthropic_api_key"])
        if an:
            st.session_state["anthropic_api_key"] = an
        for prov in ("OPENAI", "ANTHROPIC"):
            if get_api_key(prov):
                st.success(f"{prov.title()} key set ✓")
        st.caption("Keys live only in your browser session – never saved server‑side.")

                        
    # -- Main tab ------------------------------------------------------
    with tab_main:
        _render_full_ui()

# -------------------------------------------------------------------
# The full UI body (copied from the user's source) lives in the helper
# below.  It is unchanged except that initialize() now exists.
# -------------------------------------------------------------------

def _render_full_ui() -> None:
    """Large body with data load, analysis tabs, AI features, etc."""

    st.title("Pattern Recognition")
    
    # Initialize pattern recognition settings if not already initialized
    if 'pattern_recognition_settings' not in st.session_state:
        initialize()
    
    # Initialize session state for data
    if 'data' not in st.session_state:
        st.session_state.data = None
    
    # Initialize AI results state if not there
    if 'time_series_ai_results' not in st.session_state:
        st.session_state.time_series_ai_results = None
    
    # Introduction
    st.write("""
    This feature allows you to analyze data, detect patterns, and build predictive models 
    using various machine learning techniques and AI-powered pattern analysis.
    """)
    
    # Data loading section
    with st.expander("🔍 Load Data", expanded=True):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # File upload
            uploaded_file = st.file_uploader(
                "Upload your data file",
                type=["csv", "xlsx", "txt"],
                help="Upload a CSV, Excel, or text file with your data"
            )
        
        with col2:
            # Example data option
            use_example_data = st.checkbox("Use example data instead")
            
            # Check for API key availability
            openai_key = get_api_key('OPENAI')
            anthropic_key = get_api_key('ANTHROPIC')
            
            ai_available = bool(openai_key or anthropic_key)
            
            if not ai_available:
                st.info("💡 Connect OpenAI or Anthropic API keys in Settings to enable AI-powered analysis.")
    
    # Load data based on user selection
    if uploaded_file is not None:
        try:
            # Determine file type and read accordingly
            file_extension = uploaded_file.name.split(".")[-1].lower()
            
            if file_extension == "csv":
                data = pd.read_csv(uploaded_file)
            elif file_extension == "xlsx":
                data = pd.read_excel(uploaded_file)
            elif file_extension == "txt":
                data = pd.read_csv(uploaded_file, delimiter="\t")
            
            st.success(f"Successfully loaded data with {data.shape[0]} rows and {data.shape[1]} columns.")
            st.session_state.data = data
            
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
    
    elif use_example_data:
        # Let user choose which type of example data
        example_data_type = st.selectbox(
            "Select example data type", 
            [
                "Time Series", 
                "Clustering", 
                "Regression", 
                "Classification",
                "Association Rules"
            ]
        )
        
        # Generate example data based on the selected type
        if example_data_type == "Time Series":
            # Generate time series data
            date_rng = pd.date_range(start='2020-01-01', periods=100, freq='D')
            data = pd.DataFrame(date_rng, columns=['date'])
            data['value'] = np.sin(np.arange(100) * 0.1) * 10 + np.random.randn(100) * 2 + 20
            data.set_index('date', inplace=True)
            
        elif example_data_type == "Clustering":
            # Generate clustering data
            try:
                from sklearn.datasets import make_blobs
                X, y = make_blobs(n_samples=200, centers=3, n_features=2, random_state=42)
                data = pd.DataFrame(X, columns=['feature1', 'feature2'])
                data['target'] = y
            except ImportError:
                # Fallback if sklearn not available
                np.random.seed(42)
                cluster1 = np.random.normal(0, 1, (100, 2))
                cluster2 = np.random.normal(5, 1, (100, 2))
                X = np.vstack([cluster1, cluster2])
                y = np.array([0] * 100 + [1] * 100)
                data = pd.DataFrame(X, columns=['feature1', 'feature2'])
                data['target'] = y
            
        elif example_data_type == "Regression":
            # Generate regression data
            try:
                from sklearn.datasets import make_regression
                X, y = make_regression(n_samples=100, n_features=3, noise=10, random_state=42)
                data = pd.DataFrame(X, columns=['feature1', 'feature2', 'feature3'])
                data['target'] = y
            except ImportError:
                # Fallback if sklearn not available
                np.random.seed(42)
                X = np.random.rand(100, 3) * 10
                y = 2 * X[:, 0] + 3 * X[:, 1] - 1.5 * X[:, 2] + np.random.normal(0, 2, 100)
                data = pd.DataFrame(X, columns=['feature1', 'feature2', 'feature3'])
                data['target'] = y
            
        elif example_data_type == "Classification":
            # Generate classification data
            try:
                from sklearn.datasets import make_classification
                X, y = make_classification(n_samples=100, n_features=4, n_informative=2, 
                                           n_redundant=0, random_state=42)
                data = pd.DataFrame(X, columns=['feature1', 'feature2', 'feature3', 'feature4'])
                data['target'] = y
            except ImportError:
                # Fallback if sklearn not available
                np.random.seed(42)
                X = np.random.rand(100, 4) * 10
                # Simple decision boundary: if feature1 + feature2 > feature3 + feature4
                y = (X[:, 0] + X[:, 1] > X[:, 2] + X[:, 3]).astype(int)
                data = pd.DataFrame(X, columns=['feature1', 'feature2', 'feature3', 'feature4'])
                data['target'] = y
            

        elif example_data_type == "Association Rules":
            # Generate transaction data
            items = ['bread', 'milk', 'cheese', 'apples', 'eggs', 'yogurt', 'juice', 'cereal']
            n_transactions = 100
            
            # Create random transactions
            transactions = []
            for _ in range(n_transactions):
                n_items = np.random.randint(1, 5)
                transaction = np.random.choice(items, size=n_items, replace=False)
                transactions.append(transaction)
            
            # Convert to one-hot encoded DataFrame
            data = pd.DataFrame([[item in transaction for item in items] for transaction in transactions], 
                              columns=items).astype(int)
        
        # Store data in session state
        st.session_state.data = data
        st.success(f"Using example {example_data_type} data with {data.shape[0]} rows and {data.shape[1]} columns.")
    
    def analyze_patterns_with_ai(data, analysis_type, question, model="openai"):
        """
        Use AI (OpenAI or Anthropic) to analyze patterns in data
        
        Parameters:
        - data: pandas DataFrame or description of data
        - analysis_type: Type of analysis being performed
        - question: User's question about the data patterns
        - model: Which AI model to use ("openai" or "anthropic")
        
        Returns:
        - Dictionary with AI analysis results
        """
        try:
            # Get the appropriate API key
            if model.lower() == "openai":
                api_key = get_api_key('OPENAI')
                if not api_key:
                    return {
                        "error": "OpenAI API key not found. Please add it in the settings.",
                        "result": None
                    }
                return call_openai_for_pattern_analysis(data, analysis_type, question, api_key)
            
            elif model.lower() == "anthropic":
                api_key = get_api_key('ANTHROPIC')
                if not api_key:
                    return {
                        "error": "Anthropic API key not found. Please add it in the settings.",
                        "result": None
                    }
                return call_anthropic_for_pattern_analysis(data, analysis_type, question, api_key)
            
            else:
                return {
                    "error": f"Unknown model: {model}",
                    "result": None
                }
                
        except Exception as e:
            logger.error(f"Error in AI pattern analysis: {e}")
            traceback.print_exc()
            return {
                "error": str(e),
                "result": None
            }

    def call_openai_for_pattern_analysis(data, analysis_type, question, api_key):
        """Call OpenAI API for pattern analysis using direct HTTP requests"""
        try:
            import requests
            
            # Convert DataFrame to summary or sample if needed
            data_summary = ""
            if isinstance(data, pd.DataFrame):
                # Create a summary of the data
                data_summary = f"""
    Data Summary:
    - Shape: {data.shape[0]} rows x {data.shape[1]} columns
    - Columns: {', '.join(data.columns.tolist())}
    - Column types: {data.dtypes.to_dict()}
    - First 5 rows: 
    {data.head().to_string()}
    - Statistical summary:
    {data.describe().to_string()}
                """
            else:
                data_summary = str(data)
            
            # Create a prompt for OpenAI
            prompt = f"""
    You are a data science assistant with expertise in pattern recognition and statistical analysis.

    Analysis Type: {analysis_type}

    {data_summary}

    User's Question: {question}

    Analyze the provided data and answer the user's question in detail. Use your expertise to identify patterns, explain correlations, and provide actionable insights. 
    Format your response with markdown, including:
    1. Key Insights
    2. Detailed Analysis
    3. Potential Patterns and Correlations
    4. Recommendations
            """
            
            # Set up the API request
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            payload = {
                "model": "gpt-3.5-turbo",  # Use a reliable default model
                "messages": [
                    {"role": "system", "content": "You are a data science expert specializing in pattern recognition and statistical analysis."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2
            }
            
            # Make the API call
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "result": result['choices'][0]['message']['content'],
                    "model": result['model'],
                    "error": None
                }
            else:
                error_msg = f"OpenAI API Error: {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f" - {error_detail.get('error', {}).get('message', 'Unknown error')}"
                except:
                    pass
                
                logger.error(error_msg)
                return {
                    "error": error_msg,
                    "result": None
                }
                
        except Exception as e:
            logger.error(f"Error in OpenAI analysis: {e}")
            return {
                "error": str(e),
                "result": None
            }

    def call_anthropic_for_pattern_analysis(data, analysis_type, question, api_key):
        """Call Anthropic API for pattern analysis using direct HTTP requests"""
        try:
            import requests
            
            # Convert DataFrame to summary or sample if needed
            data_summary = ""
            if isinstance(data, pd.DataFrame):
                # Create a summary of the data
                data_summary = f"""
    Data Summary:
    - Shape: {data.shape[0]} rows x {data.shape[1]} columns
    - Columns: {', '.join(data.columns.tolist())}
    - Column types: {data.dtypes.to_dict()}
    - First 5 rows: 
    {data.head().to_string()}
    - Statistical summary:
    {data.describe().to_string()}
                """
            else:
                data_summary = str(data)
            
            # Create a prompt for Anthropic
            prompt = f"""
    You are a data science assistant with expertise in pattern recognition and statistical analysis.

    Analysis Type: {analysis_type}

    {data_summary}

    User's Question: {question}

    Analyze the provided data and answer the user's question in detail. Use your expertise to identify patterns, explain correlations, and provide actionable insights. 
    Format your response with markdown, including:
    1. Key Insights
    2. Detailed Analysis
    3. Potential Patterns and Correlations
    4. Recommendations
            """
            
            # Set up the API request
            headers = {
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01"
            }
            
            payload = {
                "model": "claude-3-opus-20240229",
                "max_tokens": 1000,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2
            }
            
            # Make the API call
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "result": result['content'][0]['text'],
                    "model": result['model'],
                    "error": None
                }
            else:
                error_msg = f"Anthropic API Error: {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f" - {error_detail.get('error', {}).get('message', 'Unknown error')}"
                except:
                    pass
                
                logger.error(error_msg)
                return {
                    "error": error_msg,
                    "result": None
                }
                
        except Exception as e:
            logger.error(f"Error in Anthropic analysis: {e}")
            return {
                "error": str(e),
                "result": None
            }

    def perform_time_series_analysis(data, column_name, forecast_periods=10):
        """
        Perform time series analysis and forecasting
        
        Parameters:
        - data: pandas DataFrame with time series data
        - column_name: Column to analyze
        - forecast_periods: Number of periods to forecast
        
        Returns:
        - Dictionary with analysis results
        """
        try:
            # Try to import required libraries
            try:
                from statsmodels.tsa.seasonal import seasonal_decompose
                from statsmodels.tsa.arima.model import ARIMA
                from statsmodels.tsa.stattools import adfuller
            except ImportError:
                st.warning("Installing required packages for time series analysis...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "statsmodels"])
                from statsmodels.tsa.seasonal import seasonal_decompose
                from statsmodels.tsa.arima.model import ARIMA
                from statsmodels.tsa.stattools import adfuller
            
            # Ensure data is sorted by index
            data = data.sort_index()
            
            # Extract the series to analyze
            series = data[column_name]
            
            results = {
                "original_data": series,
                "decomposition": None,
                "stationarity": None,
                "forecast": None,
                "forecast_index": None
            }
            
            # Check if series is stationary
            adf_result = adfuller(series.dropna())
            results["stationarity"] = {
                "test_statistic": adf_result[0],
                "p_value": adf_result[1],
                "is_stationary": adf_result[1] < 0.05
            }
            
            # Decompose series (trend, seasonal, residual)
            # Need enough data points for decomposition
            if len(series) >= 12:
                decomposition = seasonal_decompose(series, model='additive', period=min(12, len(series)//2))
                results["decomposition"] = {
                    "trend": decomposition.trend,
                    "seasonal": decomposition.seasonal,
                    "residual": decomposition.resid
                }
            
            # Build ARIMA model and forecast
            # Default to simple parameters for demonstration
            try:
                model = ARIMA(series, order=(1, 1, 1))
                model_fit = model.fit()
                
                # Generate forecast
                forecast = model_fit.forecast(steps=forecast_periods)
                
                # Generate forecast index (continue from last date)
                last_date = series.index[-1]
                
                # Create forecast index based on the existing index's frequency
                try:
                    if isinstance(last_date, pd.Timestamp):
                        if pd.infer_freq(series.index):
                            forecast_idx = pd.date_range(start=last_date, periods=forecast_periods+1, freq=pd.infer_freq(series.index))[1:]
                        else:
                            # If frequency can't be inferred, assume days
                            forecast_idx = pd.date_range(start=last_date, periods=forecast_periods+1, freq='D')[1:]
                    else:
                        # If not a timestamp, just continue the sequence
                        forecast_idx = np.arange(series.index[-1] + 1, series.index[-1] + forecast_periods + 1)
                except:
                    # Fallback: just use integers
                    forecast_idx = np.arange(len(series), len(series) + forecast_periods)
                    
                results["forecast"] = forecast
                results["forecast_index"] = forecast_idx
            except Exception as e:
                st.warning(f"ARIMA forecasting error: {str(e)}")
                results["forecast_error"] = str(e)
            
            return results
            
        except Exception as e:
            st.error(f"Error in time series analysis: {str(e)}")
            return None

    def perform_clustering(data, columns, n_clusters=3):
        """
        Perform clustering on the data
        
        Parameters:
        - data: pandas DataFrame
        - columns: Columns to use for clustering
        - n_clusters: Number of clusters
        
        Returns:
        - Dictionary with clustering results
        """
        try:
            # Try to import required libraries
            try:
                from sklearn.cluster import KMeans
                from sklearn.preprocessing import StandardScaler
                from sklearn.metrics import silhouette_score
            except ImportError:
                st.warning("Installing required packages for clustering...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "scikit-learn"])
                from sklearn.cluster import KMeans
                from sklearn.preprocessing import StandardScaler
                from sklearn.metrics import silhouette_score
            
            # Select features for clustering
            X = data[columns].copy()
            
            # Handle missing values
            X = X.fillna(X.mean())
            
            # Scale the data
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Perform K-means clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(X_scaled)
            
            # Get cluster centers
            centers = kmeans.cluster_centers_
            
            # Calculate silhouette score if there are multiple clusters
            silhouette = None
            if n_clusters > 1 and len(X) > n_clusters:
                silhouette = silhouette_score(X_scaled, clusters)
            
            # Add cluster labels to the original data
            data_with_clusters = data.copy()
            data_with_clusters['Cluster'] = clusters
            
            return {
                "data_with_clusters": data_with_clusters,
                "cluster_centers": pd.DataFrame(scaler.inverse_transform(centers), columns=columns),
                "model": kmeans,
                "scaler": scaler,
                "silhouette_score": silhouette
            }
            
        except Exception as e:
            st.error(f"Error in clustering: {str(e)}")
            return None

    def perform_association_analysis(data, min_support=0.1, min_confidence=0.5):
        """
        Perform association rule mining
        
        Parameters:
        - data: pandas DataFrame with transaction data
        - min_support: Minimum support for rules
        - min_confidence: Minimum confidence for rules
        
        Returns:
        - Dictionary with association rules
        """
        try:
            # Try to import required libraries
            try:
                from mlxtend.frequent_patterns import apriori, association_rules
            except ImportError:
                st.warning("Installing required packages for association analysis...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "mlxtend"])
                from mlxtend.frequent_patterns import apriori, association_rules
            
            # Check if data is one-hot encoded
            if data.values.max() > 1:
                # If not, attempt to convert to one-hot
                # Assuming each column is a categorical feature
                data_encoded = pd.get_dummies(data)
            else:
                data_encoded = data
            
            # Find frequent itemsets
            frequent_itemsets = apriori(data_encoded, min_support=min_support, use_colnames=True)
            
            # Generate association rules
            rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)
            
            return {
                "frequent_itemsets": frequent_itemsets,
                "rules": rules
            }
            
        except Exception as e:
            st.error(f"Error in association analysis: {str(e)}")
            return None

    def perform_regression(data, target_column, feature_columns):
        """
        Perform regression analysis
        
        Parameters:
        - data: pandas DataFrame
        - target_column: Target variable name
        - feature_columns: Feature variable names
        
        Returns:
        - Dictionary with regression results
        """
        try:
            # Try to import required libraries
            try:
                from sklearn.linear_model import LinearRegression
                from sklearn.model_selection import train_test_split
                from sklearn.metrics import mean_squared_error, r2_score
            except ImportError:
                st.warning("Installing required packages for regression analysis...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "scikit-learn"])
                from sklearn.linear_model import LinearRegression
                from sklearn.model_selection import train_test_split
                from sklearn.metrics import mean_squared_error, r2_score
            
            # Prepare data
            X = data[feature_columns].copy()
            y = data[target_column].copy()
            
            # Handle missing values
            X = X.fillna(X.mean())
            y = y.fillna(y.mean())
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Train model
            model = LinearRegression()
            model.fit(X_train, y_train)
            
            # Make predictions
            y_pred = model.predict(X_test)
            
            # Calculate metrics
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            # Get coefficients
            coefficients = pd.DataFrame({
                'Feature': feature_columns,
                'Coefficient': model.coef_
            })
            
            return {
                "model": model,
                "mse": mse,
                "r2": r2,
                "coefficients": coefficients,
                "y_test": y_test,
                "y_pred": y_pred
            }
            
        except Exception as e:
            st.error(f"Error in regression analysis: {str(e)}")
            return None

    def perform_classification(data, target_column, feature_columns):
        """
        Perform classification analysis
        
        Parameters:
        - data: pandas DataFrame
        - target_column: Target variable name
        - feature_columns: Feature variable names
        
        Returns:
        - Dictionary with classification results
        """
        try:
            # Try to import required libraries
            try:
                from sklearn.ensemble import RandomForestClassifier
                from sklearn.model_selection import train_test_split
                from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
            except ImportError:
                st.warning("Installing required packages for classification analysis...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "scikit-learn"])
                from sklearn.ensemble import RandomForestClassifier
                from sklearn.model_selection import train_test_split
                from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
            
            # Prepare data
            X = data[feature_columns].copy()
            y = data[target_column].copy()
            
            # Handle missing values
            X = X.fillna(X.mean())
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Train model
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            
            # Make predictions
            y_pred = model.predict(X_test)
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            report = classification_report(y_test, y_pred, output_dict=True)
            cm = confusion_matrix(y_test, y_pred)
            
            # Get feature importances
            importances = pd.DataFrame({
                'Feature': feature_columns,
                'Importance': model.feature_importances_
            }).sort_values('Importance', ascending=False)
            
            return {
                "model": model,
                "accuracy": accuracy,
                "report": report,
                "confusion_matrix": cm,
                "feature_importances": importances,
                "y_test": y_test,
                "y_pred": y_pred
            }
            
        except Exception as e:
            st.error(f"Error in classification analysis: {str(e)}")
            return None

  

    def perform_statistical_test(data, test_type, columns=None, alpha=0.05):
        """
        Perform various statistical tests on data
        
        Parameters:
        - data: pandas DataFrame
        - test_type: Type of statistical test to perform
        - columns: Columns to use in the test
        - alpha: Significance level
        
        Returns:
        - Dictionary with test results
        """
        try:
            if test_type == "t_test_ind":
                # Two-sample t-test (independent samples)
                if len(columns) != 2:
                    return {"error": "Two-sample t-test requires exactly two columns"}
                
                group1 = data[columns[0]].dropna()
                group2 = data[columns[1]].dropna()
                
                t_stat, p_value = stats.ttest_ind(group1, group2)
                
                return {
                    "test": "Two-sample t-test (independent)",
                    "t_statistic": t_stat,
                    "p_value": p_value,
                    "significant": p_value < alpha,
                    "alpha": alpha,
                    "hypothesis": "The means of the two groups are different" if p_value < alpha else "Cannot reject the null hypothesis"
                }
                
            elif test_type == "t_test_paired":
                # Paired samples t-test
                if len(columns) != 2:
                    return {"error": "Paired t-test requires exactly two columns"}
                
                # Remove rows with NaN in either column
                temp_data = data[columns].dropna()
                
                if len(temp_data) < 2:
                    return {"error": "Not enough data points for paired t-test"}
                
                t_stat, p_value = stats.ttest_rel(temp_data[columns[0]], temp_data[columns[1]])
                
                return {
                    "test": "Paired samples t-test",
                    "t_statistic": t_stat,
                    "p_value": p_value,
                    "significant": p_value < alpha,
                    "alpha": alpha,
                    "hypothesis": "The paired values have different means" if p_value < alpha else "Cannot reject the null hypothesis"
                }
                
            elif test_type == "pearson":
                # Pearson correlation
                if len(columns) != 2:
                    return {"error": "Pearson correlation requires exactly two columns"}
                
                # Remove rows with NaN in either column
                temp_data = data[columns].dropna()
                
                r, p_value = stats.pearsonr(temp_data[columns[0]], temp_data[columns[1]])
                
                return {
                    "test": "Pearson correlation",
                    "correlation": r,
                    "p_value": p_value,
                    "significant": p_value < alpha,
                    "alpha": alpha,
                    "interpretation": get_correlation_interpretation(r),
                    "hypothesis": "The correlation is significant" if p_value < alpha else "Cannot reject the null hypothesis"
                }
                
            elif test_type == "spearman":
                # Spearman correlation
                if len(columns) != 2:
                    return {"error": "Spearman correlation requires exactly two columns"}
                
                # Remove rows with NaN in either column
                temp_data = data[columns].dropna()
                
                r, p_value = stats.spearmanr(temp_data[columns[0]], temp_data[columns[1]])
                
                return {
                    "test": "Spearman rank correlation",
                    "correlation": r,
                    "p_value": p_value,
                    "significant": p_value < alpha,
                    "alpha": alpha,
                    "interpretation": get_correlation_interpretation(r),
                    "hypothesis": "The correlation is significant" if p_value < alpha else "Cannot reject the null hypothesis"
                }
                
            elif test_type == "anova":
                # One-way ANOVA - compare means of multiple groups
                if len(columns) < 2:
                    return {"error": "ANOVA requires at least two groups"}
                
                groups = []
                for col in columns:
                    groups.append(data[col].dropna())
                
                f_stat, p_value = stats.f_oneway(*groups)
                
                return {
                    "test": "One-way ANOVA",
                    "f_statistic": f_stat,
                    "p_value": p_value,
                    "significant": p_value < alpha,
                    "alpha": alpha,
                    "hypothesis": "At least one group mean is different" if p_value < alpha else "Cannot reject the null hypothesis"
                }
                
            elif test_type == "chi_square":
                # Chi-square test of independence
                if len(columns) != 2:
                    return {"error": "Chi-square test requires exactly two categorical columns"}
                
                # Create contingency table
                contingency_table = pd.crosstab(data[columns[0]], data[columns[1]])
                
                chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
                
                return {
                    "test": "Chi-square test of independence",
                    "chi2_statistic": chi2,
                    "p_value": p_value,
                    "dof": dof,
                    "contingency_table": contingency_table,
                    "expected_frequencies": pd.DataFrame(expected, index=contingency_table.index, columns=contingency_table.columns),
                    "significant": p_value < alpha,
                    "alpha": alpha,
                    "hypothesis": "The variables are dependent" if p_value < alpha else "Cannot reject the null hypothesis"
                }
                
            elif test_type == "shapiro":
                # Shapiro-Wilk test for normality
                if len(columns) != 1:
                    return {"error": "Shapiro-Wilk test requires exactly one column"}
                
                data_to_test = data[columns[0]].dropna()
                
                if len(data_to_test) < 3:
                    return {"error": "Not enough data points for Shapiro-Wilk test"}
                    
                if len(data_to_test) > 5000:
                    # Shapiro-Wilk is only valid for n <= 5000
                    return {"error": "Shapiro-Wilk test is only valid for sample sizes <= 5000"}
                    
                w, p_value = stats.shapiro(data_to_test)
                
                return {
                    "test": "Shapiro-Wilk test for normality",
                    "w_statistic": w,
                    "p_value": p_value,
                    "significant": p_value < alpha,
                    "alpha": alpha,
                    "hypothesis": "The data is not normally distributed" if p_value < alpha else "Cannot reject normality"
                }
                
            elif test_type == "levene":
                # Levene test for equality of variances
                if len(columns) < 2:
                    return {"error": "Levene test requires at least two columns"}
                
                groups = []
                for col in columns:
                    groups.append(data[col].dropna())
                
                stat, p_value = stats.levene(*groups)
                
                return {
                    "test": "Levene's test for equality of variances",
                    "statistic": stat,
                    "p_value": p_value,
                    "significant": p_value < alpha,
                    "alpha": alpha,
                    "hypothesis": "The variances are different" if p_value < alpha else "Cannot reject equal variances"
                }
                
            else:
                return {"error": f"Unknown statistical test: {test_type}"}
                
        except Exception as e:
            st.error(f"Error in statistical test: {str(e)}")
            return {"error": str(e)}

    def get_correlation_interpretation(r):
        """Return interpretation of correlation coefficient"""
        r_abs = abs(r)
        if r_abs < 0.1:
            return "Negligible correlation"
        elif r_abs < 0.3:
            return "Weak correlation"
        elif r_abs < 0.5:
            return "Moderate correlation"
        elif r_abs < 0.7:
            return "Strong correlation"
        elif r_abs < 0.9:
            return "Very strong correlation"
        else:
            return "Near perfect correlation"
    
    
    
    
    # Access data from session state
    data = st.session_state.data
    
    # Display data preview if available
    if data is not None:
        # with st.expander("📊 Data Preview", expanded=True):
        #     st.dataframe(data.head(10))
            
        #     # Display column info
        #     st.subheader("Column Information")
        #     col_info = pd.DataFrame({
        #         "Data Type": data.dtypes,
        #         "Non-Null Values": data.count(),
        #         "Missing Values": data.isnull().sum(),
        #         "Unique Values": [data[col].nunique() for col in data.columns]
        #     })
        #     st.dataframe(col_info)
            
        # Create main analysis tabs
        analysis_tabs = st.tabs([
            "Time Series", 
            "Clustering", 
            "Regression", 
            "Classification", 
            "Association Rules", 
            "Statistical Tests",
            "AI Analysis"
        ])

        # Time Series Analysis Tab
        with analysis_tabs[0]:
            st.header("Time Series Analysis")
            
            # Check if we have a time index
            if not isinstance(data.index, pd.DatetimeIndex) and 'date' in data.columns:
                st.info("Converting 'date' column to datetime index")
                data_copy = data.copy()
                data_copy['date'] = pd.to_datetime(data_copy['date'])
                data_copy.set_index('date', inplace=True)
            else:
                data_copy = data.copy()
            
            # Select column to analyze
            numeric_columns = data_copy.select_dtypes(include=[np.number]).columns.tolist()
            
            if numeric_columns:
                target_column = st.selectbox("Select column to analyze", numeric_columns, key="timeseries_column")
                
                forecast_periods = st.slider("Forecast periods", 1, 30, 10, key="timeseries_periods")
                
                if st.button("Run Time Series Analysis", key="run_timeseries"):
                    with st.spinner("Performing time series analysis..."):
                        results = perform_time_series_analysis(data_copy, target_column, forecast_periods)
                        
                        if results:
                            ts_tabs = st.tabs(["Overview", "Decomposition", "Forecast"])
                            
                            # Overview Tab
                            with ts_tabs[0]:
                                # Plot original data
                                fig, ax = plt.subplots(figsize=(10, 6))
                                results["original_data"].plot(ax=ax)
                                ax.set_title(f"Time Series: {target_column}")
                                ax.grid(True)
                                st.pyplot(fig)
                                
                                # Stationarity test
                                if results["stationarity"]:
                                    st.subheader("Stationarity Test (Augmented Dickey-Fuller)")
                                    
                                    st.write(f"Test Statistic: {results['stationarity']['test_statistic']:.4f}")
                                    st.write(f"p-value: {results['stationarity']['p_value']:.4f}")
                                    
                                    if results["stationarity"]["is_stationary"]:
                                        st.success("The series is stationary (p-value < 0.05)")
                                    else:
                                        st.warning("The series is not stationary (p-value >= 0.05)")
                            
                            # Decomposition Tab
                            with ts_tabs[1]:
                                st.subheader("Time Series Decomposition")
                                if results["decomposition"]:
                                    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(10, 12))
                                    
                                    # Original
                                    results["original_data"].plot(ax=ax1)
                                    ax1.set_title("Original")
                                    ax1.grid(True)
                                    
                                    # Trend
                                    results["decomposition"]["trend"].plot(ax=ax2)
                                    ax2.set_title("Trend")
                                    ax2.grid(True)
                                    
                                    # Seasonal
                                    results["decomposition"]["seasonal"].plot(ax=ax3)
                                    ax3.set_title("Seasonality")
                                    ax3.grid(True)
                                    
                                    # Residual
                                    results["decomposition"]["residual"].plot(ax=ax4)
                                    ax4.set_title("Residuals")
                                    ax4.grid(True)
                                    
                                    fig.tight_layout()
                                    st.pyplot(fig)
                                else:
                                    st.info("Not enough data points for decomposition. Need at least 12 observations.")
                            
                            # Forecast Tab
                            with ts_tabs[2]:
                                st.subheader("Forecast")
                                if results["forecast"] is not None:
                                    fig, ax = plt.subplots(figsize=(10, 6))
                                    
                                    # Plot original data
                                    results["original_data"].plot(ax=ax, label="Historical Data")
                                    
                                    # Plot forecast
                                    pd.Series(
                                        results["forecast"],
                                        index=results["forecast_index"]
                                    ).plot(ax=ax, style='r--', label="Forecast")
                                    
                                    ax.set_title(f"Time Series Forecast: {target_column}")
                                    ax.grid(True)
                                    ax.legend()
                                    
                                    st.pyplot(fig)
                                    
                                    # Forecast values as table
                                    st.write("Forecast Values:")
                                    forecast_df = pd.DataFrame({
                                        "Date": results["forecast_index"],
                                        "Forecast": results["forecast"]
                                    })
                                    st.dataframe(forecast_df)
                                    
                                    # Download link for forecast
                                    csv = forecast_df.to_csv(index=False)
                                    st.download_button(
                                        "Download Forecast CSV",
                                        csv,
                                        "forecast.csv",
                                        "text/csv",
                                        key='download-forecast-csv'
                                    )
                                elif "forecast_error" in results:
                                    st.error(f"Error in forecasting: {results['forecast_error']}")
                            
                           
            else:
                st.error("No numeric columns found in the data for time series analysis.")

        # Clustering Tab
        with analysis_tabs[1]:
            st.header("Clustering Analysis")
            
            # Get numeric columns for clustering
            numeric_columns = data.select_dtypes(include=[np.number]).columns.tolist()
            
            if numeric_columns:
                # Select features for clustering
                st.subheader("Select Features")
                selected_features = st.multiselect(
                    "Select columns to use for clustering", 
                    numeric_columns,
                    default=numeric_columns[:2] if len(numeric_columns) >= 2 else numeric_columns,
                    key="clustering_features"
                )
                
                if len(selected_features) < 2:
                    st.warning("Please select at least two features for meaningful clustering visualization.")
                
                # Number of clusters
                n_clusters = st.slider("Number of clusters", 2, 10, 3, key="n_clusters")
                
                if st.button("Run Clustering", key="run_clustering") and selected_features:
                    with st.spinner("Performing clustering..."):
                        results = perform_clustering(data, selected_features, n_clusters)
                        
                        if results:
                            # Display results in tabs
                            cluster_tabs = st.tabs(["Visualization", "Cluster Analysis", "Data with Clusters"])
                            
                            # Visualization tab
                            with cluster_tabs[0]:
                                st.subheader("Cluster Visualization")
                                
                                # If we have at least 2 features, create a scatter plot
                                if len(selected_features) >= 2:
                                    # Select which features to plot if more than 2
                                    if len(selected_features) > 2:
                                        col1, col2 = st.columns(2)
                                        with col1:
                                            x_feature = st.selectbox("X-axis feature", selected_features, index=0, key="x_feature")
                                        with col2:
                                            default_y_index = 1 if len(selected_features) > 1 else 0
                                            y_feature = st.selectbox("Y-axis feature", selected_features, index=default_y_index, key="y_feature")
                                    else:
                                        x_feature, y_feature = selected_features
                                    
                                    # Create scatter plot
                                    plt.figure(figsize=(10, 6))
                                    scatter = plt.scatter(
                                        results["data_with_clusters"][x_feature],
                                        results["data_with_clusters"][y_feature],
                                        c=results["data_with_clusters"]["Cluster"],
                                        cmap='viridis',
                                        alpha=0.8,
                                        s=50
                                    )
                                    
                                    # Plot cluster centers
                                    centers = results["cluster_centers"]
                                    plt.scatter(
                                        centers[x_feature],
                                        centers[y_feature],
                                        c='red',
                                        marker='X',
                                        s=200,
                                        alpha=1,
                                        label='Cluster Centers'
                                    )
                                    
                                    plt.xlabel(x_feature)
                                    plt.ylabel(y_feature)
                                    plt.title(f"Cluster Analysis ({n_clusters} clusters)")
                                    plt.grid(True, alpha=0.3)
                                    plt.legend()
                                    plt.colorbar(scatter, label='Cluster')
                                    
                                    st.pyplot(plt)
                                    
                                    # Display 3D plot if we have at least 3 features
                                    if len(selected_features) >= 3:
                                        st.subheader("3D Cluster Visualization")
                                        
                                        col1, col2, col3 = st.columns(3)
                                        with col1:
                                            x_feature_3d = st.selectbox("X-axis", selected_features, index=0, key="x_feature_3d")
                                        with col2:
                                            y_feature_3d = st.selectbox("Y-axis", selected_features, index=1, key="y_feature_3d")
                                        with col3:
                                            z_feature_3d = st.selectbox("Z-axis", selected_features, index=2, key="z_feature_3d")
                                        
                                        # Create 3D plot
                                        fig = plt.figure(figsize=(10, 8))
                                        ax = fig.add_subplot(111, projection='3d')
                                        
                                        scatter = ax.scatter(
                                            results["data_with_clusters"][x_feature_3d],
                                            results["data_with_clusters"][y_feature_3d],
                                            results["data_with_clusters"][z_feature_3d],
                                            c=results["data_with_clusters"]["Cluster"],
                                            cmap='viridis',
                                            alpha=0.8,
                                            s=50
                                        )
                                        
                                        # Plot cluster centers
                                        ax.scatter(
                                            centers[x_feature_3d],
                                            centers[y_feature_3d],
                                            centers[z_feature_3d],
                                            c='red',
                                            marker='X',
                                            s=200,
                                            alpha=1,
                                            label='Cluster Centers'
                                        )
                                        
                                        ax.set_xlabel(x_feature_3d)
                                        ax.set_ylabel(y_feature_3d)
                                        ax.set_zlabel(z_feature_3d)
                                        ax.set_title(f"3D Cluster Analysis ({n_clusters} clusters)")
                                        plt.legend()
                                        
                                        st.pyplot(fig)
                                else:
                                    st.warning("Need at least 2 features to visualize clusters.")
                            
                            # Cluster analysis tab
                            with cluster_tabs[1]:
                                st.subheader("Cluster Analysis")
                                
                                # Display cluster centers
                                st.write("### Cluster Centers")
                                st.dataframe(results["cluster_centers"])
                                
                                # Display cluster metrics
                                st.write("### Cluster Metrics")
                                
                                # Display silhouette score if available
                                if results["silhouette_score"] is not None:
                                    st.metric("Silhouette Score", f"{results['silhouette_score']:.4f}")
                                    
                                    # Interpret silhouette score
                                    if results["silhouette_score"] < 0.2:
                                        st.warning("Silhouette score indicates poor cluster separation.")
                                    elif results["silhouette_score"] < 0.5:
                                        st.info("Silhouette score indicates moderate cluster separation.")
                                    else:
                                        st.success("Silhouette score indicates good cluster separation.")
                                
                                # Display cluster sizes
                                cluster_sizes = results["data_with_clusters"]["Cluster"].value_counts().sort_index()
                                
                                st.write("### Cluster Sizes")
                                fig, ax = plt.subplots(figsize=(10, 5))
                                cluster_sizes.plot(kind='bar', ax=ax)
                                ax.set_title("Number of Data Points per Cluster")
                                ax.set_xlabel("Cluster")
                                ax.set_ylabel("Count")
                                st.pyplot(fig)
                                
                                # Display feature distributions by cluster
                                st.write("### Feature Distributions by Cluster")
                                feature_to_analyze = st.selectbox("Select feature to analyze", selected_features, key="feature_dist")
                                
                                fig, ax = plt.subplots(figsize=(12, 6))
                                for cluster in range(n_clusters):
                                    cluster_data = results["data_with_clusters"][results["data_with_clusters"]["Cluster"] == cluster][feature_to_analyze]
                                    sns.kdeplot(cluster_data, label=f"Cluster {cluster}", ax=ax)
                                
                                ax.set_title(f"Distribution of {feature_to_analyze} by Cluster")
                                ax.set_xlabel(feature_to_analyze)
                                ax.set_ylabel("Density")
                                plt.legend()
                                st.pyplot(fig)
                            
                            # Data with clusters tab
                            with cluster_tabs[2]:
                                st.subheader("Data with Cluster Labels")
                                st.dataframe(results["data_with_clusters"])
                                
                                # Download data with clusters
                                csv = results["data_with_clusters"].to_csv(index=False)
                                st.download_button(
                                    "Download Data with Clusters",
                                    csv,
                                    "clustered_data.csv",
                                    "text/csv",
                                    key='download-clustered-data'
                                )
            else:
                st.error("No numeric columns found in the data for clustering analysis.")

        # Regression Tab
        with analysis_tabs[2]:
            st.header("Regression Analysis")
            
            # Get numeric columns for regression
            numeric_columns = data.select_dtypes(include=[np.number]).columns.tolist()
            
            if numeric_columns:
                # Select target variable
                target_column = st.selectbox("Select target variable", numeric_columns, key="regression_target")
                
                # Remove target from feature list
                feature_options = [col for col in numeric_columns if col != target_column]
                
                # Select features
                selected_features = st.multiselect(
                    "Select features", 
                    feature_options,
                    default=feature_options[:min(3, len(feature_options))],
                    key="regression_features"
                )
                
                if st.button("Run Regression Analysis", key="run_regression") and selected_features:
                    with st.spinner("Performing regression analysis..."):
                        results = perform_regression(data, target_column, selected_features)
                        
                        if results:
                            # Display results in tabs
                            reg_tabs = st.tabs(["Model Summary", "Coefficients", "Predictions"])
                            
                            # Model summary tab
                            with reg_tabs[0]:
                                st.subheader("Model Summary")
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.metric("R² Score", f"{results['r2']:.4f}")
                                    if results['r2'] < 0.3:
                                        st.warning("Low R² indicates poor model fit")
                                    elif results['r2'] < 0.7:
                                        st.info("Moderate R² indicates reasonable model fit")
                                    else:
                                        st.success("High R² indicates good model fit")
                                        
                                with col2:
                                    st.metric("Mean Squared Error", f"{results['mse']:.4f}")
                                    st.write(f"Root MSE: {np.sqrt(results['mse']):.4f}")
                                
                                # Plot residuals
                                st.subheader("Residual Analysis")
                                residuals = results["y_test"] - results["y_pred"]
                                
                                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
                                
                                # Residuals vs predicted
                                ax1.scatter(results["y_pred"], residuals, alpha=0.5)
                                ax1.axhline(y=0, color='r', linestyle='--')
                                ax1.set_xlabel("Predicted Values")
                                ax1.set_ylabel("Residuals")
                                ax1.set_title("Residuals vs Predicted Values")
                                ax1.grid(True, alpha=0.3)
                                
                                # Histogram of residuals
                                ax2.hist(residuals, bins=20, alpha=0.7)
                                ax2.set_xlabel("Residual Value")
                                ax2.set_ylabel("Frequency")
                                ax2.set_title("Residual Distribution")
                                ax2.grid(True, alpha=0.3)
                                
                                fig.tight_layout()
                                st.pyplot(fig)
                            
                            # Coefficients tab
                            with reg_tabs[1]:
                                st.subheader("Coefficients Analysis")
                                
                                # Sort coefficients by absolute magnitude
                                coefs = results["coefficients"].copy()
                                coefs["Absolute"] = np.abs(coefs["Coefficient"])
                                coefs = coefs.sort_values("Absolute", ascending=False)
                                
                                # Plot coefficients
                                fig, ax = plt.subplots(figsize=(10, max(5, len(coefs) * 0.5)))
                                
                                bars = ax.barh(coefs["Feature"], coefs["Coefficient"])
                                
                                # Color positive and negative coefficients differently
                                for i, bar in enumerate(bars):
                                    if coefs["Coefficient"].iloc[i] < 0:
                                        bar.set_color('r')
                                    else:
                                        bar.set_color('g')
                                
                                ax.axvline(x=0, color='black', linestyle='--')
                                ax.set_xlabel("Coefficient Value")
                                ax.set_title("Feature Coefficients")
                                ax.grid(True, alpha=0.3)
                                
                                st.pyplot(fig)
                                
                                # Display coefficients table
                                st.dataframe(coefs[["Feature", "Coefficient"]].reset_index(drop=True))
                                
                                # Interpretation
                                st.subheader("Interpretation")
                                
                                intercept = results["model"].intercept_
                                
                                interpretation = f"The model has an intercept of {intercept:.4f}. "
                                interpretation += "The coefficients represent the change in the target variable for a one-unit change in the feature, holding all other features constant.\n\n"
                                
                                # Add interpretation for each coefficient
                                for _, row in coefs.iterrows():
                                    feature = row["Feature"]
                                    coef = row["Coefficient"]
                                    
                                    if coef > 0:
                                        interpretation += f"- **{feature}**: A one-unit increase is associated with a **{coef:.4f}** increase in {target_column}.\n"
                                    else:
                                        interpretation += f"- **{feature}**: A one-unit increase is associated with a **{abs(coef):.4f}** decrease in {target_column}.\n"
                                
                                st.markdown(interpretation)
                            
                            # Predictions tab
                            with reg_tabs[2]:
                                st.subheader("Predictions vs Actual")
                                
                                # Create a DataFrame with predictions
                                pred_df = pd.DataFrame({
                                    "Actual": results["y_test"],
                                    "Predicted": results["y_pred"],
                                    "Error": results["y_test"] - results["y_pred"]
                                })
                                
                                # Plot actual vs predicted
                                fig, ax = plt.subplots(figsize=(10, 6))
                                
                                ax.scatter(results["y_test"], results["y_pred"], alpha=0.5)
                                
                                # Add perfect prediction line
                                min_val = min(results["y_test"].min(), results["y_pred"].min())
                                max_val = max(results["y_test"].max(), results["y_pred"].max())
                                ax.plot([min_val, max_val], [min_val, max_val], 'r--')
                                
                                ax.set_xlabel("Actual Values")
                                ax.set_ylabel("Predicted Values")
                                ax.set_title("Actual vs Predicted Values")
                                ax.grid(True, alpha=0.3)
                                
                                st.pyplot(fig)
                                
                                # Show predictions DataFrame
                                st.dataframe(pred_df)
                                
                                # Download predictions
                                csv = pred_df.to_csv(index=False)
                                st.download_button(
                                    "Download Predictions",
                                    csv,
                                    "regression_predictions.csv",
                                    "text/csv",
                                    key='download-regression-predictions'
                                )
                                
                                # Interactive prediction for a single data point
                                st.subheader("Interactive Prediction")
                                st.write("Adjust feature values to see the predicted target value")
                                
                                feature_values = {}
                                cols = st.columns(min(3, len(selected_features)))
                                
                                for i, feature in enumerate(selected_features):
                                    col_index = i % len(cols)
                                    with cols[col_index]:
                                        mean_val = data[feature].mean()
                                        std_val = data[feature].std()
                                        min_val = mean_val - 3*std_val
                                        max_val = mean_val + 3*std_val
                                        
                                        feature_values[feature] = st.slider(
                                            feature, 
                                            float(min_val), 
                                            float(max_val), 
                                            float(mean_val),
                                            key=f"pred_{feature}"
                                        )
                                
                                # Create input for prediction
                                input_df = pd.DataFrame([feature_values])
                                
                                # Make prediction
                                prediction = results["model"].predict(input_df)[0]
                                
                                st.metric("Predicted Value", f"{prediction:.4f}")
            else:
                st.error("No numeric columns found in the data for regression analysis.")
                
        # Classification Tab
        with analysis_tabs[3]:
            st.header("Classification Analysis")
            
            # Get columns for classification
            numeric_columns = data.select_dtypes(include=[np.number]).columns.tolist()
            categorical_columns = data.select_dtypes(include=['object', 'category']).columns.tolist()
            
            # Prepare potential target columns - categorical columns and numeric columns with few unique values
            potential_targets = categorical_columns.copy()
            for col in numeric_columns:
                if data[col].nunique() < 10:  # Likely a categorical variable stored as numeric
                    potential_targets.append(col)
            
            if potential_targets:
                # Select target variable
                target_column = st.selectbox("Select target (class) variable", potential_targets, key="classification_target")
                
                # Get features - all numeric columns except the target
                feature_options = [col for col in numeric_columns if col != target_column]
                
                # Select features
                selected_features = st.multiselect(
                    "Select features", 
                    feature_options,
                    default=feature_options[:min(4, len(feature_options))],
                    key="classification_features"
                )
                
                if st.button("Run Classification Analysis", key="run_classification") and selected_features:
                    with st.spinner("Performing classification analysis..."):
                        results = perform_classification(data, target_column, selected_features)
                        
                        if results:
                            # Display results in tabs
                            class_tabs = st.tabs(["Model Performance", "Feature Importance", "Confusion Matrix"])
                            
                            # Model performance tab
                            with class_tabs[0]:
                                st.subheader("Model Performance")
                                
                                # Display accuracy
                                st.metric("Accuracy", f"{results['accuracy']:.4f}")
                                
                                # Display classification report
                                st.subheader("Classification Report")
                                
                                # Convert classification report to DataFrame for better display
                                report_df = pd.DataFrame(results["report"]).transpose()
                                
                                # Format DataFrame
                                if 'support' in report_df.columns:
                                    report_df['support'] = report_df['support'].astype(int)
                                
                                # Drop unnecessary rows
                                if 'accuracy' in report_df.index:
                                    accuracy_row = report_df.loc[['accuracy']]
                                    report_df = report_df.drop(['accuracy'])
                                    
                                    # Display main metrics
                                    st.dataframe(report_df)
                                    
                                    # Display accuracy separately
                                    st.write("Overall Accuracy Metrics:")
                                    st.dataframe(accuracy_row)
                                else:
                                    st.dataframe(report_df)
                                
                                
                            
                            # Feature importance tab
                            with class_tabs[1]:
                                st.subheader("Feature Importance")
                                
                                # Plot feature importance
                                importances = results["feature_importances"]
                                
                                fig, ax = plt.subplots(figsize=(10, max(5, len(importances) * 0.5)))
                                
                                # Sort by importance
                                importances = importances.sort_values("Importance", ascending=False)
                                
                                ax.barh(importances["Feature"], importances["Importance"])
                                ax.set_xlabel("Importance")
                                ax.set_title("Feature Importance")
                                ax.grid(True, alpha=0.3)
                                
                                st.pyplot(fig)
                                
                                # Display feature importance table
                                st.dataframe(importances.reset_index(drop=True))
                                
                                # Feature pair visualization
                                st.subheader("Feature Pair Visualization")
                                
                                if len(selected_features) >= 2:
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        x_feature = st.selectbox("X-axis feature", selected_features, index=0, key="x_feature_class")
                                    with col2:
                                        default_y_index = 1 if len(selected_features) > 1 else 0
                                        y_feature = st.selectbox("Y-axis feature", selected_features, index=default_y_index, key="y_feature_class")
                                    
                                    # Create scatter plot of selected features by class
                                    fig, ax = plt.subplots(figsize=(10, 6))
                                    scatter = ax.scatter(
                                        data[x_feature],
                                        data[y_feature],
                                        c=data[target_column].astype('category').cat.codes,
                                        cmap='viridis',
                                        alpha=0.6,
                                        s=50
                                    )
                                    
                                    ax.set_xlabel(x_feature)
                                    ax.set_ylabel(y_feature)
                                    ax.set_title(f"Feature Visualization by Class ({target_column})")
                                    ax.grid(True, alpha=0.3)
                                    
                                    # Add legend
                                    if data[target_column].nunique() <= 10:  # Only add legend for a reasonable number of classes
                                        classes = data[target_column].unique()
                                        handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=scatter.cmap(scatter.norm(i)), 
                                                             markersize=10, label=cls) for i, cls in enumerate(classes)]
                                        ax.legend(handles=handles, title=target_column)
                                    else:
                                        plt.colorbar(scatter, label=target_column)
                                    
                                    st.pyplot(fig)
                                else:
                                    st.warning("Need at least 2 features to create visualization.")
                            
                            # Confusion matrix tab
                            with class_tabs[2]:
                                st.subheader("Confusion Matrix")
                                
                                cm = results["confusion_matrix"]
                                
                                # Plot confusion matrix
                                fig, ax = plt.subplots(figsize=(10, 8))
                                
                                # Get unique classes (sorted)
                                classes = np.unique(np.concatenate([results["y_test"], results["y_pred"]]))
                                
                                sns.heatmap(
                                    cm, 
                                    annot=True, 
                                    fmt="d", 
                                    cmap="Blues",
                                    xticklabels=classes,
                                    yticklabels=classes,
                                    ax=ax
                                )
                                
                                ax.set_xlabel("Predicted")
                                ax.set_ylabel("Actual")
                                ax.set_title("Confusion Matrix")
                                
                                st.pyplot(fig)
                                
                                # Explain confusion matrix
                                st.subheader("Confusion Matrix Explained")
                                
                                if len(classes) == 2:
                                    # For binary classification
                                    st.markdown(f"""
                                    - **True Positives (top-left)**: {cm[0][0]} correctly predicted as class {classes[0]}
                                    - **False Negatives (top-right)**: {cm[0][1]} incorrectly predicted as class {classes[1]} when actually class {classes[0]}
                                    - **False Positives (bottom-left)**: {cm[1][0]} incorrectly predicted as class {classes[0]} when actually class {classes[1]}
                                    - **True Negatives (bottom-right)**: {cm[1][1]} correctly predicted as class {classes[1]}
                                    """)
                                else:
                                    st.write("The confusion matrix shows actual classes (rows) vs predicted classes (columns).")
                                    st.write("Diagonal elements represent correct predictions, while off-diagonal elements are incorrect predictions.")
                                
                                # Display predictions DataFrame
                                st.subheader("Predictions")
                                
                                pred_df = pd.DataFrame({
                                    "Actual": results["y_test"],
                                    "Predicted": results["y_pred"],
                                    "Correct": results["y_test"] == results["y_pred"]
                                })
                                
                                st.dataframe(pred_df)
                                
                                # Download predictions
                                csv = pred_df.to_csv(index=False)
                                st.download_button(
                                    "Download Predictions",
                                    csv,
                                    "classification_predictions.csv",
                                    "text/csv",
                                    key='download-classification-predictions'
                                )
            elif numeric_columns:
                st.warning("No categorical or low-cardinality numeric columns found that could serve as classification targets. Classification typically requires a target variable with a limited number of discrete values.")
                st.info("If your data contains a categorical target, ensure it's in the correct format. Alternatively, you can convert a numeric column with few unique values into a categorical target.")
            else:
                st.error("No numeric columns found for features in the data.")
                
        # Association Rules Tab
        with analysis_tabs[4]:
            st.header("Association Rule Mining")
            
            st.write("""
            Association rule mining finds relationships like "customers who bought X also bought Y."
            For this analysis, data should be in a one-hot encoded format where:
            - Each row represents a transaction or record
            - Each column represents an item or property
            - Values are 0 (false/absent) or 1 (true/present)
            """)
            
            # Check if data is likely one-hot encoded
            is_likely_one_hot = ((data.isin([0, 1]).sum() / len(data)) > 0.8).all() or all(data.dtypes == bool)
            
            if not is_likely_one_hot:
                st.warning("Your data may not be in the required one-hot encoded format (0/1 values only).")
                st.info("The analysis will attempt to convert categorical variables to one-hot encoding.")
            
            # Set parameters
            col1, col2 = st.columns(2)
            with col1:
                min_support = st.slider("Minimum Support", 0.01, 0.5, 0.1, 0.01, 
                                      help="Proportion of transactions that must contain an itemset")
            with col2:
                min_confidence = st.slider("Minimum Confidence", 0.1, 1.0, 0.5, 0.05,
                                        help="Proportion of transactions with X that also contain Y")
            
            if st.button("Run Association Analysis", key="run_association"):
                with st.spinner("Mining association rules..."):
                    results = perform_association_analysis(data, min_support, min_confidence)
                    
                    if results:
                        # Display results in tabs
                        assoc_tabs = st.tabs(["Rules", "Frequent Itemsets", "Visualization"])
                        
                        # Rules tab
                        with assoc_tabs[0]:
                            st.subheader("Association Rules")
                            
                            if len(results["rules"]) > 0:
                                # Format rules table
                                rules_df = results["rules"].copy()
                                
                                # Convert frozensets to readable strings
                                def format_itemset(itemset):
                                    return ', '.join(sorted(list(itemset)))
                                
                                rules_df['antecedents'] = rules_df['antecedents'].apply(format_itemset)
                                rules_df['consequents'] = rules_df['consequents'].apply(format_itemset)
                                
                                # Sort by confidence
                                rules_df = rules_df.sort_values('confidence', ascending=False)
                                
                                # Add a human-readable column that explains the rule
                                rules_df['rule'] = rules_df.apply(lambda x: f"If a transaction includes {x['antecedents']}, it's likely to include {x['consequents']}", axis=1)
                                
                                # Display rules
                                st.dataframe(rules_df)
                                
                                # Download rules
                                csv = rules_df.to_csv(index=False)
                                st.download_button(
                                    "Download Association Rules",
                                    csv,
                                    "association_rules.csv",
                                    "text/csv",
                                    key='download-association-rules'
                                )
                                
                                # Top rules interpretation
                                st.subheader("Top Rules Interpretation")
                                
                                top_rules = rules_df.head(5)
                                for i, row in top_rules.iterrows():
                                    st.markdown(f"""
                                    **Rule {i+1}**: {row['rule']}
                                    - Support: {row['support']:.3f} ({row['support']*100:.1f}% of all transactions)
                                    - Confidence: {row['confidence']:.3f} ({row['confidence']*100:.1f}% of transactions with the antecedent also have the consequent)
                                    - Lift: {row['lift']:.3f} ({row['lift']:.1f}x more likely than by chance)
                                    """)
                            else:
                                st.warning("No rules found with the current settings. Try lowering the minimum support or confidence.")
                        
                        # Frequent itemsets tab
                        with assoc_tabs[1]:
                            st.subheader("Frequent Itemsets")
                            
                            if len(results["frequent_itemsets"]) > 0:
                                # Format itemsets table
                                itemsets_df = results["frequent_itemsets"].copy()
                                
                                # Convert frozensets to readable strings
                                itemsets_df['itemsets'] = itemsets_df['itemsets'].apply(lambda x: ', '.join(sorted(list(x))))
                                
                                # Add length of itemset
                                itemsets_df['num_items'] = itemsets_df['itemsets'].apply(lambda x: len(x.split(',')))
                                
                                # Sort by support
                                itemsets_df = itemsets_df.sort_values(['num_items', 'support'], ascending=[True, False])
                                
                                # Display itemsets
                                st.dataframe(itemsets_df)
                                
                                # Download itemsets
                                csv = itemsets_df.to_csv(index=False)
                                st.download_button(
                                    "Download Frequent Itemsets",
                                    csv,
                                    "frequent_itemsets.csv",
                                    "text/csv",
                                    key='download-frequent-itemsets'
                                )
                                
                                # Visualize itemset distribution
                                st.subheader("Itemset Size Distribution")
                                
                                size_counts = itemsets_df['num_items'].value_counts().sort_index()
                                
                                fig, ax = plt.subplots(figsize=(10, 5))
                                size_counts.plot(kind='bar', ax=ax)
                                ax.set_xlabel("Number of Items in Set")
                                ax.set_ylabel("Count")
                                ax.set_title("Distribution of Frequent Itemset Sizes")
                                ax.grid(True, alpha=0.3)
                                
                                st.pyplot(fig)
                            else:
                                st.warning("No frequent itemsets found with the current minimum support. Try lowering the minimum support.")
                        
                        # Visualization tab
                        with assoc_tabs[2]:
                            st.subheader("Rule Visualization")
                            
                            if len(results["rules"]) > 0:
                                # Create scatter plot of rules
                                fig, ax = plt.subplots(figsize=(10, 8))
                                
                                scatter = ax.scatter(
                                    results["rules"]['support'],
                                    results["rules"]['confidence'],
                                    alpha=0.5,
                                    s=results["rules"]['lift'] * 20,
                                    c=results["rules"]['lift'],
                                    cmap='viridis'
                                )
                                
                                ax.set_xlabel('Support')
                                ax.set_ylabel('Confidence')
                                ax.set_title('Association Rules (color and size by lift)')
                                ax.grid(True, alpha=0.3)
                                
                                plt.colorbar(scatter, label='Lift')
                                
                                st.pyplot(fig)
                                
                                # Network visualization of top rules
                                st.subheader("Network of Top Rules")
                                
                                try:
                                    import networkx as nx
                                except ImportError:
                                    st.warning("Installing NetworkX for network visualization...")
                                    subprocess.check_call([sys.executable, "-m", "pip", "install", "networkx"])
                                    import networkx as nx
                                
                                # Create a network from top rules
                                num_top_rules = min(20, len(results["rules"]))
                                top_rules = results["rules"].sort_values('lift', ascending=False).head(num_top_rules)
                                
                                G = nx.DiGraph()
                                
                                # Add edges from antecedents to consequents
                                for _, row in top_rules.iterrows():
                                    for ant in row['antecedents']:
                                        for con in row['consequents']:
                                            if G.has_edge(ant, con):
                                                G[ant][con]['weight'] += row['lift']
                                            else:
                                                G.add_edge(ant, con, weight=row['lift'])
                                
                                # Get node positions
                                pos = nx.spring_layout(G, seed=42)
                                
                                # Create graph
                                fig, ax = plt.subplots(figsize=(12, 10))
                                
                                # Node size proportional to degree
                                node_size = [G.degree(node) * 100 for node in G.nodes()]
                                
                                # Edge width proportional to lift
                                edge_width = [G[u][v]['weight'] for u, v in G.edges()]
                                
                                # Draw nodes and edges
                                nx.draw_networkx_nodes(G, pos, node_size=node_size, node_color='skyblue', alpha=0.8, ax=ax)
                                nx.draw_networkx_edges(G, pos, width=edge_width, alpha=0.5, edge_color='gray', arrows=True, ax=ax)
                                nx.draw_networkx_labels(G, pos, font_size=10, ax=ax)
                                
                                ax.set_title("Network of Association Rules")
                                ax.axis('off')
                                
                                st.pyplot(fig)
                                
                                # Interpretation
                                st.markdown("""
                                ### Interpretation Guide
                                
                                - **Support**: The frequency of the itemset in the dataset. Higher values mean more common patterns.
                                - **Confidence**: How often items in the antecedent (if) lead to items in the consequent (then).
                                - **Lift**: How much more likely the consequent is given the antecedent, compared to its baseline probability. 
                                  - Lift = 1: Items are independent
                                  - Lift > 1: Items are positively correlated 
                                  - Lift < 1: Items are negatively correlated (substitutes)
                                  
                                In the network visualization:
                                - **Nodes**: Individual items
                                - **Edges**: Rules connecting items (from antecedent to consequent)
                                - **Node size**: More connections = larger node
                                - **Edge width**: Higher lift = thicker edge
                                """)
                            else:
                                st.warning("No rules found to visualize. Try adjusting the parameters.")
            else:
                # Show example of what the data should look like
                st.write("### Example of Appropriate Data Format")
                example_data = pd.DataFrame({
                    'bread': [1, 0, 1, 1, 0, 1],
                    'milk': [1, 1, 0, 1, 0, 1],
                    'eggs': [0, 1, 1, 1, 0, 0],
                    'cheese': [0, 0, 1, 1, 1, 0],
                    'yogurt': [0, 1, 0, 0, 0, 1]
                })
                st.dataframe(example_data)
                st.info("In this example, each row is a transaction and each column is an item. 1 means the item is present, 0 means it's absent.")
        
        
        # Statistical Tests Tab
        with analysis_tabs[5]:
            st.header("Statistical Tests")
            
            st.write("""
            Statistical tests help you determine if patterns in your data are statistically significant
            or could have occurred by random chance. Choose a test based on your research question.
            """)
            
            # Get columns by type for the tests
            numeric_columns = data.select_dtypes(include=[np.number]).columns.tolist()
            categorical_columns = data.select_dtypes(include=['object', 'category']).columns.tolist()
            
            if numeric_columns:
                # Create tabs for different types of statistical tests
                test_tabs = st.tabs([
                    "T-Tests", 
                    "Correlation Tests", 
                    "ANOVA", 
                    "Chi-Square", 
                    "Normality Tests", 
                    "Variance Tests"
                ])
                
                # T-Tests
                with test_tabs[0]:
                    st.subheader("T-Tests")
                    st.write("T-tests compare means between groups.")
                    
                    test_type = st.radio(
                        "Select T-test type",
                        ["Independent Samples T-test", "Paired Samples T-test"],
                        key="t_test_type"
                    )
                    
                    if test_type == "Independent Samples T-test":
                        st.write("Tests whether two independent groups have different means.")
                        col1, col2 = st.columns(2)
                        with col1:
                            group1 = st.selectbox("Select first variable", numeric_columns, key="t_test_group1")
                        with col2:
                            group2 = st.selectbox("Select second variable", numeric_columns, index=min(1, len(numeric_columns)-1), key="t_test_group2")
                            
                        if st.button("Run Independent T-test", key="run_ind_ttest"):
                            results = perform_statistical_test(data, "t_test_ind", [group1, group2])
                            
                            if not results.get("error"):
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("t-statistic", f"{results['t_statistic']:.4f}")
                                with col2:
                                    st.metric("p-value", f"{results['p_value']:.4f}")
                                with col3:
                                    significant = results['significant']
                                    st.metric("Significant?", "Yes" if significant else "No")
                                
                                # Display means
                                st.subheader("Group Means")
                                means_df = pd.DataFrame({
                                    "Variable": [group1, group2],
                                    "Mean": [data[group1].mean(), data[group2].mean()],
                                    "Std. Dev.": [data[group1].std(), data[group2].std()],
                                    "Count": [data[group1].count(), data[group2].count()]
                                })
                                st.dataframe(means_df)
                                
                                # Visualization
                                fig, ax = plt.subplots(figsize=(10, 6))
                                
                                # Boxplot
                                ax.boxplot([data[group1].dropna(), data[group2].dropna()], labels=[group1, group2])
                                ax.set_title("Boxplot Comparison")
                                ax.grid(True, alpha=0.3)
                                
                                st.pyplot(fig)
                                
                                # Interpretation
                                st.subheader("Interpretation")
                                mean_diff = data[group1].mean() - data[group2].mean()
                                if significant:
                                    st.success(f"The difference between means ({mean_diff:.4f}) is statistically significant (p < 0.05).")
                                    st.write(f"We can reject the null hypothesis that the means of {group1} and {group2} are equal.")
                                else:
                                    st.info(f"The difference between means ({mean_diff:.4f}) is not statistically significant (p ≥ 0.05).")
                                    st.write(f"We cannot reject the null hypothesis that the means of {group1} and {group2} are equal.")
                            else:
                                st.error(results["error"])
                    
                    else:  # Paired T-test
                        st.write("Tests whether the mean difference between paired observations is zero.")
                        col1, col2 = st.columns(2)
                        with col1:
                            var1 = st.selectbox("Select first variable", numeric_columns, key="paired_var1")
                        with col2:
                            var2 = st.selectbox("Select second variable", numeric_columns, index=min(1, len(numeric_columns)-1), key="paired_var2")
                            
                        if st.button("Run Paired T-test", key="run_paired_ttest"):
                            results = perform_statistical_test(data, "t_test_paired", [var1, var2])
                            
                            if not results.get("error"):
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("t-statistic", f"{results['t_statistic']:.4f}")
                                with col2:
                                    st.metric("p-value", f"{results['p_value']:.4f}")
                                with col3:
                                    significant = results['significant']
                                    st.metric("Significant?", "Yes" if significant else "No")
                                
                                # Calculate differences
                                valid_data = data[[var1, var2]].dropna()
                                differences = valid_data[var1] - valid_data[var2]
                                
                                # Display stats
                                st.subheader("Paired Differences")
                                stats_df = pd.DataFrame({
                                    "Statistic": ["Mean Difference", "Std. Deviation", "Sample Size"],
                                    "Value": [differences.mean(), differences.std(), len(differences)]
                                })
                                st.dataframe(stats_df)
                                
                                # Visualization
                                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
                                
                                # Paired line plot
                                for i in range(min(len(valid_data), 50)):  # Limit to 50 pairs for clarity
                                    ax1.plot([1, 2], [valid_data[var1].iloc[i], valid_data[var2].iloc[i]], 'b-', alpha=0.3)
                                
                                ax1.plot([1, 2], [valid_data[var1].mean(), valid_data[var2].mean()], 'r-', linewidth=3, label='Mean')
                                ax1.set_xticks([1, 2])
                                ax1.set_xticklabels([var1, var2])
                                ax1.set_title("Paired Values")
                                ax1.grid(True, alpha=0.3)
                                ax1.legend()
                                
                                # Histogram of differences
                                ax2.hist(differences, bins=15, alpha=0.7)
                                ax2.axvline(x=0, color='r', linestyle='--', label='Zero difference')
                                ax2.axvline(x=differences.mean(), color='g', linestyle='-', label='Mean difference')
                                ax2.set_xlabel("Difference")
                                ax2.set_ylabel("Frequency")
                                ax2.set_title("Differences Histogram")
                                ax2.grid(True, alpha=0.3)
                                ax2.legend()
                                
                                fig.tight_layout()
                                st.pyplot(fig)
                                
                                # Interpretation
                                st.subheader("Interpretation")
                                mean_diff = differences.mean()
                                if significant:
                                    st.success(f"The mean difference ({mean_diff:.4f}) is statistically significant (p < 0.05).")
                                    st.write(f"We can reject the null hypothesis that there is no difference between {var1} and {var2}.")
                                else:
                                    st.info(f"The mean difference ({mean_diff:.4f}) is not statistically significant (p ≥ 0.05).")
                                    st.write(f"We cannot reject the null hypothesis that there is no difference between {var1} and {var2}.")
                            else:
                                st.error(results["error"])
                
                # Correlation Tests
                with test_tabs[1]:
                    st.subheader("Correlation Tests")
                    st.write("Tests for relationships between variables.")
                    
                    test_type = st.radio(
                        "Select correlation test",
                        ["Pearson Correlation", "Spearman Rank Correlation"],
                        key="corr_test_type"
                    )
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        var1 = st.selectbox("Select first variable", numeric_columns, key="corr_var1")
                    with col2:
                        var2 = st.selectbox("Select second variable", numeric_columns, index=min(1, len(numeric_columns)-1), key="corr_var2")
                    
                    if test_type == "Pearson Correlation":
                        if st.button("Run Pearson Correlation", key="run_pearson"):
                            results = perform_statistical_test(data, "pearson", [var1, var2])
                            
                            if not results.get("error"):
                                show_correlation_results(results, var1, var2, data)
                            else:
                                st.error(results["error"])
                    else:  # Spearman correlation
                        if st.button("Run Spearman Correlation", key="run_spearman"):
                            results = perform_statistical_test(data, "spearman", [var1, var2])
                            
                            if not results.get("error"):
                                show_correlation_results(results, var1, var2, data)
                            else:
                                st.error(results["error"])
                
                # ANOVA
                with test_tabs[2]:
                    st.subheader("ANOVA (Analysis of Variance)")
                    st.write("Tests if there are differences among means of multiple groups.")
                    
                    # Select variables for ANOVA
                    selected_vars = st.multiselect(
                        "Select at least two numeric variables to compare", 
                        numeric_columns,
                        default=numeric_columns[:min(3, len(numeric_columns))],
                        key="anova_vars"
                    )
                    
                    if len(selected_vars) < 2:
                        st.warning("ANOVA requires at least two groups. Please select more variables.")
                    else:
                        if st.button("Run ANOVA", key="run_anova"):
                            results = perform_statistical_test(data, "anova", selected_vars)
                            
                            if not results.get("error"):
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("F-statistic", f"{results['f_statistic']:.4f}")
                                with col2:
                                    st.metric("p-value", f"{results['p_value']:.4f}")
                                with col3:
                                    significant = results['significant']
                                    st.metric("Significant?", "Yes" if significant else "No")
                                
                                # Display group stats
                                st.subheader("Group Statistics")
                                stats_df = pd.DataFrame({
                                    "Variable": selected_vars,
                                    "Mean": [data[var].mean() for var in selected_vars],
                                    "Std. Dev.": [data[var].std() for var in selected_vars],
                                    "Count": [data[var].count() for var in selected_vars]
                                })
                                st.dataframe(stats_df)
                                
                                # Visualization
                                fig, ax = plt.subplots(figsize=(12, 6))
                                
                                # Boxplot
                                boxplot_data = [data[var].dropna() for var in selected_vars]
                                ax.boxplot(boxplot_data, labels=selected_vars)
                                ax.set_title("Boxplot Comparison")
                                ax.grid(True, alpha=0.3)
                                
                                st.pyplot(fig)
                                
                                # Interpretation
                                st.subheader("Interpretation")
                                if significant:
                                    st.success("The ANOVA test is statistically significant (p < 0.05).")
                                    st.write("We can reject the null hypothesis that all group means are equal.")
                                    st.write("This suggests there are statistically significant differences between some of the groups.")
                                    
                                    # Post-hoc tests recommendation
                                    st.info("""
                                    **Next Steps**: Since the ANOVA is significant, consider running post-hoc tests 
                                    (like Tukey's HSD or Bonferroni) to determine which specific groups differ from each other.
                                    """)
                                else:
                                    st.info("The ANOVA test is not statistically significant (p ≥ 0.05).")
                                    st.write("We cannot reject the null hypothesis that all group means are equal.")
                                    st.write("There is not enough evidence to suggest differences between the groups.")
                            else:
                                st.error(results["error"])
                
                # Chi-Square
                with test_tabs[3]:
                    st.subheader("Chi-Square Test of Independence")
                    st.write("Tests if there is a relationship between categorical variables.")
                    
                    if not categorical_columns:
                        st.warning("No categorical columns found in the data. Chi-square test requires categorical variables.")
                        
                        # Option to treat numeric variables as categorical
                        st.write("You can use numeric columns with few unique values as categorical variables:")
                        
                        potential_categorical = []
                        for col in numeric_columns:
                            if data[col].nunique() < 10:
                                potential_categorical.append(col)
                                
                        if potential_categorical:
                            selected_cat_vars = st.multiselect(
                                "Select numeric variables to treat as categorical", 
                                potential_categorical,
                                default=potential_categorical[:min(2, len(potential_categorical))],
                                key="chi_square_num_vars"
                            )
                            
                            if len(selected_cat_vars) >= 2:
                                col1, col2 = st.columns(2)
                                with col1:
                                    var1 = st.selectbox("First variable", selected_cat_vars, key="chi_var1")
                                with col2:
                                    var2 = st.selectbox("Second variable", selected_cat_vars, index=1, key="chi_var2")
                                    
                                if st.button("Run Chi-Square Test", key="run_chi_square"):
                                    results = perform_statistical_test(data, "chi_square", [var1, var2])
                                    
                                    if not results.get("error"):
                                        show_chi_square_results(results, var1, var2, data)
                                    else:
                                        st.error(results["error"])
                            else:
                                st.warning("Chi-square test requires at least two categorical variables.")
                        else:
                            st.error("No suitable numeric variables found to use as categorical variables.")
                    else:
                        # Use actual categorical variables
                        col1, col2 = st.columns(2)
                        with col1:
                            var1 = st.selectbox("First categorical variable", categorical_columns, key="chi_var1")
                        with col2:
                            default_idx = 1 if len(categorical_columns) > 1 else 0
                            var2 = st.selectbox("Second categorical variable", categorical_columns, index=default_idx, key="chi_var2")
                            
                        if st.button("Run Chi-Square Test", key="run_chi_square"):
                            results = perform_statistical_test(data, "chi_square", [var1, var2])
                            
                            if not results.get("error"):
                                show_chi_square_results(results, var1, var2, data)
                            else:
                                st.error(results["error"])
                
                # Normality Tests
                with test_tabs[4]:
                    st.subheader("Normality Tests")
                    st.write("Tests whether a variable follows a normal distribution.")
                    
                    # Select variable for normality test
                    var = st.selectbox("Select variable to test", numeric_columns, key="normality_var")
                    
                    if st.button("Run Shapiro-Wilk Test", key="run_shapiro"):
                        results = perform_statistical_test(data, "shapiro", [var])
                        
                        if not results.get("error"):
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("W-statistic", f"{results['w_statistic']:.4f}")
                            with col2:
                                st.metric("p-value", f"{results['p_value']:.4f}")
                            with col3:
                                significant = results['significant']
                                st.metric("Normal?", "No" if significant else "Yes")
                            
                            # Visualization
                            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
                            
                            # Histogram with normal curve
                            var_data = data[var].dropna()
                            ax1.hist(var_data, bins=20, density=True, alpha=0.6)
                            
                            # Add normal curve
                            x = np.linspace(var_data.min(), var_data.max(), 100)
                            mu, sigma = var_data.mean(), var_data.std()
                            ax1.plot(x, stats.norm.pdf(x, mu, sigma), 'r-', linewidth=2)
                            
                            ax1.set_xlabel(var)
                            ax1.set_ylabel("Density")
                            ax1.set_title("Histogram with Normal Curve")
                            ax1.grid(True, alpha=0.3)
                            
                            # Q-Q plot
                            stats.probplot(var_data, plot=ax2)
                            ax2.set_title("Q-Q Plot")
                            ax2.grid(True, alpha=0.3)
                            
                            fig.tight_layout()
                            st.pyplot(fig)
                            
                            # Interpretation
                            st.subheader("Interpretation")
                            if significant:
                                st.warning(f"The Shapiro-Wilk test is significant (p < 0.05), suggesting that {var} is not normally distributed.")
                                st.write("The Q-Q plot shows deviations from the diagonal line, confirming departure from normality.")
                            else:
                                st.success(f"The Shapiro-Wilk test is not significant (p ≥ 0.05), suggesting that {var} follows a normal distribution.")
                                st.write("The Q-Q plot points approximately follow the diagonal line, confirming normality.")
                            
                            # Show descriptive statistics
                            st.subheader("Descriptive Statistics")
                            stats_df = pd.DataFrame({
                                "Statistic": ["Mean", "Median", "Std. Deviation", "Skewness", "Kurtosis"],
                                "Value": [
                                    var_data.mean(),
                                    var_data.median(),
                                    var_data.std(),
                                    var_data.skew(),
                                    var_data.kurtosis()
                                ]
                            })
                            st.dataframe(stats_df)
                            
                            # Interpretation of skewness and kurtosis
                            skew = var_data.skew()
                            kurt = var_data.kurtosis()
                            
                            skew_interp = ""
                            if abs(skew) < 0.5:
                                skew_interp = "approximately symmetric"
                            elif skew < -0.5:
                                skew_interp = "negatively skewed (left-skewed)"
                            else:
                                skew_interp = "positively skewed (right-skewed)"
                                
                            kurt_interp = ""
                            if abs(kurt) < 0.5:
                                kurt_interp = "approximately normal"
                            elif kurt < -0.5:
                                kurt_interp = "platykurtic (flatter than normal)"
                            else:
                                kurt_interp = "leptokurtic (more peaked than normal)"
                                
                            st.write(f"The distribution is {skew_interp} and {kurt_interp}.")
                        else:
                            st.error(results["error"])
                
                # Variance Tests
                with test_tabs[5]:
                    st.subheader("Variance Tests")
                    st.write("Tests if multiple groups have equal variances (homogeneity of variance).")
                    
                    # Select variables for Levene's test
                    selected_vars = st.multiselect(
                        "Select at least two numeric variables to compare variances", 
                        numeric_columns,
                        default=numeric_columns[:min(3, len(numeric_columns))],
                        key="var_test_vars"
                    )
                    
                    if len(selected_vars) < 2:
                        st.warning("Levene's test requires at least two groups. Please select more variables.")
                    else:
                        if st.button("Run Levene's Test", key="run_levene"):
                            results = perform_statistical_test(data, "levene", selected_vars)
                            
                            if not results.get("error"):
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Test Statistic", f"{results['statistic']:.4f}")
                                with col2:
                                    st.metric("p-value", f"{results['p_value']:.4f}")
                                with col3:
                                    significant = results['significant']
                                    st.metric("Equal Variances?", "No" if significant else "Yes")
                                
                                # Display group stats
                                st.subheader("Group Statistics")
                                stats_df = pd.DataFrame({
                                    "Variable": selected_vars,
                                    "Mean": [data[var].mean() for var in selected_vars],
                                    "Std. Dev.": [data[var].std() for var in selected_vars],
                                    "Variance": [data[var].var() for var in selected_vars],
                                    "Count": [data[var].count() for var in selected_vars]
                                })
                                st.dataframe(stats_df)
                                
                                # Visualization
                                fig, ax = plt.subplots(figsize=(12, 6))
                                
                                # Boxplot
                                boxplot_data = [data[var].dropna() for var in selected_vars]
                                ax.boxplot(boxplot_data, labels=selected_vars)
                                ax.set_title("Boxplot Comparison for Variance")
                                ax.grid(True, alpha=0.3)
                                
                                st.pyplot(fig)
                                
                                # Interpretation
                                st.subheader("Interpretation")
                                if significant:
                                    st.warning("Levene's test is significant (p < 0.05), suggesting that the variances are not equal across groups.")
                                    st.write("This indicates heteroscedasticity (unequal variances).")
                                    
                                    # Recommendations
                                    st.info("""
                                    **Recommendations**:
                                    - Consider transformations to stabilize variance
                                    - Use statistical tests that don't assume equal variances
                                    - For ANOVA, consider Welch's ANOVA instead of traditional ANOVA
                                    - For t-tests, use the Welch's t-test (unequal variance t-test)
                                    """)
                                else:
                                    st.success("Levene's test is not significant (p ≥ 0.05), suggesting that the variances are approximately equal across groups.")
                                    st.write("This supports the assumption of homoscedasticity (equal variances).")
                            else:
                                st.error(results["error"])
            else:
                st.error("No numeric columns found in the data for statistical tests.")
        
        # AI Analysis Tab
        with analysis_tabs[6]:
            st.header("AI-Powered Pattern Analysis")
            
            # Check for API key availability
            openai_key = get_api_key('OPENAI')
            anthropic_key = get_api_key('ANTHROPIC')
            
            ai_available = bool(openai_key or anthropic_key)
            
            if not ai_available:
                st.warning("AI analysis requires API keys for OpenAI or Anthropic. Please add them in Settings.")
                
                # Show an example of what the AI analysis would do
                st.subheader("What AI Analysis Can Do")
                st.info("""
                AI-powered analysis can help you:
                
                - Discover complex patterns in your data
                - Get plain-language interpretations of statistical findings
                - Generate hypotheses based on data patterns
                - Suggest next steps for analysis or data collection
                - Create data visualizations and narratives
                
                To enable this feature, you need to add your API keys in the Settings tab.
                """)
            else:
                # Choose AI model
                available_models = []
                if openai_key:
                    available_models.append("OpenAI")
                if anthropic_key:
                    available_models.append("Anthropic")
                    
                ai_model = st.radio(
                    "Select AI Model",
                    options=available_models,
                    horizontal=True,
                    key="ai_model_choice"
                )
                
                # User's question about the data
                user_question = st.text_area(
                    "What would you like to know about the patterns in this data?",
                    placeholder="Example: What are the key patterns in this dataset? Are there any correlations between the features? What insights can you provide from this data?",
                    height=100,
                    key="ai_question"
                )
                
                # Additional analysis options
                with st.expander("Advanced Analysis Options", expanded=False):
                    analysis_depth = st.select_slider(
                        "Analysis Depth",
                        options=["Basic", "Standard", "In-Depth"],
                        value="Standard",
                        key="analysis_depth"
                    )
                    
                    focus_areas = st.multiselect(
                        "Focus Areas (Optional)",
                        ["Correlations", "Outliers", "Trends", "Groups/Clusters", "Anomalies", "Predictions", "Causality"],
                        key="focus_areas"
                    )
                    
                    # Sample size for large datasets
                    if data.shape[0] > 1000:
                        sample_size = st.slider(
                            "Sample Size for Analysis",
                            min_value=100,
                            max_value=min(10000, data.shape[0]),
                            value=1000,
                            step=100,
                            help="For large datasets, using a sample can improve analysis speed."
                        )
                    else:
                        sample_size = data.shape[0]
                
                if st.button("Analyze Data with AI", key="run_ai_analysis"):
                    if user_question:
                        with st.spinner("Analyzing data with AI..."):
                            # Prepare data for AI analysis
                            data_for_ai = data
                            if data.shape[0] > sample_size:
                                data_for_ai = data.sample(sample_size, random_state=42)
                                st.info(f"Using a sample of {sample_size} rows for AI analysis due to dataset size ({data.shape[0]} rows).")
                            
                            # Enhance question with focus areas if specified
                            enhanced_question = user_question
                            if focus_areas:
                                enhanced_question += f"\n\nPlease focus especially on: {', '.join(focus_areas)}."
                            
                            if analysis_depth == "In-Depth":
                                enhanced_question += "\n\nPlease provide a very detailed analysis with statistical measures and thorough explanations."
                            elif analysis_depth == "Basic":
                                enhanced_question += "\n\nPlease provide a simple, high-level analysis with key insights only."
                            
                            # Call the AI analysis function
                            model_name = ai_model.lower()
                            results = analyze_patterns_with_ai(data_for_ai, "Comprehensive Data Analysis", enhanced_question, model_name)
                            
                            if results.get("error"):
                                st.error(f"AI Analysis Error: {results['error']}")
                            else:
                                st.success(f"Analysis completed using {results.get('model', model_name)}")
                                
                                # Create tabs for results and history
                                ai_result_tabs = st.tabs(["Analysis Results", "Analysis History"])
                                
                                with ai_result_tabs[0]:
                                    st.markdown("## AI Analysis Results")
                                    st.markdown(results["result"])
                                
                                with ai_result_tabs[1]:
                                    # Save this analysis to history
                                    if 'history' not in st.session_state.pattern_recognition_settings:
                                        st.session_state.pattern_recognition_settings['history'] = []
                                    
                                    # Add to history (limiting to last 5 analyses)
                                    st.session_state.pattern_recognition_settings['history'].append({
                                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                                        'model': model_name,
                                        'question': user_question,
                                        'result': results["result"]
                                    })
                                    
                                    # Keep only last 5 analyses
                                    if len(st.session_state.pattern_recognition_settings['history']) > 5:
                                        st.session_state.pattern_recognition_settings['history'] = st.session_state.pattern_recognition_settings['history'][-5:]
                                    
                                    # Show analysis history
                                    st.subheader("Previous Analyses")
                                    
                                    if st.session_state.pattern_recognition_settings.get('history'):
                                        for i, analysis in enumerate(reversed(st.session_state.pattern_recognition_settings['history'])):
                                            with st.expander(f"Analysis {i+1} - {analysis['timestamp']}", expanded=i==0):
                                                st.caption(f"Model: {analysis['model']}")
                                                st.info(f"Question: {analysis['question']}")
                                                st.markdown(analysis['result'])
                                    else:
                                        st.info("No analysis history yet.")
                    else:
                        st.warning("Please enter a question about the data patterns.")

def show_correlation_results(results, var1, var2, data):
    """Helper function to display correlation results"""
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Correlation", f"{results['correlation']:.4f}")
    with col2:
        st.metric("p-value", f"{results['p_value']:.4f}")
    with col3:
        significant = results['significant']
        st.metric("Significant?", "Yes" if significant else "No")
    
    # Display interpretation
    st.info(f"**Interpretation**: {results['interpretation']}")
    
    # Visualization
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Scatter plot with regression line
    ax.scatter(data[var1], data[var2], alpha=0.5)
    
    # Add regression line
    if abs(results['correlation']) > 0.1:  # Only if there's some correlation
        from scipy import stats
        slope, intercept, _, _, _ = stats.linregress(data[var1].dropna(), data[var2].dropna())
        x = np.array([data[var1].min(), data[var1].max()])
        ax.plot(x, intercept + slope * x, 'r')
    
    ax.set_xlabel(var1)
    ax.set_ylabel(var2)
    ax.set_title(f"Scatter Plot: {var1} vs {var2}")
    ax.grid(True, alpha=0.3)
    
    st.pyplot(fig)
    
    # Interpretation
    st.subheader("Interpretation")
    if significant:
        st.success(f"The correlation ({results['correlation']:.4f}) is statistically significant (p < 0.05).")
        
        if results['correlation'] > 0:
            st.write(f"There is a significant positive relationship between {var1} and {var2}.")
        else:
            st.write(f"There is a significant negative relationship between {var1} and {var2}.")
        
        st.write(f"Strength: {results['interpretation']}")
        
        # Calculate R-squared
        r_squared = results['correlation'] ** 2
        st.write(f"R² value: {r_squared:.4f} ({r_squared*100:.1f}% of variance explained)")
    else:
        st.info(f"The correlation ({results['correlation']:.4f}) is not statistically significant (p ≥ 0.05).")
        st.write(f"We cannot conclude that there is a relationship between {var1} and {var2}.")

def show_chi_square_results(results, var1, var2, data):
    """Helper function to display chi-square results"""
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Chi² Statistic", f"{results['chi2_statistic']:.4f}")
    with col2:
        st.metric("p-value", f"{results['p_value']:.4f}")
    with col3:
        significant = results['significant']
        st.metric("Significant?", "Yes" if significant else "No")
    
    # Display contingency table
    st.subheader("Contingency Table (Observed Frequencies)")
    st.dataframe(results["contingency_table"])
    
    # Display expected frequencies
    st.subheader("Expected Frequencies")
    st.dataframe(results["expected_frequencies"])
    
    # Visualization
    st.subheader("Visualization")
    
    # Categorical heatmap of contingency table
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Create heatmap
    sns.heatmap(
        results["contingency_table"],
        annot=True,
        fmt='d',
        cmap='Blues',
        ax=ax
    )
    
    ax.set_title(f"Contingency Table: {var1} vs {var2}")
    ax.set_xlabel(var2)
    ax.set_ylabel(var1)
    
    st.pyplot(fig)
    
    # Stacked bar chart
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Normalize the contingency table for percentage view
    prop_table = results["contingency_table"].div(results["contingency_table"].sum(axis=1), axis=0)
    
    prop_table.plot(kind='bar', stacked=True, ax=ax)
    ax.set_title(f"Proportions of {var2} within each {var1} Category")
    ax.set_xlabel(var1)
    ax.set_ylabel(f"Proportion of {var2}")
    ax.legend(title=var2)
    ax.grid(True, alpha=0.3)
    
    st.pyplot(fig)
    
    # Interpretation
    st.subheader("Interpretation")
    if significant:
        st.success(f"The chi-square test is statistically significant (p < 0.05, chi² = {results['chi2_statistic']:.4f}, df = {results['dof']}).")
        st.write(f"We can reject the null hypothesis of independence between {var1} and {var2}.")
        st.write(f"This suggests there is a relationship between these variables.")
        
        # Calculate Cramer's V for effect size
        n = results["contingency_table"].sum().sum()
        min_dim = min(results["contingency_table"].shape) - 1
        cramers_v = np.sqrt(results["chi2_statistic"] / (n * min_dim))
        
        st.write(f"**Effect Size (Cramer's V)**: {cramers_v:.4f}")
        
        if cramers_v < 0.1:
            strength = "very weak"
        elif cramers_v < 0.3:
            strength = "weak"
        elif cramers_v < 0.5:
            strength = "moderate"
        else:
            strength = "strong"
            
        st.write(f"This indicates a {strength} association.")
        
        # Suggest examining cells with large differences
        st.write("### Cells with Largest Differences")
        st.write("These cells contribute most to the chi-square statistic:")
        
        # Calculate cell-wise contributions to chi-square
        observed = results["contingency_table"].values
        expected = results["expected_frequencies"].values
        contributions = (observed - expected)**2 / expected
        
        # Convert to DataFrame with same labels
        contrib_df = pd.DataFrame(
            contributions, 
            index=results["contingency_table"].index,
            columns=results["contingency_table"].columns
        )
        
        # Get top 3 contributing cells
        flat_contrib = contrib_df.stack().reset_index()
        flat_contrib.columns = [var1, var2, 'Contribution']
        top_cells = flat_contrib.nlargest(3, 'Contribution')
        
        st.table(top_cells)
    else:
        st.info(f"The chi-square test is not statistically significant (p ≥ 0.05, chi² = {results['chi2_statistic']:.4f}, df = {results['dof']}).")
        st.write(f"We cannot reject the null hypothesis of independence between {var1} and {var2}.")
        st.write(f"The data does not provide sufficient evidence of a relationship between these variables.")

# -------------------------------------------------------------------
if __name__ == "__main__":
    pattern_recognition_ui()
