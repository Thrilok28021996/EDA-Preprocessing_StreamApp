# EDA & Preprocessing Application - Django Backend + Desktop App

A comprehensive application for Exploratory Data Analysis (EDA) and Data Preprocessing. Features both a Django web interface and a standalone Electron desktop application with REST API backend.

## 🚀 Features

### ✅ **Complete Feature Set**
- **File Upload**: Drag & drop CSV upload with validation (10MB limit)
- **Interactive Charts**: 8 chart types using Plotly.js (Bar, Line, Histogram, Pie, Scatter, Box, Heatmap, Area)
- **Data Analysis**: Missing values, duplicates, outliers, data types, column statistics
- **Data Preprocessing**: Column selection/dropping, value replacement, filtering, cleaning
- **Export Functionality**: CSV, JSON, Excel export formats
- **Session Management**: Persistent DataFrame storage across pages
- **Responsive Design**: Dark theme matching original Streamlit interface

### 🔧 **Preprocessing Operations**
- **Column Operations**: Select/drop columns, replace values
- **Data Cleaning**: Remove duplicates, handle missing values (drop/fill)
- **Data Filtering**: Complex multi-column filtering with operators
- **Export & Reset**: Download processed data, reset to original

### 📊 **Analysis & Visualization**
- **Statistical Analysis**: Comprehensive data profiling and insights
- **Interactive Charts**: Real-time chart generation with column selection
- **Data Quality Assessment**: Missing values, duplicates, outliers detection
- **Performance Optimized**: Efficient handling of large datasets

## 🏗️ **Architecture**

### **Technology Stack**
- **Backend**: Django 4.2.16, Python 3.13, Django REST Framework
- **Web Frontend**: Bootstrap 5, Plotly.js, jQuery
- **Desktop App**: Electron with native UI
- **Data Processing**: Pandas, NumPy
- **API**: RESTful endpoints with JWT authentication
- **Session Storage**: Pickle-based DataFrame serialization
- **Database**: SQLite (default), configurable for PostgreSQL

### **Project Structure**
```
django_eda_app/
├── eda_project/          # Django settings and configuration
├── home/                 # File upload and landing page
├── eda/                  # Exploratory data analysis features  
├── preprocessing/        # Data preprocessing and cleaning
├── feedback/             # Contact form and feedback system
├── templates/            # HTML templates with Bootstrap 5
├── static/              # CSS, JavaScript, and assets
├── utils.py             # DataFrame utility functions
├── manage.py            # Django management commands
├── requirements.txt     # Python dependencies
└── PROJECT_PLAN.md      # Detailed project documentation
```

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.8+ 
- pip package manager

### **Installation**
```bash
# Clone or download the project
cd django_eda_app

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Start development server
python manage.py runserver
```

### **Access the Application**
Open your browser and navigate to: `http://localhost:8000`

## 📖 **Usage Guide**

### **1. Upload Data**
1. Go to the Home page
2. Upload a CSV file (drag & drop or file picker)
3. File validation ensures CSV format and 10MB size limit
4. Dataset information is displayed upon successful upload

### **2. Exploratory Data Analysis**
1. Navigate to the EDA page
2. Use the sidebar to generate charts:
   - **Charts**: Bar, Line, Histogram, Pie, Scatter, Box, Heatmap, Area
   - **Analysis**: View data, missing values, duplicates, outliers, data types
3. Interactive chart configuration with column selection
4. Real-time results display without page refresh

### **3. Data Preprocessing**
1. Go to the Preprocessing page
2. Available operations:
   - **Column Operations**: Select/drop columns, replace values
   - **Data Cleaning**: Remove duplicates, handle missing values
   - **Filtering**: Apply complex filters with multiple conditions
3. Real-time dataset info updates after each operation
4. Export processed data in CSV, JSON, or Excel format

### **4. Session Management**
- Uploaded datasets persist across browser sessions
- Original data is preserved for reset functionality
- Session indicator shows current upload status

## 🎨 **User Interface**

### **Design Features**
- **Dark Theme**: Consistent with original Streamlit design
- **Responsive Layout**: Works on desktop, tablet, and mobile
- **Interactive Elements**: Modal dialogs, loading states, progress indicators
- **Accessibility**: ARIA labels, keyboard navigation, screen reader support

### **Navigation**
- **Sidebar Navigation**: Quick access to all operations
- **Breadcrumbs**: Current page and session status
- **Smart Routing**: Automatic redirects for missing data

## 🔧 **Configuration**

### **Django Settings**
```python
# File upload limits
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# Session configuration
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_SAVE_EVERY_REQUEST = True
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
```

### **Environment Variables**
```bash
# Optional configuration
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=postgresql://user:pass@localhost/dbname
```

## 📊 **Performance**

### **Optimizations**
- **Memory Efficient**: Pickle-based DataFrame serialization
- **Fast Processing**: Optimized pandas operations
- **Lazy Loading**: On-demand chart generation
- **Client-side Caching**: Reduced server requests

### **Limitations**
- **File Size**: 10MB CSV file limit (configurable)
- **Memory Usage**: Large datasets may require server optimization
- **Session Storage**: Limited by server session storage capacity

## 🧪 **Testing**

### **Manual Testing**
```bash
# Start test server
python manage.py runserver

# Test with sample CSV files
# Navigate through all features
# Verify responsive design
```

### **Test Data**
- Use any CSV file for testing
- Sample datasets available in test data directory
- Verify with different data types and sizes

## 📝 **API Endpoints**

### **File Upload**
```
POST /home/upload/          # Upload CSV file
```

### **EDA Operations**
```
POST /eda/generate-chart/   # Generate interactive charts
POST /eda/analyze/          # Perform data analysis
```

### **Preprocessing Operations**
```
POST /preprocessing/apply/              # Apply preprocessing operation
POST /preprocessing/get-column-values/  # Get unique column values
POST /preprocessing/preview/            # Preview operation results
GET  /preprocessing/export/<format>/    # Export processed data
```

## 🤝 **Contributing**

### **Development Setup**
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### **Code Standards**
- Follow Django best practices
- Use Python PEP 8 style guide
- Add docstrings to functions
- Write meaningful commit messages

## 📋 **Project Status**

### **Completed (95%)**
- ✅ **Phase 1**: Foundation Setup (100%)
- ✅ **Phase 2**: Core Features (100%) 
- ⏳ **Phase 3**: Enhancement & Polish (60%)
- ⏳ **Phase 4**: Testing & Deployment (40%)

### **Recent Updates**
- Complete preprocessing functionality implementation
- Interactive chart generation with 8 chart types
- Comprehensive data analysis tools
- Export functionality for multiple formats
- Responsive UI with Bootstrap 5 dark theme

### **Next Steps**
- Enhanced feedback system
- Advanced performance optimizations
- Comprehensive test suite
- Production deployment configuration

## 📞 **Support**

For questions, issues, or contributions:
- **Documentation**: See PROJECT_PLAN.md for detailed information
- **Issues**: Report bugs or request features via GitHub issues
- **Contact**: thriloke96@gmail.com

## 📄 **License**

This project is open source and available under the MIT License.

---

**Built with ❤️ using Django, Bootstrap, and Plotly.js**

*Migration from Streamlit to Django - Enhancing user experience with modern web technologies*