import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
from typing import Union, List, Dict, Any, Optional, Tuple
import re

# Configure the page
st.set_page_config(
    page_title="AI Indian Accounting Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== UTILITY FUNCTIONS ====================

def format_currency(amount: Union[float, int], show_symbol: bool = True) -> str:
    """Format amount in Indian currency format with ₹ symbol"""
    if amount == 0:
        return "₹0" if show_symbol else "0"
    
    try:
        amount = float(amount)
        is_negative = amount < 0
        amount = abs(amount)
        
        if amount >= 10000000:  # 1 crore
            crores = amount / 10000000
            formatted = f"{crores:,.2f}".rstrip('0').rstrip('.') + " Cr"
        elif amount >= 100000:  # 1 lakh
            lakhs = amount / 100000
            formatted = f"{lakhs:,.2f}".rstrip('0').rstrip('.') + " L"
        else:
            formatted = f"{amount:,.2f}".rstrip('0').rstrip('.')
        
        if show_symbol:
            formatted = "₹" + formatted
        
        if is_negative:
            formatted = "-" + formatted
        
        return formatted
        
    except (ValueError, TypeError):
        return "₹0" if show_symbol else "0"

def validate_positive_number(value: Union[float, int, str], 
                           field_name: str = "Value",
                           allow_zero: bool = False) -> Tuple[bool, str]:
    """Validate if the input is a positive number"""
    try:
        num_value = float(value)
        
        if num_value < 0:
            return False, f"❌ {field_name} cannot be negative"
        
        if not allow_zero and num_value == 0:
            return False, f"❌ {field_name} must be greater than zero"
        
        return True, ""
        
    except (ValueError, TypeError):
        return False, f"❌ {field_name} must be a valid number"

def validate_gst_rate(rate: Union[float, int]) -> Tuple[bool, str]:
    """Validate GST rate according to Indian GST structure"""
    try:
        rate = float(rate)
        
        if rate < 0:
            return False, "❌ GST rate cannot be negative"
        
        if rate > 28:
            return False, "❌ GST rate cannot exceed 28%"
        
        valid_rates = [0, 5, 12, 18, 28]
        if rate not in valid_rates:
            return False, f"❌ Invalid GST rate. Valid rates are: {', '.join(map(str, valid_rates))}%"
        
        return True, ""
        
    except (ValueError, TypeError):
        return False, "❌ GST rate must be a valid number"

# ==================== ACCOUNTING EQUATIONS MODULE ====================

def show_accounting_equations():
    st.header("📐 Accounting Equations Solver")
    st.markdown("**Fundamental Equation: Assets = Liabilities + Capital**")
    
    tab1, tab2, tab3 = st.tabs(["🔍 Solve Equation", "📚 Learn Concepts", "📝 Practice Problems"])
    
    with tab1:
        solve_accounting_equation()
    
    with tab2:
        show_equation_concepts()
    
    with tab3:
        show_equation_practice_problems()

def solve_accounting_equation():
    st.subheader("Enter Known Values")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 💼 Assets")
        assets = st.number_input("Total Assets (₹)", min_value=0.0, value=None, 
                                placeholder="Enter if known", key="assets")
        
        st.markdown("#### 🏦 Liabilities")
        liabilities = st.number_input("Total Liabilities (₹)", min_value=0.0, value=None,
                                     placeholder="Enter if known", key="liabilities")
        
        st.markdown("#### 👤 Capital")
        capital = st.number_input("Owner's Capital (₹)", min_value=0.0, value=None,
                                 placeholder="Enter if known", key="capital")
    
    with col2:
        st.markdown("#### 📊 Additional Information")
        drawings = st.number_input("Drawings (₹)", min_value=0.0, value=0.0, key="drawings")
        additional_capital = st.number_input("Additional Capital (₹)", min_value=0.0, value=0.0, key="add_capital")
        profit_loss = st.number_input("Profit (+) / Loss (-) (₹)", value=0.0, key="profit_loss")
    
    if st.button("🧮 Solve Equation", type="primary"):
        solve_equation(assets, liabilities, capital, drawings, additional_capital, profit_loss)

def solve_equation(assets, liabilities, capital, drawings, additional_capital, profit_loss):
    try:
        known_values = sum([x is not None and x != 0 for x in [assets, liabilities, capital]])
        
        if known_values < 2:
            st.error("❌ Please provide at least 2 known values to solve the equation!")
            return
        
        st.markdown("---")
        st.subheader("📋 Step-by-Step Solution")
        
        if capital is not None:
            adjusted_capital = capital + additional_capital - drawings + profit_loss
            st.markdown(f"""
            **Step 1: Adjust Capital**
            - Opening Capital: {format_currency(capital)}
            - Add: Additional Capital: {format_currency(additional_capital)}
            - Add: Profit: {format_currency(max(0, profit_loss))}
            - Less: Loss: {format_currency(abs(min(0, profit_loss)))}
            - Less: Drawings: {format_currency(drawings)}
            - **Adjusted Capital: {format_currency(adjusted_capital)}**
            """)
        else:
            adjusted_capital = None
        
        st.markdown("**Step 2: Apply Accounting Equation**")
        st.markdown("**Assets = Liabilities + Capital**")
        
        solution = {}
        
        if assets is None:
            if liabilities is not None and adjusted_capital is not None:
                calculated_assets = liabilities + adjusted_capital
                solution['Assets'] = calculated_assets
                st.success(f"✅ **Assets = {format_currency(liabilities)} + {format_currency(adjusted_capital)} = {format_currency(calculated_assets)}**")
        
        elif liabilities is None:
            if assets is not None and adjusted_capital is not None:
                calculated_liabilities = assets - adjusted_capital
                solution['Liabilities'] = calculated_liabilities
                st.success(f"✅ **Liabilities = {format_currency(assets)} - {format_currency(adjusted_capital)} = {format_currency(calculated_liabilities)}**")
        
        elif capital is None:
            if assets is not None and liabilities is not None:
                calculated_capital = assets - liabilities
                original_capital = calculated_capital - additional_capital + drawings - profit_loss
                solution['Original Capital'] = original_capital
                solution['Adjusted Capital'] = calculated_capital
                st.success(f"✅ **Adjusted Capital = {format_currency(assets)} - {format_currency(liabilities)} = {format_currency(calculated_capital)}**")
                st.success(f"✅ **Original Capital = {format_currency(original_capital)}**")
        
        final_assets = assets or solution.get('Assets')
        final_liabilities = liabilities or solution.get('Liabilities')
        final_capital = adjusted_capital or solution.get('Adjusted Capital')
        
        if final_assets and final_liabilities and final_capital:
            st.markdown("**Step 3: Verification**")
            if abs(final_assets - (final_liabilities + final_capital)) < 0.01:
                st.success(f"✅ **Verified: {format_currency(final_assets)} = {format_currency(final_liabilities)} + {format_currency(final_capital)}**")
            else:
                st.error("❌ **Error in calculation - equation doesn't balance!**")
        
        create_equation_summary_table(assets, liabilities, capital, solution, adjusted_capital)
        
    except Exception as e:
        st.error(f"❌ Error in calculation: {str(e)}")

def create_equation_summary_table(assets, liabilities, capital, solution, adjusted_capital):
    st.markdown("### 📊 Summary")
    
    summary_data = []
    
    if assets or 'Assets' in solution:
        summary_data.append({
            'Component': 'Assets',
            'Amount (₹)': format_currency(assets or solution['Assets']),
            'Status': 'Given' if assets else 'Calculated'
        })
    
    if liabilities or 'Liabilities' in solution:
        summary_data.append({
            'Component': 'Liabilities', 
            'Amount (₹)': format_currency(liabilities or solution['Liabilities']),
            'Status': 'Given' if liabilities else 'Calculated'
        })
    
    if capital or 'Original Capital' in solution:
        summary_data.append({
            'Component': 'Capital (Original)',
            'Amount (₹)': format_currency(capital or solution['Original Capital']),
            'Status': 'Given' if capital else 'Calculated'
        })
    
    if adjusted_capital or 'Adjusted Capital' in solution:
        summary_data.append({
            'Component': 'Capital (Adjusted)',
            'Amount (₹)': format_currency(adjusted_capital or solution['Adjusted Capital']),
            'Status': 'Calculated'
        })
    
    df = pd.DataFrame(summary_data)
    st.table(df)

def show_equation_concepts():
    st.markdown("""
    ## 📚 Accounting Equation Concepts
    
    ### Basic Equation
    **Assets = Liabilities + Owner's Equity (Capital)**
    
    ### Components Explained:
    
    #### 🏢 Assets
    - **Current Assets**: Cash, Bank, Inventory, Debtors
    - **Fixed Assets**: Land, Building, Machinery, Furniture
    
    #### 🏦 Liabilities  
    - **Current Liabilities**: Creditors, Outstanding expenses
    - **Long-term Liabilities**: Bank loans, Mortgages
    
    #### 👤 Owner's Equity (Capital)
    - Initial capital invested
    - Plus: Additional capital
    - Plus: Profits earned
    - Less: Drawings taken
    - Less: Losses incurred
    
    ### 🔄 Effects of Transactions:
    
    | Transaction Type | Assets | Liabilities | Capital |
    |------------------|--------|-------------|---------|
    | Capital introduced | +₹ | - | +₹ |
    | Purchase on credit | +₹ | +₹ | - |
    | Payment to creditor | -₹ | -₹ | - |
    | Drawings | -₹ | - | -₹ |
    | Profit earned | +₹ | - | +₹ |
    """)

def show_equation_practice_problems():
    st.markdown("## 📝 Practice Problems")
    
    problems = [
        {
            "title": "Problem 1: Find Missing Assets",
            "description": "Liabilities: ₹50,000, Capital: ₹1,50,000. Find Assets.",
            "solution": "Assets = ₹50,000 + ₹1,50,000 = ₹2,00,000"
        },
        {
            "title": "Problem 2: Find Missing Capital", 
            "description": "Assets: ₹3,00,000, Liabilities: ₹75,000. Find Capital.",
            "solution": "Capital = ₹3,00,000 - ₹75,000 = ₹2,25,000"
        },
        {
            "title": "Problem 3: With Drawings and Profit",
            "description": "Opening Capital: ₹2,00,000, Profit: ₹50,000, Drawings: ₹30,000, Assets: ₹3,00,000. Find Liabilities.",
            "solution": "Adjusted Capital = ₹2,00,000 + ₹50,000 - ₹30,000 = ₹2,20,000\nLiabilities = ₹3,00,000 - ₹2,20,000 = ₹80,000"
        }
    ]
    
    for i, problem in enumerate(problems, 1):
        with st.expander(f"📚 {problem['title']}"):
            st.markdown(f"**Problem:** {problem['description']}")
            if st.button(f"Show Solution", key=f"eq_solution_{i}"):
                st.markdown(f"**Solution:**\n{problem['solution']}")

# ==================== JOURNAL ENTRIES MODULE ====================

def show_journal_entries():
    st.header("📝 Journal Entries Generator")
    st.markdown("**Record business transactions in proper journal format**")
    
    tab1, tab2, tab3 = st.tabs(["✍️ Create Entry", "📚 Entry Types", "📖 Rules & Format"])
    
    with tab1:
        create_journal_entry()
    
    with tab2:
        show_journal_entry_types()
    
    with tab3:
        show_journal_rules()

def create_journal_entry():
    st.subheader("Transaction Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        entry_date = st.date_input("Date", value=datetime.now())
        transaction_type = st.selectbox(
            "Transaction Type",
            [
                "Cash/Bank Transaction",
                "Purchase Transaction", 
                "Sales Transaction",
                "Expense Transaction",
                "Income Transaction",
                "Capital Transaction",
                "Custom Entry"
            ]
        )
    
    with col2:
        amount = st.number_input("Amount (₹)", min_value=0.01, value=1000.0)
        narration = st.text_area("Narration/Description", 
                                placeholder="Brief description of the transaction")
    
    if transaction_type != "Custom Entry":
        create_predefined_entry(transaction_type, entry_date, amount, narration)
    else:
        create_custom_journal_entry(entry_date, amount, narration)

def create_predefined_entry(transaction_type, entry_date, amount, narration):
    st.subheader("Transaction Specific Details")
    
    if transaction_type == "Cash/Bank Transaction":
        handle_cash_bank_transaction(entry_date, amount, narration)
    elif transaction_type == "Purchase Transaction":
        handle_purchase_transaction(entry_date, amount, narration)
    elif transaction_type == "Sales Transaction":
        handle_sales_transaction(entry_date, amount, narration)
    elif transaction_type == "Expense Transaction":
        handle_expense_transaction(entry_date, amount, narration)
    elif transaction_type == "Income Transaction":
        handle_income_transaction(entry_date, amount, narration)
    elif transaction_type == "Capital Transaction":
        handle_capital_transaction(entry_date, amount, narration)

def handle_cash_bank_transaction(entry_date, amount, narration):
    col1, col2 = st.columns(2)
    
    with col1:
        cash_bank = st.selectbox("Cash/Bank", ["Cash", "Bank"])
        transaction_nature = st.selectbox("Nature", ["Receipt", "Payment"])
    
    with col2:
        if transaction_nature == "Receipt":
            from_account = st.text_input("Received from", placeholder="e.g., Debtors, Sales")
        else:
            to_account = st.text_input("Paid to", placeholder="e.g., Creditors, Expenses")
    
    if st.button("📝 Generate Journal Entry", type="primary"):
        entries = []
        
        if transaction_nature == "Receipt":
            entries.append({
                'Account': cash_bank,
                'Dr_Amount': amount,
                'Cr_Amount': 0
            })
            entries.append({
                'Account': f"To {from_account}",
                'Dr_Amount': 0,
                'Cr_Amount': amount
            })
        else:
            to_account_name = to_account if 'to_account' in locals() else "Expense"
            entries.append({
                'Account': to_account_name,
                'Dr_Amount': amount,
                'Cr_Amount': 0
            })
            entries.append({
                'Account': f"To {cash_bank}",
                'Dr_Amount': 0,
                'Cr_Amount': amount
            })
        
        display_journal_entry(entry_date, entries, narration)

def handle_purchase_transaction(entry_date, amount, narration):
    col1, col2 = st.columns(2)
    
    with col1:
        purchase_type = st.selectbox("Purchase Type", ["Cash Purchase", "Credit Purchase"])
        goods_type = st.text_input("Goods/Item", value="Goods", placeholder="e.g., Goods, Machinery")
    
    with col2:
        if purchase_type == "Credit Purchase":
            supplier = st.text_input("Supplier Name", placeholder="Supplier name")
        
        include_gst = st.checkbox("Include GST")
        if include_gst:
            gst_rate = st.selectbox("GST Rate (%)", [5, 12, 18, 28], index=2)
    
    if st.button("📝 Generate Purchase Entry", type="primary"):
        entries = []
        
        if include_gst:
            basic_amount = amount / (1 + gst_rate/100)
            gst_amount = amount - basic_amount
            
            entries.append({
                'Account': f"{goods_type} Purchase",
                'Dr_Amount': basic_amount,
                'Cr_Amount': 0
            })
            entries.append({
                'Account': "Input GST",
                'Dr_Amount': gst_amount,
                'Cr_Amount': 0
            })
        else:
            entries.append({
                'Account': f"{goods_type} Purchase",
                'Dr_Amount': amount,
                'Cr_Amount': 0
            })
        
        if purchase_type == "Credit Purchase":
            entries.append({
                'Account': f"To {supplier or 'Creditors'}",
                'Dr_Amount': 0,
                'Cr_Amount': amount
            })
        else:
            entries.append({
                'Account': "To Cash/Bank",
                'Dr_Amount': 0,
                'Cr_Amount': amount
            })
        
        display_journal_entry(entry_date, entries, narration)

def handle_sales_transaction(entry_date, amount, narration):
    col1, col2 = st.columns(2)
    
    with col1:
        sales_type = st.selectbox("Sales Type", ["Cash Sales", "Credit Sales"])
        goods_type = st.text_input("Goods/Service", value="Goods", placeholder="e.g., Goods, Services")
    
    with col2:
        if sales_type == "Credit Sales":
            customer = st.text_input("Customer Name", placeholder="Customer name")
        
        include_gst = st.checkbox("Include GST", key="sales_gst")
        if include_gst:
            gst_rate = st.selectbox("GST Rate (%)", [5, 12, 18, 28], index=2, key="sales_gst_rate")
    
    if st.button("📝 Generate Sales Entry", type="primary"):
        entries = []
        
        if sales_type == "Credit Sales":
            entries.append({
                'Account': customer or "Debtors",
                'Dr_Amount': amount,
                'Cr_Amount': 0
            })
        else:
            entries.append({
                'Account': "Cash/Bank",
                'Dr_Amount': amount,
                'Cr_Amount': 0
            })
        
        if include_gst:
            basic_amount = amount / (1 + gst_rate/100)
            gst_amount = amount - basic_amount
            
            entries.append({
                'Account': f"To {goods_type} Sales",
                'Dr_Amount': 0,
                'Cr_Amount': basic_amount
            })
            entries.append({
                'Account': "To Output GST",
                'Dr_Amount': 0,
                'Cr_Amount': gst_amount
            })
        else:
            entries.append({
                'Account': f"To {goods_type} Sales",
                'Dr_Amount': 0,
                'Cr_Amount': amount
            })
        
        display_journal_entry(entry_date, entries, narration)

def handle_expense_transaction(entry_date, amount, narration):
    col1, col2 = st.columns(2)
    
    with col1:
        expense_type = st.selectbox(
            "Expense Type",
            ["Rent", "Salary", "Electricity", "Telephone", "Office Supplies", "Other"]
        )
        if expense_type == "Other":
            expense_type = st.text_input("Specify Expense", placeholder="Enter expense name")
    
    with col2:
        payment_method = st.selectbox("Payment Method", ["Cash", "Bank", "Credit"])
        if payment_method == "Credit":
            creditor_name = st.text_input("Creditor Name", placeholder="Name of creditor")
    
    if st.button("📝 Generate Expense Entry", type="primary"):
        entries = []
        
        entries.append({
            'Account': f"{expense_type} Expense",
            'Dr_Amount': amount,
            'Cr_Amount': 0
        })
        
        if payment_method == "Credit":
            entries.append({
                'Account': f"To {creditor_name or 'Creditors'}",
                'Dr_Amount': 0,
                'Cr_Amount': amount
            })
        else:
            entries.append({
                'Account': f"To {payment_method}",
                'Dr_Amount': 0,
                'Cr_Amount': amount
            })
        
        display_journal_entry(entry_date, entries, narration)

def handle_income_transaction(entry_date, amount, narration):
    col1, col2 = st.columns(2)
    
    with col1:
        income_type = st.selectbox(
            "Income Type",
            ["Commission Income", "Interest Income", "Rent Income", "Miscellaneous Income", "Other"]
        )
        if income_type == "Other":
            income_type = st.text_input("Specify Income", placeholder="Enter income name")
    
    with col2:
        receipt_method = st.selectbox("Receipt Method", ["Cash", "Bank"], key="income_receipt")
    
    if st.button("📝 Generate Income Entry", type="primary"):
        entries = []
        
        entries.append({
            'Account': receipt_method,
            'Dr_Amount': amount,
            'Cr_Amount': 0
        })
        
        entries.append({
            'Account': f"To {income_type}",
            'Dr_Amount': 0,
            'Cr_Amount': amount
        })
        
        display_journal_entry(entry_date, entries, narration)

def handle_capital_transaction(entry_date, amount, narration):
    col1, col2 = st.columns(2)
    
    with col1:
        capital_type = st.selectbox(
            "Transaction Type",
            ["Capital Introduced", "Additional Capital", "Drawings", "Capital Withdrawal"]
        )
    
    with col2:
        asset_type = st.selectbox("Asset Type", ["Cash", "Bank", "Goods", "Other Assets"])
        if asset_type == "Other Assets":
            asset_type = st.text_input("Specify Asset", placeholder="Enter asset name")
    
    if st.button("📝 Generate Capital Entry", type="primary"):
        entries = []
        
        if capital_type in ["Capital Introduced", "Additional Capital"]:
            entries.append({
                'Account': asset_type,
                'Dr_Amount': amount,
                'Cr_Amount': 0
            })
            entries.append({
                'Account': "To Capital",
                'Dr_Amount': 0,
                'Cr_Amount': amount
            })
        else:  # Drawings or Withdrawal
            entries.append({
                'Account': "Drawings",
                'Dr_Amount': amount,
                'Cr_Amount': 0
            })
            entries.append({
                'Account': f"To {asset_type}",
                'Dr_Amount': 0,
                'Cr_Amount': amount
            })
        
        display_journal_entry(entry_date, entries, narration)

def create_custom_journal_entry(entry_date, amount, narration):
    st.subheader("Custom Journal Entry")
    
    # Initialize session state for custom entries
    if 'custom_entries' not in st.session_state:
        st.session_state.custom_entries = []
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        account_name = st.text_input("Account Name", key="custom_account")
    
    with col2:
        entry_type = st.selectbox("Entry Type", ["Debit", "Credit"], key="custom_type")
    
    with col3:
        entry_amount = st.number_input("Amount (₹)", min_value=0.01, key="custom_amount")
    
    if st.button("➕ Add Entry"):
        if account_name and entry_amount > 0:
            entry = {
                'Account': account_name,
                'Dr_Amount': entry_amount if entry_type == "Debit" else 0,
                'Cr_Amount': entry_amount if entry_type == "Credit" else 0
            }
            st.session_state.custom_entries.append(entry)
            st.success(f"✅ Added {entry_type} entry for {account_name}")
            st.rerun()
    
    if st.session_state.custom_entries:
        st.subheader("Current Entries")
        for i, entry in enumerate(st.session_state.custom_entries):
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.write(f"{entry['Account']}")
            with col2:
                if entry['Dr_Amount'] > 0:
                    st.write(f"Dr: {format_currency(entry['Dr_Amount'])}")
                else:
                    st.write(f"Cr: {format_currency(entry['Cr_Amount'])}")
            with col3:
                if st.button("🗑️", key=f"del_{i}"):
                    st.session_state.custom_entries.pop(i)
                    st.rerun()
        
        total_dr = sum(entry['Dr_Amount'] for entry in st.session_state.custom_entries)
        total_cr = sum(entry['Cr_Amount'] for entry in st.session_state.custom_entries)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Debits", format_currency(total_dr))
        with col2:
            st.metric("Total Credits", format_currency(total_cr))
        with col3:
            if abs(total_dr - total_cr) < 0.01:
                st.success("✅ Balanced")
            else:
                st.error("❌ Not Balanced")
        
        if st.button("📝 Generate Custom Entry", type="primary"):
            if abs(total_dr - total_cr) < 0.01:
                display_journal_entry(entry_date, st.session_state.custom_entries, narration)
                st.session_state.custom_entries = []
            else:
                st.error("❌ Please ensure total debits equal total credits")

def display_journal_entry(entry_date, entries, narration):
    st.markdown("---")
    st.subheader("📋 Generated Journal Entry")
    
    # Create journal entry table
    journal_data = []
    total_dr = 0
    total_cr = 0
    
    for entry in entries:
        dr_amount = entry.get('Dr_Amount', 0)
        cr_amount = entry.get('Cr_Amount', 0)
        
        journal_data.append({
            'Date': entry_date.strftime('%d-%m-%Y') if journal_data == [] else '',
            'Particulars': entry['Account'],
            'Dr Amount (₹)': format_currency(dr_amount) if dr_amount > 0 else '',
            'Cr Amount (₹)': format_currency(cr_amount) if cr_amount > 0 else ''
        })
        
        total_dr += dr_amount
        total_cr += cr_amount
    
    # Add narration row
    journal_data.append({
        'Date': '',
        'Particulars': f"({narration})",
        'Dr Amount (₹)': '',
        'Cr Amount (₹)': ''
    })
    
    # Add totals row
    journal_data.append({
        'Date': '',
        'Particulars': '**TOTAL**',
        'Dr Amount (₹)': f"**{format_currency(total_dr)}**",
        'Cr Amount (₹)': f"**{format_currency(total_cr)}**"
    })
    
    df = pd.DataFrame(journal_data)
    st.table(df)
    
    # Verification
    if abs(total_dr - total_cr) < 0.01:
        st.success(f"✅ **Journal Entry is Balanced** - Dr: {format_currency(total_dr)} = Cr: {format_currency(total_cr)}")
    else:
        st.error(f"❌ **Journal Entry is NOT Balanced** - Dr: {format_currency(total_dr)} ≠ Cr: {format_currency(total_cr)}")

def show_journal_entry_types():
    st.markdown("""
    ## 📚 Types of Journal Entries
    
    ### 1. 💰 Opening Entries
    - Record opening balances at start of accounting period
    - **Format**: Various Assets Dr / To Capital & Liabilities
    
    ### 2. 📝 Trading Entries
    - Record day-to-day business transactions
    - Purchase, Sales, Expenses, Income transactions
    
    ### 3. 🔧 Adjusting Entries
    - Made at the end of accounting period
    - Outstanding expenses, Prepaid expenses, Depreciation
    
    ### 4. ❌ Rectifying Entries
    - Correct errors in previous entries
    - Wrong account, Wrong amount, Wrong side entries
    
    ### 5. 🔒 Closing Entries
    - Transfer nominal accounts to P&L
    - Close revenue and expense accounts
    
    ### 6. 💼 Capital Entries
    - Capital introduction, Additional capital, Drawings
    
    ### 7. 🏦 Banking Entries
    - Bank deposits, Withdrawals, Bank charges
    
    ### 8. 🧾 Credit Transactions
    - Purchases on credit, Sales on credit
    - Payments to creditors, Receipts from debtors
    """)

def show_journal_rules():
    st.markdown("""
    ## 📖 Journal Entry Rules & Format
    
    ### Golden Rules of Accounting
    
    #### 🏷️ Personal Accounts
    - **Debit**: The receiver
    - **Credit**: The giver
    
    #### 🏢 Real Accounts (Assets)
    - **Debit**: What comes in
    - **Credit**: What goes out
    
    #### 💰 Nominal Accounts (Income/Expenses)
    - **Debit**: All expenses and losses
    - **Credit**: All income and gains
    
    ### Journal Entry Format
    
    ```
    Date: DD-MM-YYYY
    
    Dr.  Account Name                     Amount
         To Account Name                          Amount
         To Account Name                          Amount
         (Narration explaining the transaction)
    ```
    
    ### Important Points
    
    1. **Date**: Always record transaction date
    2. **Debit First**: Debit accounts are written first
    3. **Credit with 'To'**: Credit accounts start with 'To'
    4. **Narration**: Brief explanation in brackets
    5. **Equal Totals**: Total debits must equal total credits
    6. **Proper Accounts**: Use correct account names
    7. **Amount Columns**: Separate columns for Dr and Cr amounts
    
    ### Common Account Types
    
    **Assets**: Cash, Bank, Machinery, Building, Debtors
    **Liabilities**: Creditors, Bank Loan, Outstanding Expenses
    **Capital**: Owner's Capital, Retained Earnings
    **Income**: Sales, Interest Income, Commission Income
    **Expenses**: Rent, Salary, Electricity, Depreciation
    """)

# ==================== GST CALCULATOR MODULE ====================

def show_gst_calculator():
    st.header("💰 GST Calculator")
    st.markdown("**Calculate CGST, SGST, IGST as per Indian GST Rules**")
    
    tab1, tab2, tab3 = st.tabs(["🧮 Calculate GST", "📊 GST Rates", "📚 GST Rules"])
    
    with tab1:
        calculate_gst()
    
    with tab2:
        show_gst_rates()
    
    with tab3:
        show_gst_rules()

def calculate_gst():
    st.subheader("Transaction Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        transaction_type = st.selectbox(
            "Transaction Type",
            ["Intrastate (Within State)", "Interstate (Between States)"]
        )
        
        amount_type = st.selectbox(
            "Amount Type",
            ["Exclusive of GST", "Inclusive of GST"]
        )
        
        amount = st.number_input("Amount (₹)", min_value=0.01, value=1000.0)
    
    with col2:
        gst_rate = st.selectbox(
            "GST Rate (%)",
            [0, 5, 12, 18, 28],
            index=3  # Default to 18%
        )
        
        reverse_charge = st.checkbox("Reverse Charge Mechanism")
        
        if reverse_charge:
            st.info("💡 In reverse charge, recipient pays GST")
    
    # Additional details
    st.subheader("Additional Details")
    col1, col2 = st.columns(2)
    
    with col1:
        from_state = st.text_input("From State", placeholder="e.g., Maharashtra")
        to_state = st.text_input("To State", placeholder="e.g., Gujarat")
    
    with col2:
        hsn_code = st.text_input("HSN/SAC Code", placeholder="e.g., 1001")
        description = st.text_input("Item Description", placeholder="Description of goods/services")
    
    if st.button("🧮 Calculate GST", type="primary"):
        calculate_and_display_gst(
            amount, gst_rate, amount_type, transaction_type, 
            from_state, to_state, hsn_code, description, reverse_charge
        )

def calculate_and_display_gst(amount, gst_rate, amount_type, transaction_type, 
                             from_state, to_state, hsn_code, description, reverse_charge):
    
    st.markdown("---")
    st.subheader("📊 GST Calculation Results")
    
    # Determine if interstate based on states
    is_interstate = False
    if from_state and to_state and from_state.strip().lower() != to_state.strip().lower():
        is_interstate = True
    elif transaction_type == "Interstate (Between States)":
        is_interstate = True
    
    # Calculate basic amount and GST
    if amount_type == "Inclusive of GST":
        basic_amount = amount / (1 + gst_rate/100)
        gst_amount = amount - basic_amount
    else:
        basic_amount = amount
        gst_amount = amount * (gst_rate/100)
    
    total_amount = basic_amount + gst_amount
    
    # Display step-by-step calculation
    st.markdown("### 📝 Step-by-Step Calculation")
    
    if amount_type == "Inclusive of GST":
        st.markdown(f"""
        **Step 1: Extract Basic Amount from GST Inclusive Amount**
        - GST Inclusive Amount: {format_currency(amount)}
        - GST Rate: {gst_rate}%
        - Basic Amount = {format_currency(amount)} ÷ (1 + {gst_rate}/100)
        - Basic Amount = {format_currency(amount)} ÷ {1 + gst_rate/100}
        - **Basic Amount = {format_currency(basic_amount)}**
        """)
    else:
        st.markdown(f"""
        **Step 1: Basic Amount (GST Exclusive)**
        - **Basic Amount = {format_currency(basic_amount)}**
        """)
    
    st.markdown(f"""
    **Step 2: Calculate GST Amount**
    - GST Amount = {format_currency(basic_amount)} × {gst_rate}%
    - **GST Amount = {format_currency(gst_amount)}**
    """)
    
    # Determine GST split
    if is_interstate:
        igst = gst_amount
        cgst = 0
        sgst = 0
        
        st.markdown(f"""
        **Step 3: GST Classification (Interstate Transaction)**
        - Transaction Type: Interstate (Between {from_state or 'State A'} and {to_state or 'State B'})
        - **IGST (100%) = {format_currency(igst)}**
        - **CGST = {format_currency(cgst)}**
        - **SGST = {format_currency(sgst)}**
        """)
    else:
        cgst = gst_amount / 2
        sgst = gst_amount / 2
        igst = 0
        
        st.markdown(f"""
        **Step 3: GST Classification (Intrastate Transaction)**
        - Transaction Type: Intrastate (Within {from_state or 'Same State'})
        - **CGST (50%) = {format_currency(cgst)}**
        - **SGST (50%) = {format_currency(sgst)}**
        - **IGST = {format_currency(igst)}**
        """)
    
    # Summary table
    st.markdown("### 📊 GST Calculation Summary")
    
    summary_data = [
        {"Component": "Basic Amount", "Amount": format_currency(basic_amount), "Rate": "-"},
        {"Component": "CGST", "Amount": format_currency(cgst), "Rate": f"{gst_rate/2}%" if cgst > 0 else "0%"},
        {"Component": "SGST", "Amount": format_currency(sgst), "Rate": f"{gst_rate/2}%" if sgst > 0 else "0%"},
        {"Component": "IGST", "Amount": format_currency(igst), "Rate": f"{gst_rate}%" if igst > 0 else "0%"},
        {"Component": "**Total GST**", "Amount": f"**{format_currency(gst_amount)}**", "Rate": f"**{gst_rate}%**"},
        {"Component": "**Grand Total**", "Amount": f"**{format_currency(total_amount)}**", "Rate": "**-**"}
    ]
    
    df_summary = pd.DataFrame(summary_data)
    st.table(df_summary)
    
    # Journal entries for GST
    if not reverse_charge:
        st.markdown("### 📝 Journal Entries")
        
        if is_interstate:
            # Interstate transaction
            journal_entries = f"""
            **For Sales (Interstate):**
            ```
            Dr. Debtors/Cash                        {format_currency(total_amount)}
                To Sales                                    {format_currency(basic_amount)}
                To IGST Payable                            {format_currency(igst)}
            ```
            
            **For Purchase (Interstate):**
            ```
            Dr. Purchase                            {format_currency(basic_amount)}
            Dr. IGST Input                         {format_currency(igst)}
                To Creditors/Cash                          {format_currency(total_amount)}
            ```
            """
        else:
            # Intrastate transaction
            journal_entries = f"""
            **For Sales (Intrastate):**
            ```
            Dr. Debtors/Cash                        {format_currency(total_amount)}
                To Sales                                    {format_currency(basic_amount)}
                To CGST Payable                            {format_currency(cgst)}
                To SGST Payable                            {format_currency(sgst)}
            ```
            
            **For Purchase (Intrastate):**
            ```
            Dr. Purchase                            {format_currency(basic_amount)}
            Dr. CGST Input                         {format_currency(cgst)}
            Dr. SGST Input                         {format_currency(sgst)}
                To Creditors/Cash                          {format_currency(total_amount)}
            ```
            """
        
        st.markdown(journal_entries)
    else:
        st.info("💡 **Reverse Charge:** GST will be paid by the recipient as per reverse charge mechanism rules.")

def show_gst_rates():
    st.markdown("## 📊 Standard GST Rates in India")
    
    # Create GST rates table
    gst_rates_data = [
        {"Rate": "0%", "Category": "Exempted", "Examples": "Basic food items, Books, Newspapers"},
        {"Rate": "5%", "Category": "Essential Items", "Examples": "Sugar, Tea, Coffee, Medicines"},
        {"Rate": "12%", "Category": "Standard Items", "Examples": "Mobile phones, Computers, Processed food"},
        {"Rate": "18%", "Category": "Standard Items", "Examples": "Most goods and services, Electronics"},
        {"Rate": "28%", "Category": "Luxury Items", "Examples": "Cars, Cigarettes, Luxury goods"}
    ]
    
    df_rates = pd.DataFrame(gst_rates_data)
    st.table(df_rates)
    
    st.markdown("""
    ### 🏢 GST Registration Limits
    
    - **Regular Business**: ₹40 Lakhs annual turnover
    - **Special States** (NE, Hills): ₹20 Lakhs annual turnover
    - **Service Providers**: ₹20 Lakhs annual turnover
    - **E-commerce**: Mandatory registration regardless of turnover
    
    ### 📋 GST Return Filing
    
    - **GSTR-1**: Monthly/Quarterly sales return
    - **GSTR-3B**: Monthly summary return
    - **GSTR-9**: Annual return
    - **GSTR-4**: Quarterly return for composition scheme
    
    ### 💰 Input Tax Credit (ITC)
    
    - Available on business purchases
    - Cannot claim ITC on personal use items
    - Must have valid tax invoice
    - Supplier should have filed returns
    """)

def show_gst_rules():
    st.markdown("""
    ## 📚 GST Rules & Concepts
    
    ### 🎯 What is GST?
    
    **Goods and Services Tax (GST)** is a comprehensive indirect tax levied on supply of goods and services.
    It replaced multiple taxes like VAT, Service Tax, Excise Duty, etc.
    
    ### 🏛️ GST Structure
    
    #### Central GST (CGST)
    - Collected by Central Government
    - Applied on intrastate transactions
    - Rate: 50% of total GST rate
    
    #### State GST (SGST) / Union Territory GST (UTGST)
    - Collected by State/UT Government
    - Applied on intrastate transactions
    - Rate: 50% of total GST rate
    
    #### Integrated GST (IGST)
    - Collected by Central Government
    - Applied on interstate transactions
    - Rate: 100% of total GST rate
    - Later distributed between Centre and States
    
    ### 🔄 GST Transaction Types
    
    #### Intrastate Transaction (Within State)
    - **Formula**: CGST + SGST = Total GST
    - **Example**: Mumbai to Pune (both in Maharashtra)
    - **Tax Split**: 9% CGST + 9% SGST = 18% Total
    
    #### Interstate Transaction (Between States)
    - **Formula**: IGST = Total GST
    - **Example**: Mumbai to Delhi
    - **Tax**: 18% IGST only
    
    ### ⚖️ Input Tax Credit (ITC)
    
    - **Principle**: Tax on tax avoided
    - **Available**: On business purchases
    - **Conditions**: Valid invoice, supplier compliance
    - **Restrictions**: Personal use, blocked items
    
    ### 🔄 Reverse Charge Mechanism
    
    - **Normal**: Supplier pays GST
    - **Reverse Charge**: Recipient pays GST
    - **Applicable**: Specified goods/services
    - **Examples**: GTA services, legal services to business
    
    ### 📋 GST Compliance
    
    1. **Registration**: Above threshold turnover
    2. **Invoice**: GST compliant tax invoices
    3. **Returns**: Monthly/Quarterly filing
    4. **Payment**: Online through GSTN portal
    5. **Records**: Maintain proper books
    
    ### 🚫 GST Exemptions
    
    - **Agricultural produce**
    - **Healthcare services**
    - **Educational services**
    - **Basic food items**
    - **Religious services**
    
    ### 💡 Key Benefits
    
    - **One Nation, One Tax**
    - **Eliminates tax on tax**
    - **Transparent system**
    - **Increased compliance**
    - **Easy interstate trade**
    """)

# ==================== MAIN APPLICATION ====================

def main():
    # Main title
    st.title("🇮🇳 AI Indian Accounting Assistant")
    st.markdown("### CBSE Class 11-12 | CA Foundation | GST Compliance")
    
    # Sidebar navigation
    st.sidebar.title("📚 Accounting Topics")
    
    topics = {
        "🏠 Home": "home",
        "📐 Accounting Equations": "equations",
        "📝 Journal Entries": "journal",
        "💰 GST Calculator": "gst"
    }
    
    selected_topic = st.sidebar.selectbox(
        "Choose a topic:",
        list(topics.keys()),
        index=0
    )
    
    topic_key = topics[selected_topic]
    
    # Main content area
    if topic_key == "home":
        show_home_page()
    elif topic_key == "equations":
        show_accounting_equations()
    elif topic_key == "journal":
        show_journal_entries()
    elif topic_key == "gst":
        show_gst_calculator()

def show_home_page():
    st.markdown("---")
    
    # Welcome section
    st.markdown("""
    ## Welcome to Your AI Accounting Assistant! 🎓
    
    This comprehensive tool helps you solve and understand various Indian accounting concepts with step-by-step explanations.
    """)
    
    # Features grid
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 📐 Accounting Equations
        - Solve basic accounting equations
        - Asset = Liability + Capital
        - Step-by-step working
        
        ### 💰 GST Calculator
        - CGST + SGST (Intrastate)
        - IGST (Interstate)
        - Rate-wise calculations
        """)
    
    with col2:
        st.markdown("""
        ### 📝 Journal Entries
        - Opening entries
        - Adjustment entries
        - Rectification entries
        - Closing entries
        """)
    
    with col3:
        st.markdown("""
        ### 🎯 Educational Focus
        - CBSE Class 11-12 curriculum
        - CA Foundation preparation
        - Step-by-step explanations
        - Indian accounting standards
        """)
    
    st.markdown("---")
    
    # Quick start guide
    st.markdown("""
    ## 🚀 Quick Start Guide
    
    1. **Select a topic** from the sidebar menu
    2. **Fill in the required details** in the form
    3. **Click Calculate/Solve** to get step-by-step solutions
    4. **Export results** as needed for your studies
    
    All solutions follow **CBSE/ICAI format** with proper Indian accounting standards.
    """)
    
    # Sample problems section
    with st.expander("📚 Sample Problems Available"):
        st.markdown("""
        - **Accounting Equations**: Find missing values in A = L + C
        - **Journal Entries**: Record business transactions properly
        - **GST Calculations**: Calculate tax for different scenarios
        """)

if __name__ == "__main__":
    main()
