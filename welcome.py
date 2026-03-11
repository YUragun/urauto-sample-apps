# streamlit run C:\Users\yavuz\urauto\frontend\apps\welcome\welcome.py
# streamlit run c:/Users/yavuzuragun/Desktop/URAUTO_APPS/app2/app.py --server.port 8502
import sys
import streamlit as st
import time
import random
import sys
import collections
import collections.abc

# Add backward compatibility for libraries that expect collections.abc to be in collections
sys.modules['collections'].abc = collections.abc

def main():
    # Page configuration
    st.set_page_config(
        page_title="urauto.ai Tutorial",
        layout="wide"
    )

    # Create tabs for different sections
    tabs = st.tabs([
        "Overview",
        "Quick Build",
        "Components",
        "Component Configurations",
        "Application Builder",
        "Running & Managing Apps",
        "QB Advanced Features",
        "Account Management",
        "FAQ"
    ])

    # ===============================
    # TAB 1: OVERVIEW
    # ===============================
    tab_counter = 0
    with tabs[tab_counter]:
        st.title("🚀 Welcome to urauto.ai")
        
        # Introduction with animation
        st.markdown("""
        ### Your AI App Creation Platform

        urauto.ai helps you quickly **create, manage, and integrate** AI-powered applications without coding skills. Simply describe what you want, and our platform builds it for you.
        
        ### What You Can Do:
        """)
        
        # Create a multi-column layout to display key features
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            - **Create AI apps** from simple text prompts
            - **Integrate with popular SaaS tools** like Slack, Stripe, etc.
            - **Add advanced capabilities** like computer vision or voice
            - **Run apps** on your own subdomain
            """)
            
        with col2:
            st.markdown("""
            - **Access API keys** securely for different services
            - **Revise and improve** your apps with additional prompts
            - **Share your creations** in the marketplace
            - **Monitor usage** and manage your payments
            """)
        
        st.divider()
        
        # Interactive demo with random app ideas
        st.subheader("💡 Sample App Ideas")
        
        # Define a list of app ideas
        app_ideas = [
            {
                "title": "News Summarizer with Email Delivery",
                "description": "Web app that scrapes news from major websites, summarizes the articles using AI, and delivers daily summaries via email.",
                "features": ["Web scraping", "AI summarization", "Daily email dispatch", "User preference settings"],
                "tokens": 5
            },
            {
                "title": "Customer Support Chatbot",
                "description": "AI-powered chatbot that answers customer questions based on your company's knowledge base and product documentation.",
                "features": ["NLP processing", "Knowledge base integration", "Conversation history", "Handoff to human support"],
                "tokens": 7
            },
            {
                "title": "Social Media Content Generator",
                "description": "Creates engaging social media posts and images for multiple platforms based on your brand guidelines and target audience.",
                "features": ["Content creation", "Image generation", "Platform-specific formatting", "Scheduling"],
                "tokens": 6
            },
            {
                "title": "Real Estate Market Analyzer",
                "description": "Monitors property listings across multiple sites, analyzes price trends, and alerts you to potential investment opportunities.",
                "features": ["Property data scraping", "Price trend analysis", "Investment scoring", "Email alerts"],
                "tokens": 8
            },
            {
                "title": "Personal Fitness Coach",
                "description": "Creates personalized workout plans and nutrition advice based on your goals, preferences, and progress.",
                "features": ["Workout planning", "Nutrition recommendations", "Progress tracking", "Video demonstrations"],
                "tokens": 5
            }
        ]
        
        # Display a random app idea
        random_idea = random.choice(app_ideas)
        
        st.write(f"""
        **App Concept:** {random_idea["title"]}
        
        **Description:** {random_idea["description"]}
        
        **Features:**
        """)
        
        for feature in random_idea["features"]:
            st.write(f"- {feature}")
        
        if st.button("Show Another Idea"):
            st.cache_data.clear()
            st.rerun()
            
        st.divider()
        
        # Navigation guide
        st.header("📍 How to Navigate This Tutorial")
        st.write("Use the tabs above to explore different aspects of the platform:")
        
        tab_descriptions = {
            "Overview": "Platform introduction and key features",
            "Quick Build": "Fastest way to create and deploy an app",
            "Components": "Understanding and using building blocks",
            "Component Configurations": "Setting up default configurations",
            "Application Builder": "Visual app builder interface tutorial",
            "Running & Managing Apps": "Operating and updating your apps",
            "QB Advanced Features": "Enhancing quick build apps with special capabilities",
            "Account Management": "Recharging balance and account settings",
            "FAQ": "Find answers to frequently asked questions"
        }
        
        for tab, description in tab_descriptions.items():
            st.markdown(f"- **{tab}**: {description}")
            
    tab_counter += 1

    # ===============================
    # TAB 2: QUICK BUILD
    # ===============================
    with tabs[tab_counter]:
        st.header("⚡ Quick Build Guide")
        
        st.markdown("""
        Get your first app running in under 10 minutes! This is the fastest path from idea to live application.
        """)
        
        # Prerequisites section
        st.subheader("📋 Prerequisites")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Required:**
            - urauto.ai account with sufficient balance ($50+ recommended)
            - Clear idea of what you want to build
            
            **Helpful to have:**
            - API keys for external services (if needed)
            - 7-10 minutes of uninterrupted time
            """)
            
        with col2:
            st.info("""
            **💡 Pro Tip:** Start with a simple app idea first. You can always add complexity through revisions later!
            """)
        
        st.divider()
        
        # Step-by-step guide
        st.subheader("🚀 Quick Build Process")
        
        # Step 1
        with st.expander("**Step 1: Access the Dashboard** (30 seconds)", expanded=True):
            st.markdown("""
            1. Log into your urauto.ai account
            2. Navigate to your **Dashboard**
            3. Click on the **Applications** tab
            4. Click the **"Add App"** button (green plus icon)
            
            ✅ You should now see the app creation form
            """)
        
        # Step 2
        with st.expander("**Step 2: Fill Basic Information** (1 minute)"):
            st.markdown("""
            **App Name:** Choose a unique name (lowercase, hyphens only)
            - ✅ Good: `my-weather-app`, `task-manager`, `news-reader`
            - ❌ Bad: `My App!`, `App 123`, `test`
            
            **App Idea:** Be specific but concise
            - ✅ Good: "Create a web app that fetches weather data and sends daily forecasts via email"
            - ❌ Bad: "Make a weather app"
            
            **Runtime:** Start with 1 hour for testing
            
            **Public:** Leave unchecked for the first run of your app
            """)
            
            st.code("""
            Example Quick Build Form:
            
            App Name: weather-notifier
            App Idea: Create a web app that fetches weather data from OpenWeatherMap API 
                     and displays current conditions with a 5-day forecast. Include 
                     temperature, humidity, and weather icons.
            Runtime: 1 hour
            Public: ☐ (unchecked)
            """)
        
        # Step 3
        with st.expander("**Step 3: API Keys (if needed)** (1 minute)"):
            st.markdown("""
            **If your app needs external APIs:**
            1. Go to **Settings & API Keys** tab first
            2. Add required API keys for services like:
               - OpenAI (for AI features)
               - OpenWeatherMap (for weather data)  
               - Stripe (for payments)
               - Twilio (for SMS)
            
            **If your app is self-contained:**
            - Skip this step - you can always add API keys later
            
            **Common free API keys to get:**
            - OpenWeatherMap: Free 1000 calls/day
            - News API: Free 1000 requests/day
            - JSONPlaceholder: No key needed (test data)
            """)
        
        # Step 4
        with st.expander("**Step 4: Submit and Wait** (7 minutes)"):
            st.markdown("""
            1. Click **"Create App"**
            2. Your app will start building immediately
            3. **Wait approximately 7 minutes** - don't refresh!
            4. You'll see the status change from "Building" to "Running"
            5. Your app URL will be: `https://your-app-name.urauto.ai`
            
            **While you wait:**
            - The AI agent is writing your code
            - Installing dependencies  
            - Setting up the web server
            - Configuring your domain
            """)
        
        # Step 5
        with st.expander("**Step 5: Test Your App** (30 seconds)"):
            st.markdown("""
            1. Click on your app URL when it becomes active
            2. Test the basic functionality
            3. Check that all features work as expected
            
            **If something's not right:**
            - Use the **Revisions** panel to request changes
            - Example: "Add a dark mode toggle" or "Make the text bigger"
            """)
        
        st.divider()
        
        # Quick build examples
        st.subheader("📝 Quick Build Templates")
        
        quick_templates = {
            "Simple Dashboard": {
                "name": "my-dashboard", 
                "idea": "Create a personal dashboard with widgets for weather, news headlines, and a to-do list. Use a clean, modern design with cards and responsive layout.",
                "time": "7 minutes",
                "apis": "None required"
            },
            "Task Manager": {
                "name": "task-tracker",
                "idea": "Build a task management app where users can add, edit, delete, and mark tasks as complete. Include categories and due dates with a simple interface.",
                "time": "7 minutes", 
                "apis": "None required"
            },
            "Weather App": {
                "name": "weather-today",
                "idea": "Create a weather app that shows current conditions and 5-day forecast for a user's location. Include temperature, humidity, wind speed, and weather icons.",
                "time": "7 minutes",
                "apis": "OpenWeatherMap (free)"
            },
            "News Reader": {
                "name": "daily-news",
                "idea": "Build a news aggregator that displays latest headlines from multiple sources with article summaries and links to full articles.",
                "time": "7 minutes",
                "apis": "News API (free tier)"
            }
        }
        
        for template_name, details in quick_templates.items():
            with st.expander(f"**{template_name}** - {details['time']} build"):
                st.markdown(f"""
                **App Name:** `{details['name']}`
                
                **App Idea:**
                ```
                {details['idea']}
                ```
                
                **APIs Needed:** {details['apis']}
                
                **Estimated Build Time:** {details['time']}
                """)
        
        st.divider()
                # Advanced options
        st.subheader("Advanced Options")
        st.markdown("""
        When creating your quick build app, you can also select and configure advanced options:
        """)
        
        # Create expandable sections for each advanced option
        with st.expander("Feature Options"):
            st.markdown("""
            - **SaaS Integration**: Connect to external services
            - **Object Detection**: Identify objects in images using CV2/YOLO
            - **Pattern Recognition**: Detect patterns using RNN/LSTM models
            - **Realtime Voice**: Voice processing and commands
            - **Content Creation**: Generate text and images with LLMs
            - **Email (SMTP)**: Send emails from your app
            - **Data Collection**: Web crawling and data gathering tools
            """)
        
        # Best practices
        st.subheader("💡 Tips for Successful App Creation")
        st.markdown("""
        - Be specific in your app descriptions
        - Start with a focused scope, then expand with revisions
        - Only select features you actually need
        - Check the marketplace for inspiration
        """)
        st.divider()
        
        # Troubleshooting
        st.subheader("🔧 Quick Troubleshooting")
        
        troubleshooting = {
            "App won't load": [
                "Wait the full 7 minutes for initial build",
                "Check your account balance is sufficient",
                "Try refreshing the page once",
                "Verify your app name doesn't conflict with existing apps"
            ],
            "Missing features": [
                "Use the Revisions panel to request additions",
                "Be specific: 'Add a search box to filter items'",
                "Wait 7 minutes between revision requests"
            ],
            "API errors": [
                "Verify API keys are correctly entered in Settings",
                "Check API key has proper permissions",
                "Ensure API service is not rate-limited"
            ],
            "Out of balance": [
                "Go to 'Recharge Account' tab",
                "Add minimum $20 to continue",
                "Apps will auto-shutdown when balance runs out"
            ]
        }
        
        for issue, solutions in troubleshooting.items():
            st.markdown(f"**{issue}:**")
            for solution in solutions:
                st.markdown(f"- {solution}")
            st.markdown("")
        
        st.success("""
        🎉 **Congratulations!** You've learned the Quick Build process. 
        
        **Next Steps:**
        - Try building one of the template apps above
        - Explore the Components tab to understand building blocks
        - Learn about Component Configurations for reusable settings
        """)
        
    tab_counter += 1

    # ===============================
    # TAB 3: COMPONENTS
    # ===============================
    with tabs[tab_counter]:
        st.header("🧩 Understanding Components")
        
        st.markdown("""
        Components are the building blocks of your applications. Each component provides specific functionality 
        that can be connected together to create powerful workflows.
        """)
        
        # Component categories overview
        st.subheader("📂 Component Categories")
        
        # Create tabs for each category
        component_tabs = st.tabs(["Automate", "Integrate", "Prototype"])
        
        # AUTOMATE tab
        with component_tabs[0]:
            st.markdown("### 🔄 Automate Components")
            st.markdown("These components help you automate tasks and processes.")
            
            # Communication subcategory
            st.markdown("#### 📨 Communication")
            
            comm_col1, comm_col2, comm_col3 = st.columns(3)
            
            with comm_col1:
                st.markdown("""
                **📧 Email**
                - Send automated emails
                - SMTP server configuration
                - Support for HTML and plain text
                - Attachment handling
                
                *Example use:* Daily report delivery, user notifications
                """)
            
            with comm_col2:
                st.markdown("""
                **💬 SMS**
                - Send text messages via Twilio
                - Support for international numbers
                - Delivery status tracking
                - Two-way messaging
                
                *Example use:* Order confirmations, alerts
                """)
            
            with comm_col3:
                st.markdown("""
                **🎤 Voice** *(Coming Soon)*
                - Text-to-speech conversion
                - Voice call automation
                - Interactive voice response
                - Call recording
                
                *Example use:* Phone notifications, surveys
                """)
            
            st.divider()
            
            # Object Detection subcategory
            st.markdown("#### 👁️ Object Detection")
            
            obj_col1, obj_col2 = st.columns(2)
            
            with obj_col1:
                st.markdown("""
                **🖼️ Image**
                - Identify objects in images
                - Face detection and recognition
                - OCR (text extraction)
                - Image classification
                
                *Example use:* Product catalog tagging, ID verification
                """)
            
            with obj_col2:
                st.markdown("""
                **🎬 Video** *(Coming Soon)*
                - Object tracking in video
                - Scene analysis
                - Motion detection
                - Video summarization
                
                *Example use:* Security monitoring, content analysis
                """)
            
            st.divider()
            
            # Data Collection subcategory
            st.markdown("#### 🔍 Data Collection")
            
            data_col1, data_col2 = st.columns(2)
            
            with data_col1:
                st.markdown("""
                **🔌 API Endpoint**
                - Connect to REST APIs
                - Handle authentication
                - Parse JSON responses
                - Error handling and retries
                
                *Example use:* Fetch stock prices, weather data
                """)
            
            with data_col2:
                st.markdown("""
                **🌐 Website**
                - Web scraping capabilities
                - CSS selector targeting
                - Handle JavaScript rendering
                - Rate limiting and politeness
                
                *Example use:* Price monitoring, news aggregation
                """)
            
            st.divider()
            
            # Data Analysis subcategory
            st.markdown("#### 📊 Data Analysis")
            
            analysis_col1, analysis_col2 = st.columns(2)
            
            with analysis_col1:
                st.markdown("""
                **📈 Statistics**
                - Descriptive statistics
                - Hypothesis testing
                - Correlation analysis
                - Data visualization
                
                *Example use:* Sales analysis, A/B testing
                """)
                
                st.markdown("""
                **🧠 LLM**
                - Large Language Model processing
                - Text generation and analysis
                - Conversation handling
                - Prompt engineering
                
                *Example use:* Content creation, chatbots
                """)
            
            with analysis_col2:
                st.markdown("""
                **🔄 RNN LSTM** *(Coming Soon)*
                - Time series prediction
                - Sequence modeling
                - Pattern recognition
                - Memory-based learning
                
                *Example use:* Stock prediction, text generation
                """)
                
                st.markdown("""
                **👁️ CNN** *(Coming Soon)*
                - Image classification
                - Feature extraction
                - Computer vision tasks
                - Transfer learning
                
                *Example use:* Medical imaging, quality control
                """)
            
            st.divider()
            
            # Content Generation subcategory
            st.markdown("#### ✨ Content Generation")
            
            content_col1, content_col2 = st.columns(2)
            
            with content_col1:
                st.markdown("""
                **📝 Text**
                - AI-powered text generation
                - Multiple language support
                - Style and tone control
                - Template-based generation
                
                *Example use:* Blog posts, product descriptions
                """)
                
                st.markdown("""
                **🎨 Image**
                - AI image generation
                - Style transfer
                - Image editing
                - Multiple output formats
                
                *Example use:* Marketing materials, concept art
                """)
            
            with content_col2:
                st.markdown("""
                **🔊 Audio** *(Coming Soon)*
                - Text-to-speech
                - Music generation
                - Sound effects
                - Voice cloning
                
                *Example use:* Podcasts, voice overs
                """)
                
                st.markdown("""
                **🎥 Video** *(Coming Soon)*
                - Video generation
                - Animation creation
                - Video editing
                - Effects and transitions
                
                *Example use:* Explainer videos, ads
                """)
        
        # INTEGRATE tab
        with component_tabs[1]:
            st.markdown("### 🔗 Integrate Components")
            st.markdown("Connect your apps with popular SaaS tools and services.")
            
            # Create a searchable list of SaaS tools
            st.markdown("#### 🛠️ Available SaaS Integrations")
            
            # Organize SaaS tools by category
            saas_categories = {
                "AI & ML Services": {
                    "OpenAI": "GPT models, DALL-E image generation, Whisper speech-to-text",
                    "Anthropic": "Claude AI models for conversation and analysis"
                },
                "Productivity & Project Management": {
                    "Asana": "Task management, project tracking, team collaboration",
                    "Trello": "Kanban boards, card management, workflow automation",
                    "Microsoft": "Office 365, Outlook, OneDrive, Teams integration",
                    "Calendly": "Meeting scheduling, calendar management, booking automation"
                },
                "Communication": {
                    "Slack": "Team messaging, channel management, bot integration",
                    "Twilio": "SMS, voice calls, WhatsApp messaging",
                    "Zoom": "Video conferencing, meeting management, recording"
                },
                "Finance & Payments": {
                    "Stripe": "Payment processing, subscription management, invoicing",
                    "PayPal": "Online payments, money transfers, buyer protection"
                },
                "CRM & Sales": {
                    "Salesforce": "Customer relationship management, sales automation",
                    "Pipedrive": "Sales pipeline management, deal tracking",
                    "Zoho CRM": "Customer management, sales analytics, automation"
                },
                "E-commerce": {
                    "Shopify": "Online store management, inventory, order processing"
                },
                "Marketing": {
                    "Mailchimp": "Email marketing, audience management, campaign analytics"
                },
                "HR & Accounting": {
                    "BambooHR": "Human resources management, employee data, time tracking",
                    "Workday": "Enterprise HR, payroll, financial management",
                    "MYOB": "Accounting software, invoicing, expense tracking"
                },
                "Data & Storage": {
                    "Airtable": "Database management, spreadsheet functionality, API access"
                },
                "Support & Help Desk": {
                    "Zendesk": "Customer support, ticketing system, knowledge base"
                },
                "Design & Creative": {
                    "Adobe Creative Cloud": "Design tools integration, asset management"
                }
            }
            
            for category, tools in saas_categories.items():
                with st.expander(f"**{category}** ({len(tools)} tools)"):
                    for tool, description in tools.items():
                        st.markdown(f"**{tool}:** {description}")
            
            st.divider()
            
            # Integration examples
            st.markdown("#### 🔄 Integration Patterns")
            
            pattern_col1, pattern_col2 = st.columns(2)
            
            with pattern_col1:
                st.markdown("""
                **Data Flow Patterns:**
                - **Trigger → Action:** Slack message triggers email
                - **Sync:** Keep Airtable and Salesforce in sync  
                - **Transform:** Convert data between different formats
                - **Aggregate:** Combine data from multiple sources
                """)
            
            with pattern_col2:
                st.markdown("""
                **Common Use Cases:**
                - **Notifications:** Send alerts to Slack/email
                - **Data Entry:** Automatically populate forms
                - **Reporting:** Generate reports from multiple sources
                - **Automation:** Eliminate manual tasks
                """)
        
        # PROTOTYPE tab
        with component_tabs[2]:
            st.markdown("### 🚀 Prototype Components")
            st.markdown("Rapidly prototype websites, business tools, products, and features.")
            
            proto_col1, proto_col2 = st.columns(2)
            
            with proto_col1:
                st.markdown("""
                **🌐 Website Prototype**
                - Landing pages and marketing sites
                - Responsive design templates
                - Contact forms and lead capture
                - SEO-friendly structure
                
                *Perfect for:* MVP websites, landing pages, portfolios
                """)
                
                st.markdown("""
                **📦 Product**
                - Product concept validation
                - Feature specification
                - User story mapping
                - Market fit analysis
                
                *Perfect for:* New product ideas, market research
                """)
            
            with proto_col2:
                st.markdown("""
                **🔧 Business Tool**
                - Internal workflow applications
                - Data management interfaces
                - Reporting dashboards
                - Process automation tools
                
                *Perfect for:* Streamlining operations, productivity tools
                """)
                
                st.markdown("""
                **⭐ Feature**
                - Individual feature prototypes
                - User interaction testing
                - Functionality validation
                - Integration planning
                
                *Perfect for:* Feature development, user testing
                """)
        
        st.divider()
        
        # Component connections
        st.subheader("🔗 Connecting Components")
        
        st.markdown("""
        Components become powerful when connected together. Here's how connections work:
        """)
        
        connection_col1, connection_col2 = st.columns(2)
        
        with connection_col1:
            st.markdown("""
            **Connection Types:**
            - **Data Flow:** Pass data from one component to another
            - **Trigger:** One component triggers another to execute
            - **Sync:** Keep components synchronized
            - **Transform:** Modify data as it flows between components
            """)
        
        with connection_col2:
            st.markdown("""
            **Best Practices:**
            - Start simple with 2-3 components
            - Test each connection individually
            - Use clear, descriptive connection labels
            - Document complex workflows
            """)
        
        # Example workflows
        st.subheader("🌟 Example Component Workflows")
        
        workflow_examples = {
            "Email Newsletter Automation": {
                "components": ["Website (Data Collection)", "LLM (Data Analysis)", "Email (Communication)"],
                "flow": "Scrape news → Summarize with AI → Send daily email",
                "connections": "Website → LLM → Email"
            },
            "Customer Support Bot": {
                "components": ["Slack (Integrate)", "LLM (Data Analysis)", "Airtable (Integrate)"],
                "flow": "Receive question → Process with AI → Log in database",
                "connections": "Slack → LLM → Airtable"
            },
            "E-commerce Price Monitor": {
                "components": ["Website (Data Collection)", "Statistics (Data Analysis)", "SMS (Communication)"],
                "flow": "Monitor prices → Analyze trends → Alert on changes",
                "connections": "Website → Statistics → SMS"
            }
        }
        
        for workflow, details in workflow_examples.items():
            with st.expander(f"**{workflow}**"):
                st.markdown(f"""
                **Components Used:** {', '.join(details['components'])}
                
                **Data Flow:** {details['flow']}
                
                **Connection Pattern:** {details['connections']}
                """)
        
        st.success("""
        🎓 **Next Steps:**
        - Learn about Component Configurations to set up defaults
        - Try the Application Builder to visually connect components
        - Start with simple 2-component workflows
        """)
    
    tab_counter += 1

    # ===============================
    # TAB 4: COMPONENT CONFIGURATIONS
    # ===============================
    with tabs[tab_counter]:
        st.header("⚙️ Component Configurations")
        
        st.markdown("""
        Component Configurations allow you to set up default settings for components that you use frequently. 
        This saves time and ensures consistency across your applications.
        """)
        
        # What are component configurations
        st.subheader("🤔 What are Component Configurations?")
        
        config_col1, config_col2 = st.columns(2)
        
        with config_col1:
            st.markdown("""
            **Think of them as templates:**
            - Pre-filled settings for components
            - API keys and credentials stored securely
            - Default parameters and preferences
            - Reusable across multiple apps
            """)
        
        with config_col2:
            st.info("""
            **💡 Example:** Configure your OpenAI component once with your API key and preferred model. 
            Every time you add OpenAI to an app, it will use these settings automatically.
            """)
        
        st.divider()
        
        # How to access configurations
        st.subheader("📍 How to Access Component Configurations")
        
        with st.expander("**Step 1: Navigate to Component Config Tab**", expanded=True):
            st.markdown("""
            1. Go to your **Dashboard**
            2. Look for the **Component Config** tab
            3. Click to open the configuration interface
            
            You'll see a sidebar with component categories and a main configuration area.
            """)
        
        with st.expander("**Step 2: Browse Components by Category**"):
            st.markdown("""
            The sidebar is organized into three main categories:
            
            **🔄 Automate**
            - Communication (Email, SMS, Voice)
            - Object Detection (Image, Video)
            - Data Collection (API Endpoint, Website)
            - Data Analysis (Statistics, LLM, RNN LSTM, CNN)
            - Content Generation (Text, Image, Audio, Video)
            
            **🔗 Integrate**
            - SaaS Tools (OpenAI, Slack, Stripe, Salesforce, etc.)
            
            **🚀 Prototype**
            - Website Prototype, Business Tool, Product, Feature
            """)
        
        with st.expander("**Step 3: Select and Configure a Component**"):
            st.markdown("""
            1. Click on any component from the sidebar
            2. A configuration form will open
            3. Fill in the relevant settings
            4. Click **Save** to store the configuration
            
            ✅ **Green checkmark** appears next to configured components
            """)
        
        st.divider()
        
        # Configuration examples by category
        st.subheader("📝 Configuration Examples")
        
        config_tabs = st.tabs(["Communication", "SaaS Tools", "AI/ML", "Data Collection"])
        
        # Communication examples
        with config_tabs[0]:
            st.markdown("### 📨 Communication Components")
            
            # Email configuration
            with st.expander("**📧 Email Component Configuration**"):
                st.markdown("""
                **SMTP Settings:**
                - SMTP Server: `smtp.gmail.com`
                - SMTP Port: `587`
                - SMTP Security: `TLS`
                - Email Address: `your@email.com`
                - Password/API Key: `your-app-password`
                
                **Receiving Configuration (Optional):**
                - POP3/IMAP Server: `imap.gmail.com`
                - Port: `993`
                - Protocol: `IMAP`
                
                **💡 Pro Tip:** Use app-specific passwords for Gmail instead of your main password.
                """)
            
            # SMS configuration
            with st.expander("**💬 SMS Component Configuration**"):
                st.markdown("""
                **Twilio SMS Settings:**
                - Account SID: `AC...` (from Twilio dashboard)
                - Auth Token: `your-auth-token`
                - Phone Number: `+15551234567` (your Twilio number)
                
                **How to get Twilio credentials:**
                1. Sign up at twilio.com
                2. Verify your phone number
                3. Get $15 free trial credit
                4. Copy SID and token from dashboard
                5. Purchase or use trial phone number
                """)
        
        # SaaS Tools examples
        with config_tabs[1]:
            st.markdown("### 🔗 SaaS Tool Integrations")
            
            # OpenAI configuration
            with st.expander("**🤖 OpenAI Configuration**"):
                st.markdown("""
                **Required Settings:**
                - API Key: `sk-...` (from OpenAI dashboard)
                - Organization ID: `org-...` (optional)
                
                **How to get OpenAI API key:**
                1. Go to platform.openai.com
                2. Sign up or log in
                3. Navigate to API section
                4. Create new API key
                5. Copy and paste into configuration
                """)
            
            # Slack configuration
            with st.expander("**💬 Slack Configuration**"):
                st.markdown("""
                **Required Settings:**
                - Bot Token: `xoxb-...`
                - Signing Secret: `your-signing-secret`
                - App Token: `xapp-...` (optional)
                - Default Channel: `#general` (optional)
                
                **Setup Steps:**
                1. Go to api.slack.com/apps
                2. Create new app
                3. Add bot token scopes (chat:write, channels:read)
                4. Install app to workspace
                5. Copy bot token and signing secret
                """)
            
            # Stripe configuration
            with st.expander("**💳 Stripe Configuration**"):
                st.markdown("""
                **Required Settings:**
                - Secret Key: `sk_test_...` or `sk_live_...`
                - Publishable Key: `pk_test_...` or `pk_live_...`
                - Webhook Secret: `whsec_...` (optional)
                
                **Test vs Live:**
                - Use `test` keys for development
                - Switch to `live` keys for production
                - Test keys work with fake card numbers
                """)
        
        # AI/ML examples
        with config_tabs[2]:
            st.markdown("### 🧠 AI/ML Components")
            
            # LLM configuration
            with st.expander("**🧠 LLM (Large Language Model) Configuration**"):
                st.markdown("""
                **Provider Settings:**
                - AI Provider: `OpenAI` or `Anthropic`
                - Model: `gpt-4`, `gpt-3.5-turbo`, `claude-sonnet-4-20250514`
                - API Key: Your provider's API key
                - Base URL: (usually auto-filled)
                
                **Generation Parameters:**
                - Max Tokens: `4096` (response length limit)
                - Temperature: `0.7` (creativity level 0-2)
                - Top P: `0.95` (nucleus sampling)
                - Frequency Penalty: `0` (repetition reduction)
                
                **System Prompt (Optional):**
                ```
                You are a helpful AI assistant that provides clear, 
                concise answers to user questions.
                ```
                """)
            
            # Statistics configuration
            with st.expander("**📊 Statistics Component Configuration**"):
                st.markdown("""
                **Available Analysis Types:**
                ✅ **Descriptive Statistics**
                - Mean, median, mode
                - Standard deviation, variance
                - Range, quartiles
                
                ✅ **Inferential & Predictive Statistics**
                - T-Tests
                - Correlation Tests  
                - ANOVA
                - Chi-Square Tests
                - Normality Tests
                - Variance Tests
                
                **Additional Parameters (JSON):**
                ```json
                {
                  "confidenceLevel": 0.95,
                  "alpha": 0.05
                }
                ```
                """)
        
        # Data Collection examples
        with config_tabs[3]:
            st.markdown("### 🔍 Data Collection Components")
            
            # API Endpoint configuration
            with st.expander("**🔌 API Endpoint Configuration**"):
                st.markdown("""
                **Basic Settings:**
                - API URL: `https://api.example.com/endpoint`
                - API Key: Your service's API key
                - Request Method: `GET`, `POST`, `PUT`, `DELETE`
                
                **Additional Headers (JSON format):**
                ```json
                {
                  "Authorization": "Bearer your-token",
                  "Content-Type": "application/json",
                  "User-Agent": "YourApp/1.0"
                }
                ```
                
                **Common Free APIs to try:**
                - JSONPlaceholder: `https://jsonplaceholder.typicode.com/posts`
                - OpenWeatherMap: `https://api.openweathermap.org/data/2.5/weather`
                - News API: `https://newsapi.org/v2/top-headlines`
                """)
            
            # Website scraping configuration
            with st.expander("**🌐 Website Scraping Configuration**"):
                st.markdown("""
                **Basic Settings:**
                - Website URL: `https://www.example.com`
                - Username: (if login required)
                - Password: (if login required)
                
                **CSS Selectors (JSON format):**
                ```json
                {
                  "title": "h1.main-title",
                  "price": ".product-price",
                  "description": ".product-description",
                  "links": "a.product-link"
                }
                ```
                
                **⚠️ Important:** Some websites require CAPTCHA solving and may limit access.
                """)
        
        st.divider()
        
        # Import defaults feature
        st.subheader("📥 Import Defaults Feature")
        
        st.markdown("""
        The **Import Defaults** feature automatically applies your saved configurations to components in your apps.
        """)
        
        with st.expander("**How Import Defaults Works**"):
            st.markdown("""
            **When to use:**
            - After creating an app with components
            - When you want to apply saved settings quickly
            - To ensure consistency across multiple apps
            
            **Steps:**
            1. Build your app with components
            2. Go to the App Builder or Applications tab
            3. Click **"Import Defaults"** button
            4. System matches your canvas components with saved configurations
            5. Settings are automatically applied
            
            **What gets imported:**
            - API keys and credentials
            - Default parameters and settings
            - Provider preferences (OpenAI vs Anthropic)
            - Custom configurations you've saved
            """)
        
        # Best practices
        st.subheader("✅ Configuration Best Practices")
        
        best_practices_col1, best_practices_col2 = st.columns(2)
        
        with best_practices_col1:
            st.markdown("""
            **Security:**
            - Never share API keys publicly
            - Use environment-specific keys (test vs production)
            - Rotate keys regularly
            - Use least-privilege access
            """)
            
            st.markdown("""
            **Organization:**
            - Configure components you use frequently
            - Keep settings up to date
            - Document complex configurations
            - Test configurations before deploying
            """)
        
        with best_practices_col2:
            st.markdown("""
            **Efficiency:**
            - Configure once, use many times
            - Start with free tier APIs
            - Monitor usage and costs
            - Set reasonable limits and timeouts
            """)
            
            st.markdown("""
            **Troubleshooting:**
            - Test API keys in isolation first
            - Check service status pages
            - Verify JSON formatting
            - Review error logs
            """)
        
        st.success("""
        🎯 **Quick Start Checklist:**
        1. ✅ Configure OpenAI (for AI features)
        2. ✅ Configure Email (for notifications) 
        3. ✅ Configure one SaaS tool you use regularly
        4. ✅ Test configurations with a simple app
        5. ✅ Use Import Defaults on your next app
        """)
    
    tab_counter += 1

    # ===============================
    # TAB 5: APPLICATION BUILDER
    # ===============================
    with tabs[tab_counter]:
        st.header("🎨 Application Builder")
        
        st.markdown("""
        The Application Builder is a visual interface that allows you to design your app by connecting components together. 
        This is an alternative to describing your app in text - instead, you can drag and drop components to create workflows.
        """)
        
        # Overview
        st.subheader("🎯 What is the Application Builder?")
        
        builder_col1, builder_col2 = st.columns(2)
        
        with builder_col1:
            st.markdown("""
            **Visual App Design:**
            - Drag components onto a canvas
            - Connect components with visual links
            - Configure each component individually
            - See your app structure at a glance
            """)
        
        with builder_col2:
            st.info("""
            **💡 Think of it like:** A flowchart editor where each box is a component 
            and each arrow is a data flow between components.
            """)
        
        st.divider()
        
        # How to access
        st.subheader("📍 How to Access the Application Builder")
        
        with st.expander("**Opening the Builder**", expanded=True):
            st.markdown("""
            **App Builder**
            1. Go to your Dashboard
            2. Click on the **Application Builder** tab
            3. Start building visually
            """)
        
        # Interface overview
        st.subheader("🖥️ Interface Overview")
        
        interface_tabs = st.tabs(["Components Panel", "Canvas Area", "Properties Panel", "Toolbar"])
        
        with interface_tabs[0]:
            st.markdown("### 🧩 Components Panel")
            st.markdown("""
            **Located:** Left sidebar
            
            **Contains:**
            - **Automate** category (Communication, Data Collection, etc.)
            - **Integrate** category (SaaS tools)
            - **Prototype** category (Website, Business Tools)
            
            **How to use:**
            1. Browse categories by clicking to expand
            2. Find the component you need
            3. Drag it onto the canvas
            4. Or click a component to place it in the next available spot
            """)
            
            st.markdown("""
            **🎨 Visual Indicators:**
            - ✅ Green checkmark = Component has saved configuration
            - 🔒 "Coming Soon" = Component not yet available
            - 📝 Component count badge = Number of components in category
            """)
        
        with interface_tabs[1]:
            st.markdown("### 🎯 Canvas Area")
            st.markdown("""
            **The main workspace where you build your app.**
            
            **Grid System:**
            - Components snap to a grid for organized layout
            - Grid automatically expands as you add more components
            - Each component takes one grid cell
            
            **Component Management:**
            - **Drag to move:** Click and drag components to rearrange
            - **Connection points:** Each component has 4 connection points (top, right, bottom, left)
            - **Visual feedback:** Hover effects and selection highlights
            
            **Connections:**
            - **Drag from edge node to edge node** to create connections
            - **Click connections** to edit labels and descriptions
            - **Different colors** for different component pairs
            """)
        
        with interface_tabs[2]:
            st.markdown("### ⚙️ Properties Panel")
            st.markdown("""
            **Appears when you select a component or connection.**
            
            **Component Properties:**
            - Component-specific configuration options
            - API keys and credentials
            - Parameters and settings
            - Import defaults button to apply saved configurations
            
            **Connection Properties:**
            - Connection label (short description)
            - Connection description (detailed explanation)
            - How data flows between components
            - Connection order information
            """)
        
        with interface_tabs[3]:
            st.markdown("### 🛠️ Toolbar")
            st.markdown("""
            **Located:** Top of the interface
            
            **Available Actions:**
            - **Clear Canvas:** Remove all components and connections
            - **Import Defaults:** Apply saved configurations to all components
            - **Settings:** Configure app name, runtime, and deployment options
            - **Build:** Generate your app from the visual design
            - **Export:** Save your design as a PDF or template
            
            **Additional Tools:**
            - **Undo/Redo:** Step backward/forward through your changes
            - **Save Template:** Save your design for reuse
            - **Load Template:** Load a previously saved design
            """)
        
        st.divider()
        
        # Step-by-step tutorial
        st.subheader("📚 Step-by-Step Tutorial")
        
        # Tutorial steps
        with st.expander("**Step 1: Start with a Simple App**", expanded=True):
            st.markdown("""
            **Goal:** Create a news summarizer that emails daily summaries
            
            **Components needed:**
            1. Website (Data Collection) - for scraping news
            2. LLM (Data Analysis) - for summarizing articles  
            3. Email (Communication) - for sending summaries
            
            **Start by dragging these components onto the canvas:**
            - Find **Website** under Automate → Data Collection
            - Find **LLM** under Automate → Data Analysis
            - Find **Email** under Automate → Communication
            """)
        
        with st.expander("**Step 2: Arrange Components**"):
            st.markdown("""
            **Layout your workflow:**
            1. Place **Website** component on the left
            2. Place **LLM** component in the middle
            3. Place **Email** component on the right
            
            **Tips:**
            - Components automatically snap to grid positions
            - Leave space between components for clear visual flow
            - Think about the data flow direction (left to right is common)
            """)
        
        with st.expander("**Step 3: Create Connections**"):
            st.markdown("""
            **Connect your workflow:**
            1. **Website → LLM:** Drag from Website's right edge to LLM's left edge
            2. **LLM → Email:** Drag from LLM's right edge to Email's left edge
            
            **Connection Properties:**
            - **Website → LLM:** Label: "Raw News Data"
            - **LLM → Email:** Label: "Summarized Content"
            
            **Description examples:**
            - "Pass scraped news articles to AI for summarization"
            - "Send AI-generated summaries to email component for delivery"
            """)
        
        with st.expander("**Step 4: Configure Components**"):
            st.markdown("""
            **Click each component to configure:**
            
            **Website Component:**
            - Website URL: `https://news.ycombinator.com`
            - CSS Selectors: `{"title": ".storylink", "url": ".storylink"}`
            
            **LLM Component:**
            - Provider: OpenAI
            - Model: gpt-4
            - System Prompt: "Summarize news articles in 2-3 sentences each"
            
            **Email Component:**
            - SMTP Server: `smtp.gmail.com`
            - Your email credentials
            - Recipient: Your email address
            """)
        
        with st.expander("**Step 5: Build Your App**"):
            st.markdown("""
            **Ready to create your app:**
            1. Click the **Settings** button in toolbar
            2. Enter your app details:
               - App Name: `news-summarizer`
               - Runtime: 1 hour (for testing)
               - Make public: No (for now)
            3. Click **Build** button
            4. Wait approximately 7 minutes for your app to be created
            
            **What happens during build:**
            - The visual design is converted to an app description
            - AI agent writes the code to implement your workflow
            - Your app is deployed and becomes accessible
            """)
        
        st.divider()
        
        # Advanced features
        st.subheader("🚀 Advanced Builder Features")
        
        advanced_tabs = st.tabs(["Templates", "Multiple Connections", "Complex Workflows", "Collaboration"])
        
        with advanced_tabs[0]:
            st.markdown("### 📋 Templates")
            st.markdown("""
            **Save and reuse your designs:**
            
            **Saving Templates:**
            1. Build a working app design
            2. Click **Save Template** in toolbar
            3. Give it a descriptive name
            4. Add notes about what it does
            
            **Loading Templates:**
            1. Click **Load Template** in toolbar
            2. Browse your saved templates
            3. Click to load onto canvas
            4. Modify as needed for your new app
            
            **Template Ideas:**
            - Email newsletter automation
            - Social media monitoring
            - Data analysis pipelines
            - Customer notification systems
            """)
        
        with advanced_tabs[1]:
            st.markdown("### 🔗 Multiple Connections")
            st.markdown("""
            **Connect components in complex ways:**
            
            **One-to-Many:**
            - One data source feeding multiple processors
            - Example: API data going to both statistics and email
            
            **Many-to-One:**
            - Multiple sources feeding one component
            - Example: Multiple websites feeding one summarizer
            
            **Branching Logic:**
            - Different paths based on conditions
            - Example: Filter data, then route to different outputs
            
            **Connection Management:**
            - Each connection has its own label and description
            - Color-coded by component pairs
            - Click any connection to edit or delete
            """)
        
        with advanced_tabs[2]:
            st.markdown("### 🏗️ Complex Workflows")
            st.markdown("""
            **Build sophisticated applications:**
            
            **Multi-Stage Processing:**
            1. Data Collection → Data Analysis → Content Generation → Communication
            2. Example: Scrape → Analyze → Generate Report → Email + Slack
            
            **Parallel Processing:**
            1. Split data streams for simultaneous processing
            2. Example: News → (Summary + Sentiment) → Combined Output
            
            **Integration Chains:**
            1. SaaS tool → Processing → Multiple SaaS outputs
            2. Example: Airtable → Statistics → Slack + Email + Stripe
            
            **Best Practices:**
            - Start simple, add complexity gradually
            - Test each connection individually
            - Use clear, descriptive connection labels
            - Document complex logic in connection descriptions
            """)
        
        with advanced_tabs[3]:
            st.markdown("### 👥 Collaboration")
            st.markdown("""
            **Share and collaborate on designs:**
            
            **Template Sharing:**
            - Save useful templates with descriptive names
            - Include documentation in template descriptions
            - Export templates as files for sharing
            
            **Documentation:**
            - Use connection labels to explain data flow
            - Add detailed descriptions for complex logic
            - Include setup instructions in app settings
            
            **Version Control:**
            - Save multiple versions as different templates
            - Use descriptive names: "v1-basic", "v2-with-slack"
            - Keep notes about changes and improvements
            """)
        
        st.divider()
        
        # Tips and best practices
        st.subheader("💡 Builder Tips & Best Practices")
        
        tips_col1, tips_col2 = st.columns(2)
        
        with tips_col1:
            st.markdown("""
            **Design Tips:**
            - **Start simple:** Begin with 2-3 components
            - **Think data flow:** Left to right, top to bottom
            - **Group related components:** Keep similar functions together
            - **Leave space:** Don't crowd components together
            """)
            
            st.markdown("""
            **Testing:**
            - **Test configurations:** Use Component Config tab first
            - **Start small:** 1-hour runtime for initial testing
            - **One change at a time:** Build incrementally
            - **Check connections:** Verify all connections make sense
            """)
        
        with tips_col2:
            st.markdown("""
            **Organization:**
            - **Clear labels:** Use descriptive connection names
            - **Document logic:** Explain complex connections
            - **Save often:** Use templates to save progress
            - **Consistent naming:** Use clear, consistent names
            """)
            
            st.markdown("""
            **Troubleshooting:**
            - **Missing connections:** Check all edge nodes are connected
            - **Configuration errors:** Verify component settings
            - **Build failures:** Check app name and settings
            - **Runtime issues:** Verify API keys and permissions
            """)
        
        st.success("""
        🎨 **You're Ready to Build Visually!**
        
        **Quick Start:**
        1. ✅ Open the Application Builder
        2. ✅ Try the tutorial workflow above
        3. ✅ Configure your components
        4. ✅ Build and test your first visual app
        5. ✅ Save as a template for future use
        """)
    
    tab_counter += 1


    # ===============================
    # TAB 7: RUNNING & MANAGING APPS
    # ===============================
    with tabs[tab_counter]:
        st.header("▶️ Running & Managing Your Apps")
        
        # App management overview
        st.markdown("""
        Once you've created apps, you'll need to manage them through their lifecycle. The Applications tab in your dashboard shows all your apps with their current status and controls.
        """)
        
        # App statuses
        st.subheader("Understanding App Status")
        
        # Create an expandable comparison table of different statuses
        with st.expander("App Status Types"):
            status_data = {
                "Status": ["Running", "Shutdown"],
                "Description": [
                    "App is active and accessible",
                    "App is stopped and not consuming credits"
                ],
                "Action Needed": [
                    "None (consuming credits while running)",
                    "Run the app again when needed"
                ]
            }
            
            st.dataframe(status_data, use_container_width=True)
        
        st.divider()
        
        # App management actions
        st.subheader("App Management Actions")
        
        # Create columns for different actions
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Running an App")
            st.markdown("""
            1. Find your app in the Applications list
            2. Click the ▶️ (Run) button
            3. Enter the number of hours to run
            4. Click "Run App"
            
            Your app will start running and be accessible at its URL.
            """)
        
            
        with col2:
            st.markdown("### Editing an App")
            st.markdown("""
            1. Find your app in the Applications list
            2. Click the ✏️ (Edit) button
            3. Adjust settings like hours, model, etc.
            4. Click "Run & Edit"
            
            Your app will restart with the new settings.
            """)
            
            with st.expander("Edit Options"):
                st.markdown("""
                - Available in Marketplace: Yes/No
                - Hours to Run: 1+ hours
                - Agent Model: Claude Sonnet 4
                """)
        
        st.divider()
        
        # Revisions
        st.subheader("Making App Revisions")
        st.markdown("""
        You can improve your app by sending revision prompts:
        
        1. Open your app by clicking on its card in the Applications list
        2. Use the "Revisions" panel (toggle open if minimized)
        3. Enter your revision request (e.g., "Add a dark mode option")
        4. Submit the revision
        
        The revision will be processed and your app updated within about 7 minutes.
        """)
        
        # Revision example
        with st.expander("Example Revision Prompts"):
            revision_examples = [
                "Add a search function at the top of the page",
                "Change the color scheme to blue and white",
                "Add the ability to filter news by category",
                "Create a mobile-friendly responsive layout",
                "Add user authentication with email and password",
                "Implement a data visualization dashboard",
                "Add the ability to save favorites",
                "Create a PDF export function",
                "Add social media sharing buttons",
                "Implement a comment/feedback system",
                "Add an image upload feature",
                "Create a user profile page",
                "Add localization support for multiple languages",
                "Implement a notification system",
                "Add a rating system for content",
                "Create a calendar view for scheduled items",
                "Add a map interface to show locations",
                "Implement a recommendation engine",
                "Add a simple analytics dashboard",
                "Create a printable report feature",
                "Add drag-and-drop functionality",
                "Implement a simple e-commerce checkout",
                "Add a newsletter subscription form",
                "Create an admin panel for content management",
                "Add a contact form with validation"
            ]
            
            for i, example in enumerate(revision_examples):
                st.markdown(f"**Example {i+1}:** {example}")
        
        # App deletion
        st.markdown("""
        ### Deleting an App
        
        To remove an app you no longer need:
        
        1. Find your app in the Applications list
        2. Click the 🗑️ (Delete) button
        3. Confirm the deletion
        
        Note: Deletion may take a few minutes to complete and cannot be undone.
        """)
    tab_counter += 1
    
    # ===============================
    # TAB 8: ADVANCED FEATURES
    # ===============================
    with tabs[tab_counter]:
        st.header("⚙️ Advanced App Features")
        
        # Advanced features intro
        st.markdown("""
        urauto.ai provides specialized capabilities you can add to your quick build apps. These features can be selected during quick build app creation or added through revisions.
        """)
        
        # Feature showcase
        feature_list = [
            {
                "name": "Object Detection & Recognition",
                "icon": "🔍",
                "description": "Identify objects and patterns in images using computer vision",
                "use_cases": ["Product identification", "Face detection", "Image tagging", "Visual search"],
                "example_prompt": "Add the ability to detect and count people in uploaded photos"
            },
            {
                "name": "Pattern Recognition",
                "icon": "📊",
                "description": "Identify patterns in data streams using RNN/LSTM models",
                "use_cases": ["Trend forecasting", "Anomaly detection", "Behavioral analysis", "Time-series prediction"],
                "example_prompt": "Add a feature to detect unusual patterns in the data and send alerts"
            },
            {
                "name": "Realtime Voice",
                "icon": "🎤",
                "description": "Process and respond to voice input in real-time",
                "use_cases": ["Voice assistants", "Voice commands", "Speech-to-text", "Audio analysis"],
                "example_prompt": "Add voice command capability to control the interface hands-free"
            },
            {
                "name": "Content Creation",
                "icon": "✍️",
                "description": "Generate and manipulate content using LLMs",
                "use_cases": ["Text generation", "Summarization", "Translation", "Creative writing"],
                "example_prompt": "Add an AI writer that can generate blog post content based on keywords"
            },
            {
                "name": "Email Integration",
                "icon": "📧",
                "description": "Send and receive emails from your app",
                "use_cases": ["Notifications", "Newsletter distribution", "Email automation", "Contact forms"],
                "example_prompt": "Add functionality to send a daily email digest of the top content"
            },
            {
                "name": "Data Collection",
                "icon": "🕸️",
                "description": "Gather data from websites and APIs",
                "use_cases": ["Price monitoring", "News aggregation", "Competitive analysis", "Research"],
                "example_prompt": "Add a crawler to collect product prices from these competitor websites"
            }
        ]
        
        # Feature selector
        selected_feature = st.selectbox(
            "Explore Advanced Features",
            options=[feature["name"] for feature in feature_list]
        )
        
        # Find the selected feature
        feature = next((f for f in feature_list if f["name"] == selected_feature), None)
        
        if feature:
            # Display feature details
            st.subheader(f"{feature['icon']} {feature['name']}")
            st.markdown(f"**Description:** {feature['description']}")
            
            # Use cases
            st.markdown("**Common Use Cases:**")
            for use_case in feature['use_cases']:
                st.markdown(f"- {use_case}")
            
            # Example implementation
            st.markdown("**Example Prompt:**")
            st.code(feature['example_prompt'], language="markdown")
            
            # Interactive elements based on feature
            if feature["name"] == "Object Detection & Recognition":
                pass
                
            elif feature["name"] == "Pattern Recognition":
                # Just display the textual information without a chart for now
                st.markdown("""
                ### Pattern Recognition Feature
                
                This feature enables your app to identify trends, anomalies, and recurring patterns in time-series data.
                
                **Examples:**
                - Detecting unusual spikes in network traffic
                - Identifying seasonal trends in sales data
                - Recognizing user behavior patterns
                - Predicting equipment failures before they occur
                
                The chart would normally show time-series data with anomaly detection capabilities.
                """)
                
                # Display a static image of a chart instead of generating one
                # This avoids the dependency issues with chart libraries
                
                # HTML/CSS-based simple visualization that doesn't rely on chart libraries
                st.markdown("""
                <div style="background-color:#f0f0f0; border-radius:5px; padding:10px; margin:10px 0;">
                    <div style="width:100%; height:200px; position:relative; border-bottom:1px solid #333; border-left:1px solid #333;">
                        <!-- Normal data line -->
                        <div style="position:absolute; bottom:0; left:0; width:40%; height:50px; border-top:2px solid blue;"></div>
                        <!-- Anomaly spike -->
                        <div style="position:absolute; bottom:0; left:40%; width:20%; height:150px; border-top:2px solid red;"></div>
                        <!-- Normal data continuation -->
                        <div style="position:absolute; bottom:0; left:60%; width:40%; height:50px; border-top:2px solid blue;"></div>
                        <!-- Axis labels -->
                        <div style="position:absolute; bottom:-20px; left:0;">0</div>
                        <div style="position:absolute; bottom:-20px; left:50%;">Time</div>
                        <div style="position:absolute; bottom:-20px; right:0;">100</div>
                        <div style="position:absolute; transform:rotate(-90deg); left:-30px; top:50%;">Value</div>
                    </div>
                    <div style="text-align:center; margin-top:25px; color:#555;">Pattern recognition identifying an anomaly spike in time-series data</div>
                </div>
                """, unsafe_allow_html=True)
                
            elif feature["name"] == "Realtime Voice":
                st.audio("https://cdn.pixabay.com/download/audio/2021/08/09/audio_303b7a7705.mp3?filename=voice-giving-instructions-6-36355.mp3")
                st.caption("Voice commands can trigger app actions")
                
            elif feature["name"] == "Content Creation":
                content_examples = [
                    "# Artificial Intelligence in Healthcare\n\nArtificial intelligence is revolutionizing the healthcare industry in numerous ways. From diagnostic tools to personalized treatment plans, AI is enhancing the capability of healthcare providers and improving patient outcomes.\n\n## Key Applications:\n- **Diagnostic imaging analysis**\n- **Predictive analytics for patient risk**\n- **Drug discovery acceleration**\n- **Administrative workflow automation**\n\nResearch indicates that AI-assisted diagnoses can improve accuracy by up to 30% in certain conditions...",
                    "# The Future of Renewable Energy\n\nRenewable energy sources are rapidly transforming the global energy landscape. As technology advances and costs decrease, solar, wind, and other renewable sources are becoming increasingly competitive with fossil fuels.\n\n## Major Developments:\n- **Grid-scale battery storage solutions**\n- **Floating offshore wind farms**\n- **Perovskite solar cell technology**\n- **Green hydrogen production**\n\nExperts predict that renewable energy will account for over 50% of global electricity generation by 2030..."
                ]
                
                if st.button("Generate Content Example"):
                    with st.spinner("Generating content..."):
                        time.sleep(2)
                        st.markdown(random.choice(content_examples))
                
            elif feature["name"] == "Email Integration":
                col1, col2 = st.columns(2)
                with col1:
                    st.text_input("Recipient email", disabled=True)
                    st.text_input("Subject", disabled=True)
                    st.text_area("Message body", disabled=True)
                with col2:
                    st.markdown("**Email Configuration**")
                    st.code("""
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "your-app@example.com"
EMAIL_PASSWORD = "${SECURE_PASSWORD}"
                    """)
                    
            elif feature["name"] == "Data Collection":
                st.code("""
# Example web scraping code
import requests
from bs4 import BeautifulSoup

def scrape_product_prices(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all price elements
    price_elements = soup.select('.product-price')
    
    prices = []
    for element in price_elements:
        prices.append({
            'price': element.text.strip(),
            'product': element.find_parent('.product-item').select_one('.product-title').text.strip()
        })
    
    return prices
                """)
        
        st.divider()
        
        # Feature combinations
        st.subheader("🧩 Combining Features")
        st.markdown("""
        The real power comes when you combine multiple features in your apps. Here are some powerful combinations:
        """)
        
        # Example combinations
        combinations = [
            {
                "title": "Data Collection + Email Integration",
                "description": "Monitor websites for changes and send email alerts",
                "example": "An app that tracks product prices on competitor websites and emails you when prices drop"
            },
            {
                "title": "Object Detection + Content Creation",
                "description": "Generate descriptions of detected objects in images",
                "example": "An app that analyzes uploaded photos and generates detailed descriptions of the contents"
            },
            {
                "title": "Pattern Recognition + SaaS Integration",
                "description": "Identify trends and trigger actions in other services",
                "example": "An app that monitors social media sentiment and creates tasks in Asana when negative patterns emerge"
            }
        ]
        
        for combo in combinations:
            st.markdown(f"**{combo['title']}**")
            st.markdown(combo['description'])
            st.markdown(f"*Example:* {combo['example']}")
            st.write("---")
        
        # Best practices
        st.info("""
        **💡 Tips for Advanced Features:**
        - Start with core functionality, then add advanced features
        - Test each feature thoroughly before adding another
        - Consider the cost of computationally intensive features
        - Be specific in your revision prompts when adding features
        """)
    tab_counter += 1
    
    # ===============================
    # TAB 9: ACCOUNT MANAGEMENT
    # ===============================
    with tabs[tab_counter]:
        st.header("💰 Account Management & Recharging")
        
        # Token system explanation
        st.subheader("Your Balance")
        st.markdown("""
        urauto.ai uses a usage based payment system:
        
        - Credits are used to create, run, and edit apps
        - Costs of creating and editing apps is based on complexity and revisions
        - Running apps varies based on selected cloud resources and runtime
        - Your balance is visible in the navigation bar
        """)
        
                
        st.divider()
        
        # Recharging tokens
        st.subheader("Recharging Your Account")
        st.markdown("""
        When your balance runs low, you'll need to recharge:
        
        1. Go to the "Recharge Account" tab in your dashboard
        2. Enter the amount you want to add (minimum $20)
        3. Enter your payment details (credit card or Google Pay)
        4. Complete the secure payment
        
        Credits are added to your account immediately after successful payment.
        """)
        
        # Mock recharge form
        with st.expander("Recharge Form Example"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.number_input("Amount (USD)", min_value=20, value=50, disabled=True)
                st.text_input("Cardholder Name", value="John Smith", disabled=True)
                
                payment_method = st.radio("Payment Method", ["Credit Card", "Google Pay"], disabled=True)
                
                if payment_method == "Credit Card":
                    st.text_input("Card Number", value="4242 XXXX XXXX XXXX", disabled=True)
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.text_input("Expiry", value="12/25", disabled=True)
                    with col_b:
                        st.text_input("CVC", value="XXX", disabled=True)
            
            with col2:
                st.markdown("### Payment Summary")
                st.markdown("Amount: **$50.00**")
                st.markdown("Payment method: **Credit Card**")
                
                st.markdown("---")
                st.markdown("🔒 **Secure Payment**")
                st.markdown("Your payment is processed securely through Stripe.")
        
        st.divider()
        
        # Payment history
        st.subheader("Payment History")
        st.markdown("""
        You can view your payment history in the "Recharge Account" tab. This includes:
        
        - Date of payment
        - Amount paid
        - Payment method
        - Transaction status
        """)
        
        # Example payment history
        with st.expander("Payment History Example"):
            payment_history = {
                "Date": ["2023-09-15", "2023-08-22", "2023-07-10"],
                "Amount": ["$100.00", "$50.00", "$20.00"],
                "Payment Method": ["Credit Card", "Google Pay", "Credit Card"],
                "Card Type": ["Visa", "N/A", "Mastercard"],
                "Card Last Four": ["**** **** **** 4242", "N/A", "**** **** **** 8432"],
                "Status": ["Completed", "Completed", "Completed"]
            }
            
            st.dataframe(payment_history, use_container_width=True)
        
        st.divider()
        
        # Account management tips
        st.subheader("💡 Account Management Tips")
        st.markdown("""
        - **Budget wisely**: Estimate your app runtime needs before creating
        - **Monitor usage**: Check your balance regularly
        - **Run in intervals**: For testing, run apps for 1-hour intervals
        """)
        
        # FAQ about billing
        with st.expander("Billing FAQs"):
            st.markdown("""
            **Q: Are payments refundable?**  
            A: No, payments are non-refundable once purchased.
            
            **Q: What happens if I run out of credits while an app is running?**  
            A: The app will be shut down automatically.
            
            **Q: Does my balance expire?**  
            A: No, your balance does not expire and payments will remain in your account until used.
            
            **Q: Is there a subscription option?**  
            A: Currently, urauto.ai uses a pay-as-you-go usaged based model rather than subscriptions.
            
            **Q: What payment methods are accepted?**  
            A: Credit cards and Google Pay are currently supported.
            """)
    tab_counter += 1

    # ===============================
    # TAB 10: FAQ
    # ===============================
    with tabs[tab_counter]:
        st.header("Frequently Asked Questions")

        # Just replicate the questions from your HTML FAQ section inside Streamlit expanders:
        with st.expander("1) What is an AI-generated app/integration?"):
            st.write("""
If you're dealing with time-consuming repetitive tasks, would like to rapidly prototype ideas, or even integrate various SaaS tools together, urauto.ai is the ideal solution for automating these processes. Just describe your idea, and an AI/Agent will create it for you!
            """)

        with st.expander("2) How do I create an application?"):
            st.write("""
Navigate to the "Applications" tab and click on the "Add App" button. Enter your app name, idea, and run time, then click "Create". There are also "Advanced" settings which allow you to further customise your app with various features if needed. Click on the app card to access your build. Note that duplicate names are not allowed.
            """)

        with st.expander("3) What is the difference between applications & integrations?"):
            st.write("""
Applications can be spun up and down as needed. Integrations, on the other hand, link SaaS tools together and can run continuously, 24/7.
            """)

        with st.expander("4) How is the application created?"):
            st.write("""
An AI/LLM/Agent writes and deploys the code needed to bring your app idea to life.
            """)

        with st.expander("5) How long does it take to create an app?"):
            st.write("""
The first app creation can take up to 7 minutes as backend resources are provisioned and the subdomain DNS record is updated/propagated.
            """)

        with st.expander("6) How do I tweak/update my app?"):
            st.write("""
Click on your app project, ensure the revision tab isn't minimized, enter your revision prompt, and send it through.
            """)

        with st.expander("7) How do I fund my account? Are payments securely processed?"):
            st.write("""
We support secure Stripe payments and no card details are stored. Use the "Recharge Account" section. Please note payments are non-refundable.
            """)

        with st.expander("8) How does pricing work?"):
            st.write("""
Each app or integration that is created will deduct an amount based on the duration of the runtime or the scheduled usage time. For example, if your app is scheduled to run for 2 hours, we deduct 2 hours' worth of funds, and then the resources will be deprovisioned. If the app or integration is long-running (e.g., 24/7), funds will be deducted at the start of each day. If there are insufficient credits, the app will be shut down.
            """)

        with st.expander("9) What if my app doesn't run?"):
            st.write("""
You must make sure you hold enough funds in your account on this platform and (for the issuer of the API key, if applicable) you may also need to provide further revisions to troubleshoot or refine your app.
            """)

        with st.expander("10) Nothing is loading. Nginx Error"):
            st.write("""
The initial app should be available within under 10 minutes. Prompts are processed by the Agent and revisions become available at ~7 minute intervals. Try reloading the page or running the app again.
            """)

        with st.expander("11) How do I get an API key?"):
            st.write("""
To obtain an API key for a SaaS tool or website, you typically need to sign up for a developer account with the service provider. Visit the SaaS tool's official website and look for sections like "Developers," "API Documentation," or "Integrations." Follow the instructions to create a new application or generate an API key. Once you have the key, you can enter it in the "Settings & API Keys" section of your dashboard.
            """)

        with st.expander("12) What is the marketplace?"):
            st.write("""
Apps you or other users have made publicly available — and are currently running — are shown in the marketplace 7 minutes after the web applications initially launch.
            """)
    tab_counter += 1

if __name__ == "__main__":
    main()
