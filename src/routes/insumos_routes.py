from flask import Blueprint, render_template, redirect, url_for, flash, request
from controlers.tonercontroler import all_toners, one_toner, add_toner, less_toner, plus_toner
from controlers.sectorcontroler import all_sectors
from controlers.movementcontroler import new_movement
from controlers.validationcontroler import validar_entrada_sector, validar_entrada_toner, validar_salida_toner

insumos_bp = Blueprint('insumos', __name__)

@insumos_bp.route('/insunmos', methods=['GET','POST'])
def insumo():
    return render_template('insumos.html', insumos = all_toners())

@insumos_bp.route('/salida_insunmo', methods=['GET','POST'])
def salida_insumo():
    if request.method == 'POST':
        toner_id = request.form.get('toner_id')
        sector_id = request.form.get('sector_id')
        cantidad = request.form.get('cantidad', type=int)

        if validar_salida_toner(toner_id, sector_id, cantidad):    
            if less_toner(toner_id, cantidad):
                return redirect(url_for('salida_insumo'))

            new_movement('Salida', cantidad, toner_id, sector_id)

    return render_template('salida_insumo.html', toners = all_toners(), sectors = all_sectors())

@insumos_bp.route('/entrada_insumo', methods=['GET','POST'])
def entrada_insumo():
    if request.method == 'POST':
        toner_id = request.form.get('toner_id')
        cantidad = request.form.get('cantidad', type=int)
        
        if validar_entrada_toner(toner_id, cantidad):
            if plus_toner(toner_id, cantidad):
                return redirect(url_for('entrada_insumo'))
        
            new_movement('Entrada', cantidad, toner_id)
    return render_template('entrada_insumo.html', toners= all_toners())

@insumos_bp.route('/solicitar_insumos', methods=['GET', 'POST'])
def solicitar_insumos():
    if request.method == 'POST':
        toner_ids = request.form.getlist('toners')
        pedidos = {}

        for toner_id in toner_ids:
            toner = one_toner(toner_id)
            if toner.preferences.proveedor_email in pedidos:
                pedidos[toner.preferences.proveedor_email].insumos_bpend(toner)
            else:
                pedidos[toner.preferences.proveedor_email] = [toner]

        #for proveedor_email, toners in pedidos.items():
            #enviar_correo_pedido(proveedor_email, toners)

        flash('Solicitud de insumos enviada con éxito', 'success')
        return redirect(url_for('index'))
    return render_template('solicitar_insumos.html', toners=all_toners())

insumos_bp.route('/alta_insumos', methods=['POST'])
def alta_insumos():
    if request.method == 'POST':
        insumo_nombre = request.form.get('insumo_nombre', type= str)

        if validar_entrada_sector(insumo_nombre):              
            if add_toner(insumo_nombre):
                flash('insumo registrado exitosamente.', 'success')
                return redirect(url_for('insumos'))         
            else:
                flash(f'Error al registrar el insumo', 'danger')
        
        return redirect(url_for('insumos'))
