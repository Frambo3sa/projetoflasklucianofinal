
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'LULUEOMELHOR'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class Cliente(db.Model, UserMixin):  
    id = db.Column(db.Integer, primary_key=True)
    nomeusu = db.Column(db.String(150), unique=True, nullable=False)  
    senha = db.Column(db.String(150), nullable=False)  
    listausu = db.relationship('ListaCompra', backref='owner', lazy=True)

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    desc = db.Column(db.String(300), nullable=False)
    estoque = db.Column(db.Integer, nullable=False)

class ListaCompra(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_usu = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    product = db.relationship('Produto', backref='lista_compras')

class Funcionario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nomeusu = db.Column(db.String(150), unique=True, nullable=False)
    senha = db.Column(db.String(150), nullable=False)
    lista_funcao = db.relationship('FuncionarioFuncao', backref='funcionario', lazy=True)

class Funcao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    descricao = db.Column(db.String(300), nullable=False)
    salario = db.Column(db.Float, nullable=False)
    horas_por_dia = db.Column(db.Integer, nullable=False)
    vagas = db.Column(db.Integer, nullable=False)
    funcionarios = db.relationship('FuncionarioFuncao', backref='funcao', lazy=True)

class FuncionarioFuncao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    funcionario_id = db.Column(db.Integer, db.ForeignKey('funcionario.id'), nullable=False)
    funcao_id = db.Column(db.Integer, db.ForeignKey('funcao.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    user = Cliente.query.get(int(user_id))
    if user is None:
        user = Funcionario.query.get(int(user_id))
    return user

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        nomeusu = request.form['nomeusu']
        senha = request.form['senha']
        hashed_password = generate_password_hash(senha)  
        new_user = Cliente(nomeusu=nomeusu, senha=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('registrar.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nomeusu = request.form['nomeusu']
        senha = request.form['senha']

       
        if nomeusu == "massachefe" and senha == "1234":
            funcionario = Funcionario.query.filter_by(nomeusu=nomeusu).first()
            if funcionario:
                login_user(funcionario)
                flash('Login bem-sucedido como massachefe!', 'success')
                return redirect(url_for('admin'))
            else:
                flash('Funcionário não encontrado.', 'danger')

        cliente = Cliente.query.filter_by(nomeusu=nomeusu).first()
        if cliente and check_password_hash(cliente.senha, senha):
            login_user(cliente)
            return redirect(url_for('pagusuario'))
        
        funcionario = Funcionario.query.filter_by(nomeusu=nomeusu).first()
        if funcionario and check_password_hash(funcionario.senha, senha):
            login_user(funcionario)
            return redirect(url_for('funcionario_page'))
        
        flash('Login não bem-sucedido. Verifique nome de usuário e senha', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if request.method == 'POST':
       
        if 'adicionar_produto' in request.form:
            nome = request.form['nome']
            preco = request.form['preco']
            desc = request.form['desc']
            estoque = request.form['estoque']
            new_product = Produto(nome=nome, preco=preco, desc=desc, estoque=estoque)
            db.session.add(new_product)
            db.session.commit()
            flash('Produto adicionado com sucesso!', 'success')
            return redirect(url_for('admin'))
        
       
        if 'adicionar_funcao' in request.form:
            nome = request.form['nome_funcao']
            descricao = request.form['descricao']
            salario = request.form['salario']
            horas_por_dia = request.form['horas_por_dia']
            vagas = request.form['vagas']
            new_funcao = Funcao(nome=nome, descricao=descricao, salario=salario, horas_por_dia=horas_por_dia, vagas=vagas)
            db.session.add(new_funcao)
            db.session.commit()
            flash('Função adicionada com sucesso!', 'success')
            return redirect(url_for('admin'))

    produtos = Produto.query.all()
    funcoes = Funcao.query.all()
    return render_template('admin.html', produtos=produtos, funcoes=funcoes)

@app.route('/produto/editar/<int:product_id>', methods=['GET', 'POST'])
@login_required
def produto_edit(product_id):
    produto = Produto.query.get_or_404(product_id)
    if request.method == 'POST':
        produto.nome = request.form['nome']
        produto.preco = request.form['preco']
        produto.desc = request.form['desc']
        produto.estoque = request.form['estoque']
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template('product_form.html', produto=produto)

@app.route('/produto/deletar/<int:product_id>', methods=['POST'])
@login_required
def produto_delete(product_id):
    produto = Produto.query.get_or_404(product_id)
    db.session.delete(produto)
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/pagusuario', methods=['GET'])
@login_required
def pagusuario():
    produtos = Produto.query.all()
    listausu = ListaCompra.query.filter_by(id_usu=current_user.id).all()
    return render_template('pagusuario.html', produtos=produtos, listausu=listausu)

@app.route('/adicionar_a_lista/<int:product_id>', methods=['POST'])
@login_required
def adicionar_a_lista(product_id):
    nova_entrada = ListaCompra(id_usu=current_user.id, product_id=product_id)
    db.session.add(nova_entrada)
    db.session.commit()
    return redirect(url_for('pagusuario'))

@app.route('/remover_da_lista/<int:item_id>', methods=['POST'])
@login_required
def remover_da_lista(item_id):
    item = ListaCompra.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('pagusuario'))

@app.route('/admin_funcionarios', methods=['GET', 'POST'])
@login_required
def admin_funcionarios():
    if request.method == 'POST':
        nomeusu = request.form['nomeusu']
        senha = request.form['senha']
        hashed_password = generate_password_hash(senha)
        new_funcionario = Funcionario(nomeusu=nomeusu, senha=hashed_password)
        db.session.add(new_funcionario)
        db.session.commit()
        return redirect(url_for('admin_funcionarios'))
    funcionarios = Funcionario.query.all()
    return render_template('admin_funcionarios.html', funcionarios=funcionarios)

@app.route('/admin_funcoes', methods=['GET', 'POST'])
@login_required
def admin_funcoes():
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        salario = request.form['salario']
        horas_por_dia = request.form['horas_por_dia']
        vagas = request.form['vagas']
        new_funcao = Funcao(nome=nome, descricao=descricao, salario=salario, horas_por_dia=horas_por_dia, vagas=vagas)
        db.session.add(new_funcao)
        db.session.commit()
        return redirect(url_for('admin_funcoes'))
    funcoes = Funcao.query.all()
    return render_template('admin_funcoes.html', funcoes=funcoes)

@app.route('/funcionario/adicionar_funcao/<int:funcionario_id>/<int:funcao_id>', methods=['POST'])
@login_required
def adicionar_funcao(funcionario_id, funcao_id):
    nova_funcao = FuncionarioFuncao(funcionario_id=funcionario_id, funcao_id=funcao_id)
    db.session.add(nova_funcao)
    db.session.commit()
    return redirect(url_for('funcionario_page'))  

@app.route('/funcionario/remover_funcao/<int:funcionario_funcao_id>', methods=['POST'])
@login_required
def remover_funcao(funcionario_funcao_id):
    funcionario_funcao = FuncionarioFuncao.query.get_or_404(funcionario_funcao_id)
    db.session.delete(funcionario_funcao)
    db.session.commit()
    return redirect(url_for('funcionario_page')) 

@app.route('/colocar_funcionario', methods=['GET', 'POST'])
def colocar_funcionario():
    if request.method == 'POST':
        nomeusu = request.form['nomeusu']
        senha = request.form['senha']
        hashed_password = generate_password_hash(senha)
        new_funcionario = Funcionario(nomeusu=nomeusu, senha=hashed_password)
        db.session.add(new_funcionario)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('colocar_funcionario.html')

@app.route('/funcionario', methods=['GET'])
@login_required
def funcionario_page():
    funcoes = Funcao.query.all()
    funcionario_funcoes = FuncionarioFuncao.query.filter_by(funcionario_id=current_user.id).all()
    return render_template('funcionario.html', funcoes=funcoes, funcionario_funcoes=funcionario_funcoes)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)