from flask import Flask, render_template, request, send_file
from fpdf import FPDF
import os
import sqlite3
from datetime import datetime
from PyPDF2 import PdfMerger
from PIL import Image

app = Flask(__name__)

# Diretório de upload e PDF
UPLOAD_FOLDER = 'static/uploads'
PDF_FOLDER = 'pdfs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PDF_FOLDER'] = PDF_FOLDER

# Criar diretórios se não existirem
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PDF_FOLDER, exist_ok=True)

# Texto padrão fixo da proposta
TEXTO_PADRAO = """
Em atenção à sua solicitação, temos o prazer de apresentar a presente proposta da CONTA ESCROW
TESOURARIA©VINCULADA, uma conta bancária de sua titularidade operada em instituição financeira parceira, 
do tipo escrow account, com diversas funções interessantes e exclusivas da TAURI SECURITIZADORA...
"""

# Função para conectar ao banco de dados
def conectar_banco():
    conn = sqlite3.connect('banco.db')
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    try:
        # Captura os dados do formulário
        consultor = request.form.get("consultor", "").strip()
        telefone = request.form.get("telefone", "").strip()
        email = request.form.get("email", "").strip()
        cliente = request.form.get("cliente", "").strip()
        telefone_cliente = request.form.get("telefone_cliente", "").strip()
        email_cliente = request.form.get("email_cliente", "").strip()
        descricao = request.form.get("descricao", "").strip()
        valor = request.form.get("valor", "").strip()
        taxa = request.form.get("taxa", "").strip()

        # Verifica se a imagem foi enviada
        foto = request.files.get('foto_consultor')
        foto_path = "static/uploads/default.jpg"  # Imagem padrão

        if foto and foto.filename:
            foto_path = os.path.join(app.config['UPLOAD_FOLDER'], foto.filename)
            foto.save(foto_path)

            # Verifica se a imagem é válida
            try:
                img = Image.open(foto_path)
                img.verify()
            except Exception:
                os.remove(foto_path)
                foto_path = "static/uploads/default.jpg"

        # Criar a primeira página do PDF com os dados
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # Adicionar a logo destacada
        logo_path = "static/logo.png"
        if os.path.exists(logo_path):
            pdf.image(logo_path, x=70, y=10, w=70)

        # Título
        pdf.set_font("Arial", "B", 16)
        pdf.ln(50)
        pdf.cell(200, 10, "Proposta Comercial de Conta Vinculada", ln=True, align='C')

        # Informações da proposta
        pdf.set_font("Arial", size=12)
        pdf.ln(10)
        pdf.cell(200, 10, f"Consultor: {consultor}", ln=True)
        pdf.cell(200, 10, f"Telefone: {telefone} | E-mail: {email}", ln=True)
        pdf.cell(200, 10, f"Cliente: {cliente}", ln=True)
        pdf.cell(200, 10, f"Telefone do Cliente: {telefone_cliente} | E-mail: {email_cliente}", ln=True)
        pdf.cell(200, 10, f"Valor: R$ {valor} | Taxa: {taxa}%", ln=True)

        # Adicionar a descrição em um box organizado
        pdf.ln(5)
        pdf.set_fill_color(230, 230, 230)  # Cinza claro
        pdf.multi_cell(190, 10, f"Descrição da Negociação:\n{descricao}", border=1, fill=True)

        # Adicionar texto fixo separado e formatado
        pdf.ln(10)
        pdf.set_font("Arial", "I", 10)
        pdf.multi_cell(190, 7, TEXTO_PADRAO, border=1)

        # Adicionar a foto do consultor
        pdf.ln(10)
        if os.path.exists(foto_path):
            pdf.image(foto_path, x=80, y=230, w=50)

        # Salvar PDF da primeira página
        pdf_cadastro_path = os.path.join(app.config['PDF_FOLDER'], "proposta_cadastro.pdf")
        pdf.output(pdf_cadastro_path)

        # Caminho do PDF padrão
        pdf_padrao_path = os.path.join(app.config['PDF_FOLDER'], "proposta_padrao.pdf")
        if not os.path.exists(pdf_padrao_path):
            return "❌ Erro: O arquivo da proposta padrão não foi encontrado.", 400

        # Unificar os PDFs
        pdf_final_path = os.path.join(app.config['PDF_FOLDER'], "proposta_comercial_unificada.pdf")
        merger = PdfMerger()
        merger.append(pdf_cadastro_path)
        merger.append(pdf_padrao_path)
        merger.write(pdf_final_path)
        merger.close()

        # Salvar a proposta no banco com contador por consultor
        conn = conectar_banco()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO propostas (consultor, cliente, descricao, data) VALUES (?, ?, ?, ?)", 
                       (consultor, cliente, descricao, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        conn.close()

        # Retornar o arquivo final
        return send_file(pdf_final_path, as_attachment=True)

    except Exception as e:
        return f"❌ Erro interno: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)
