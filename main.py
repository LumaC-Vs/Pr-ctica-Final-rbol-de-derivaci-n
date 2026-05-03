import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import nltk
from nltk import CFG

class Gramatica:
    def __init__(self, texto):
        self.texto = texto
        self.cfg = CFG.fromstring(texto)

class Derivador:
    def __init__(self, gramatica):
        self.gramatica = gramatica
        self.parser = nltk.ChartParser(gramatica.cfg)

    def obtener_arboles(self, expresion):
        tokens = [t for t in list(expresion) if t.strip()]
        arboles = list(self.parser.parse(tokens))
        return arboles

    def obtener_derivacion(self, arbol, direccion='izquierda'):
        pasos = []
        producciones = arbol.productions()
        if direccion == 'derecha':
            producciones = list(reversed(producciones))
        for produccion in producciones:
            pasos.append(f"{produccion.lhs()} -> {' '.join(str(s) for s in produccion.rhs())}")
        return pasos

    def obtener_ast(self, arbol):
        def simplificar(subarbol):
            if isinstance(subarbol, str):
                return subarbol
            if len(subarbol) == 1:
                return simplificar(subarbol[0])
            hijos = [simplificar(h) for h in subarbol]
            return nltk.Tree(str(subarbol.label()), hijos)
        return simplificar(arbol)

class AppVentana(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Generador de Árboles Sintácticos")
        self.setMinimumSize(1100, 650)
        self.arboles = []
        self.derivador = None
        self.initUI()

    def initUI(self):
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        layout_principal = QHBoxLayout(widget_central)

        # Panel izquierdo
        panel_izq = QVBoxLayout()
        layout_principal.addLayout(panel_izq, 2)

        gramatica_default = (
            "E -> E '+' T | E '-' T | T\n"
            "T -> T '*' F | T '/' F | F\n"
            "F -> '(' E ')' | '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9' | 'a' | 'b' | 'c' | 'd' | 'e' | 'f' | 'g' | 'h' | 'i' | 'j' | 'k' | 'l' | 'm' | 'n' | 'o' | 'p' | 'q' | 'r' | 's' | 't' | 'u' | 'v' | 'w' | 'x' | 'y' | 'z'"
        )

        self.texto_gramatica = QTextEdit()
        self.texto_gramatica.setText(gramatica_default)
        self.texto_gramatica.setMaximumHeight(220)
        panel_izq.addWidget(QLabel("Gramática:"))
        panel_izq.addWidget(self.texto_gramatica)

        self.texto_expresion = QLineEdit()
        self.texto_expresion.setPlaceholderText("Ejemplo: (5*x)+y")
        panel_izq.addWidget(QLabel("Expresión:"))
        panel_izq.addWidget(self.texto_expresion)

        panel_izq.addWidget(QLabel("Opciones de Derivación:"))
        self.radio_izq = QRadioButton("Derivación por la Izquierda")
        self.radio_der = QRadioButton("Derivación por la Derecha")
        self.radio_izq.setChecked(True)
        panel_izq.addWidget(self.radio_izq)
        panel_izq.addWidget(self.radio_der)

        boton = QPushButton("Generar Derivación")
        boton.clicked.connect(self.generar)
        panel_izq.addWidget(boton)

        boton_ast = QPushButton("Mostrar AST")
        boton_ast.clicked.connect(self.mostrar_ast)
        panel_izq.addWidget(boton_ast)

        panel_izq.addStretch()

        # Panel central
        panel_centro = QVBoxLayout()
        layout_principal.addLayout(panel_centro, 3)
        self.resultado = QTextEdit()
        self.resultado.setReadOnly(True)
        panel_centro.addWidget(QLabel("Derivación Paso a Paso:"))
        panel_centro.addWidget(self.resultado)

        # Panel derecho
        panel_der = QVBoxLayout()
        layout_principal.addLayout(panel_der, 2)
        boton_arbol = QPushButton("Ver Árbol de Derivación")
        boton_arbol.clicked.connect(self.mostrar_arbol)
        panel_der.addWidget(boton_arbol)
        panel_der.addStretch()

    def generar(self):
        try:
            gramatica = Gramatica(self.texto_gramatica.toPlainText())
            self.derivador = Derivador(gramatica)
            expresion = self.texto_expresion.text().strip()
            self.arboles = self.derivador.obtener_arboles(expresion)

            if not self.arboles:
                self.resultado.setText("No se encontró derivación para esa expresión.")
                return

            direccion = 'izquierda' if self.radio_izq.isChecked() else 'derecha'
            pasos = self.derivador.obtener_derivacion(self.arboles[0], direccion)

            texto = f"Derivación por la {direccion}:\n\n"
            for i, paso in enumerate(pasos):
                texto += f"  => {paso}\n"
            self.resultado.setText(texto)

        except Exception as e:
            self.resultado.setText(f"Error: {str(e)}")

    def mostrar_arbol(self):
        if not self.arboles:
            self.resultado.setText("Primero genera una derivación.")
            return
        self.arboles[0].draw()

    def mostrar_ast(self):
        if not self.arboles:
            self.resultado.setText("Primero genera una derivación.")
            return
        ast = self.derivador.obtener_ast(self.arboles[0])
        if isinstance(ast, nltk.Tree):
            ast.draw()
        else:
            self.resultado.setText(f"AST: {ast}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = AppVentana()
    ventana.show()
    sys.exit(app.exec())