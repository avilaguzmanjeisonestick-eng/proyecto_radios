# ui/styles.py

STYLESHEET = """
/* --- ESTILOS GLOBALES --- */
QWidget {
    background-color: #f8fafc;
    font-family: "Segoe UI", Arial, sans-serif;
    color: #172033;
}

/* --- RECUADRO DE USUARIO EN EL SIDEBAR --- */
#user_frame {
    background-color: #00276e; /* Azul un poco más oscuro */
    border: 1px solid #dfff00; /* Margen delgado amarillo */
    border-radius: 4px;
    margin: 0px 15px 15px 15px;
}
#user_label {
    color: white;
    font-weight: bold;
    font-size: 15px;
    background: transparent;
    border: none;
}
#role_label {
    color: #a8bad6;
    font-size: 11px;
    background: transparent;
    border: none;
}

/* --- MENÚ LATERAL (SIDEBAR) --- */
#sidebar { 
    background-color: #003087; 
    color: white; 
}

/* Botones inactivos: rellenos de gris claro, letra negra */
#sidebar QPushButton {
    color: #334155; 
    background-color: #e2e8f0; 
    text-align: left;
    padding: 10px 15px; 
    font-size: 14px; 
    border: none; 
    margin: 4px 15px;
    border-radius: 4px;
}

/* Botones al pasar el mouse */
#sidebar QPushButton:hover { 
    background-color: #cbd5e1; 
}

/* Botón activo: Relleno con color neón, letra negra */
#sidebar QPushButton[active="true"] {
    background-color: #dfff00; 
    color: black; 
    font-weight: bold;
}

/* --- BARRA SUPERIOR --- */
#topbar { 
    background-color: white; 
    border-bottom: 1px solid #e2e8f0; 
}
#page_title { 
    font-size: 18px; 
    font-weight: bold; 
    color: #172033; 
}

/* --- TABLAS --- */
QTableWidget {
    background-color: white; 
    border: 1px solid #e2e8f0;
    border-radius: 4px; 
    font-size: 13px;
    gridline-color: #f1f5f9;
}
QHeaderView::section {
    background-color: #f8fafc; 
    padding: 8px;
    font-weight: bold; 
    color: #475569;
    border: none; 
    border-bottom: 1px solid #e2e8f0;
}

/* --- BOTONES PRINCIPALES --- */
#primary_btn {
    background-color: #dfff00; 
    color: black; 
    border-radius: 4px;
    padding: 10px 20px; 
    font-weight: bold;
    border: none;
}
#primary_btn:hover { 
    background-color: #cbe600; 
}

/* --- PANTALLA DE LOGIN --- */
#login_bg { background-color: #003087; }
#login_card { background-color: white; border-radius: 8px; padding: 40px; }
#login_title { font-size: 22px; font-weight: bold; color: #10213c; }
#login_btn {
    background-color: #dfff00; color: black; border-radius: 4px;
    padding: 12px; font-weight: bold; font-size: 14px; border: none;
}
#login_btn:hover { background-color: #cbe600; }
QLineEdit {
    padding: 10px; border: 1px solid #cbd5e1; border-radius: 4px;
    background-color: white; font-size: 13px;
}
QLineEdit:focus { border: 1px solid #003087; }

/* --- BARRAS DE PROGRESO (Dashboard) --- */
QProgressBar {
    background-color: #f1f5f9;
    border: none;
    border-radius: 3px;
}
QProgressBar::chunk {
    border-radius: 3px;
}
"""