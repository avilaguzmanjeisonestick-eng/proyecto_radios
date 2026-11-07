# ui/styles.py
STYLESHEET = """
QWidget {
    background-color: #f3f5f8;
    font-family: "Segoe UI", Arial, sans-serif;
    color: #172033;
}
#login_bg { background-color: #003087; }
#login_card { background-color: white; border-radius: 8px; padding: 40px; }
#login_title { font-size: 22px; font-weight: bold; color: #10213c; }
#login_btn {
    background-color: #003087; color: white; border-radius: 4px;
    padding: 12px; font-weight: bold; font-size: 14px;
}
#login_btn:hover { background-color: #00276e; }
QLineEdit {
    padding: 10px; border: 1px solid #d5dbe5; border-radius: 4px;
    background-color: white; font-size: 13px;
}
QLineEdit:focus { border: 1px solid #003087; }
#sidebar { background-color: #003087; color: white; }
#sidebar QPushButton {
    color: #c7d3e7; background-color: transparent; text-align: left;
    padding: 15px; font-size: 14px; border: none;
}
#sidebar QPushButton:hover { background-color: rgba(255, 255, 255, 0.1); color: white; }
#sidebar QPushButton[active="true"] {
    background-color: rgba(255, 255, 255, 0.15); color: white;
    border-left: 4px solid #dfff00; font-weight: bold;
}
#topbar { background-color: white; border-bottom: 1px solid #e1e5eb; }
#page_title { font-size: 18px; font-weight: bold; color: #172033; }
QTableWidget {
    background-color: white; border: 1px solid #e1e5eb;
    border-radius: 4px; font-size: 13px;
}
QHeaderView::section {
    background-color: #f7f8fa; padding: 8px;
    font-weight: bold; border: none; border-bottom: 1px solid #e1e5eb;
}
#primary_btn {
    background-color: #003087; color: white; border-radius: 4px;
    padding: 10px 20px; font-weight: bold;
}
#primary_btn:hover { background-color: #00276e; }
"""