from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail, Message
import pandas as pd  
from models import db, Toner, Movement, Sector, Preferences
#import from controlers
from controlers.movementcontroler import all_movements, rev_movement, new_movement
from controlers.tonercontroler import all_toners, one_toner, plus_toner, less_toner, add_toner
from controlers.sectorcontroler import all_sectors, del_sector, add_sector
from controlers.validationcontroler import validar_salida_toner, validar_entrada_toner, validar_entrada_sector
#import from bluuprint
from routes.insumos_routes import insumos_bp
from routes.movimientos_routes import movements_bp
from routes.sectores_routes import sector_bp

app = Flask(__name__)
app.config.from_object('config.Config')

db.init_app(app)
migrate = Migrate(app, db)
mail = Mail(app)

app.register_blueprint(insumos_bp)
app.register_blueprint(movements_bp)
app.register_blueprint(sector_bp)


@app.route('/')
def index():
    return render_template('index.html', toners = all_toners(), sectors = all_sectors())

def enviar_correo_pedido(proveedor_email, toners):
    msg = Message(subject='Solicitud de Insumos',
                  sender=app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[proveedor_email])
    msg.body = "Solicitamos la cotización de los siguientes insumos:\n\n"
    for toner in toners:
        cantidad_necesaria = toner.preferences.min_stock - toner.cantidad_actual
        msg.body += f"Modelo: {toner.modelo}, Cantidad necesaria: {cantidad_necesaria}\n"

    try:
        mail.send(msg)
    except Exception as e:
        print(f"Error al enviar el correo: {e}")

@app.route('/preferences')
def preferences():
    return render_template('preferences.html', all_toners())

@app.route('/set_preferences', methods=['POST'])
def set_preferences():
    toner_id = request.form.get('toner_id')
    min_stock = request.form.get('min_stock', type=int)
    proveedor_email = request.form.get('proveedor_email')

    preferences = Preferences.query.filter_by(toner_id=toner_id).first()
    if preferences:
        preferences.min_stock = min_stock
        preferences.proveedor_email = proveedor_email
    else:
        preferences = Preferences(toner_id=toner_id, min_stock=min_stock, proveedor_email=proveedor_email)
        db.session.add(preferences)

    db.session.commit()
    flash('Preferencias actualizadas con éxito', 'success')
    return redirect(url_for('preferences'))

@app.route('/statistics')
def statistics():
    consumos_por_sector = db.session.query(
        Sector.nombre, db.func.sum(Movement.cantidad).label('total_consumido')
    ).join(Movement).filter(Movement.tipo == 'Salida', Movement.reverted == False).group_by(Sector.nombre).all()

    df_consumos = pd.DataFrame(consumos_por_sector, columns=['nombre', 'total_consumido'])
    graph_html = df_consumos.to_html(classes='table table-bordered')

    return render_template('statistics.html', graph_html=graph_html)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
