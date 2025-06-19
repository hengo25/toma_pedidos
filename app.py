from flask import Flask, render_template, request, redirect, url_for, send_file, send_from_directory
from datetime import datetime
import csv, os
from fpdf import FPDF

app = Flask(__name__)

CLIENTES_CSV = 'clientes.csv'
PRODUCTOS_CSV = 'productos.csv'

def leer_csv(name):
    if not os.path.exists(name):
        return []
    with open(name, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def escribir_csv(name, data, headers):
    with open(name, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)

@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json', mimetype='application/manifest+json')

@app.route('/sw.js')
def sw():
    return send_from_directory('static', 'sw.js', mimetype='application/javascript')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/clientes')
def ver_clientes():
    clientes = leer_csv(CLIENTES_CSV)
    return render_template('clientes.html', clientes=clientes)

@app.route('/clientes/agregar', methods=['POST'])
def agregar_cliente():
    nombre = request.form['nombre']
    clientes = leer_csv(CLIENTES_CSV)
    nuevos = len(clientes) + 1
    clientes.append({'id': str(nuevos), 'nombre': nombre})
    escribir_csv(CLIENTES_CSV, clientes, ['id', 'nombre'])
    return redirect(url_for('ver_clientes'))

@app.route('/clientes/eliminar/<id>', methods=['POST'])
def eliminar_cliente(id):
    clientes = [c for c in leer_csv(CLIENTES_CSV) if c['id'] != id]
    escribir_csv(CLIENTES_CSV, clientes, ['id', 'nombre'])
    return redirect(url_for('ver_clientes'))

@app.route('/productos')
def ver_productos():
    productos = leer_csv(PRODUCTOS_CSV)
    return render_template('productos.html', productos=productos)

@app.route('/productos/agregar', methods=['POST'])
def agregar_producto():
    nombre = request.form['nombre']
    p1 = request.form['precio1']
    p2 = request.form['precio2']
    productos = leer_csv(PRODUCTOS_CSV)
    nuevos = len(productos) + 1
    productos.append({'id': str(nuevos), 'nombre': nombre, 'precio1': p1, 'precio2': p2})
    escribir_csv(PRODUCTOS_CSV, productos, ['id', 'nombre', 'precio1', 'precio2'])
    return redirect(url_for('ver_productos'))

@app.route('/productos/eliminar/<id>', methods=['POST'])
def eliminar_producto(id):
    productos = [p for p in leer_csv(PRODUCTOS_CSV) if p['id'] != id]
    escribir_csv(PRODUCTOS_CSV, productos, ['id', 'nombre', 'precio1', 'precio2'])
    return redirect(url_for('ver_productos'))

@app.route('/toma_pedidos', methods=['GET', 'POST'])
def toma_pedidos():
    clientes = leer_csv(CLIENTES_CSV)
    productos = leer_csv(PRODUCTOS_CSV)
    pedido, total = [], 0
    cliente_sel, fecha, obs = '', '', ''

    if request.method == 'POST':
        cliente_id = request.form['cliente']
        obs = request.form.get('observaciones', '')
        fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for pid, cant, tipo in zip(
            request.form.getlist('producto[]'),
            request.form.getlist('cantidad[]'),
            request.form.getlist('precio[]')
        ):
            if not pid:
                continue
            prod = next(p for p in productos if p['id'] == pid)
            cantidad = int(cant)
            precio = float(prod[tipo])
            subtotal = cantidad * precio
            pedido.append({
                'producto': prod['nombre'],
                'cantidad': cantidad,
                'precio': precio,
                'subtotal': subtotal
            })
            total += subtotal

        cliente_sel = next(c['nombre'] for c in clientes if c['id'] == cliente_id)

        class PDF(FPDF):
            def header(self):
                self.image('static/img.jpeg', 10, 8, 30)
                self.set_font('Arial', 'B', 12)
                self.cell(0, 10, 'DETALLE PEDIDO', border=0, ln=True, align='C')
                self.ln(10)

            def footer(self):
                self.set_y(-15)
                self.set_font('Arial', 'I', 8)
                self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

        pdf = PDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 8, f'Cliente: {cliente_sel}', ln=True)
        pdf.cell(0, 8, f'Fecha: {fecha}', ln=True)
        pdf.multi_cell(0, 8, f'Observaciones: {obs}')
        pdf.ln(5)

        pdf.set_fill_color(230, 230, 250)
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(80, 8, 'Producto', 1, 0, 'C', fill=True)
        pdf.cell(20, 8, 'Cant', 1, 0, 'C', fill=True)
        pdf.cell(40, 8, 'Precio', 1, 0, 'C', fill=True)
        pdf.cell(40, 8, 'Subtotal', 1, 1, 'C', fill=True)

        pdf.set_font('Arial', '', 10)
        for item in pedido:
    # Verificar si estamos cerca del final de la página
            if pdf.get_y() > 260:  # Aproximadamente cerca del margen inferior
                pdf.add_page()
                # Repetir encabezado de tabla
                pdf.set_fill_color(230, 230, 250)
                pdf.set_font('Arial', 'B', 11)
                pdf.cell(80, 8, 'Producto', 1, 0, 'C', fill=True)
                pdf.cell(20, 8, 'Cant', 1, 0, 'C', fill=True)
                pdf.cell(40, 8, 'Precio', 1, 0, 'C', fill=True)
                pdf.cell(40, 8, 'Subtotal', 1, 1, 'C', fill=True)
                pdf.set_font('Arial', '', 10)

            # Dibujar fila con multílinea
            x = pdf.get_x()
            y = pdf.get_y()
            pdf.multi_cell(80, 8, item['producto'], border=1)
            height = pdf.get_y() - y
            pdf.set_xy(x + 80, y)
            pdf.cell(20, height, str(item['cantidad']), border=1, align='C')
            pdf.cell(40, height, f"{item['precio']:.2f}", border=1, align='C')
            pdf.cell(40, height, f"{item['subtotal']:.2f}", border=1, ln=True, align='C')


           # TOTAL FINAL
        pdf.set_font('Arial', 'B', 12)
        pdf.ln(5)
        pdf.cell(140, 10, 'TOTAL', border=1, align='R')
        pdf.cell(40, 10, f"${total:,.0f}", border=1, ln=True, align='R')   

        pdf.output('pedido.pdf')

        return render_template('toma_pedidos.html',
            clientes=clientes, productos=productos,
            pedido=pedido, total=total,
            cliente=cliente_sel, fecha=fecha,
            observaciones=obs, mostrar_pdf=True)

    return render_template('toma_pedidos.html', clientes=clientes, productos=productos)

@app.route('/descarga_pedido')
def descarga_pedido():
    return send_file('pedido.pdf', as_attachment=True, mimetype='application/pdf')

if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0', port=5000)