from flask import Flask, render_template, request, send_file
from fpdf import FPDF
import os
from PyPDF2 import PdfMerger
from PIL import Image

app = Flask(__name__)

# Diretórios de upload e PDFs
UPLOAD_FOLDER = 'static/uploads'
PDF_FOLDER = 'pdfs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PDF_FOLDER'] = PDF_FOLDER

# Caminho da foto padrão do consultor
FOTO_PADRAO = os.path.join(app.config['UPLOAD_FOLDER'], "foto_padrao.jpg")

# Criar diretórios se não existirem
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PDF_FOLDER, exist_ok=True)

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
        valor = request.form.get("valor", "").strip().replace("R$ ", "")
        taxa = request.form.get("taxa", "").strip().replace("%", "")

        # Verificar se o vendedor enviou uma foto personalizada
        foto = request.files.get("foto_consultor")
        if foto and foto.filename != "":
            foto_path = os.path.join(app.config['UPLOAD_FOLDER'], foto.filename)
            foto.save(foto_path)

            # Verificar se a imagem é válida
            try:
                img = Image.open(foto_path)
                img.verify()
            except Exception:
                os.remove(foto_path)
                return "❌ Erro: O arquivo enviado não é uma imagem válida.", 400
        else:
            # Se nenhuma foto foi enviada, usa a foto padrão
            foto_path = FOTO_PADRAO if os.path.exists(FOTO_PADRAO) else None

        # Criar o PDF
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # Adicionar a logo maior e destacada no cabeçalho
        logo_path = "static/logo.png"
        if os.path.exists(logo_path):
            pdf.image(logo_path, x=50, y=10, w=100)  # Ajustado para centralizar e aumentar o tamanho

        # Adicionar título destacado
        pdf.set_font("Arial", "B", 18)
        pdf.ln(35)  # Ajusta o espaçamento
        pdf.cell(200, 10, "Proposta Comercial de Conta Vinculada", ln=True, align='C')

        # Informações principais
        pdf.set_font("Arial", size=12)
        pdf.ln(10)
        pdf.cell(200, 10, f"Consultor: {consultor}", ln=True)
        pdf.cell(200, 10, f"Telefone: {telefone} | E-mail: {email}", ln=True)
        pdf.cell(200, 10, f"Cliente: {cliente}", ln=True)
        pdf.cell(200, 10, f"Telefone do Cliente: {telefone_cliente} | E-mail: {email_cliente}", ln=True)
        pdf.cell(200, 10, f"Descrição: {descricao}", ln=True)
        pdf.cell(200, 10, f"Valor: R$ {valor} | Taxa: {taxa}%", ln=True)

        # Adicionar a foto do consultor no rodapé esquerdo
        if foto_path and os.path.exists(foto_path):
            pdf.image(foto_path, x=10, y=240, w=40)

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

        # Retornar o arquivo final
        return send_file(pdf_final_path, as_attachment=True)

    except Exception as e:
        return f"❌ Erro interno: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)
