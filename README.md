# Cavendish School Portal

A comprehensive school management portal for Cavendish University.

## Features

### Student Features
- Course registration for each year and semester
- Payment system for tuition and module registration
- Access to CAT1, CAT2, and final exam results
- Docket printing with payment requirements
- Payment tracking and balance display

### Payment Requirements for Dockets
- CAT1: 50% of fees paid
- CAT2: 75% of fees paid  
- Final Exam: 100% of fees paid
- Separate K5 payment for docket printing

### Admin Features
- User management
- Payment monitoring
- Student records management
- System configuration

### Lecturer Features
- Results management
- Student performance tracking

## Installation

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run the application: `python app.py`
6. Visit: `http://localhost:5000`

## Configuration

Update `config.py` with your specific settings and database configuration.

Create a `.env` file in the root directory with: