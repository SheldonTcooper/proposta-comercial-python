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
        valor = request.form.get("valor", "").strip()
        taxa = request.form.get("taxa", "").strip()

        # Remover "R$" e "%" caso já estejam na entrada do usuário
        valor_corrigido = valor.replace("R$", "").strip()
        taxa_corrigida = taxa.replace("%", "").strip()

        # Verificar se a imagem foi enviada
        if 'foto_consultor' not in request.files:
            return "❌ Erro: Nenhuma foto foi enviada.", 400

        foto = request.files['foto_consultor']
        if foto.filename == "":
            return "❌ Erro: Nenhuma foto foi enviada.", 400

        # Salvar a foto do consultor
        foto_path = os.path.join(app.config['UPLOAD_FOLDER'], foto.filename)
        foto.save(foto_path)

        # Verificar se o arquivo de imagem é válido
        try:
            img = Image.open(foto_path)
            img.verify()  # Verifica se a imagem é válida
        except Exception:
            os.remove(foto_path)  # Remove a imagem corrompida
            return "❌ Erro: O arquivo enviado não é uma imagem válida.", 400

        # Criar a primeira página do PDF
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # Adicionar a logo
        logo_path = "static/logo.png"
        if os.path.exists(logo_path):
            pdf.image(logo_path, x=10, y=10, w=190)

        # Título
        pdf.set_font("Arial", "B", 16)
        pdf.ln(50)
        pdf.cell(200, 10, "Proposta Comercial de Conta Vinculada", ln=True, align='C')

        # Informações principais
        pdf.set_font("Arial", size=12)
        pdf.ln(10)
        pdf.cell(200, 10, f"Consultor: {consultor}", ln=True)
        pdf.cell(200, 10, f"Telefone: {telefone} | E-mail: {email}", ln=True)
        pdf.cell(200, 10, f"Cliente: {cliente}", ln=True)
        pdf.cell(200, 10, f"Telefone do Cliente: {telefone_cliente} | E-mail: {email_cliente}", ln=True)
        pdf.cell(200, 10, f"Descrição: {descricao}", ln=True)
        pdf.cell(200, 10, f"Valor: R$ {valor_corrigido} | Taxa: {taxa_corrigida}%", ln=True)

        # Adicionar a foto do consultor no rodapé
        pdf.ln(20)
        if os.path.exists(foto_path):
            pdf.image(foto_path, x=80, y=220, w=50)

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
