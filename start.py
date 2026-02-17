from flask import Flask, request, redirect, url_for, send_file, flash, render_template
from fpdf import FPDF
from random import choice
import qrcode
import socket
import io
from datetime import datetime

app = Flask(__name__)
app.secret_key = "XONIDU-Darian_Alberto_Camacho_Salas"

# Inicialización de las listas globales
list_p = []
list_d = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
list_c = []
list_l = []

def get_server_ip():
    """Obtiene la dirección IP del servidor"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        try:
            s.connect(('10.254.254.254', 1))
            ip = s.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip
    except Exception:
        return '127.0.0.1'

def generate_terminal_qr(url):
    """Genera un código QR en ASCII para la terminal"""
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=2,
            border=1,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        qr_text = qr.get_matrix()
        ascii_qr = ""
        for row in qr_text:
            for pixel in row:
                if pixel:
                    ascii_qr += "██"
                else:
                    ascii_qr += "  "
            ascii_qr += "\n"
        
        return ascii_qr
    except Exception:
        return ""

class ElegantPDF(FPDF):
    def __init__(self):
        super().__init__()
    
    def header(self):
        self.set_font('Arial', 'B', 24)
        self.set_text_color(102, 126, 234)
        self.cell(0, 20, 'CITA GENERADA - XONIDU', 0, 1, 'C')
        self.ln(5)
        
        self.set_draw_color(102, 126, 234)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(10)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Pagina ' + str(self.page_no()), 0, 0, 'C')
    
    def add_gradient_background(self):
        self.set_fill_color(240, 245, 255)
        self.rect(0, 0, 210, 297, 'F')
    
    def chapter_title(self, label):
        self.set_font('Arial', 'B', 16)
        self.set_text_color(102, 126, 234)
        self.set_fill_color(240, 245, 255)
        self.cell(0, 10, label, 0, 1, 'L', True)
        self.ln(4)
    
    def add_info_card(self, title, content):
        self.set_fill_color(255, 255, 255)
        self.set_draw_color(220, 220, 220)
        self.set_line_width(0.3)
        
        y = self.get_y()
        self.rect(10, y, 190, 20, 'DF')
        
        self.set_font('Arial', 'B', 12)
        self.set_text_color(102, 126, 234)
        self.set_xy(15, y + 5)
        self.cell(40, 10, title, 0, 0, 'L')
        
        self.set_font('Arial', '', 12)
        self.set_text_color(30, 30, 30)
        self.set_xy(60, y + 5)
        self.cell(0, 10, content, 0, 1, 'L')
        
        self.set_y(y + 25)
    
    def add_attendants_list(self, attendants):
        self.chapter_title("ASISTENTES")
        self.set_font('Arial', '', 12)
        self.set_text_color(50, 50, 50)
        
        for i, person in enumerate(attendants, 1):
            self.cell(10, 8, f"{i}.", 0, 0, 'L')
            self.cell(0, 8, person, 0, 1, 'L')
        
        self.ln(10)

@app.route("/", methods=["GET", "POST"])
def index():
    global list_p, list_d, list_c, list_l
    
    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "add_person":
            person = request.form.get("person", "").strip()
            if person and person not in list_p:
                list_p.append(person)
                flash(f"✅ Asistente '{person}' agregado exitosamente")
        
        elif action == "remove_day":
            day = request.form.get("day")
            if day in list_d:
                list_d.remove(day)
                flash(f"❌ Día '{day}' eliminado de las opciones")
        
        elif action == "add_food":
            food = request.form.get("food", "").strip()
            if food and food not in list_c:
                list_c.append(food)
                flash(f"🍴 Comida '{food}' agregada exitosamente")
        
        elif action == "add_place":
            place = request.form.get("place", "").strip()
            if place and place not in list_l:
                list_l.append(place)
                flash(f"🏙️ Lugar '{place}' agregado exitosamente")
        
        elif action == "generate":
            if not list_d:
                flash("⚠️ No hay días disponibles para generar la cita")
                return redirect(url_for("index"))
            
            if not list_p:
                flash("⚠️ Agrega al menos un asistente antes de generar")
                return redirect(url_for("index"))
            
            dia = choice(list_d)
            comida = choice(list_c) if list_c else "Por definir"
            lugar = choice(list_l) if list_l else "Por definir"
            
            # Generar PDF en memoria
            pdf_data = generate_pdf_in_memory(dia, comida, lugar, list_p)
            
            # Limpiar listas después de generar
            list_p = []
            list_d = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
            list_c = []
            list_l = []
            
            flash("🎉 ¡Cita generada exitosamente! Descarga tu PDF")
            
            return send_file(
                pdf_data,
                as_attachment=True,
                download_name=f"cita_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mimetype='application/pdf'
            )
        
        return redirect(url_for("index"))
    
    server_ip = get_server_ip()
    port = request.environ.get('SERVER_PORT', 5000)
    server_url = f"http://{server_ip}:{port}"
    
    return render_template('index.html',
                         list_p=list_p,
                         list_d=list_d,
                         list_c=list_c,
                         list_l=list_l,
                         server_url=server_url)

def generate_pdf_in_memory(dia, comida, lugar, asistentes):
    """Genera un PDF en memoria sin guardarlo en disco"""
    pdf = ElegantPDF()
    pdf.add_page()
    pdf.add_gradient_background()
    
    pdf.set_font('Arial', 'B', 24)
    pdf.set_text_color(102, 126, 234)
    pdf.cell(0, 20, "TU CITA HA SIDO GENERADA", 0, 1, 'C')
    pdf.ln(5)
    
    pdf.set_font('Arial', 'I', 10)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 10, f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", 0, 1, 'C')
    pdf.ln(15)
    
    pdf.add_info_card("DIA:", dia)
    pdf.add_info_card("LUGAR:", lugar)
    pdf.add_info_card("COMIDA:", comida)
    
    pdf.add_attendants_list(asistentes)
    
    pdf.set_draw_color(102, 126, 234)
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)
    
    pdf.set_font('Arial', 'I', 12)
    pdf.set_text_color(102, 126, 234)
    pdf.multi_cell(0, 10, "¡Disfruta de este encuentro especial! Que sea memorable y lleno de buenos momentos.", 0, 'C')
    
    pdf.ln(15)
    pdf.set_font('Arial', '', 9)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(0, 6, "Generado automaticamente por XONIDU - Generador de Citas\n"
                        "Organiza tus encuentros sociales de forma facil y divertida", 0, 'C')
    
    # Generar PDF en memoria
    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    return io.BytesIO(pdf_bytes)

def display_terminal_info():
    """Muestra información en la terminal al iniciar"""
    server_ip = get_server_ip()
    port = 5000
    server_url = f"http://{server_ip}:{port}"
    
    print("\n" + "="*60)
    print("🎉 GENERADOR DE CITAS XONIDU")
    print("="*60)
    print("Organiza tus encuentros sociales de forma fácil y divertida")
    print("="*60)
    print(f"\n🌐 URL Local:  http://127.0.0.1:{port}/")
    print(f"🌐 URL Red:    {server_url}/")
    print("\n📱 Código QR para acceso rápido desde tu teléfono:")
    print("="*60)
    
    qr_ascii = generate_terminal_qr(server_url)
    if qr_ascii:
        print(qr_ascii)
        print("Escanea este código QR con la cámara de tu teléfono")
    else:
        print("(Ejecuta 'pip install qrcode' para ver el código QR)")
    
    print("="*60)
    print("\n💡 Características:")
    print("  • ✅ Añade asistentes por nombre")
    print("  • 📅 Elimina días no disponibles")
    print("  • 🍕 Sugiere comidas")
    print("  • 🏙️ Propone lugares")
    print("  • 🎯 Genera citas aleatorias")
    print("  • 📄 Crea PDFs elegantes (sin guardar en servidor)")
    print("  • 🔄 Reinicio automático después de cada generación")
    print("="*60)
    print("\nPresiona Ctrl+C para detener el servidor\n")

if __name__ == "__main__":
    display_terminal_info()
    app.run(host='0.0.0.0', port=5000, debug=True)
